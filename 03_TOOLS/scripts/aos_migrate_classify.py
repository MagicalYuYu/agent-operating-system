#!/usr/bin/env python3
"""
AOS 迁移分类脚本
用法：python aos_migrate_classify.py

功能：
1. 自动检测 AOS 根目录
2. 读取 08_INBOX/migration/ 下的所有采集结果
3. 按分类决策树分类到 AOS 目录体系
4. 去重合并：同一知识多来源时合并为一条，标注所有来源
5. 关联分析：分析项目间的端口映射、服务依赖、共享配置、API调用链
6. 生成 project_map.json 关联图
7. 输出分类结果到 08_INBOX/migration/classification_result.json
"""

import os
import re
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ── AOS 根目录自动检测 ──────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
AOS_ROOT = SCRIPT_DIR.parent.parent

# ── 排除目录 ────────────────────────────────────────────────
EXCLUDE_DIRS = {".git", ".trae", "__pycache__", "node_modules"}

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

# ── 分类决策树关键词 ────────────────────────────────────────
# 项目代码/配置关键词
PROJECT_KEYWORDS = [
    "项目", "project", "代码", "code", "仓库", "repository", "repo",
    "配置", "config", "部署", "deploy", "docker", "k8s", "kubernetes",
    "package.json", "cargo.toml", "go.mod", "pom.xml", ".csproj",
    "dockerfile", "docker-compose", "nginx", "apache", "env",
    "数据库", "database", "redis", "mysql", "postgres", "mongodb",
    "微服务", "microservice", "api网关", "gateway", "服务注册",
]

# 参考知识/文档关键词
REFERENCE_KEYWORDS = [
    "文档", "document", "doc", "教程", "tutorial", "指南", "guide",
    "参考", "reference", "手册", "manual", "规范", "specification",
    "架构", "architecture", "设计", "design", "原理", "principle",
    "最佳实践", "best-practice", "白皮书", "whitepaper",
    "api文档", "api-doc", "协议", "protocol", "标准", "standard",
]

# 经验/坑点关键词
FEEDBACK_KEYWORDS = [
    "坑", "坑点", "踩坑", "gotcha", "bug", "错误", "error",
    "经验", "experience", "教训", "lesson", "注意", "warning",
    "修复", "fix", "调试", "debug", "排错", "troubleshoot",
    "失败", "fail", "问题", "issue", "不兼容", "incompatible",
    "陷阱", "pitfall", "避坑", "踩雷",
]

# 项目状态/进度关键词
PROJECT_STATUS_KEYWORDS = [
    "状态", "status", "进度", "progress", "里程碑", "milestone",
    "待办", "todo", "计划", "plan", "路线图", "roadmap",
    "版本", "version", "发布", "release", "变更", "changelog",
    "sprint", "迭代", "iteration", "回顾", "retrospective",
]

# 工具/脚本关键词
TOOL_KEYWORDS = [
    "脚本", "script", "工具", "tool", "自动化", "automation",
    "cli", "命令行", "pipeline", "ci/cd", "jenkins", "github-actions",
    "批量", "batch", "定时", "cron", "监控", "monitor",
    "构建", "build", "编译", "compile", "测试", "test",
]

# 日志/调试记录关键词
LOG_KEYWORDS = [
    "日志", "log", "调试", "debug", "trace", "运行记录",
    "输出", "output", "堆栈", "stack", "崩溃", "crash",
    "性能", "performance", "耗时", "latency", "慢查询",
]

# ── 关联分析关键词 ──────────────────────────────────────────
PORT_PATTERN = re.compile(r"(?:端口|port)[：:\s]*(\d{1,5})", re.IGNORECASE)
DEPENDENCY_PATTERN = re.compile(r"(?:依赖|depend|require|import)[：:\s]*(\S+)", re.IGNORECASE)
API_CALL_PATTERN = re.compile(r"(?:调用|call|request|fetch|invoke)[：:\s]*(\S+)", re.IGNORECASE)
CONFIG_SHARE_PATTERN = re.compile(r"(?:共享|common|shared|global)[：:\s]*(\S+)", re.IGNORECASE)
SERVICE_PATTERN = re.compile(r"(?:服务|service)[：:\s]*(\S+)", re.IGNORECASE)


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


def compute_content_hash(content):
    """计算内容哈希，用于去重"""
    # 去除空白字符后计算哈希，避免格式差异导致误判
    normalized = re.sub(r"\s+", "", content.lower())
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()


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


def load_migration_sources():
    """加载 08_INBOX/migration/ 下的所有采集结果"""
    sources = []

    if not MIGRATION_DIR.exists():
        print(f"[警告] 迁移目录不存在：{MIGRATION_DIR}")
        print(f"  将创建空目录")
        MIGRATION_DIR.mkdir(parents=True, exist_ok=True)
        return sources

    # 支持的文件格式
    supported_ext = {".md", ".json", ".txt", ".yaml", ".yml", ".toml"}

    for item in MIGRATION_DIR.rglob("*"):
        # 跳过目录和排除目录
        if item.is_dir():
            continue
        if any(excluded in item.parts for excluded in EXCLUDE_DIRS):
            continue
        # 跳过分类结果文件本身
        if item.name == "classification_result.json":
            continue
        if item.name == "project_map.json":
            continue
        # 跳过不支持的格式
        if item.suffix.lower() not in supported_ext:
            continue

        try:
            content = item.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  [警告] 读取失败，跳过：{item.name} ({e})")
            continue

        rel_path = item.relative_to(MIGRATION_DIR)
        source_info = {
            "file": str(rel_path),
            "filename": item.name,
            "content": content,
            "content_hash": compute_content_hash(content),
            "size_bytes": item.stat().st_size,
            "modified_time": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
        }

        # 尝试解析 JSON 格式的采集结果
        if item.suffix == ".json":
            try:
                data = json.loads(content)
                # 如果是数组格式，展开为多个条目
                if isinstance(data, list):
                    for idx, entry in enumerate(data):
                        entry_content = json.dumps(entry, ensure_ascii=False)
                        sources.append({
                            **source_info,
                            "entry_index": idx,
                            "entry_content": entry_content,
                            "content_hash": compute_content_hash(entry_content),
                            "parsed_json": entry,
                        })
                    continue
                else:
                    source_info["parsed_json"] = data
            except json.JSONDecodeError:
                pass

        sources.append(source_info)

    return sources


def classify_single(source):
    """对单个来源进行分类决策"""
    content = source.get("entry_content", source["content"]).lower()
    filename = source["filename"].lower()

    # 评分系统：每类关键词命中计分
    scores = {
        "project": 0,
        "reference": 0,
        "feedback": 0,
        "project_status": 0,
        "tool": 0,
        "log": 0,
    }

    keyword_map = {
        "project": PROJECT_KEYWORDS,
        "reference": REFERENCE_KEYWORDS,
        "feedback": FEEDBACK_KEYWORDS,
        "project_status": PROJECT_STATUS_KEYWORDS,
        "tool": TOOL_KEYWORDS,
        "log": LOG_KEYWORDS,
    }

    for category, keywords in keyword_map.items():
        for kw in keywords:
            if kw.lower() in content:
                scores[category] += 1
            # 文件名匹配权重加倍
            if kw.lower() in filename:
                scores[category] += 2

    # 文件名后缀加分
    if filename.endswith((".py", ".sh", ".bat", ".ps1", ".js", ".ts")):
        scores["tool"] += 3
    if filename.endswith((".log", ".trace")):
        scores["log"] += 5
    if "config" in filename or filename.endswith((".yaml", ".yml", ".toml", ".ini", ".env")):
        scores["project"] += 2

    # 解析 JSON 中的类型提示
    parsed = source.get("parsed_json")
    if parsed and isinstance(parsed, dict):
        source_type = parsed.get("type", "").lower()
        source_category = parsed.get("category", "").lower()
        if source_type in keyword_map or source_category in keyword_map:
            key = source_type if source_type in keyword_map else source_category
            scores[key] += 5

    # 找出最高分类
    max_score = max(scores.values())
    if max_score == 0:
        return "uncertain", scores

    # 取最高分分类（平局时按优先级：project > reference > feedback > project_status > tool > log）
    priority_order = ["project", "reference", "feedback", "project_status", "tool", "log"]
    for cat in priority_order:
        if scores[cat] == max_score:
            return cat, scores

    return "uncertain", scores


def determine_target_path(category, source):
    """根据分类确定目标路径"""
    filename = source["filename"]
    stem = Path(filename).stem

    if category == "project":
        # 尝试从内容中提取项目名
        project_name = extract_project_name(source)
        return str(DIR_PROJECTS / project_name / filename)

    elif category == "reference":
        # 区分 web 和 system
        content = source.get("entry_content", source["content"]).lower()
        if any(kw in content for kw in ["http", "url", "网页", "网站", "web", "爬取", "抓取"]):
            return str(DIR_REFERENCE / "web" / filename)
        return str(DIR_REFERENCE / "system" / filename)

    elif category == "feedback":
        slug = re.sub(r"[^a-z0-9]+", "_", stem.lower()).strip("_")
        return str(DIR_MEMORY / "feedback" / f"fb_{slug}.md")

    elif category == "project_status":
        project_name = extract_project_name(source)
        return str(DIR_MEMORY / "project" / f"proj_{project_name}_status.md")

    elif category == "tool":
        # 区分脚本和 Skill
        if filename.endswith((".py", ".sh", ".bat", ".ps1")):
            return str(DIR_TOOLS / "scripts" / filename)
        return str(DIR_TOOLS / filename)

    elif category == "log":
        date_prefix = datetime.now().strftime("%Y%m%d")
        return str(DIR_LOGS / f"{date_prefix}_{filename}")

    else:  # uncertain
        return str(PENDING_DIR / filename)


def extract_project_name(source):
    """从内容中提取项目名"""
    content = source.get("entry_content", "") or source.get("content", "")

    # 尝试从 JSON 中提取
    parsed = source.get("parsed_json")
    if parsed and isinstance(parsed, dict):
        for key in ["project", "project_name", "name", "repo"]:
            if key in parsed:
                name = str(parsed[key]).strip()
                if name:
                    return re.sub(r"[^a-z0-9_-]", "_", name.lower())

    # 尝试从文件名提取
    filename = source["filename"]
    # 常见格式：20260621_project-name_topic.md
    match = re.match(r"\d{8}[_-]([a-z0-9_-]+)", filename.lower())
    if match:
        return match.group(1).strip("_-")

    # 尝试从内容中提取项目名关键词
    patterns = [
        r"项目[名称：:]*\s*([a-zA-Z0-9_-]+)",
        r"project[名称：:]*\s*([a-zA-Z0-9_-]+)",
        r"repo[：:]*\s*([a-zA-Z0-9_-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return re.sub(r"[^a-z0-9_-]", "_", match.group(1).lower())

    # 使用文件名 stem 作为回退
    stem = Path(filename).stem
    return re.sub(r"[^a-z0-9_-]", "_", stem.lower()).strip("_")[:30]


def deduplicate(sources):
    """去重合并：同一知识在多个来源中出现时合并为一条"""
    hash_groups = defaultdict(list)

    for source in sources:
        hash_groups[source["content_hash"]].append(source)

    merged = []
    duplicates_count = 0

    for content_hash, group in hash_groups.items():
        if len(group) == 1:
            merged.append(group[0])
        else:
            # 合并：保留内容最长的版本，标注所有来源
            best = max(group, key=lambda s: len(s.get("entry_content", s["content"])))
            all_sources = [s["file"] for s in group]
            best["merged_from"] = all_sources
            best["dedup_note"] = f"合并自 {len(group)} 个来源：{', '.join(all_sources)}"
            merged.append(best)
            duplicates_count += len(group) - 1

    return merged, duplicates_count


def analyze_relations(sources):
    """关联分析：分析项目间的端口映射、服务依赖、共享配置、API调用链"""
    relations = {
        "port_mappings": [],
        "service_dependencies": [],
        "shared_configs": [],
        "api_call_chains": [],
        "project_connections": [],
    }

    # 按项目分组
    project_groups = defaultdict(list)
    for source in sources:
        project_name = extract_project_name(source)
        project_groups[project_name].append(source)

    # 分析每个来源中的关联信息
    for source in sources:
        content = source.get("entry_content", source["content"])
        source_file = source["file"]

        # 端口映射
        for match in PORT_PATTERN.finditer(content):
            port = match.group(1)
            project = extract_project_name(source)
            relations["port_mappings"].append({
                "project": project,
                "port": port,
                "source": source_file,
                "context": content[max(0, match.start() - 30):match.end() + 30].strip(),
            })

        # 服务依赖
        for match in DEPENDENCY_PATTERN.finditer(content):
            dep = match.group(1)
            project = extract_project_name(source)
            relations["service_dependencies"].append({
                "project": project,
                "dependency": dep,
                "source": source_file,
            })

        # API 调用链
        for match in API_CALL_PATTERN.finditer(content):
            api = match.group(1)
            project = extract_project_name(source)
            relations["api_call_chains"].append({
                "project": project,
                "api": api,
                "source": source_file,
            })

        # 共享配置
        for match in CONFIG_SHARE_PATTERN.finditer(content):
            config = match.group(1)
            relations["shared_configs"].append({
                "config": config,
                "source": source_file,
            })

    # 分析项目间连接
    project_names = list(project_groups.keys())
    for i, proj_a in enumerate(project_names):
        for proj_b in project_names[i + 1:]:
            connections = []

            # 检查端口冲突
            ports_a = {r["port"] for r in relations["port_mappings"] if r["project"] == proj_a}
            ports_b = {r["port"] for r in relations["port_mappings"] if r["project"] == proj_b}
            shared_ports = ports_a & ports_b
            if shared_ports:
                connections.append(f"端口冲突：{', '.join(shared_ports)}")

            # 检查依赖关系
            deps_a = {r["dependency"] for r in relations["service_dependencies"] if r["project"] == proj_a}
            deps_b = {r["dependency"] for r in relations["service_dependencies"] if r["project"] == proj_b}
            shared_deps = deps_a & deps_b
            if shared_deps:
                connections.append(f"共享依赖：{', '.join(shared_deps)}")

            # 检查 API 调用
            apis_a = {r["api"] for r in relations["api_call_chains"] if r["project"] == proj_a}
            apis_b = {r["api"] for r in relations["api_call_chains"] if r["project"] == proj_b}
            # A 调用 B 的 API
            a_calls_b = apis_a & {proj_b}
            b_calls_a = apis_b & {proj_a}
            if a_calls_b:
                connections.append(f"{proj_a} → {proj_b}")
            if b_calls_a:
                connections.append(f"{proj_b} → {proj_a}")

            if connections:
                relations["project_connections"].append({
                    "project_a": proj_a,
                    "project_b": proj_b,
                    "connections": connections,
                })

    return relations


def generate_project_map(relations, classified_sources):
    """生成 project_map.json 关联图"""
    # 收集所有项目节点
    nodes = {}
    edges = []

    for source in classified_sources:
        project = extract_project_name(source)
        if project not in nodes:
            nodes[project] = {
                "id": project,
                "label": project,
                "type": source.get("category", "unknown"),
                "file_count": 0,
                "ports": [],
            }
        nodes[project]["file_count"] += 1

    # 添加端口信息
    for pm in relations["port_mappings"]:
        proj = pm["project"]
        if proj in nodes and pm["port"] not in nodes[proj]["ports"]:
            nodes[proj]["ports"].append(pm["port"])

    # 生成边
    for conn in relations["project_connections"]:
        edges.append({
            "source": conn["project_a"],
            "target": conn["project_b"],
            "relations": conn["connections"],
        })

    # 服务依赖边
    for dep in relations["service_dependencies"]:
        edges.append({
            "source": dep["project"],
            "target": dep["dependency"],
            "relations": ["服务依赖"],
        })

    project_map = {
        "generated_at": datetime.now().isoformat(),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": list(nodes.values()),
        "edges": edges,
        "port_mappings": relations["port_mappings"],
        "service_dependencies": relations["service_dependencies"],
        "shared_configs": relations["shared_configs"],
        "api_call_chains": relations["api_call_chains"],
    }

    return project_map


def classify_sources(sources):
    """对所有来源执行分类"""
    classified = []

    for source in sources:
        category, scores = classify_single(source)
        target_path = determine_target_path(category, source)

        classified.append({
            "file": source["file"],
            "filename": source["filename"],
            "category": category,
            "category_label": {
                "project": "项目代码/配置",
                "reference": "参考知识/文档",
                "feedback": "经验/坑点",
                "project_status": "项目状态/进度",
                "tool": "工具/脚本",
                "log": "日志/调试记录",
                "uncertain": "不确定",
            }.get(category, "未知"),
            "target_path": target_path,
            "scores": scores,
            "content_hash": source["content_hash"],
            "size_bytes": source.get("size_bytes", 0),
            "merged_from": source.get("merged_from", []),
            "dedup_note": source.get("dedup_note", ""),
            "content": source.get("content", ""),
            "entry_content": source.get("entry_content", ""),
        })

    return classified


def print_classification_summary(classified, duplicates_count, relations):
    """输出分类摘要"""
    # 按类别统计
    category_counts = defaultdict(int)
    category_sizes = defaultdict(int)
    for item in classified:
        category_counts[item["category_label"]] += 1
        category_sizes[item["category_label"]] += item["size_bytes"]

    print("\n" + "=" * 60)
    print("AOS 迁移分类结果摘要")
    print("=" * 60)

    print(f"\n总条目数：{len(classified)}")
    print(f"去重合并：{duplicates_count} 条重复已合并")

    print("\n── 分类统计 ──")
    print(f"{'类别':<16} {'数量':>6} {'大小':>12}")
    print("-" * 36)
    for cat in sorted(category_counts.keys()):
        count = category_counts[cat]
        size_kb = category_sizes[cat] / 1024
        print(f"{cat:<16} {count:>6} {size_kb:>10.1f} KB")

    print("\n── 关联分析 ──")
    print(f"端口映射：{len(relations['port_mappings'])} 条")
    print(f"服务依赖：{len(relations['service_dependencies'])} 条")
    print(f"共享配置：{len(relations['shared_configs'])} 条")
    print(f"API调用链：{len(relations['api_call_chains'])} 条")
    print(f"项目连接：{len(relations['project_connections'])} 条")

    if relations["project_connections"]:
        print("\n── 项目间关联 ──")
        for conn in relations["project_connections"]:
            print(f"  {conn['project_a']} ↔ {conn['project_b']}")
            for detail in conn["connections"]:
                print(f"    · {detail}")

    print("\n── 分类详情 ──")
    for item in classified:
        dedup_info = f" (合并自{len(item['merged_from'])}个来源)" if item["merged_from"] else ""
        print(f"  [{item['category_label']}] {item['filename']}{dedup_info}")
        print(f"    → {item['target_path']}")

    print("=" * 60)


def main():
    start_time = datetime.now()

    print("=" * 60)
    print(f"AOS 迁移分类脚本 — {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"根目录：{AOS_ROOT}")
    print("=" * 60)

    # ── 步骤 1：验证 AOS 根目录 ──
    print_step(1, 6, "验证 AOS 根目录", "执行中 ●")
    detect_aos_root()
    print_step(1, 6, "验证 AOS 根目录", "完成 ✓")

    # ── 步骤 2：加载采集结果 ──
    print_step(2, 6, "加载采集结果", "执行中 ●", str(MIGRATION_DIR))
    sources = load_migration_sources()
    if not sources:
        print(f"\n[信息] 08_INBOX/migration/ 下没有找到可分类的文件")
        print(f"  请先将采集结果放入该目录")
        sys.exit(0)
    elapsed = (datetime.now() - start_time).total_seconds()
    print_step(2, 6, "加载采集结果", "完成 ✓", str(MIGRATION_DIR), f"已用 {elapsed:.1f}s",
               f"加载 {len(sources)} 个条目")

    # ── 步骤 3：去重合并 ──
    step3_start = datetime.now()
    print_step(3, 6, "去重合并", "执行中 ●")
    merged_sources, duplicates_count = deduplicate(sources)
    elapsed = (datetime.now() - step3_start).total_seconds()
    print_step(3, 6, "去重合并", "完成 ✓", elapsed=f"已用 {elapsed:.1f}s",
               output_path=f"合并后 {len(merged_sources)} 条，去除 {duplicates_count} 条重复")

    # ── 步骤 4：分类决策 ──
    step4_start = datetime.now()
    print_step(4, 6, "分类决策", "执行中 ●")
    classified = classify_sources(merged_sources)
    elapsed = (datetime.now() - step4_start).total_seconds()
    print_step(4, 6, "分类决策", "完成 ✓", elapsed=f"已用 {elapsed:.1f}s",
               output_path=f"分类 {len(classified)} 条")

    # ── 步骤 5：关联分析 ──
    step5_start = datetime.now()
    print_step(5, 6, "关联分析", "执行中 ●")
    relations = analyze_relations(merged_sources)
    project_map = generate_project_map(relations, classified)
    elapsed = (datetime.now() - step5_start).total_seconds()
    print_step(5, 6, "关联分析", "完成 ✓", elapsed=f"已用 {elapsed:.1f}s",
               output_path=str(MIGRATION_DIR / "project_map.json"))

    # ── 步骤 6：输出结果 ──
    step6_start = datetime.now()
    print_step(6, 6, "输出分类结果", "执行中 ●")
    result = {
        "generated_at": datetime.now().isoformat(),
        "total_sources": len(sources),
        "after_dedup": len(merged_sources),
        "duplicates_removed": duplicates_count,
        "classified_items": classified,
        "relations": relations,
        "summary": {
            "project": sum(1 for c in classified if c["category"] == "project"),
            "reference": sum(1 for c in classified if c["category"] == "reference"),
            "feedback": sum(1 for c in classified if c["category"] == "feedback"),
            "project_status": sum(1 for c in classified if c["category"] == "project_status"),
            "tool": sum(1 for c in classified if c["category"] == "tool"),
            "log": sum(1 for c in classified if c["category"] == "log"),
            "uncertain": sum(1 for c in classified if c["category"] == "uncertain"),
        },
    }

    # 确保目录存在
    MIGRATION_DIR.mkdir(parents=True, exist_ok=True)

    # 写入分类结果
    result_path = MIGRATION_DIR / "classification_result.json"
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 写入项目关联图
    map_path = MIGRATION_DIR / "project_map.json"
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(project_map, f, ensure_ascii=False, indent=2)

    elapsed = (datetime.now() - step6_start).total_seconds()
    print_step(6, 6, "输出分类结果", "完成 ✓", elapsed=f"已用 {elapsed:.1f}s",
               output_path=str(result_path))

    # 输出摘要
    print_classification_summary(classified, duplicates_count, relations)

    total_elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n总耗时：{total_elapsed:.1f}s")
    print(f"下一步：运行 python aos_migrate_ingest.py 执行入库")


if __name__ == "__main__":
    main()
