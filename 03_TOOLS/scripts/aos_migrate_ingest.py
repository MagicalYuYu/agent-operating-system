#!/usr/bin/env python3
"""
AOS 迁移入库脚本
用法：python aos_migrate_ingest.py [--confirm]

选项：
  无参数    — 自动入库，冲突时暂停等待确认
  --confirm — 每个入库操作均需用户确认

功能：
1. 自动检测 AOS 根目录
2. 读取 08_INBOX/migration/classification_result.json
3. 入库前强制执行脱敏处理
4. 将分类后的内容写入 AOS 目录体系对应位置
5. 不覆盖已有文件（冲突时向用户确认）
6. 更新所有相关索引（INDEX.md / _index.md / 项目状态）
7. 更新迁移状态为 completed
8. 更新 SYSTEM_STATE.md 事件日志
"""

import os
import re
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# ── AOS 根目录自动检测 ──────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
AOS_ROOT = SCRIPT_DIR.parent.parent

# ── 目录常量 ────────────────────────────────────────────────
DIR_PROJECTS = AOS_ROOT / "01_PROJECTS"
DIR_SANDBOX = AOS_ROOT / "02_SANDBOX"
DIR_TOOLS = AOS_ROOT / "03_TOOLS"
DIR_MEMORY = AOS_ROOT / "04_MEMORY"
DIR_LOGS = AOS_ROOT / "06_LOGS"
DIR_INBOX = AOS_ROOT / "08_INBOX"
DIR_REFERENCE = AOS_ROOT / "09_REFERENCE"
MIGRATION_DIR = DIR_INBOX / "migration"
PENDING_DIR = DIR_SANDBOX / "migration_pending"

# ── 索引文件路径 ────────────────────────────────────────────
MEMORY_INDEX_PATH = DIR_MEMORY / "INDEX.md"
REFERENCE_INDEX_PATH = DIR_REFERENCE / "_index.md"
SYSTEM_STATE_PATH = AOS_ROOT / "00_BOOT" / "SYSTEM_STATE.md"

# ── 脱敏规则 ────────────────────────────────────────────────
DESENSITIZE_RULES = [
    # IP 地址
    (
        re.compile(r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b"),
        "[IP_ADDRESS]",
        "IP地址",
    ),
    # 密钥/Token（api_key, secret, token, password 后跟值）
    (
        re.compile(
            r"(?i)(api[_-]?key|secret|token|password|passwd|pwd|access[_-]?key|private[_-]?key)"
            r"\s*[：:=]\s*\S+",
        ),
        None,  # 特殊处理：保留键名，替换值
        "密钥/Token",
    ),
    # 内部 URL
    (
        re.compile(
            r"https?://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3})"
            r"(:\d+)?(/[^\s]*)?",
        ),
        "[INTERNAL_URL]",
        "内部URL",
    ),
    # 邮箱地址
    (
        re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"),
        "[EMAIL]",
        "邮箱地址",
    ),
    # 个人昵称模式（常见中英文昵称格式）
    # 匹配 "作者：xxx" / "by xxx" / "@nickname" 等模式
    (
        re.compile(r"(?i)(作者|by|author)\s*[：:]\s*[a-zA-Z0-9_\u4e00-\u9fff]{2,20}"),
        None,  # 特殊处理
        "个人昵称",
    ),
    (
        re.compile(r"@[a-zA-Z0-9_]{2,30}\b"),
        "[USER]",
        "个人昵称(@)",
    ),
]

# ── 统计计数器 ──────────────────────────────────────────────
stats = {
    "total": 0,
    "ingested": 0,
    "skipped": 0,
    "conflicts": 0,
    "desensitized": 0,
    "desensitize_details": {},
    "index_updates": 0,
    "errors": 0,
}


def print_step(step_num, total, name, status, target="", elapsed="", output_path=""):
    """可视化步骤输出"""
    print(f"┌─ [步骤 {step_num}/{total}] {name} ─{'─' * max(1, 40 - len(name))}┐")
    print(f"│ 状态：{status}")
    if target:
        print(f"│ 目标：{target}")
    if elapsed:
        print(f"│ 耗时：{elapsed}")
    if output_path:
        print(f"│ 产出：{output_path}")
    print(f"└{'─' * 60}┘")


def detect_aos_root():
    """验证 AOS 根目录是否有效"""
    required_dirs = ["00_BOOT", "03_TOOLS", "04_MEMORY", "08_INBOX"]
    for d in required_dirs:
        if not (AOS_ROOT / d).exists():
            print(f"[错误] 未找到 AOS 必要目录：{d}")
            print(f"  当前检测的根目录：{AOS_ROOT}")
            print(f"  请确认脚本位于 03_TOOLS/scripts/ 下")
            sys.exit(1)
    return AOS_ROOT


def desensitize_content(content):
    """对内容执行脱敏处理"""
    result = content
    desensitize_count = 0

    for pattern, replacement, label in DESENSITIZE_RULES:
        matches = list(pattern.finditer(result))
        if not matches:
            continue

        if replacement is not None:
            # 直接替换模式
            count = len(matches)
            result = pattern.sub(replacement, result)
        else:
            # 特殊处理模式
            count = 0
            if "密钥" in label:
                # 保留键名，替换值部分
                def redact_key_value(match):
                    nonlocal count
                    count += 1
                    key_part = match.group(1)
                    return f"{key_part}=[REDACTED_KEY]"
                result = pattern.sub(redact_key_value, result)
            elif "昵称" in label and "by" in pattern.pattern.lower():
                # 保留标签，替换名字
                def redact_author(match):
                    nonlocal count
                    count += 1
                    label_part = match.group(1)
                    return f"{label_part}：[USER]"
                result = pattern.sub(redact_author, result)
            else:
                count = len(matches)

        if count > 0:
            desensitize_count += count
            stats["desensitize_details"][label] = stats["desensitize_details"].get(label, 0) + count

    return result, desensitize_count


def load_classification_result():
    """加载分类结果"""
    result_path = MIGRATION_DIR / "classification_result.json"

    if not result_path.exists():
        print(f"[错误] 分类结果文件不存在：{result_path}")
        print(f"  请先运行 python aos_migrate_classify.py")
        sys.exit(1)

    try:
        with open(result_path, "r", encoding="utf-8") as f:
            result = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[错误] 分类结果文件格式错误：{e}")
        sys.exit(1)

    # 检查是否已完成入库
    if result.get("ingestion_status") == "completed":
        print(f"[警告] 分类结果已标记为 completed，重复入库可能覆盖文件")
        response = input("是否继续？(y/N)：").strip().lower()
        if response != "y":
            print("已取消入库")
            sys.exit(0)

    return result


def load_source_content(source_file):
    """加载源文件内容"""
    source_path = MIGRATION_DIR / source_file
    if not source_path.exists():
        print(f"  [警告] 源文件不存在：{source_file}")
        return None

    try:
        return source_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  [警告] 读取源文件失败：{source_file} ({e})")
        return None


def confirm_action(message, confirm_mode):
    """确认操作"""
    if not confirm_mode:
        return True
    response = input(f"  确认：{message} (y/N)：").strip().lower()
    return response == "y"


def write_to_target(content, target_path_str, confirm_mode):
    """将内容写入目标路径，处理冲突"""
    target_path = Path(target_path_str)

    # 确保父目录存在
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # 检查文件是否已存在
    if target_path.exists():
        stats["conflicts"] += 1
        existing_size = target_path.stat().st_size
        print(f"  [冲突] 目标文件已存在：{target_path.relative_to(AOS_ROOT)}")
        print(f"    现有文件大小：{existing_size} 字节")

        response = input(f"  覆盖/跳过/追加？(o/s/a)：").strip().lower()
        if response == "o":
            if not confirm_action(f"覆盖 {target_path.relative_to(AOS_ROOT)}", confirm_mode):
                print(f"  → 跳过")
                stats["skipped"] += 1
                return False
        elif response == "a":
            # 追加模式
            try:
                existing = target_path.read_text(encoding="utf-8")
                separator = f"\n\n---\n\n# 迁移追加内容（{datetime.now().strftime('%Y-%m-%d %H:%M')}）\n\n"
                new_content = existing + separator + content
                target_path.write_text(new_content, encoding="utf-8")
                print(f"  → 追加到现有文件")
                stats["ingested"] += 1
                return True
            except Exception as e:
                print(f"  [错误] 追加失败：{e}")
                stats["errors"] += 1
                return False
        else:
            print(f"  → 跳过")
            stats["skipped"] += 1
            return False

    # 写入文件
    try:
        target_path.write_text(content, encoding="utf-8")
        print(f"  → 写入：{target_path.relative_to(AOS_ROOT)}")
        stats["ingested"] += 1
        return True
    except Exception as e:
        print(f"  [错误] 写入失败：{e}")
        stats["errors"] += 1
        return False


def update_memory_index(classified_items):
    """更新 04_MEMORY/INDEX.md"""
    if not MEMORY_INDEX_PATH.exists():
        print(f"  [警告] INDEX.md 不存在，跳过更新")
        return

    try:
        content = MEMORY_INDEX_PATH.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  [警告] 读取 INDEX.md 失败：{e}")
        return

    new_entries = []

    for item in classified_items:
        category = item["category"]
        target_path = Path(item["target_path"])

        if category == "feedback":
            # 添加到 feedback 段
            slug = target_path.stem
            rel_path = f"feedback/{target_path.name}"
            description = item["filename"][:80]
            entry_line = f"- [{slug}]({rel_path}) — {description}"
            if entry_line not in content:
                new_entries.append(("feedback", entry_line))

        elif category == "project_status":
            # 添加到 project 段
            slug = target_path.stem
            rel_path = f"project/{target_path.name}"
            description = item["filename"][:80]
            entry_line = f"- [{slug}]({rel_path}) — {description}"
            if entry_line not in content:
                new_entries.append(("project", entry_line))

    if not new_entries:
        return

    # 按段落插入新条目
    lines = content.split("\n")
    section_positions = {}
    for i, line in enumerate(lines):
        if line.startswith("## "):
            section_positions[line[3:].strip().lower()] = i

    # 从后往前插入，避免行号偏移
    for section, entry in reversed(new_entries):
        section_key = section
        if section_key in section_positions:
            # 找到该段的最后一行
            insert_pos = section_positions[section_key]
            for i in range(insert_pos + 1, len(lines)):
                if lines[i].startswith("## ") or (lines[i].strip() == "" and i + 1 < len(lines) and lines[i + 1].startswith("## ")):
                    break
                insert_pos = i
            lines.insert(insert_pos + 1, entry)

    new_content = "\n".join(lines)

    # 检查 INDEX.md 行数限制（200行/25KB）
    line_count = new_content.count("\n") + 1
    size_kb = len(new_content.encode("utf-8")) / 1024
    if line_count > 200 or size_kb > 25:
        print(f"  [警告] INDEX.md 超出限制（{line_count}行/{size_kb:.1f}KB），需要手动精简")

    try:
        MEMORY_INDEX_PATH.write_text(new_content, encoding="utf-8")
        stats["index_updates"] += 1
        print(f"  → 更新 INDEX.md：新增 {len(new_entries)} 条索引")
    except Exception as e:
        print(f"  [错误] 写入 INDEX.md 失败：{e}")


def update_reference_index(classified_items):
    """更新 09_REFERENCE/_index.md"""
    if not REFERENCE_INDEX_PATH.exists():
        print(f"  [警告] _index.md 不存在，跳过更新")
        return

    try:
        content = REFERENCE_INDEX_PATH.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  [警告] 读取 _index.md 失败：{e}")
        return

    new_rows = []

    for item in classified_items:
        if item["category"] != "reference":
            continue

        target_path = Path(item["target_path"])
        filename = target_path.name
        slug = target_path.stem

        # 检查是否已存在
        if slug in content:
            continue

        # 确定子目录
        sub_dir = "system/"
        if "web" in str(target_path.parent):
            sub_dir = "web/"

        # 生成表格行
        tags = "migrated, " + item["filename"].replace("_", ", ")[:50]
        source = "迁移入库"
        credibility = "0.7"
        row = f"| {slug} | {item['filename'][:40]} | {tags} | {source} | {credibility} | 09_REFERENCE/{sub_dir} |"
        new_rows.append(row)

    if not new_rows:
        return

    # 在索引表末尾追加行
    lines = content.split("\n")

    # 找到表格最后一行（以 | 开头）
    last_table_line = 0
    for i, line in enumerate(lines):
        if line.startswith("|"):
            last_table_line = i

    for row in new_rows:
        lines.insert(last_table_line + 1, row)
        last_table_line += 1

    new_content = "\n".join(lines)

    try:
        REFERENCE_INDEX_PATH.write_text(new_content, encoding="utf-8")
        stats["index_updates"] += 1
        print(f"  → 更新 _index.md：新增 {len(new_rows)} 条索引")
    except Exception as e:
        print(f"  [错误] 写入 _index.md 失败：{e}")


def update_project_status(classified_items):
    """更新 04_MEMORY/project/ 下的项目状态文件"""
    # 按项目分组
    project_items = {}
    for item in classified_items:
        if item["category"] in ("project", "project_status"):
            target_path = Path(item["target_path"])
            # 从路径中提取项目名
            parts = target_path.parts
            # 路径格式：01_PROJECTS/{project_name}/... 或 04_MEMORY/project/proj_{name}_status.md
            project_name = None
            for i, part in enumerate(parts):
                if part == "01_PROJECTS" and i + 1 < len(parts):
                    project_name = parts[i + 1]
                    break
                if part == "project" and i + 1 < len(parts):
                    fname = parts[i + 1]
                    if fname.startswith("proj_") and fname.endswith("_status.md"):
                        project_name = fname[5:-11]  # 去掉 proj_ 前缀和 _status.md 后缀

            if project_name:
                if project_name not in project_items:
                    project_items[project_name] = []
                project_items[project_name].append(item)

    for project_name, items in project_items.items():
        status_file = DIR_MEMORY / "project" / f"proj_{project_name}_status.md"

        if not status_file.exists():
            # 创建新的项目状态文件
            frontmatter = f"""---
name: proj-{project_name}
description: {project_name} 项目状态（迁移入库）
type: project
---

# {project_name} 项目状态

## 迁移信息
- 迁移入库时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
- 迁移条目数：{len(items)}

## 迁移内容
"""
            for item in items:
                frontmatter += f"- [{item['category_label']}] {item['filename']} → {item['target_path']}\n"

            frontmatter += f"""
## 待办
- 整理迁移内容，补充项目描述
"""
            try:
                status_file.parent.mkdir(parents=True, exist_ok=True)
                status_file.write_text(frontmatter, encoding="utf-8")
                stats["index_updates"] += 1
                print(f"  → 创建项目状态：{status_file.relative_to(AOS_ROOT)}")
            except Exception as e:
                print(f"  [错误] 创建项目状态文件失败：{e}")


def update_system_state(classified_items):
    """更新 SYSTEM_STATE.md 事件日志"""
    if not SYSTEM_STATE_PATH.exists():
        print(f"  [警告] SYSTEM_STATE.md 不存在，跳过更新")
        return

    try:
        content = SYSTEM_STATE_PATH.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  [警告] 读取 SYSTEM_STATE.md 失败：{e}")
        return

    now = datetime.now().strftime("%Y-%m-%d")
    total_items = len(classified_items)
    category_summary = {}
    for item in classified_items:
        label = item["category_label"]
        category_summary[label] = category_summary.get(label, 0) + 1

    summary_parts = [f"{label}{count}条" for label, count in category_summary.items()]
    summary_str = "、".join(summary_parts)

    # 在事件日志表格中追加一行
    event_line = f"| {now} | MIGRATION_INGEST | 迁移入库完成：共{total_items}条（{summary_str}） |"

    # 找到事件日志段的最后表格行
    lines = content.split("\n")
    in_event_log = False
    last_table_line = -1

    for i, line in enumerate(lines):
        if "事件日志" in line:
            in_event_log = True
        # 遇到新的二级标题，退出事件日志段
        if in_event_log and line.startswith("## ") and "事件日志" not in line:
            in_event_log = False
        if in_event_log and line.startswith("|"):
            last_table_line = i

    if last_table_line >= 0:
        lines.insert(last_table_line + 1, event_line)
    else:
        # 找不到事件日志表格，追加到文件末尾
        lines.append("")
        lines.append(event_line)

    new_content = "\n".join(lines)

    try:
        SYSTEM_STATE_PATH.write_text(new_content, encoding="utf-8")
        stats["index_updates"] += 1
        print(f"  → 更新 SYSTEM_STATE.md 事件日志")
    except Exception as e:
        print(f"  [错误] 写入 SYSTEM_STATE.md 失败：{e}")


def mark_migration_completed():
    """更新迁移状态为 completed"""
    result_path = MIGRATION_DIR / "classification_result.json"
    if not result_path.exists():
        return

    try:
        with open(result_path, "r", encoding="utf-8") as f:
            result = json.load(f)

        result["ingestion_status"] = "completed"
        result["ingestion_time"] = datetime.now().isoformat()
        result["ingestion_stats"] = {
            "ingested": stats["ingested"],
            "skipped": stats["skipped"],
            "conflicts": stats["conflicts"],
            "desensitized": stats["desensitized"],
            "errors": stats["errors"],
        }

        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"  → 迁移状态更新为 completed")
    except Exception as e:
        print(f"  [错误] 更新迁移状态失败：{e}")


def print_ingestion_summary():
    """输出入库摘要"""
    print("\n" + "=" * 60)
    print("AOS 迁移入库结果摘要")
    print("=" * 60)

    print(f"\n总条目数：{stats['total']}")
    print(f"成功入库：{stats['ingested']}")
    print(f"跳过（冲突/用户取消）：{stats['skipped']}")
    print(f"冲突文件：{stats['conflicts']}")
    print(f"脱敏处理：{stats['desensitized']} 处")
    print(f"索引更新：{stats['index_updates']} 个")
    print(f"错误：{stats['errors']}")

    if stats["desensitize_details"]:
        print("\n── 脱敏详情 ──")
        for label, count in stats["desensitize_details"].items():
            print(f"  {label}：{count} 处")

    print("=" * 60)


def main():
    start_time = datetime.now()
    confirm_mode = "--confirm" in sys.argv

    print("=" * 60)
    print(f"AOS 迁移入库脚本 — {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"根目录：{AOS_ROOT}")
    print(f"模式：{'逐条确认' if confirm_mode else '自动入库（冲突时确认）'}")
    print("=" * 60)

    # ── 步骤 1：验证 AOS 根目录 ──
    print_step(1, 7, "验证 AOS 根目录", "执行中 ●")
    detect_aos_root()
    print_step(1, 7, "验证 AOS 根目录", "完成 ✓")

    # ── 步骤 2：加载分类结果 ──
    print_step(2, 7, "加载分类结果", "执行中 ●", str(MIGRATION_DIR / "classification_result.json"))
    classification = load_classification_result()
    classified_items = classification.get("classified_items", [])
    if not classified_items:
        print(f"\n[信息] 分类结果中没有待入库的条目")
        sys.exit(0)
    stats["total"] = len(classified_items)
    elapsed = (datetime.now() - start_time).total_seconds()
    print_step(2, 7, "加载分类结果", "完成 ✓", elapsed=f"已用 {elapsed:.1f}s",
               output_path=f"加载 {len(classified_items)} 条分类结果")

    # ── 步骤 3：脱敏处理 ──
    step3_start = datetime.now()
    print_step(3, 7, "脱敏处理", "执行中 ●")
    print(f"  处理 {len(classified_items)} 条内容的脱敏...")

    for item in classified_items:
        source_file = item["file"]
        content = load_source_content(source_file)
        if content is None:
            stats["skipped"] += 1
            continue

        # 执行脱敏
        desensitized_content, desensitize_count = desensitize_content(content)
        if desensitize_count > 0:
            print(f"  [脱敏] {item['filename']}：{desensitize_count} 处")
        stats["desensitized"] += desensitize_count

        # 保存脱敏后的内容到 item 中
        item["_desensitized_content"] = desensitized_content

    elapsed = (datetime.now() - step3_start).total_seconds()
    print_step(3, 7, "脱敏处理", "完成 ✓", elapsed=f"已用 {elapsed:.1f}s",
               output_path=f"共处理 {stats['desensitized']} 处脱敏")

    # ── 步骤 4：写入目标位置 ──
    step4_start = datetime.now()
    print_step(4, 7, "写入目标位置", "执行中 ●")

    for idx, item in enumerate(classified_items, 1):
        target_path = item["target_path"]
        content = item.get("_desensitized_content")
        if content is None:
            print(f"  [{idx}/{len(classified_items)}] 跳过（无内容）：{item['filename']}")
            stats["skipped"] += 1
            continue

        print(f"  [{idx}/{len(classified_items)}] {item['category_label']} → {Path(target_path).relative_to(AOS_ROOT)}")

        if confirm_mode:
            if not confirm_action(f"入库 {item['filename']} → {target_path}", confirm_mode):
                print(f"  → 跳过")
                stats["skipped"] += 1
                continue

        write_to_target(content, target_path, confirm_mode)

    elapsed = (datetime.now() - step4_start).total_seconds()
    print_step(4, 7, "写入目标位置", "完成 ✓", elapsed=f"已用 {elapsed:.1f}s",
               output_path=f"入库 {stats['ingested']} 条，跳过 {stats['skipped']} 条")

    # ── 步骤 5：更新索引 ──
    step5_start = datetime.now()
    print_step(5, 7, "更新索引", "执行中 ●")

    print("  更新 04_MEMORY/INDEX.md...")
    update_memory_index(classified_items)

    print("  更新 09_REFERENCE/_index.md...")
    update_reference_index(classified_items)

    print("  更新项目状态文件...")
    update_project_status(classified_items)

    elapsed = (datetime.now() - step5_start).total_seconds()
    print_step(5, 7, "更新索引", "完成 ✓", elapsed=f"已用 {elapsed:.1f}s",
               output_path=f"更新 {stats['index_updates']} 个索引")

    # ── 步骤 6：更新迁移状态 ──
    print_step(6, 7, "更新迁移状态", "执行中 ●")
    mark_migration_completed()
    print_step(6, 7, "更新迁移状态", "完成 ✓")

    # ── 步骤 7：更新 SYSTEM_STATE.md ──
    print_step(7, 7, "更新系统状态", "执行中 ●")
    update_system_state(classified_items)
    print_step(7, 7, "更新系统状态", "完成 ✓")

    # 输出摘要
    print_ingestion_summary()

    total_elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n总耗时：{total_elapsed:.1f}s")

    if stats["errors"] > 0:
        print(f"\n[警告] 有 {stats['errors']} 个错误，请检查上方日志")
        sys.exit(1)


if __name__ == "__main__":
    main()
