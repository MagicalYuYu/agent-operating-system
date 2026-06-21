#!/usr/bin/env python3
"""
AOS 迁移采集脚本
用法：
  python aos_migrate_collect.py --source=project --path="项目路径"
  python aos_migrate_collect.py --source=chat --input="对话提取文件路径"
  python aos_migrate_collect.py --source=scan --path="目录路径"
  python aos_migrate_collect.py --source=server --path="服务器项目路径"
  python aos_migrate_collect.py --source=phase0 --path="服务器项目路径"

功能：
  - project 模式：扫描本地项目，检测技术栈、文件树、配置、依赖、端口、环境变量、API 端点
  - chat 模式：处理 Markdown 格式的对话提取文件
  - scan 模式：扫描目录下所有项目并逐一采集
  - server 模式：Phase 0 环境调研与安全准备 + 采集阶段
  - phase0 模式：仅执行 Phase 0 环境调研与安全准备，不进入采集阶段
"""

import os
import re
import sys
import json
import argparse
import shutil
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional


# ──────────────────────────────────────────────
# 常量定义
# ──────────────────────────────────────────────

# 排除的目录（依赖目录、构建产物、版本控制等）
EXCLUDE_DIRS = {
    "node_modules", ".git", "venv", ".venv", "env", ".env",
    "__pycache__", "dist", "build", ".next", ".nuxt",
    "target", "bin", "obj", ".idea", ".vscode",
    "coverage", ".cache", ".tox", "eggs", "*.egg-info",
}

# 技术栈检测映射：配置文件 → 技术栈名称
TECH_STACK_MARKERS = {
    "package.json": "Node.js",
    "requirements.txt": "Python",
    "pyproject.toml": "Python",
    "setup.py": "Python",
    "Pipfile": "Python",
    ".csproj": "C#",
    ".sln": "C#",
    "Cargo.toml": "Rust",
    "go.mod": "Go",
    "go.sum": "Go",
    "pom.xml": "Java (Maven)",
    "build.gradle": "Java (Gradle)",
    "build.gradle.kts": "Java (Gradle/Kotlin)",
    "Gemfile": "Ruby",
    "composer.json": "PHP",
    "pubspec.yaml": "Dart/Flutter",
    "mix.exs": "Elixir",
    "project.clj": "Clojure",
    "deps.edn": "Clojure",
    "flake.nix": "Nix",
}

# 配置文件匹配模式
CONFIG_FILE_PATTERNS = [
    ".env", ".env.local", ".env.production", ".env.development",
    "docker-compose.yml", "docker-compose.yaml", "docker-compose.override.yml",
    "Dockerfile", "Dockerfile.prod", "Dockerfile.dev",
    "nginx.conf", "apache.conf",
]

CONFIG_FILE_GLOBS = [
    "config.*", "*.config.*", ".*rc",
    "*.yaml", "*.yml", "*.json", "*.toml", "*.ini", "*.cfg",
]

# 端口匹配正则
PORT_PATTERN = re.compile(
    r"(?:port|PORT|listen|LISTEN|bind|BIND)\s*[:=]\s*['\"]?(\d{4,5})['\"]?"
    r"|:(\d{4,5})\b"
    r"|(?:localhost|127\.0\.0\.1|0\.0\.0\.0):(\d{4,5})"
)

# 环境变量引用模式
ENV_VAR_PATTERNS = [
    re.compile(r"process\.env\.([A-Za-z_][A-Za-z0-9_]*)"),           # Node.js
    re.compile(r"os\.environ(?:\.get)?\(['\"]([^'\"]+)['\"]\)"),      # Python
    re.compile(r"os\.Getenv\(['\"]([^'\"]+)['\"]\)"),                 # Go
    re.compile(r"System\.getenv\(['\"]([^'\"]+)['\"]\)"),             # Java
    re.compile(r"env\(['\"]([^'\"]+)['\"]\)"),                        # 通用
    re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}"),                   # Shell/Docker
    re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*):-([^}]*)\}"),          # 带默认值
    re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)\b"),                     # Shell 简写
]

# API 端点匹配模式
API_ENDPOINT_PATTERNS = [
    re.compile(r'https?://[^\s"\'<>]+', re.IGNORECASE),
    re.compile(r'(?:localhost|127\.0\.0\.1|0\.0\.0\.0):\d{2,5}[^\s"\'<>]*'),
]

# 可扫描的源代码扩展名
SOURCE_EXTENSIONS = {
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".py", ".pyi", ".pyx",
    ".cs", ".java", ".go", ".rs",
    ".rb", ".php", ".swift", ".kt", ".scala",
    ".vue", ".svelte",
    ".html", ".css", ".scss", ".less",
    ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg",
    ".env", ".sh", ".bash", ".zsh", ".ps1",
    ".sql",
    ".md",
}


# ──────────────────────────────────────────────
# 工具函数
# ──────────────────────────────────────────────

def find_aos_root() -> Path:
    """从脚本位置向上查找 AGENTS.md，自动检测 AOS 根目录"""
    current = Path(__file__).resolve().parent
    for _ in range(10):  # 最多向上查找 10 层
        if (current / "AGENTS.md").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    print("[错误] 无法找到 AOS 根目录（未找到 AGENTS.md）")
    sys.exit(1)


def print_step(step_num: int, total: int, name: str, target: str = "", status: str = "执行中"):
    """可视化输出步骤信息"""
    icon = {"执行中": "●", "完成": "✓", "失败": "✗"}.get(status, "○")
    target_line = f"\n│ 目标：{target}" if target else ""
    print(f"\n┌─ [步骤 {step_num}/{total}] {name} ──────────────────────┐")
    print(f"│ 状态：{status} {icon}{target_line}")
    print(f"└──────────────────────────────────────────────┘")


def safe_read_text(filepath: Path, encoding: str = "utf-8") -> Optional[str]:
    """安全读取文件内容，出错返回 None"""
    try:
        return filepath.read_text(encoding=encoding, errors="replace")
    except Exception as e:
        print(f"  [警告] 无法读取文件 {filepath}: {e}")
        return None


def safe_read_json(filepath: Path) -> Optional[dict]:
    """安全读取 JSON 文件，出错返回 None"""
    content = safe_read_text(filepath)
    if content is None:
        return None
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"  [警告] JSON 解析失败 {filepath}: {e}")
        return None


def should_exclude_dir(dirname: str) -> bool:
    """判断目录是否应被排除"""
    if dirname in EXCLUDE_DIRS:
        return True
    # 支持 *.egg-info 等通配符
    for pattern in EXCLUDE_DIRS:
        if "*" in pattern and re.match(pattern.replace("*", ".*"), dirname):
            return True
    return False


# ──────────────────────────────────────────────
# 项目扫描功能
# ──────────────────────────────────────────────

def detect_tech_stack(project_path: Path) -> list:
    """检测项目技术栈（根据配置文件和文件扩展名）"""
    stacks = set()
    total_steps = 2
    step = 0

    # 步骤 1：检查配置文件标记
    step += 1
    print_step(step, total_steps, "技术栈检测（配置文件）", str(project_path))

    for marker_file, stack_name in TECH_STACK_MARKERS.items():
        # 检查根目录
        if (project_path / marker_file).exists():
            stacks.add(stack_name)
            print(f"  发现标记文件：{marker_file} → {stack_name}")
        # 检查子目录（最多 2 层，用于 monorepo）
        for item in project_path.iterdir():
            if item.is_dir() and not should_exclude_dir(item.name):
                if (item / marker_file).exists():
                    stacks.add(stack_name)
                    print(f"  发现标记文件：{item.name}/{marker_file} → {stack_name}")

    # 步骤 2：检查文件扩展名统计
    step += 1
    print_step(step, total_steps, "技术栈检测（文件扩展名）", str(project_path))

    ext_counts = {}
    for dirpath, dirnames, filenames in os.walk(project_path):
        dirnames[:] = [d for d in dirnames if not should_exclude_dir(d)]
        for f in filenames:
            ext = Path(f).suffix.lower()
            if ext:
                ext_counts[ext] = ext_counts.get(ext, 0) + 1

    # 根据扩展名推断技术栈
    ext_to_stack = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
        ".jsx": "React", ".tsx": "React/TypeScript",
        ".cs": "C#", ".java": "Java", ".go": "Go", ".rs": "Rust",
        ".rb": "Ruby", ".php": "PHP", ".swift": "Swift",
        ".kt": "Kotlin", ".vue": "Vue", ".svelte": "Svelte",
    }
    for ext, count in ext_counts.items():
        if ext in ext_to_stack and count >= 3:
            stacks.add(ext_to_stack[ext])

    print_step(step, total_steps, "技术栈检测", status="完成")
    result = sorted(stacks)
    print(f"  检测结果：{', '.join(result) if result else '未识别'}")
    return result


def generate_file_tree(project_path: Path, max_depth: int = 4) -> str:
    """生成项目文件树（排除依赖目录）"""
    print_step(1, 1, "生成文件树", str(project_path))

    lines = []
    project_name = project_path.name
    lines.append(f"{project_name}/")

    def _walk(directory: Path, prefix: str, depth: int):
        if depth > max_depth:
            lines.append(f"{prefix}... (深度超限，已截断)")
            return
        try:
            items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            lines.append(f"{prefix}[权限不足]")
            return

        # 过滤排除目录
        items = [i for i in items if not should_exclude_dir(i.name) and not i.name.startswith(".")]

        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "
            child_prefix = "    " if is_last else "│   "

            if item.is_dir():
                lines.append(f"{prefix}{connector}{item.name}/")
                _walk(item, prefix + child_prefix, depth + 1)
            else:
                lines.append(f"{prefix}{connector}{item.name}")

    _walk(project_path, "", 0)
    print_step(1, 1, "生成文件树", status="完成")
    return "\n".join(lines)


def find_config_files(project_path: Path) -> list:
    """查找项目中的配置文件"""
    print_step(1, 1, "查找配置文件", str(project_path))

    config_files = []

    for dirpath, dirnames, filenames in os.walk(project_path):
        dirnames[:] = [d for d in dirnames if not should_exclude_dir(d)]

        for f in filenames:
            filepath = Path(dirpath) / f
            rel_path = filepath.relative_to(project_path)

            # 检查精确匹配
            if f in CONFIG_FILE_PATTERNS:
                config_files.append(str(rel_path))
                continue

            # 检查 glob 模式匹配
            import fnmatch
            for pattern in CONFIG_FILE_GLOBS:
                if fnmatch.fnmatch(f, pattern):
                    config_files.append(str(rel_path))
                    break

    # 去重并排序
    config_files = sorted(set(config_files))
    print_step(1, 1, "查找配置文件", status="完成")
    print(f"  发现 {len(config_files)} 个配置文件")
    return config_files


def parse_dependencies(project_path: Path, tech_stacks: list) -> dict:
    """解析项目依赖关系"""
    print_step(1, 1, "解析依赖关系", str(project_path))

    dependencies = {}

    # Node.js — package.json
    if "Node.js" in tech_stacks or any(
        (project_path / d / "package.json").exists()
        for d in [""] + [d.name for d in project_path.iterdir() if d.is_dir()]
    ):
        pkg_path = project_path / "package.json"
        if pkg_path.exists():
            data = safe_read_json(pkg_path)
            if data:
                deps = {}
                for section in ["dependencies", "devDependencies", "peerDependencies"]:
                    if section in data:
                        deps[section] = data[section]
                dependencies["npm"] = deps
                print(f"  解析 package.json：{sum(len(v) for v in deps.values())} 个依赖")

    # Python — requirements.txt
    if "Python" in tech_stacks:
        req_path = project_path / "requirements.txt"
        if req_path.exists():
            content = safe_read_text(req_path)
            if content:
                reqs = []
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("-"):
                        reqs.append(line)
                dependencies["pip"] = reqs
                print(f"  解析 requirements.txt：{len(reqs)} 个依赖")

        # Python — pyproject.toml
        pyproject_path = project_path / "pyproject.toml"
        if pyproject_path.exists():
            content = safe_read_text(pyproject_path)
            if content:
                # 简单解析 [project.dependencies] 段
                in_deps = False
                deps = []
                for line in content.splitlines():
                    stripped = line.strip()
                    if stripped == "[project.dependencies]" or stripped == "[tool.poetry.dependencies]":
                        in_deps = True
                        continue
                    if stripped.startswith("[") and in_deps:
                        in_deps = False
                        continue
                    if in_deps and stripped and not stripped.startswith("#"):
                        deps.append(stripped)
                if deps:
                    dependencies["pyproject"] = deps
                    print(f"  解析 pyproject.toml：{len(deps)} 个依赖")

    # Go — go.mod
    if "Go" in tech_stacks:
        gomod_path = project_path / "go.mod"
        if gomod_path.exists():
            content = safe_read_text(gomod_path)
            if content:
                go_deps = []
                in_require = False
                for line in content.splitlines():
                    stripped = line.strip()
                    if stripped.startswith("require ("):
                        in_require = True
                        continue
                    if stripped == ")" and in_require:
                        in_require = False
                        continue
                    if in_require and stripped and not stripped.startswith("//"):
                        go_deps.append(stripped)
                    elif stripped.startswith("require ") and not stripped.endswith("("):
                        # 单行 require
                        go_deps.append(stripped.replace("require ", "").rstrip())
                dependencies["go"] = go_deps
                print(f"  解析 go.mod：{len(go_deps)} 个依赖")

    # Rust — Cargo.toml
    if "Rust" in tech_stacks:
        cargo_path = project_path / "Cargo.toml"
        if cargo_path.exists():
            content = safe_read_text(cargo_path)
            if content:
                in_deps = False
                deps = []
                for line in content.splitlines():
                    stripped = line.strip()
                    if stripped == "[dependencies]":
                        in_deps = True
                        continue
                    if stripped.startswith("[") and in_deps:
                        in_deps = False
                        continue
                    if in_deps and stripped and not stripped.startswith("#"):
                        deps.append(stripped)
                dependencies["cargo"] = deps
                print(f"  解析 Cargo.toml：{len(deps)} 个依赖")

    print_step(1, 1, "解析依赖关系", status="完成")
    return dependencies


def scan_ports(project_path: Path) -> list:
    """扫描项目中的端口引用"""
    print_step(1, 1, "扫描端口引用", str(project_path))

    ports = []
    seen = set()

    for dirpath, dirnames, filenames in os.walk(project_path):
        dirnames[:] = [d for d in dirnames if not should_exclude_dir(d)]

        for f in filenames:
            filepath = Path(dirpath) / f
            if filepath.suffix.lower() not in SOURCE_EXTENSIONS:
                continue

            content = safe_read_text(filepath)
            if content is None:
                continue

            rel_path = filepath.relative_to(project_path)

            for match in PORT_PATTERN.finditer(content):
                # 从三个捕获组中取第一个非空值
                port_num = match.group(1) or match.group(2) or match.group(3)
                if port_num and port_num not in seen:
                    # 过滤掉明显不是端口的数字（如年份 2024、版本号等）
                    port_int = int(port_num)
                    if 1024 <= port_int <= 65535:
                        seen.add(port_num)
                        # 获取上下文行
                        line_num = content[:match.start()].count("\n") + 1
                        lines = content.split("\n")
                        context = lines[line_num - 1].strip() if line_num <= len(lines) else ""
                        ports.append({
                            "port": port_num,
                            "file": str(rel_path),
                            "line": line_num,
                            "context": context[:200],  # 截断过长行
                        })

    ports.sort(key=lambda x: int(x["port"]))
    print_step(1, 1, "扫描端口引用", status="完成")
    print(f"  发现 {len(ports)} 个端口引用")
    return ports


def scan_env_vars(project_path: Path) -> list:
    """扫描项目中的环境变量引用"""
    print_step(1, 1, "扫描环境变量引用", str(project_path))

    env_vars = []
    seen = set()

    for dirpath, dirnames, filenames in os.walk(project_path):
        dirnames[:] = [d for d in dirnames if not should_exclude_dir(d)]

        for f in filenames:
            filepath = Path(dirpath) / f
            if filepath.suffix.lower() not in SOURCE_EXTENSIONS:
                continue

            content = safe_read_text(filepath)
            if content is None:
                continue

            rel_path = filepath.relative_to(project_path)

            for pattern in ENV_VAR_PATTERNS:
                for match in pattern.finditer(content):
                    var_name = match.group(1)
                    # 过滤掉常见非环境变量（如 Shell 内置变量、CSS 变量等）
                    if var_name in {"PATH", "HOME", "USER", "SHELL", "PWD", "IFS",
                                    "true", "false", "null", "undefined", "self"}:
                        continue
                    # 过滤过短或过长的变量名
                    if len(var_name) < 2 or len(var_name) > 64:
                        continue
                    # 过滤纯小写（通常是代码变量而非环境变量）
                    if var_name.islower() and not var_name.startswith("app_"):
                        continue

                    key = (var_name, str(rel_path))
                    if key not in seen:
                        seen.add(key)
                        line_num = content[:match.start()].count("\n") + 1
                        env_vars.append({
                            "name": var_name,
                            "file": str(rel_path),
                            "line": line_num,
                        })

    env_vars.sort(key=lambda x: x["name"])
    print_step(1, 1, "扫描环境变量引用", status="完成")
    print(f"  发现 {len(env_vars)} 个环境变量引用")
    return env_vars


def scan_api_endpoints(project_path: Path) -> list:
    """扫描项目中的 API 端点引用"""
    print_step(1, 1, "扫描 API 端点引用", str(project_path))

    endpoints = []
    seen = set()

    for dirpath, dirnames, filenames in os.walk(project_path):
        dirnames[:] = [d for d in dirnames if not should_exclude_dir(d)]

        for f in filenames:
            filepath = Path(dirpath) / f
            if filepath.suffix.lower() not in SOURCE_EXTENSIONS:
                continue

            content = safe_read_text(filepath)
            if content is None:
                continue

            rel_path = filepath.relative_to(project_path)

            for pattern in API_ENDPOINT_PATTERNS:
                for match in pattern.finditer(content):
                    endpoint = match.group(0).rstrip(",;)]}'\"")
                    # 过滤过短或明显非端点的匹配
                    if len(endpoint) < 10:
                        continue
                    # 过滤常见非端点 URL
                    if any(skip in endpoint.lower() for skip in [
                        "github.com", "npmjs.com", "pypi.org", "crates.io",
                        "registry.npmjs.org", "fonts.googleapis", "cdn.",
                        "creativecommons.org", "w3.org", "schema.org",
                        "example.com", "example.org",
                    ]):
                        continue

                    if endpoint not in seen:
                        seen.add(endpoint)
                        line_num = content[:match.start()].count("\n") + 1
                        endpoints.append({
                            "url": endpoint,
                            "file": str(rel_path),
                            "line": line_num,
                        })

    endpoints.sort(key=lambda x: x["url"])
    print_step(1, 1, "扫描 API 端点引用", status="完成")
    print(f"  发现 {len(endpoints)} 个 API 端点引用")
    return endpoints


def scan_project(project_path: Path) -> dict:
    """完整扫描一个项目，返回结构化结果"""
    project_path = project_path.resolve()
    if not project_path.exists():
        print(f"[错误] 项目路径不存在：{project_path}")
        sys.exit(1)
    if not project_path.is_dir():
        print(f"[错误] 路径不是目录：{project_path}")
        sys.exit(1)

    project_name = project_path.name
    total_steps = 7

    print("\n" + "=" * 60)
    print(f"AOS 迁移采集 — 项目扫描")
    print(f"项目：{project_name} | 路径：{project_path}")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 步骤 1：检测技术栈
    print_step(1, total_steps, "检测技术栈", str(project_path))
    tech_stacks = detect_tech_stack(project_path)

    # 步骤 2：生成文件树
    print_step(2, total_steps, "生成文件树", str(project_path))
    file_tree = generate_file_tree(project_path)

    # 步骤 3：查找配置文件
    print_step(3, total_steps, "查找配置文件", str(project_path))
    config_files = find_config_files(project_path)

    # 步骤 4：解析依赖关系
    print_step(4, total_steps, "解析依赖关系", str(project_path))
    dependencies = parse_dependencies(project_path, tech_stacks)

    # 步骤 5：扫描端口引用
    print_step(5, total_steps, "扫描端口引用", str(project_path))
    ports = scan_ports(project_path)

    # 步骤 6：扫描环境变量引用
    print_step(6, total_steps, "扫描环境变量引用", str(project_path))
    env_vars = scan_env_vars(project_path)

    # 步骤 7：扫描 API 端点引用
    print_step(7, total_steps, "扫描 API 端点引用", str(project_path))
    api_endpoints = scan_api_endpoints(project_path)

    result = {
        "project_name": project_name,
        "project_path": str(project_path),
        "scanned_at": datetime.now().isoformat(),
        "tech_stacks": tech_stacks,
        "file_tree": file_tree,
        "config_files": config_files,
        "dependencies": dependencies,
        "ports": ports,
        "env_vars": env_vars,
        "api_endpoints": api_endpoints,
        "summary": {
            "tech_stack_count": len(tech_stacks),
            "config_file_count": len(config_files),
            "port_count": len(ports),
            "env_var_count": len(env_vars),
            "api_endpoint_count": len(api_endpoints),
            "dependency_count": sum(
                len(v) if isinstance(v, list) else sum(len(vv) for vv in v.values())
                for v in dependencies.values()
            ),
        },
    }

    print("\n" + "=" * 60)
    print(f"项目扫描完成 — {project_name}")
    print(f"技术栈：{', '.join(tech_stacks) if tech_stacks else '未识别'}")
    print(f"配置文件：{len(config_files)} | 端口：{len(ports)} | 环境变量：{len(env_vars)} | API端点：{len(api_endpoints)}")
    print("=" * 60)

    return result


# ──────────────────────────────────────────────
# 对话提取处理功能
# ──────────────────────────────────────────────

def parse_frontmatter(content: str) -> tuple:
    """解析 Markdown 文件的 frontmatter，返回 (metadata, body)"""
    metadata = {}
    body = content

    # 匹配 --- 包裹的 frontmatter
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if fm_match:
        fm_text = fm_match.group(1)
        body = content[fm_match.end():]

        # 简单 YAML 解析（不依赖 PyYAML）
        for line in fm_text.splitlines():
            line = line.strip()
            if ":" in line and not line.startswith("#"):
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                # 处理列表值
                if value.startswith("[") and value.endswith("]"):
                    value = [v.strip().strip('"').strip("'") for v in value[1:-1].split(",") if v.strip()]
                metadata[key] = value

    return metadata, body


def extract_key_decisions(body: str) -> list:
    """从对话正文中提取关键决策"""
    decisions = []
    # 匹配决策标记：## 决策、**决策**、决定、选择 等关键词
    decision_patterns = [
        re.compile(r'(?:^|\n)#{1,3}\s*(?:决策|决定|选择|方案|结论)[：:\s]*(.*?)(?=\n#{1,3}|\n\n|\Z)', re.DOTALL),
        re.compile(r'\*\*(?:决策|决定|选择|方案|结论)\*\*[：:\s]*(.*?)(?=\n\n|\Z)', re.DOTALL),
    ]
    for pattern in decision_patterns:
        for match in pattern.finditer(body):
            text = match.group(1).strip()
            if text and len(text) > 5:
                # 截取第一行作为摘要
                summary = text.split("\n")[0].strip()[:200]
                decisions.append(summary)

    return decisions


def extract_modified_files(body: str) -> list:
    """从对话正文中提取修改的文件路径"""
    files = set()
    # 匹配文件路径引用
    file_patterns = [
        re.compile(r'(?:修改|编辑|创建|新增|删除|更新)\s*[了：:]?\s*[`"\']?([a-zA-Z0-9_./\\-]+\.[a-zA-Z0-9]+)[`"\']?', re.IGNORECASE),
        re.compile(r'[`"\']([a-zA-Z0-9_./\\-]+\.(?:py|js|ts|jsx|tsx|go|rs|java|cs|rb|php|yaml|yml|json|toml|md|sql|sh))[`"\']'),
    ]
    for pattern in file_patterns:
        for match in pattern.finditer(body):
            filepath = match.group(1)
            # 过滤过短的匹配
            if len(filepath) > 3 and "/" in filepath or "\\" in filepath or "." in filepath:
                files.add(filepath)

    return sorted(files)


def extract_unresolved_issues(body: str) -> list:
    """从对话正文中提取未解决问题"""
    issues = []
    issue_patterns = [
        re.compile(r'(?:^|\n)#{1,3}\s*(?:未解决|待解决|TODO|FIXME|问题|疑问)[：:\s]*(.*?)(?=\n#{1,3}|\n\n|\Z)', re.DOTALL),
        re.compile(r'\*\*(?:未解决|待解决|TODO|FIXME)\*\*[：:\s]*(.*?)(?=\n\n|\Z)', re.DOTALL),
        re.compile(r'(?:TODO|FIXME|HACK|XXX)[：:\s]+(.*?)(?=\n|\Z)'),
    ]
    for pattern in issue_patterns:
        for match in pattern.finditer(body):
            text = match.group(1).strip()
            if text and len(text) > 3:
                summary = text.split("\n")[0].strip()[:200]
                issues.append(summary)

    return issues


def extract_gotchas(body: str) -> list:
    """从对话正文中提取经验坑点"""
    gotchas = []
    gotcha_patterns = [
        re.compile(r'(?:^|\n)#{1,3}\s*(?:坑点|注意|踩坑|经验|教训|避坑)[：:\s]*(.*?)(?=\n#{1,3}|\n\n|\Z)', re.DOTALL),
        re.compile(r'\*\*(?:坑点|注意|踩坑|经验|教训)\*\*[：:\s]*(.*?)(?=\n\n|\Z)', re.DOTALL),
    ]
    for pattern in gotcha_patterns:
        for match in pattern.finditer(body):
            text = match.group(1).strip()
            if text and len(text) > 3:
                summary = text.split("\n")[0].strip()[:200]
                gotchas.append(summary)

    return gotchas


def process_chat_extract(input_path: Path) -> dict:
    """处理对话提取文件，返回结构化结果"""
    input_path = input_path.resolve()
    if not input_path.exists():
        print(f"[错误] 对话提取文件不存在：{input_path}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print(f"AOS 迁移采集 — 对话提取处理")
    print(f"文件：{input_path.name}")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    total_steps = 5

    # 步骤 1：读取文件
    print_step(1, total_steps, "读取对话提取文件", str(input_path))
    content = safe_read_text(input_path)
    if content is None:
        print(f"[错误] 无法读取文件：{input_path}")
        sys.exit(1)

    # 步骤 2：解析 frontmatter
    print_step(2, total_steps, "解析 frontmatter")
    metadata, body = parse_frontmatter(content)
    print(f"  元数据字段：{list(metadata.keys())}")

    # 步骤 3：提取关键决策
    print_step(3, total_steps, "提取关键决策")
    decisions = extract_key_decisions(body)
    print(f"  发现 {len(decisions)} 条关键决策")

    # 步骤 4：提取修改文件和未解决问题
    print_step(4, total_steps, "提取修改文件与未解决问题")
    modified_files = extract_modified_files(body)
    unresolved = extract_unresolved_issues(body)
    gotchas = extract_gotchas(body)
    print(f"  修改文件：{len(modified_files)} | 未解决问题：{len(unresolved)} | 经验坑点：{len(gotchas)}")

    # 步骤 5：组装结果
    print_step(5, total_steps, "组装提取结果")
    result = {
        "source_file": input_path.name,
        "processed_at": datetime.now().isoformat(),
        "frontmatter": metadata,
        "key_decisions": decisions,
        "modified_files": modified_files,
        "unresolved_issues": unresolved,
        "gotchas": gotchas,
        "related_projects": metadata.get("project", []),
        "summary": {
            "decision_count": len(decisions),
            "modified_file_count": len(modified_files),
            "unresolved_count": len(unresolved),
            "gotcha_count": len(gotchas),
        },
    }

    print_step(5, total_steps, "组装提取结果", status="完成")
    print("\n" + "=" * 60)
    print(f"对话提取处理完成 — {input_path.name}")
    print(f"决策：{len(decisions)} | 修改文件：{len(modified_files)} | 未解决：{len(unresolved)} | 坑点：{len(gotchas)}")
    print("=" * 60)

    return result


# ──────────────────────────────────────────────
# 目录扫描功能
# ──────────────────────────────────────────────

def is_project_directory(directory: Path) -> bool:
    """判断目录是否是一个项目（包含项目标记文件）"""
    project_markers = [
        "package.json", "requirements.txt", "pyproject.toml", "setup.py",
        "Cargo.toml", "go.mod", ".csproj", "pom.xml", "build.gradle",
        "Gemfile", "composer.json", "pubspec.yaml", "mix.exs",
        ".git",  # Git 仓库也视为项目
    ]
    for marker in project_markers:
        # 检查根目录
        if (directory / marker).exists():
            return True
        # 检查 .csproj 等可能带前缀的文件
        if marker.startswith("."):
            continue
        for f in directory.iterdir():
            if f.is_file() and f.name.endswith(marker.lstrip("*")):
                return True
    return False


def scan_directory(dir_path: Path) -> list:
    """扫描目录下所有项目"""
    dir_path = dir_path.resolve()
    if not dir_path.exists():
        print(f"[错误] 扫描目录不存在：{dir_path}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print(f"AOS 迁移采集 — 目录扫描")
    print(f"目录：{dir_path}")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 步骤 1：发现项目
    print_step(1, 2, "发现项目目录", str(dir_path))
    projects = []

    try:
        items = list(dir_path.iterdir())
    except PermissionError:
        print(f"[错误] 无权限访问目录：{dir_path}")
        sys.exit(1)

    for item in items:
        if item.is_dir() and not should_exclude_dir(item.name) and not item.name.startswith("."):
            if is_project_directory(item):
                projects.append(item)
                print(f"  发现项目：{item.name}")

    if not projects:
        print("  未发现项目目录")
        return []

    print(f"  共发现 {len(projects)} 个项目")

    # 步骤 2：逐一扫描
    print_step(2, 2, "逐一扫描项目")
    results = []
    for i, proj in enumerate(projects, 1):
        print(f"\n  [{i}/{len(projects)}] 扫描：{proj.name}")
        try:
            result = scan_project(proj)
            results.append(result)
        except Exception as e:
            print(f"  [错误] 扫描失败 {proj.name}: {e}")

    print_step(2, 2, "逐一扫描项目", status="完成")
    print(f"\n目录扫描完成 — 共扫描 {len(results)} 个项目")
    return results


# ──────────────────────────────────────────────
# Phase 0：环境调研与安全准备
# ──────────────────────────────────────────────

def _run_cmd(cmd: str, timeout: int = 30) -> tuple:
    """执行 shell 命令，返回 (returncode, stdout, stderr)"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", f"命令超时（{timeout}s）"
    except Exception as e:
        return -1, "", str(e)


def append_operation_log(log_file: Path, phase: str, step: str,
                         action: str, status: str, detail: str = ""):
    """追加一条操作日志到 operation_log.json"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "phase": phase,
        "step": step,
        "action": action,
        "status": status,
        "detail": detail,
    }
    logs = []
    if log_file.exists():
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except (json.JSONDecodeError, IOError):
            logs = []
    logs.append(entry)
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def phase0_detect_service_status(project_path: Path, log_file: Path) -> dict:
    """Phase 0 步骤 a：服务状态检测"""
    step_name = "服务状态检测"
    print_step(1, 5, step_name, str(project_path))
    append_operation_log(log_file, "phase0", "1", step_name, "执行中")

    service_info = {
        "processes": [],
        "listening_ports": [],
        "docker_containers": [],
        "systemd_services": [],
    }

    # 1. 扫描运行中进程
    rc, out, err = _run_cmd("ps aux --sort=-%mem 2>/dev/null || tasklist /FO CSV 2>NUL")
    if rc == 0 and out:
        lines = out.splitlines()
        # 最多取前 50 行
        for line in lines[:50]:
            service_info["processes"].append(line.strip())
    else:
        print(f"  [警告] 进程扫描失败：{err or '无输出'}")

    # 2. 扫描监听端口
    rc, out, err = _run_cmd("ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null || netstat -an 2>NUL")
    if rc == 0 and out:
        for line in out.splitlines():
            stripped = line.strip()
            if stripped and ("LISTEN" in stripped.upper() or "监听" in stripped):
                service_info["listening_ports"].append(stripped)
    else:
        print(f"  [警告] 端口扫描失败：{err or '无输出'}")

    # 3. 扫描 Docker 容器
    rc, out, err = _run_cmd("docker ps --format '{{.ID}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}\\t{{.Names}}' 2>/dev/null")
    if rc == 0 and out:
        for line in out.splitlines():
            parts = line.strip().split("\t")
            if len(parts) >= 5:
                service_info["docker_containers"].append({
                    "id": parts[0],
                    "image": parts[1],
                    "status": parts[2],
                    "ports": parts[3],
                    "name": parts[4],
                })
    else:
        print(f"  [提示] Docker 容器扫描跳过：{err or 'Docker 未运行或未安装'}")

    # 4. 扫描 systemd 服务
    rc, out, err = _run_cmd("systemctl list-units --type=service --state=running --no-pager 2>/dev/null")
    if rc == 0 and out:
        for line in out.splitlines():
            stripped = line.strip()
            if stripped and ".service" in stripped:
                service_info["systemd_services"].append(stripped)
    else:
        print(f"  [提示] systemd 服务扫描跳过：{err or '非 systemd 系统'}")

    # 同时扫描项目目录下的 docker-compose 文件以补充信息
    for compose_name in ["docker-compose.yml", "docker-compose.yaml"]:
        compose_path = project_path / compose_name
        if compose_path.exists():
            content = safe_read_text(compose_path)
            if content:
                service_info["compose_file"] = content[:5000]

    print_step(1, 5, step_name, status="完成")
    append_operation_log(
        log_file, "phase0", "1", step_name, "完成",
        f"进程:{len(service_info['processes'])} 端口:{len(service_info['listening_ports'])} "
        f"容器:{len(service_info['docker_containers'])} 服务:{len(service_info['systemd_services'])}"
    )
    return service_info


def phase0_health_check(project_path: Path, service_info: dict,
                        log_file: Path) -> dict:
    """Phase 0 步骤 b：健康检查"""
    step_name = "健康检查"
    print_step(2, 5, step_name, str(project_path))
    append_operation_log(log_file, "phase0", "2", step_name, "执行中")

    health = {
        "service_status": "unknown",
        "disk_space": {},
        "database_connections": [],
        "warnings": [],
    }

    # 1. 验证服务运行状态
    running_containers = len(service_info.get("docker_containers", []))
    running_services = len(service_info.get("systemd_services", []))
    if running_containers > 0 or running_services > 0:
        health["service_status"] = "running"
    else:
        health["service_status"] = "no_active_service_detected"
        health["warnings"].append("未检测到活跃的 Docker 容器或 systemd 服务")

    # 2. 检查磁盘空间
    rc, out, err = _run_cmd("df -h 2>/dev/null || wmic logicaldisk get size,freespace,caption 2>NUL")
    if rc == 0 and out:
        for line in out.splitlines():
            stripped = line.strip()
            if stripped:
                health["disk_space"][f"line_{len(health['disk_space'])}"] = stripped
    else:
        health["warnings"].append(f"磁盘空间检查失败：{err or '无输出'}")

    # 3. 检查数据库连接（扫描项目配置中的数据库连接信息）
    db_keywords = ["mysql", "postgres", "mongodb", "redis", "sqlite", "database", "db_host", "db_port"]
    for dirpath, dirnames, filenames in os.walk(project_path):
        dirnames[:] = [d for d in dirnames if not should_exclude_dir(d)]
        for f in filenames:
            filepath = Path(dirpath) / f
            if filepath.suffix.lower() not in SOURCE_EXTENSIONS:
                continue
            content = safe_read_text(filepath)
            if content is None:
                continue
            content_lower = content.lower()
            for kw in db_keywords:
                if kw in content_lower:
                    rel_path = str(filepath.relative_to(project_path))
                    # 避免重复
                    existing_paths = [c["config_file"] for c in health["database_connections"]]
                    if rel_path not in existing_paths:
                        health["database_connections"].append({
                            "config_file": rel_path,
                            "keyword_matched": kw,
                        })
                    break

    if health["warnings"]:
        print(f"  警告：{'; '.join(health['warnings'])}")

    print_step(2, 5, step_name, status="完成")
    append_operation_log(
        log_file, "phase0", "2", step_name, "完成",
        f"服务状态:{health['service_status']} 数据库配置:{len(health['database_connections'])} 警告:{len(health['warnings'])}"
    )
    return health


def phase0_security_backup(project_path: Path, log_file: Path) -> dict:
    """Phase 0 步骤 c：安全备份"""
    step_name = "安全备份"
    print_step(3, 5, step_name, str(project_path))
    append_operation_log(log_file, "phase0", "3", step_name, "执行中")

    backup_info = {
        "backup_location": "",
        "backup_checksum": "",
        "file_count": 0,
        "total_size_bytes": 0,
    }

    # 备份目标目录
    aos_root = find_aos_root()
    backup_dir = aos_root / "08_INBOX" / "migration" / "backups" / project_path.name
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"backup_{timestamp}"

    try:
        # 完整复制项目到备份位置
        shutil.copytree(project_path, backup_path, ignore=shutil.ignore_patterns(
            "node_modules", ".git", "venv", ".venv", "__pycache__",
            "dist", "build", ".next", "target", "bin", "obj",
            ".cache", ".tox", "*.egg-info",
        ))
        print(f"  备份已创建：{backup_path}")
    except Exception as e:
        print(f"  [错误] 备份失败：{e}")
        print_step(3, 5, step_name, status="失败")
        append_operation_log(log_file, "phase0", "3", step_name, "失败", str(e))
        return backup_info

    # 计算备份校验和（对关键文件生成 SHA256 摘要）
    hasher = hashlib.sha256()
    file_count = 0
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(backup_path):
        dirnames.sort()
        for f in sorted(filenames):
            filepath = Path(dirpath) / f
            try:
                data = filepath.read_bytes()
                hasher.update(data)
                total_size += len(data)
                file_count += 1
            except Exception:
                pass

    checksum = hasher.hexdigest()
    backup_info["backup_location"] = str(backup_path)
    backup_info["backup_checksum"] = checksum
    backup_info["file_count"] = file_count
    backup_info["total_size_bytes"] = total_size

    print(f"  备份文件数：{file_count} | 总大小：{total_size} 字节")
    print(f"  校验和：{checksum[:16]}...")

    print_step(3, 5, step_name, status="完成")
    append_operation_log(
        log_file, "phase0", "3", step_name, "完成",
        f"文件数:{file_count} 大小:{total_size} 校验和:{checksum[:16]}"
    )
    return backup_info


def phase0_extract_sensitive_info(project_path: Path, service_info: dict,
                                  log_file: Path) -> dict:
    """Phase 0 步骤 d：敏感信息提取"""
    step_name = "敏感信息提取"
    print_step(4, 5, step_name, str(project_path))
    append_operation_log(log_file, "phase0", "4", step_name, "执行中")

    sensitive = {
        "project_name": project_path.name,
        "extracted_at": datetime.now().isoformat(),
        "ports": [],
        "interfaces": [],
        "file_paths": [],
        "env_vars": [],
        "dependencies": [],
        "cron_jobs": [],
        "migration_warnings": [],
    }

    # 1. 提取端口映射
    seen_ports = set()
    # 从项目文件中提取
    for dirpath, dirnames, filenames in os.walk(project_path):
        dirnames[:] = [d for d in dirnames if not should_exclude_dir(d)]
        for f in filenames:
            filepath = Path(dirpath) / f
            if filepath.suffix.lower() not in SOURCE_EXTENSIONS:
                continue
            content = safe_read_text(filepath)
            if content is None:
                continue
            rel_path = str(filepath.relative_to(project_path))
            for match in PORT_PATTERN.finditer(content):
                port_num = match.group(1) or match.group(2) or match.group(3)
                if port_num and port_num not in seen_ports:
                    port_int = int(port_num)
                    if 1024 <= port_int <= 65535:
                        seen_ports.add(port_num)
                        # 推断协议和服务
                        protocol = "tcp"
                        service = ""
                        critical = port_int < 1024 + 1000
                        content_lower = content.lower()
                        if "https" in content_lower or "ssl" in content_lower or port_int == 443:
                            protocol = "https"
                            service = "https"
                            critical = True
                        elif "http" in content_lower or port_int == 80 or port_int == 8080:
                            protocol = "http"
                            service = "http"
                        elif port_int == 5432:
                            service = "postgresql"
                            critical = True
                        elif port_int == 3306:
                            service = "mysql"
                            critical = True
                        elif port_int == 6379:
                            service = "redis"
                            critical = True
                        elif port_int == 27017:
                            service = "mongodb"
                            critical = True
                        sensitive["ports"].append({
                            "port": port_int,
                            "protocol": protocol,
                            "service": service,
                            "config_file": rel_path,
                            "critical": critical,
                        })

    # 从系统监听端口补充
    for line in service_info.get("listening_ports", []):
        port_match = re.search(r':(\d{4,5})\s', line)
        if port_match:
            port_str = port_match.group(1)
            if port_str not in seen_ports:
                seen_ports.add(port_str)
                sensitive["ports"].append({
                    "port": int(port_str),
                    "protocol": "tcp",
                    "service": "",
                    "config_file": "",
                    "critical": int(port_str) < 2000,
                })

    # 从 Docker 容器端口映射补充
    for container in service_info.get("docker_containers", []):
        ports_str = container.get("ports", "")
        for port_match in re.finditer(r'(\d{4,5})', ports_str):
            port_str = port_match.group(1)
            if port_str not in seen_ports:
                seen_ports.add(port_str)
                sensitive["ports"].append({
                    "port": int(port_str),
                    "protocol": "tcp",
                    "service": f"docker:{container.get('name', '')}",
                    "config_file": "",
                    "critical": int(port_str) < 2000,
                })

    # 2. 提取接口清单
    seen_endpoints = set()
    for dirpath, dirnames, filenames in os.walk(project_path):
        dirnames[:] = [d for d in dirnames if not should_exclude_dir(d)]
        for f in filenames:
            filepath = Path(dirpath) / f
            if filepath.suffix.lower() not in SOURCE_EXTENSIONS:
                continue
            content = safe_read_text(filepath)
            if content is None:
                continue
            # 路由定义模式
            route_patterns = [
                re.compile(r'(?:@app\.route|@router\.(?:get|post|put|delete|patch)|router\.(?:get|post|put|delete|patch))\s*\(\s*["\']([^"\']+)["\']', re.IGNORECASE),
                re.compile(r'(?:app\.(?:get|post|put|delete|patch)|server\.(?:get|post|put|delete|patch))\s*\(\s*["\']([^"\']+)["\']', re.IGNORECASE),
                re.compile(r'(?:GET|POST|PUT|DELETE|PATCH)\s+(/[/\w\-{}:]+)', re.IGNORECASE),
                re.compile(r'["\'](/api/[/\w\-{}:]+)["\']', re.IGNORECASE),
            ]
            for pattern in route_patterns:
                for match in pattern.finditer(content):
                    endpoint = match.group(1)
                    if endpoint in seen_endpoints or len(endpoint) < 2:
                        continue
                    seen_endpoints.add(endpoint)
                    internal = "internal" in content[:match.start()].lower()[-200:] or "localhost" in content[:match.start()].lower()[-200:]
                    sensitive["interfaces"].append({
                        "type": "api",
                        "endpoint": endpoint,
                        "internal": internal,
                        "critical": not internal,
                    })

    # 3. 提取关键文件路径
    critical_path_patterns = [
        (".env", "环境变量文件", True),
        (".env.local", "本地环境变量文件", True),
        (".env.production", "生产环境变量文件", True),
        ("docker-compose.yml", "Docker 编排文件", True),
        ("docker-compose.yaml", "Docker 编排文件", True),
        ("Dockerfile", "Docker 构建文件", True),
        ("nginx.conf", "Nginx 配置", True),
        ("config.json", "JSON 配置文件", True),
        ("config.yaml", "YAML 配置文件", True),
        ("config.yml", "YAML 配置文件", True),
    ]
    for pattern_str, type_label, critical in critical_path_patterns:
        if (project_path / pattern_str).exists():
            sensitive["file_paths"].append({
                "path": pattern_str,
                "type": type_label,
                "critical": critical,
            })
    # 扫描其他配置文件
    for dirpath, dirnames, filenames in os.walk(project_path):
        dirnames[:] = [d for d in dirnames if not should_exclude_dir(d)]
        for f in filenames:
            rel = str((Path(dirpath) / f).relative_to(project_path))
            if any(p["path"] == rel for p in sensitive["file_paths"]):
                continue
            if f.endswith((".key", ".pem", ".p12", ".jks", ".cert", ".crt")):
                sensitive["file_paths"].append({
                    "path": rel,
                    "type": "证书/密钥文件",
                    "critical": True,
                })
                sensitive["migration_warnings"].append(f"发现证书/密钥文件：{rel}，迁移时需特殊处理")
            elif f.endswith((".sql", ".db", ".sqlite", ".sqlite3")):
                sensitive["file_paths"].append({
                    "path": rel,
                    "type": "数据库文件",
                    "critical": True,
                })

    # 4. 提取环境变量
    seen_env_keys = set()
    for dirpath, dirnames, filenames in os.walk(project_path):
        dirnames[:] = [d for d in dirnames if not should_exclude_dir(d)]
        for f in filenames:
            filepath = Path(dirpath) / f
            if filepath.suffix.lower() not in SOURCE_EXTENSIONS:
                continue
            content = safe_read_text(filepath)
            if content is None:
                continue
            for pattern in ENV_VAR_PATTERNS:
                for match in pattern.finditer(content):
                    var_name = match.group(1)
                    if var_name in {"PATH", "HOME", "USER", "SHELL", "PWD", "IFS",
                                    "true", "false", "null", "undefined", "self"}:
                        continue
                    if len(var_name) < 2 or len(var_name) > 64:
                        continue
                    if var_name.islower() and not var_name.startswith("app_"):
                        continue
                    if var_name in seen_env_keys:
                        continue
                    seen_env_keys.add(var_name)
                    # 推断值模式（不记录实际值）
                    value_pattern = "<string>"
                    critical = any(kw in var_name.upper() for kw in [
                        "PASSWORD", "SECRET", "KEY", "TOKEN", "PRIVATE",
                        "DATABASE_URL", "DB_PASS", "API_KEY", "ACCESS_KEY",
                    ])
                    if "URL" in var_name.upper():
                        value_pattern = "<url>"
                    elif "PORT" in var_name.upper():
                        value_pattern = "<port>"
                    elif "HOST" in var_name.upper():
                        value_pattern = "<hostname>"
                    elif "PATH" in var_name.upper():
                        value_pattern = "<path>"
                    elif "EMAIL" in var_name.upper():
                        value_pattern = "<email>"
                    sensitive["env_vars"].append({
                        "key": var_name,
                        "value_pattern": value_pattern,
                        "critical": critical,
                    })

    # 5. 提取依赖服务
    # 从 docker-compose 中提取
    compose_content = service_info.get("compose_file", "")
    if compose_content:
        service_pattern = re.compile(r'^\s{2}(\w[\w-]*):\s*$', re.MULTILINE)
        for match in service_pattern.finditer(compose_content):
            svc_name = match.group(1)
            if svc_name in ("build", "image", "ports", "volumes", "environment",
                            "depends_on", "networks", "restart", "command"):
                continue
            sensitive["dependencies"].append({
                "service": svc_name,
                "type": "docker-compose",
                "version_constraint": "",
                "critical": True,
            })

    # 从项目依赖文件中提取
    tech_stacks = detect_tech_stack(project_path)
    deps = parse_dependencies(project_path, tech_stacks)
    for pkg_manager, pkg_list in deps.items():
        if isinstance(pkg_list, dict):
            for section, items in pkg_list.items():
                if isinstance(items, dict):
                    for name, version in items.items():
                        sensitive["dependencies"].append({
                            "service": name,
                            "type": f"{pkg_manager}/{section}",
                            "version_constraint": str(version) if version else "",
                            "critical": False,
                        })
        elif isinstance(pkg_list, list):
            for item in pkg_list:
                name = item.split(">=")[0].split("==")[0].split("<=")[0].split("~=")[0].split("!")[0].strip()
                version = item.replace(name, "").strip()
                sensitive["dependencies"].append({
                    "service": name,
                    "type": pkg_manager,
                    "version_constraint": version,
                    "critical": False,
                })

    # 6. 提取定时任务
    rc, out, err = _run_cmd("crontab -l 2>/dev/null")
    if rc == 0 and out:
        for line in out.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                parts = stripped.split(None, 5)
                if len(parts) >= 6:
                    schedule = " ".join(parts[:5])
                    command = parts[5]
                    sensitive["cron_jobs"].append({
                        "schedule": schedule,
                        "command": command[:500],
                        "description": "",
                        "critical": any(kw in command.lower() for kw in [
                            "backup", "dump", "sync", "deploy", "migrate",
                        ]),
                    })

    # 检查项目目录中的定时任务配置
    for cron_file in ["crontab", ".crontab", "cron.txt"]:
        cron_path = project_path / cron_file
        if cron_path.exists():
            content = safe_read_text(cron_path)
            if content:
                for line in content.splitlines():
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#"):
                        parts = stripped.split(None, 5)
                        if len(parts) >= 6:
                            schedule = " ".join(parts[:5])
                            command = parts[5]
                            sensitive["cron_jobs"].append({
                                "schedule": schedule,
                                "command": command[:500],
                                "description": f"from {cron_file}",
                                "critical": True,
                            })

    # 汇总警告
    if not sensitive["ports"]:
        sensitive["migration_warnings"].append("未检测到端口映射，可能遗漏了服务入口")
    if not sensitive["interfaces"]:
        sensitive["migration_warnings"].append("未检测到 API 接口，可能需要手动补充")
    if not sensitive["env_vars"]:
        sensitive["migration_warnings"].append("未检测到环境变量引用，可能项目未使用外部配置")

    print_step(4, 5, step_name, status="完成")
    append_operation_log(
        log_file, "phase0", "4", step_name, "完成",
        f"端口:{len(sensitive['ports'])} 接口:{len(sensitive['interfaces'])} "
        f"文件:{len(sensitive['file_paths'])} 环境变量:{len(sensitive['env_vars'])} "
        f"依赖:{len(sensitive['dependencies'])} 定时任务:{len(sensitive['cron_jobs'])} "
        f"警告:{len(sensitive['migration_warnings'])}"
    )
    return sensitive


def phase0_generate_rollback_plan(project_path: Path, service_info: dict,
                                  backup_info: dict, log_file: Path) -> dict:
    """Phase 0 步骤 e：回滚方案生成"""
    step_name = "回滚方案生成"
    print_step(5, 5, step_name, str(project_path))
    append_operation_log(log_file, "phase0", "5", step_name, "执行中")

    rollback = {
        "project_name": project_path.name,
        "rollback_steps": [],
        "rollback_triggers": [],
        "backup_location": backup_info.get("backup_location", ""),
        "backup_checksum": backup_info.get("backup_checksum", ""),
    }

    step_num = 1

    # 步骤：停止服务
    docker_containers = service_info.get("docker_containers", [])
    if docker_containers:
        container_names = [c["name"] for c in docker_containers if c.get("name")]
        if container_names:
            rollback["rollback_steps"].append({
                "step": step_num,
                "action": "停止 Docker 容器",
                "command": f"docker stop {' '.join(container_names)}",
            })
            step_num += 1

    systemd_services = service_info.get("systemd_services", [])
    if systemd_services:
        service_names = []
        for line in systemd_services:
            match = re.search(r'(\S+\.service)', line)
            if match:
                service_names.append(match.group(1))
        if service_names:
            for svc in service_names:
                rollback["rollback_steps"].append({
                    "step": step_num,
                    "action": f"停止 systemd 服务 {svc}",
                    "command": f"sudo systemctl stop {svc}",
                })
                step_num += 1

    # 步骤：恢复备份
    if backup_info.get("backup_location"):
        rollback["rollback_steps"].append({
            "step": step_num,
            "action": "恢复项目文件备份",
            "command": f"cp -r {backup_info['backup_location']}/* {project_path}/",
        })
        step_num += 1

    # 步骤：重启服务
    if docker_containers:
        rollback["rollback_steps"].append({
            "step": step_num,
            "action": "重启 Docker 容器",
            "command": "docker-compose up -d",
        })
        step_num += 1

    if systemd_services:
        for svc in service_names:
            rollback["rollback_steps"].append({
                "step": step_num,
                "action": f"重启 systemd 服务 {svc}",
                "command": f"sudo systemctl start {svc}",
            })
            step_num += 1

    # 步骤：验证恢复
    rollback["rollback_steps"].append({
        "step": step_num,
        "action": "验证服务恢复状态",
        "command": "curl -f http://localhost/ || echo '服务未恢复'",
    })

    # 回滚触发条件
    rollback["rollback_triggers"] = [
        "迁移后服务无法启动超过 10 分钟",
        "核心接口返回 5xx 错误率超过 50%",
        "数据库连接失败且无法在 5 分钟内恢复",
        "关键数据丢失或损坏",
    ]

    print_step(5, 5, step_name, status="完成")
    append_operation_log(
        log_file, "phase0", "5", step_name, "完成",
        f"回滚步骤:{len(rollback['rollback_steps'])} 触发条件:{len(rollback['rollback_triggers'])}"
    )
    return rollback


def run_phase0(project_path: Path) -> dict:
    """执行 Phase 0：环境调研与安全准备"""
    project_path = project_path.resolve()
    if not project_path.exists():
        print(f"[错误] 项目路径不存在：{project_path}")
        sys.exit(1)
    if not project_path.is_dir():
        print(f"[错误] 路径不是目录：{project_path}")
        sys.exit(1)

    project_name = project_path.name
    total_steps = 5

    # 确保输出目录
    aos_root = find_aos_root()
    migration_dir = aos_root / "08_INBOX" / "migration"
    migration_dir.mkdir(parents=True, exist_ok=True)
    log_file = migration_dir / "operation_log.json"

    print("\n" + "=" * 60)
    print(f"AOS 迁移采集 — Phase 0 环境调研与安全准备")
    print(f"项目：{project_name} | 路径：{project_path}")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 步骤 a：服务状态检测
    service_info = phase0_detect_service_status(project_path, log_file)

    # 步骤 b：健康检查
    health = phase0_health_check(project_path, service_info, log_file)
    if health.get("service_status") == "no_active_service_detected":
        print("[警告] 未检测到活跃服务，继续执行但请确认项目运行状态")

    # 步骤 c：安全备份
    backup_info = phase0_security_backup(project_path, log_file)
    if not backup_info.get("backup_location"):
        print("[错误] 安全备份失败，终止后续步骤")
        append_operation_log(log_file, "phase0", "整体", "安全备份", "失败", "备份失败，流程终止")
        sys.exit(1)

    # 步骤 d：敏感信息提取
    sensitive_info = phase0_extract_sensitive_info(project_path, service_info, log_file)

    # 步骤 e：回滚方案生成
    rollback_plan = phase0_generate_rollback_plan(project_path, service_info, backup_info, log_file)

    # 写入敏感信息文件
    sensitive_file = migration_dir / "sensitive_info.json"
    with open(sensitive_file, "w", encoding="utf-8") as f:
        json.dump(sensitive_info, f, ensure_ascii=False, indent=2)
    print(f"  敏感信息已保存：{sensitive_file}")

    # 写入回滚方案文件
    rollback_file = migration_dir / "rollback_plan.json"
    with open(rollback_file, "w", encoding="utf-8") as f:
        json.dump(rollback_plan, f, ensure_ascii=False, indent=2)
    print(f"  回滚方案已保存：{rollback_file}")

    append_operation_log(log_file, "phase0", "整体", "Phase 0 完成", "完成",
                         f"项目:{project_name}")

    print("\n" + "=" * 60)
    print(f"Phase 0 完成 — {project_name}")
    print(f"端口：{len(sensitive_info['ports'])} | 接口：{len(sensitive_info['interfaces'])} | "
          f"环境变量：{len(sensitive_info['env_vars'])} | 依赖：{len(sensitive_info['dependencies'])}")
    print(f"回滚步骤：{len(rollback_plan['rollback_steps'])} | "
          f"警告：{len(sensitive_info['migration_warnings'])}")
    print("=" * 60)

    return {
        "service_info": service_info,
        "health": health,
        "backup_info": backup_info,
        "sensitive_info": sensitive_info,
        "rollback_plan": rollback_plan,
    }


# ──────────────────────────────────────────────
# 输出与状态管理
# ──────────────────────────────────────────────

def ensure_output_dirs(aos_root: Path) -> tuple:
    """确保输出目录存在，返回 (scan_dir, chat_dir, state_file) 路径"""
    scan_dir = aos_root / "08_INBOX" / "migration" / "project_scans"
    chat_dir = aos_root / "08_INBOX" / "migration" / "chat_extracts"
    state_file = aos_root / "08_INBOX" / "migration" / "migration_state.json"

    scan_dir.mkdir(parents=True, exist_ok=True)
    chat_dir.mkdir(parents=True, exist_ok=True)

    return scan_dir, chat_dir, state_file


def save_project_scan(result: dict, scan_dir: Path):
    """保存项目扫描结果到 JSON 文件"""
    project_name = result["project_name"]
    # 清理项目名中的特殊字符
    safe_name = re.sub(r'[^\w\-.]', '_', project_name)
    output_path = scan_dir / f"{safe_name}_scan.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"  扫描结果已保存：{output_path}")
    return output_path


def save_chat_extract(result: dict, chat_dir: Path, input_path: Path):
    """保存对话提取结果到 JSON 文件"""
    safe_name = input_path.stem
    output_path = chat_dir / f"{safe_name}_extract.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 同时复制原始文件到 chat_extracts 目录
    dest_file = chat_dir / input_path.name
    if input_path.resolve() != dest_file.resolve():
        shutil.copy2(input_path, dest_file)
        print(f"  原始文件已复制：{dest_file}")

    print(f"  提取结果已保存：{output_path}")
    return output_path


def update_migration_state(state_file: Path, entry_type: str, entry_data: dict):
    """更新迁移状态文件"""
    # 读取现有状态
    state = {}
    if state_file.exists():
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
        except (json.JSONDecodeError, IOError):
            state = {}

    # 确保结构完整
    if "version" not in state:
        state["version"] = "1.0.0"
    if "created_at" not in state:
        state["created_at"] = datetime.now().isoformat()
    if "project_scans" not in state:
        state["project_scans"] = []
    if "chat_extracts" not in state:
        state["chat_extracts"] = []

    state["updated_at"] = datetime.now().isoformat()

    # 添加条目
    if entry_type == "project_scan":
        # 避免重复（同项目名覆盖）
        state["project_scans"] = [
            e for e in state["project_scans"]
            if e.get("project_name") != entry_data.get("project_name")
        ]
        state["project_scans"].append({
            "project_name": entry_data.get("project_name", "unknown"),
            "scan_file": str(entry_data.get("scan_file", "")),
            "tech_stacks": entry_data.get("tech_stacks", []),
            "scanned_at": entry_data.get("scanned_at", datetime.now().isoformat()),
            "summary": entry_data.get("summary", {}),
        })
    elif entry_type == "chat_extract":
        state["chat_extracts"].append({
            "source_file": entry_data.get("source_file", "unknown"),
            "extract_file": str(entry_data.get("extract_file", "")),
            "processed_at": entry_data.get("processed_at", datetime.now().isoformat()),
            "summary": entry_data.get("summary", {}),
        })

    # 写入状态文件
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    print(f"  迁移状态已更新：{state_file}")


# ──────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="AOS 迁移采集脚本 — 扫描项目、处理对话提取、服务器环境调研",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python aos_migrate_collect.py --source=project --path="D:/projects/my-app"
  python aos_migrate_collect.py --source=chat --input="D:/exports/chat_20260621.md"
  python aos_migrate_collect.py --source=scan --path="D:/projects"
  python aos_migrate_collect.py --source=server --path="/opt/my-service"
  python aos_migrate_collect.py --source=phase0 --path="/opt/my-service"
        """,
    )
    parser.add_argument(
        "--source",
        required=True,
        choices=["project", "chat", "scan", "server", "phase0"],
        help="采集来源：project=单个项目, chat=对话提取, scan=目录扫描, "
             "server=Phase0环境调研+采集, phase0=仅Phase0环境调研",
    )
    parser.add_argument(
        "--path",
        help="项目路径或扫描目录路径（source=project/scan/server/phase0 时必填）",
    )
    parser.add_argument(
        "--input",
        help="对话提取文件路径（source=chat 时必填）",
    )
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()

    # 检测 AOS 根目录
    aos_root = find_aos_root()
    print(f"AOS 根目录：{aos_root}")

    # 确保输出目录
    scan_dir, chat_dir, state_file = ensure_output_dirs(aos_root)

    if args.source == "project":
        if not args.path:
            print("[错误] --source=project 需要指定 --path 参数")
            sys.exit(1)

        project_path = Path(args.path)
        result = scan_project(project_path)

        # 保存结果
        scan_file = save_project_scan(result, scan_dir)
        update_migration_state(state_file, "project_scan", {
            "project_name": result["project_name"],
            "scan_file": str(scan_file),
            "tech_stacks": result["tech_stacks"],
            "scanned_at": result["scanned_at"],
            "summary": result["summary"],
        })

    elif args.source == "chat":
        if not args.input:
            print("[错误] --source=chat 需要指定 --input 参数")
            sys.exit(1)

        input_path = Path(args.input)
        result = process_chat_extract(input_path)

        # 保存结果
        extract_file = save_chat_extract(result, chat_dir, input_path)
        update_migration_state(state_file, "chat_extract", {
            "source_file": result["source_file"],
            "extract_file": str(extract_file),
            "processed_at": result["processed_at"],
            "summary": result["summary"],
        })

    elif args.source == "scan":
        if not args.path:
            print("[错误] --source=scan 需要指定 --path 参数")
            sys.exit(1)

        dir_path = Path(args.path)
        results = scan_directory(dir_path)

        # 保存所有结果
        for result in results:
            scan_file = save_project_scan(result, scan_dir)
            update_migration_state(state_file, "project_scan", {
                "project_name": result["project_name"],
                "scan_file": str(scan_file),
                "tech_stacks": result["tech_stacks"],
                "scanned_at": result["scanned_at"],
                "summary": result["summary"],
            })

    elif args.source == "server":
        if not args.path:
            print("[错误] --source=server 需要指定 --path 参数")
            sys.exit(1)

        project_path = Path(args.path)

        # 先执行 Phase 0
        phase0_result = run_phase0(project_path)

        # Phase 0 完成后进入采集阶段
        result = scan_project(project_path)

        # 保存采集结果
        scan_file = save_project_scan(result, scan_dir)
        update_migration_state(state_file, "project_scan", {
            "project_name": result["project_name"],
            "scan_file": str(scan_file),
            "tech_stacks": result["tech_stacks"],
            "scanned_at": result["scanned_at"],
            "summary": result["summary"],
        })

    elif args.source == "phase0":
        if not args.path:
            print("[错误] --source=phase0 需要指定 --path 参数")
            sys.exit(1)

        project_path = Path(args.path)
        run_phase0(project_path)

    print("\n" + "=" * 60)
    print("AOS 迁移采集完成")
    print(f"输出目录：{aos_root / '08_INBOX' / 'migration'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
