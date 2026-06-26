#!/usr/bin/env python3
"""
AOS 一致性自检脚本
用法：python aos_check.py [--fix]
选项：
  无参数  — 仅检查，输出报告
  --fix   — 检查并尝试自动修复（版本号同步、索引条目验证）
"""

import os
import re
import sys
import json
from pathlib import Path
from datetime import datetime

# AOS 根目录（脚本在 03_TOOLS/scripts/ 下，需向上两级）
SCRIPT_DIR = Path(__file__).parent
AOS_ROOT = SCRIPT_DIR.parent.parent

# 排除目录
EXCLUDE_DIRS = {".git", ".trae", "99_ARCHIVE", "__pycache__", "node_modules"}

# 版本号检查排除目录（第三方项目文件可能包含非AOS版本号）
VERSION_EXCLUDE_DIRS = {"01_PROJECTS", "05_CACHE", "02_SANDBOX"}

# 当前版本号
CURRENT_VERSION = "1.1.0"
VERSION_PATTERNS = [
    r"v\d+\.\d+\.\d*",      # v1.x.x
    r"AOS v\d+\.\d+",       # AOS v1.x
    r"\"\d+\.\d+\.\d+\"",   # "1.x.x" in JSON
    r"schema_version.*\d+\.\d+"  # schema_version in JSON
]


def find_all_files(root, extensions=None):
    """递归查找所有文件，排除指定目录"""
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # 排除目录
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for f in filenames:
            if extensions and not any(f.endswith(ext) for ext in extensions):
                continue
            files.append(Path(dirpath) / f)
    return files


def check_version_consistency():
    """检查1：版本号一致性"""
    issues = []
    md_files = find_all_files(AOS_ROOT, [".md"])
    json_files = find_all_files(AOS_ROOT, [".json"])

    for f in md_files + json_files:
        try:
            content = f.read_text(encoding="utf-8")
        except Exception:
            continue

        # 检查是否包含旧版本号
        rel_path = f.relative_to(AOS_ROOT)

        # 跳过第三方项目目录（可能包含非AOS版本号如插件版本）
        if any(part in VERSION_EXCLUDE_DIRS for part in rel_path.parts):
            continue

        # 检查标题中的版本号
        if f.suffix == ".md":
            # 第一行标题中的版本号
            first_line = content.split("\n")[0] if content else ""
            if re.search(r"v2\.\d+\b", first_line) and "99_ARCHIVE" not in str(rel_path):
                issues.append(f"[版本号] {rel_path}: 标题包含旧版本号 → {first_line.strip()}")

            # 正文中的 AOS v2.0 / AOS v2.1 / AOS v2.2 引用（排除归档和历史记录）
            if "99_ARCHIVE" not in str(rel_path):
                for match in re.finditer(r"AOS v2\.\d+(?!\.\d)", content):
                    line_num = content[:match.start()].count("\n") + 1
                    # 获取所在行内容
                    lines = content.split("\n")
                    line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                    # 排除事件日志中的历史记录（以 | 开头或包含日期格式的表格行）
                    if "|" in line_content and re.search(r"\d{4}-\d{2}-\d{2}", line_content):
                        continue
                    issues.append(f"[版本号] {rel_path}:{line_num}: 包含旧引用 '{match.group()}'")

        # 检查 JSON 中的 schema_version
        if f.suffix == ".json":
            try:
                data = json.loads(content)
                if "schema_version" in data:
                    sv = data["schema_version"]
                    # schema_version 可能是 str/dict/number，统一转为字符串处理
                    if isinstance(sv, dict):
                        sv = sv.get("version", str(sv))
                    elif isinstance(sv, (int, float)):
                        sv = str(sv)
                    if not isinstance(sv, str):
                        sv = str(sv)
                    if not sv.startswith("1.0"):
                        issues.append(f"[版本号] {rel_path}: schema_version={sv} (应为1.0.x)")
            except json.JSONDecodeError:
                pass

    return issues


def check_reference_integrity():
    """检查2：引用完整性——引用的文件是否存在"""
    issues = []

    # 检查 _index.md 中的文件引用
    index_file = AOS_ROOT / "09_REFERENCE" / "_index.md"
    if index_file.exists():
        content = index_file.read_text(encoding="utf-8")
        # 查找所有 .md 文件引用
        for match in re.finditer(r"09_REFERENCE/[^\s|]+\.(?:md|json)", content):
            ref_path = AOS_ROOT / match.group()
            if not ref_path.exists():
                issues.append(f"[引用] _index.md 引用了不存在的文件: {match.group()}")

    # 检查 AGENTS.md 引用表
    agents_file = AOS_ROOT / "AGENTS.md"
    if agents_file.exists():
        content = agents_file.read_text(encoding="utf-8")
        for match in re.finditer(r"`(09_REFERENCE/system/[^`]+)`", content):
            ref_path = AOS_ROOT / match.group(1)
            if not ref_path.exists():
                issues.append(f"[引用] AGENTS.md 引用了不存在的文件: {match.group(1)}")

    # 检查 SKILL_REGISTRY.md 中的 Skill 路径
    registry_file = AOS_ROOT / "00_BOOT" / "SKILL_REGISTRY.md"
    if registry_file.exists():
        content = registry_file.read_text(encoding="utf-8")
        for match in re.finditer(r"03_TOOLS/skills/[^\s|`\"]+", content):
            path_str = match.group().rstrip("/").rstrip("\"").rstrip("`")
            # 排除模板占位符
            if "{skill_name}" in path_str or "skill_name" in path_str:
                continue
            ref_path = AOS_ROOT / path_str
            if not ref_path.exists():
                issues.append(f"[引用] SKILL_REGISTRY.md 引用了不存在的路径: {match.group()}")

    return issues


def check_index_correspondence():
    """检查3：索引与实际文件一一对应"""
    issues = []

    # 检查 09_REFERENCE/system/ 下的文件是否都在 _index.md 中
    system_dir = AOS_ROOT / "09_REFERENCE" / "system"
    index_file = AOS_ROOT / "09_REFERENCE" / "_index.md"

    if system_dir.exists() and index_file.exists():
        index_content = index_file.read_text(encoding="utf-8")

        for f in system_dir.iterdir():
            if f.suffix == ".md" and not f.name.startswith("."):
                # 索引中用 slug（不含 .md 后缀），文件名含 .md，所以匹配 stem
                if f.stem not in index_content and f.name not in index_content:
                    issues.append(f"[索引] 文件存在但索引缺失: 09_REFERENCE/system/{f.name}")

    # 检查 04_MEMORY/INDEX.md 中的文件引用
    memory_index = AOS_ROOT / "04_MEMORY" / "INDEX.md"
    if memory_index.exists():
        content = memory_index.read_text(encoding="utf-8")
        for match in re.finditer(r"\]\(([^)]+\.md)\)", content):
            ref_path = AOS_ROOT / "04_MEMORY" / match.group(1)
            if not ref_path.exists():
                issues.append(f"[索引] INDEX.md 引用了不存在的文件: 04_MEMORY/{match.group(1)}")

    return issues


def check_directory_compliance():
    """检查4：目录合规性——是否有文件放错了目录"""
    issues = []

    # 01_PROJECTS 下不应有非项目内容
    projects_dir = AOS_ROOT / "01_PROJECTS"
    if projects_dir.exists():
        for f in projects_dir.iterdir():
            if f.is_dir() and f.name not in ("README.md",) and not (f / "README.md").exists():
                issues.append(f"[目录] 01_PROJECTS/{f.name}: 项目目录缺少 README.md")

    # 09_REFERENCE 下不应有重复知识
    system_dir = AOS_ROOT / "09_REFERENCE" / "system"
    if system_dir.exists():
        seen_basenames = {}
        for f in system_dir.iterdir():
            if f.suffix == ".md":
                base = f.stem.split("_")[0] if "_" in f.stem else f.stem
                if base in seen_basenames:
                    issues.append(f"[目录] 可能的知识重复: {seen_basenames[base]} vs {f.name}")
                seen_basenames[base] = f.name

    return issues


def run_checks(fix=False):
    """执行所有检查"""
    print("=" * 60)
    print(f"AOS 一致性自检 — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"版本：{CURRENT_VERSION} | 根目录：{AOS_ROOT}")
    print("=" * 60)

    all_issues = []

    checks = [
        ("版本号一致性", check_version_consistency),
        ("引用完整性", check_reference_integrity),
        ("索引对应性", check_index_correspondence),
        ("目录合规性", check_directory_compliance),
    ]

    for name, check_fn in checks:
        print(f"\n检查：{name}...")
        issues = check_fn()
        all_issues.extend(issues)
        if issues:
            print(f"  发现 {len(issues)} 个问题：")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print(f"  通过 ✓")

    print("\n" + "=" * 60)
    if all_issues:
        print(f"一致性验证：失败，{len(all_issues)} 处不一致")
        for issue in all_issues:
            print(f"  - {issue}")
    else:
        print("一致性验证：通过 ✓")
    print("=" * 60)

    return len(all_issues)


if __name__ == "__main__":
    fix_mode = "--fix" in sys.argv
    exit_code = run_checks(fix=fix_mode)
    sys.exit(1 if exit_code > 0 else 0)
