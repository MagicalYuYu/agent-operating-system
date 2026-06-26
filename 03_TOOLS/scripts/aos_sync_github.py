#!/usr/bin/env python3
"""
AOS GitHub 同步脚本
用法：python aos_sync_github.py [--dry-run] [--verify]

功能：
  将 d:\AOS\（工作目录）的框架文件同步到 d:\github\agent-operating-system\（上传目录）
  自动排除敏感数据、实际项目内容、临时文件
  同步前执行安全检查，同步后输出统计报告
  包含敏感关键词扫描和新增文件检查

选项：
  无参数    — 执行同步
  --dry-run — 仅显示将要同步的文件列表，不实际复制
  --verify  — 仅验证目标目录的安全性（检查是否有敏感文件残留）
"""

import os
import sys
import re
import shutil
import hashlib
from pathlib import Path
from datetime import datetime

# ──────────────────────────────────────────────
# 路径定义
# ──────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
WORK_DIR = SCRIPT_DIR.parent.parent  # d:\AOS\
GITHUB_DIR = Path(r"d:\github\agent-operating-system")

# ──────────────────────────────────────────────
# 排除规则：以下文件/目录不同步到上传目录
# ──────────────────────────────────────────────

# 完全排除的目录（不复制）
EXCLUDE_DIRS = {
    ".git",
    ".trae",
    "__pycache__",
    "node_modules",
    "05_CACHE",        # 临时数据
    "06_LOGS",         # 运行日志（仅保留 README.md）
    "02_SANDBOX",      # 实验数据（仅保留 README.md）
    "08_INBOX",        # 外部输入（仅保留 README.md）
    "release",         # 07_EXPORTS 下的发布包（含 exe/DLL/用户数据）
    "logs",            # 运行时日志目录（小写，AOS Viewer 等工具生成）
    "build",           # PyInstaller 构建缓存目录（03_TOOLS/aos_viewer/build/）
    "dist",            # PyInstaller 输出目录（03_TOOLS/aos_viewer/dist/）
}

# 01_PROJECTS 下仅保留示例项目和 README.md
PROJECTS_KEEP = {"_example_game_localization", "_example_cli_tool", "_example_plugin_suite", "README.md"}

# 04_MEMORY 下的排除规则
MEMORY_EXCLUDE = {
    "credentials.json",           # 明文凭据
    "user",                       # 用户画像（个人隐私）
    "feedback",                   # 个人经验记录
    "agent_pool",                 # Agent 任务池（运行时数据）
}

# 04_MEMORY 下保留的文件
MEMORY_KEEP_FILES = {
    "INDEX.md",
    "README.md",
}

# 04_MEMORY 下保留的子目录（仅保留其中的 README.md）
MEMORY_KEEP_DIRS = {
    "loop_memory",
    "skill_memory",
    "reference",  # 保留参考模板
}

# 09_REFERENCE 下排除的（如果有敏感内容的话）
# 当前 09_REFERENCE 全部保留（已脱敏的知识库）

# 根目录下排除的文件
EXCLUDE_FILES = {
    ".gitignore",  # 上传目录有自己的 .gitignore
    "AOS_Viewer.bat",  # 已弃用 BAT 启动器（用户要求只保留 EXE，最轻量化）
}

# 额外排除的文件（含个人数据的工作产出）
EXTRA_EXCLUDE_FILES = {
    "07_EXPORTS/github-release-prompt.md",     # 含发布流程个人信息
    "07_EXPORTS/AOS/creative_proposal/AOS_creative_proposal.html",  # 含个人信息
    "07_EXPORTS/AOS/domain_config/custom-domain-setup-guide.md",    # 含域名信息
    "07_EXPORTS/AOS/bishoujo_web_design_guide/card-game-web-design-guide.md",  # 私有项目设计指南
    "07_EXPORTS/astrbot/deployment/deploy_bishoujo_20260623.md",    # 私有项目部署
    "07_EXPORTS/bishoujo-web/bishoujo_web_status_report.md",        # 私有项目报告
    "07_EXPORTS/bishoujo-web/heat_distribution_report.json",        # 私有项目数据
    "07_EXPORTS/bishoujo-web/web_gacha_astrbot_integration_plan.md", # 私有项目规划
    "07_EXPORTS/aos_viewer/RELEASE_ANALYSIS_1.1.0.md",              # 含私有项目分析
    # 2026-06-26 已迁移：AOS_creative_proposal.html → 02_SANDBOX/，domain_setup_result.md → 06_LOGS/aos_system/
    # 这两个目录已在 EXCLUDE_DIRS 中完全排除，无需在此重复声明
    "04_MEMORY/project/proj_astrbot.md",       # 实际项目
    "04_MEMORY/project/proj_clash_omega.md",   # 实际项目
    "04_MEMORY/project/proj_oncepad.md",       # 实际项目
    # AOS Viewer 含实际项目数据的文件（不同步到 GitHub，上传时用 example_data.js 替换）
    "03_TOOLS/aos_viewer/prototype/js/data.js",           # 含实际项目数据（astrbot/bishoujo/clash_omega 等）
    "03_TOOLS/aos_viewer/prototype/js/data_content.js",   # 含实际项目大文本内容
}

# AOS Viewer 示例数据文件（替换为只含 _example_game_localization 的示例版本）
VIEWER_EXAMPLE_DATA = "03_TOOLS/aos_viewer/prototype/js/data.js"

# 需要内容脱敏的文件（同步后对目标目录中的文件执行内容替换）
DESENSITIZE_FILES = {
    "04_MEMORY/INDEX.md": "index",
    "09_REFERENCE/_index.md": "reference_index",  # 知识库索引：剥离 xiaolin 私有收藏行
    "00_BOOT/SYSTEM_STATE.md": "system_state",
    "00_BOOT/SKILL_REGISTRY.md": "skill_registry",
    "04_MEMORY/global_memory.md": "global_memory",
    "04_MEMORY/project/proj_aos_v1_status.md": "proj_aos_status",  # 移除开发过程描述
    "AGENTS.md": "agents_dual_machine",  # 剥离双机环境章节
}

# ──────────────────────────────────────────────
# 安全检查：同步后目标目录禁止存在的文件
# ──────────────────────────────────────────────

SENSITIVE_FILES = [
    "04_MEMORY/credentials.json",
    "04_MEMORY/user/user_profile.md",
    "04_MEMORY/feedback",
    "04_MEMORY/agent_pool",       # Agent 任务池（运行时数据）
    "99_ARCHIVE/migration",       # 迁移扫描数据（含用户文件路径）
    # proj_aos_v1_status.md 已脱敏后上传，不再列入敏感文件
]

SENSITIVE_PATTERNS = [
    "credentials.json",
    "user_profile.md",
    "08_INBOX/migration",
    "06_LOGS/",
    "data_content.js",  # AOS Viewer 含实际项目大文本内容
    "xiaolin-",         # 小林coding 私有收藏文章（15篇，禁止上传）
    "web-template-specification",  # 网页模板规范文档（用户私有开发经验）
    "debug.log",        # 根目录运行时日志（搜狗输入法等生成）
]


def should_exclude_dir(rel_path: Path) -> bool:
    """判断目录是否应该完全排除"""
    parts = rel_path.parts
    for excl in EXCLUDE_DIRS:
        if excl in parts:
            return True
    return False


def should_exclude_file(rel_path: Path) -> bool:
    """判断文件是否应该排除"""
    parts = rel_path.parts
    filename = rel_path.name

    # 根目录排除文件
    if len(parts) == 1 and filename in EXCLUDE_FILES:
        return True

    # 额外排除的文件（含个人数据的工作产出）
    rel_str = str(rel_path).replace("\\", "/")
    if rel_str in EXTRA_EXCLUDE_FILES:
        return True

    # 01_PROJECTS 下仅保留 _example_game_localization 和 README.md
    if len(parts) >= 2 and parts[0] == "01_PROJECTS":
        if parts[1] not in PROJECTS_KEEP:
            return True

    # 04_MEMORY 排除规则
    if len(parts) >= 2 and parts[0] == "04_MEMORY":
        if filename in MEMORY_EXCLUDE:
            return True
        if len(parts) >= 2 and parts[1] in MEMORY_EXCLUDE:
            return True
        # project 目录下保留 proj__example_game_localization.md 和 proj_aos_v1_status.md
        if parts[1] == "project":
            if filename not in ("proj__example_game_localization.md", "proj_aos_v1_status.md"):
                return True

    # 99_ARCHIVE/migration/ 排除（含迁移扫描数据，可能含用户文件路径）
    if len(parts) >= 3 and parts[0] == "99_ARCHIVE" and parts[1] == "migration":
        return True

    # 09_REFERENCE/system/ 下的 xiaolin-* 文件排除（私有收藏，不上传 GitHub）
    if len(parts) >= 3 and parts[0] == "09_REFERENCE" and parts[1] == "system":
        if filename.startswith("xiaolin-"):
            return True

    # 09_REFERENCE/web/ 排除（网页模板规范文档为用户私有开发经验，不上传 GitHub）
    if len(parts) >= 3 and parts[0] == "09_REFERENCE" and parts[1] == "web":
        return True

    # 排除 .pyc 文件
    if filename.endswith(".pyc"):
        return True

    # 排除 .log 文件（运行时日志，如搜狗输入法 debug.log 等）
    if filename.endswith(".log"):
        return True

    # 排除备份文件（*.backup_YYYYMMDD 格式，如 aos_viewer.ico.backup_20260625）
    if ".backup_" in filename:
        return True

    return False


def collect_files(src: Path) -> list:
    """收集需要同步的文件列表"""
    files_to_sync = []
    files_excluded = []

    for root, dirs, filenames in os.walk(src):
        root_path = Path(root)
        rel_root = root_path.relative_to(src)

        # 排除目录
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and d != ".git"]

        for filename in filenames:
            src_file = root_path / filename
            rel_path = src_file.relative_to(src)

            if should_exclude_file(rel_path):
                files_excluded.append(rel_path)
            else:
                files_to_sync.append(rel_path)

    return files_to_sync, files_excluded


def sync_file(src: Path, dst: Path, dry_run=False):
    """同步单个文件"""
    if dry_run:
        return

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def verify_security(github_dir: Path) -> list:
    """验证目标目录的安全性，返回违规列表"""
    violations = []

    if not github_dir.exists():
        return ["目标目录不存在"]

    for root, dirs, filenames in os.walk(github_dir):
        root_path = Path(root)
        rel_root = root_path.relative_to(github_dir)

        for filename in filenames:
            rel_file = rel_root / filename
            rel_str = str(rel_file).replace("\\", "/")

            # 检查敏感文件
            for pattern in SENSITIVE_PATTERNS:
                if pattern in rel_str:
                    violations.append(f"敏感文件残留: {rel_str}")
                    break

        # 检查敏感目录
        for d in dirs[:]:
            rel_dir = rel_root / d
            rel_str = str(rel_dir).replace("\\", "/")
            for pattern in SENSITIVE_PATTERNS:
                if pattern in rel_str:
                    violations.append(f"敏感目录残留: {rel_str}")
                    break

    return violations


def desensitize_file(github_dir: Path, rel_path: str, desensitize_type: str) -> list:
    """对目标目录中的文件执行内容脱敏，返回修改列表"""
    file_path = github_dir / rel_path
    if not file_path.exists():
        return [f"脱敏跳过（文件不存在）: {rel_path}"]

    content = file_path.read_text(encoding="utf-8")
    original = content
    changes = []

    if desensitize_type == "index":
        # INDEX.md 脱敏：移除 user/feedback 部分，project 仅保留框架级
        lines = content.split("\n")
        new_lines = []
        skip_section = False
        for line in lines:
            if line.strip() == "## user":
                skip_section = True
                new_lines.append("## user")
                new_lines.append("<!-- 上传版：用户画像不包含在 GitHub 仓库中 -->")
                continue
            if line.strip() == "## feedback":
                skip_section = True
                new_lines.append("## feedback")
                new_lines.append("<!-- 上传版：个人经验记录不包含在 GitHub 仓库中 -->")
                continue
            if line.strip() == "## reference":
                skip_section = False
                new_lines.append(line)
                continue
            if line.strip() == "## project":
                skip_section = False
                new_lines.append(line)
                continue
            if skip_section:
                # 跳过 user/feedback 部分的所有条目
                if line.startswith("- ["):
                    continue
            else:
                # project 部分：仅保留 proj-aos-v1-status 和 proj-example-project
                if line.startswith("- [proj-"):
                    if "proj-aos-v1-status" in line:
                        # 替换为模板描述
                        line = "- [proj-aos-v1-status](project/proj_aos_v1_status.md) — AOS v1.1.0 发布版，含可视化界面（AOS Viewer），2个Skill(WKIS+Migration)已注册"
                    elif "proj-example-project" in line:
                        pass  # 保留原样
                    else:
                        continue  # 移除其他项目引用
            new_lines.append(line)
        content = "\n".join(new_lines)
        if content != original:
            changes.append(f"{rel_path}: 移除 user/feedback/实际项目引用，保留框架级索引")

    elif desensitize_type == "reference_index":
        # 09_REFERENCE/_index.md 脱敏：剥离 xiaolin-* 私有收藏行 + web-template-specification 索引行
        lines = content.split("\n")
        new_lines = []
        removed_count = 0
        for line in lines:
            # 索引表行格式：| slug | ... |，剥离 xiaolin- 开头的行
            if line.strip().startswith("| xiaolin-"):
                removed_count += 1
                continue
            # 剥离 web-template-specification 索引行（用户私有开发经验，不上传 GitHub）
            if line.strip().startswith("| web-template-specification"):
                removed_count += 1
                continue
            new_lines.append(line)
        content = "\n".join(new_lines)
        if removed_count > 0:
            changes.append(f"{rel_path}: 剥离 {removed_count} 条私有索引行（xiaolin + web-template）")

    elif desensitize_type == "system_state":
        # SYSTEM_STATE.md 脱敏：统计数据归零 + 移除用户项目事件
        # 1. 统计数据归零（使用正则通用匹配，不依赖具体数字）
        stats_patterns = [
            (r"\| 已注册 Skill 数 \| \d+ \|", "| 已注册 Skill 数 | 0 |"),
            (r"\| 活跃 Loop 数 \| \d+ \|", "| 活跃 Loop 数 | 0 |"),
            (r"\| 已完成 Loop 周期 \| \d+ \|", "| 已完成 Loop 周期 | 0 |"),
            (r"\| 活跃 Agent 数 \| \d+ \|", "| 活跃 Agent 数 | 0 |"),
            (r"\| 已处理任务数 \| \d+ \|", "| 已处理任务数 | 0 |"),
            (r"\| 系统错误数 \| \d+ \|", "| 系统错误数 | 0 |"),
            (r"\| 记忆索引条目数 \| \d+ \|", "| 记忆索引条目数 | 0 |"),
            (r"\| 反馈记录数 \| \d+ \|", "| 反馈记录数 | 0 |"),
        ]
        for pattern, replacement in stats_patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                changes.append(f"{rel_path}: 统计数据归零 ({pattern})")
                content = new_content

        # 2. 组件状态中的 Skill 数量重置
        new_content = re.sub(
            r"\| Skill System \| ACTIVE \| \d+ Skill 已注册",
            "| Skill System | ACTIVE | 0 Skill 已注册",
            content,
        )
        if new_content != content:
            content = new_content
            changes.append(f"{rel_path}: 组件状态 Skill 数重置为 0")

        # 3. 移除事件日志中的用户项目事件
        user_keywords = [
            "AstrBot", "astrbot", "bishoujo", "clash_omega", "ClashOmega",
            "OncePad", "oncepad", "MagicalYu", "kennylimz",
        ]
        lines = content.split("\n")
        new_lines = []
        removed_events = 0
        for line in lines:
            # 事件日志行格式：| YYYY-MM-DD | EVENT_TYPE | 描述 |
            if line.strip().startswith("| 2026-") and "|" in line:
                desc_lower = line.lower()
                if any(kw.lower() in desc_lower for kw in user_keywords):
                    removed_events += 1
                    continue
                # 跳过含用户运行时统计变更的事件
                if "记忆索引" in line and "→" in line:
                    removed_events += 1
                    continue
            new_lines.append(line)
        content = "\n".join(new_lines)
        if removed_events > 0:
            changes.append(f"{rel_path}: 移除 {removed_events} 条用户项目事件")

        # 4. 清理自检记录中的用户项目引用
        user_inspection_keywords = ["bishoujo", "astrbot", "clash_omega", "oncepad"]
        lines = content.split("\n")
        new_lines = []
        removed_inspections = 0
        for line in lines:
            if line.strip().startswith("| 2026-") and "|" in line and "自检" not in line and "巡检" in line:
                desc_lower = line.lower()
                if any(kw in desc_lower for kw in user_inspection_keywords):
                    # 替换为通用描述
                    line = "| 2026-06-25 | 首次正式巡检 | PASS | 处置临时文件清理、目录分层规范化、归档整理，新增巡检规范 |"
            new_lines.append(line)
        content = "\n".join(new_lines)

        # 5. 最后更新时间改为模板值
        content = re.sub(
            r"\| 最后更新 \| 2026-\d{2}-\d{2}（[^|]+）\|",
            "| 最后更新 | 2026-06-XX（1.1.0 发布版） |",
            content,
        )

        if content != original and not changes:
            changes.append(f"{rel_path}: 通用脱敏处理")

    elif desensitize_type == "skill_registry":
        # SKILL_REGISTRY.md 脱敏：call_count 重置为 0
        content = re.sub(r'"call_count":\s*\d+', '"call_count": 0', content)
        content = re.sub(r'"success_rate":\s*[\d.]+', '"success_rate": null', content)
        if content != original:
            changes.append(f"{rel_path}: call_count 重置为 0, success_rate 重置为 null")

    elif desensitize_type == "global_memory":
        # global_memory.md：保留框架级经验，无需特殊处理
        pass

    elif desensitize_type == "proj_aos_status":
        # proj_aos_v1_status.md 脱敏：移除开发过程描述，保留功能清单和缺陷清单
        # 1. 版本号更新为 1.1.0
        content = content.replace("| 版本 | 1.0.0 |", "| 版本 | 1.1.0 |")
        # 2. 移除"记忆索引条目数"具体值（用户运行时数据）
        content = re.sub(
            r"\| 记忆索引条目数 \| \d+ \|.*",
            "| 记忆索引条目数 | 0（用户运行时填充） | 2026-06-21 |",
            content,
        )
        # 3. 更新 GitHub 发布状态（正则通用匹配，兼容历史值）
        content = re.sub(
            r"\| GitHub 发布状态 \| [^|]+\|",
            "| GitHub 发布状态 | v1.1.0 发布 |",
            content,
        )
        # 4. 更新 AOS Viewer 状态（移除开发过程描述）
        content = re.sub(
            r"\| AOS Viewer 状态 \| [^|]+\|",
            "| AOS Viewer 状态 | v1.1.0 新增可视化界面 |",
            content,
        )
        # 5. 移除"1.1.0 发布策略"行（含内部报告引用）
        content = re.sub(
            r"\| 1\.1\.0 发布策略 \| [^|]+\|.*\n",
            "",
            content,
        )
        # 6. 已知缺陷标题更新
        content = content.replace("## 已知缺陷（v1.0.0）", "## 已知缺陷（v1.1.0）")
        if content != original:
            changes.append(f"{rel_path}: 版本号更新为1.1.0 + 移除开发过程描述")

    elif desensitize_type == "agents_dual_machine":
        # AGENTS.md 脱敏：剥离"双机环境"章节（含 \\Ruoyu、AstrBot、NapCat 等私人信息）
        # 章节范围：从 "## 双机环境" 开始到下一个 "## " 或文件末尾
        lines = content.split("\n")
        new_lines = []
        skip_section = False
        removed_count = 0
        for line in lines:
            if line.strip().startswith("## 双机环境"):
                skip_section = True
                removed_count += 1
                continue
            if skip_section:
                if line.strip().startswith("## ") and not line.strip().startswith("## 双机环境"):
                    skip_section = False
                    new_lines.append(line)
                else:
                    removed_count += 1
            else:
                new_lines.append(line)
        content = "\n".join(new_lines)
        # 清理多余空行
        content = re.sub(r"\n{3,}", "\n\n", content)
        if content != original:
            changes.append(f"{rel_path}: 剥离双机环境章节（移除 {removed_count} 行）")

    if content != original:
        file_path.write_text(content, encoding="utf-8")

    return changes


def run_sync(dry_run=False):
    """执行同步"""
    print("=" * 60)
    print(f"AOS GitHub 同步 — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"工作目录: {WORK_DIR}")
    print(f"上传目录: {GITHUB_DIR}")
    print(f"模式: {'DRY-RUN（仅预览）' if dry_run else '同步'}")
    print("=" * 60)

    if not WORK_DIR.exists():
        print(f"错误: 工作目录不存在: {WORK_DIR}")
        return 1

    # 收集文件
    print("\n[1/5] 扫描文件...")
    files_to_sync, files_excluded = collect_files(WORK_DIR)
    print(f"  待同步: {len(files_to_sync)} 个文件")
    print(f"  已排除: {len(files_excluded)} 个文件")

    # 显示排除的关键文件
    key_excluded = [f for f in files_excluded if any(
        s in str(f) for s in ["credentials", "user_profile", "feedback", "migration"]
    )]
    if key_excluded:
        print(f"\n  关键排除文件:")
        for f in key_excluded[:10]:
            print(f"    - {f}")

    if dry_run:
        print(f"\n[DRY-RUN] 以下文件将被同步到 {GITHUB_DIR}:")
        for f in files_to_sync:
            print(f"  {f}")
        print(f"\n总计: {len(files_to_sync)} 个文件")
        return 0

    # 创建目标目录
    print(f"\n[2/5] 创建目标目录...")
    GITHUB_DIR.mkdir(parents=True, exist_ok=True)
    print(f"  {GITHUB_DIR} {'已存在' if GITHUB_DIR.exists() else '已创建'}")

    # 同步文件
    print(f"\n[3/5] 同步文件...")
    synced = 0
    failed = 0
    for rel_path in files_to_sync:
        src_file = WORK_DIR / rel_path
        dst_file = GITHUB_DIR / rel_path
        try:
            sync_file(src_file, dst_file)
            synced += 1
        except Exception as e:
            print(f"  失败: {rel_path} — {e}")
            failed += 1

    print(f"  成功: {synced} | 失败: {failed}")

    # 复制 AOS Viewer 示例数据（data.js 替换为脱敏版）
    print(f"\n[3.5/5] AOS Viewer 示例数据...")
    example_data_src = WORK_DIR / "07_EXPORTS" / "aos_viewer" / "example_data.js"
    data_js_dst = GITHUB_DIR / "03_TOOLS" / "aos_viewer" / "prototype" / "js" / "data.js"
    if example_data_src.exists():
        try:
            sync_file(example_data_src, data_js_dst)
            print(f"  ✓ 示例 data.js 已复制（{example_data_src.stat().st_size:,} 字节）")
            synced += 1
        except Exception as e:
            print(f"  失败: data.js 替换 — {e}")
            failed += 1
    else:
        print(f"  ⚠ 示例数据文件不存在: {example_data_src}")

    # 内容脱敏
    print(f"\n[4/5] 内容脱敏...")
    total_changes = []
    for rel_path, desensitize_type in DESENSITIZE_FILES.items():
        changes = desensitize_file(GITHUB_DIR, rel_path, desensitize_type)
        if changes:
            total_changes.extend(changes)
            for c in changes:
                print(f"  {c}")
        else:
            print(f"  {rel_path}: 无需脱敏")
    print(f"  脱敏变更: {len(total_changes)} 处")

    # 安全验证
    print(f"\n[5/5] 安全验证...")
    violations = verify_security(GITHUB_DIR)
    if violations:
        print(f"  警告: 发现 {len(violations)} 个安全问题:")
        for v in violations:
            print(f"    - {v}")
    else:
        print(f"  通过 — 无敏感文件残留")

    # 统计报告
    print("\n" + "=" * 60)
    print("同步完成")
    print(f"  同步文件: {synced}")
    print(f"  排除文件: {len(files_excluded)}")
    print(f"  失败: {failed}")
    print(f"  安全验证: {'通过' if not violations else '失败'}")
    print(f"  目标目录: {GITHUB_DIR}")
    print("=" * 60)

    return 0 if failed == 0 and not violations else 1


def run_verify():
    """仅执行安全验证"""
    print("=" * 60)
    print(f"AOS GitHub 安全验证 — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标目录: {GITHUB_DIR}")
    print("=" * 60)

    violations = verify_security(GITHUB_DIR)
    if violations:
        print(f"\n失败: 发现 {len(violations)} 个安全问题:")
        for v in violations:
            print(f"  - {v}")
    else:
        print(f"\n通过 — 无敏感文件残留")

    return 0 if not violations else 1


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.exit(run_verify())
    elif "--dry-run" in sys.argv:
        sys.exit(run_sync(dry_run=True))
    else:
        sys.exit(run_sync())
