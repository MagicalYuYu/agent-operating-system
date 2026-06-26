#!/usr/bin/env python3
"""
AOS Data Generator — 扫描 AOS 目录生成 data.js 供可视化界面使用

用法：
  python aos_generate_data.py [AOS_ROOT] [OUTPUT_PATH]

参数：
  AOS_ROOT     — AOS 根目录（默认自动检测，含 AGENTS.md 的目录）
  OUTPUT_PATH  — 输出 data.js 路径（默认 AOS_ROOT/03_TOOLS/aos_viewer/prototype/js/data.js）

功能：
  1. 解析 00_BOOT/SYSTEM_STATE.md → 组件状态、运行时统计、事件日志
  2. 解析 00_BOOT/SKILL_REGISTRY.md → Skill 列表
  3. 扫描 01_PROJECTS/ → 项目列表（AGENTS.md + STATUS.md + README.md）
  4. 扫描 04_MEMORY/ → 记忆索引和内容
  5. 扫描 09_REFERENCE/ → 知识库索引和内容
  6. 生成 data.js 文件
"""

import os
import sys
import re
import json
from pathlib import Path
from datetime import datetime


# ═══════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════

def find_aos_root():
    """自动检测 AOS 根目录"""
    # 1. 命令行参数
    if len(sys.argv) > 1:
        root = Path(sys.argv[1])
        if (root / "AGENTS.md").exists():
            return root
    # 2. 当前工作目录
    cwd = Path.cwd()
    if (cwd / "AGENTS.md").exists():
        return cwd
    # 3. 脚本所在目录向上查找
    script_dir = Path(__file__).resolve().parent
    for parent in [script_dir] + list(script_dir.parents):
        if (parent / "AGENTS.md").exists():
            return parent
    # 4. 常见路径
    for p in [Path("D:/AOS"), Path("C:/AOS"), Path("d:/AOS"), Path("c:/AOS")]:
        if p.exists() and (p / "AGENTS.md").exists():
            return p
    print("错误：无法找到 AOS 根目录（需包含 AGENTS.md）")
    sys.exit(1)


def read_file(path, encoding='utf-8'):
    """安全读取文件内容"""
    try:
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception:
        return ''


def parse_md_table(content, header_row_idx=0):
    """解析 Markdown 表格，返回字典列表"""
    lines = content.strip().split('\n')
    if len(lines) < header_row_idx + 2:
        return []

    # 解析表头
    header_line = lines[header_row_idx]
    headers = [h.strip() for h in header_line.strip('|').split('|')]

    # 跳过分隔行，解析数据行
    rows = []
    for line in lines[header_row_idx + 2:]:
        line = line.strip()
        if not line or not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        row = {}
        for i, h in enumerate(headers):
            row[h] = cells[i] if i < len(cells) else ''
        rows.append(row)
    return rows


def parse_md_tables_from_section(content, section_title):
    """从 Markdown 内容中找到指定 section，解析其中所有表格"""
    # 找到 section 起始位置
    lines = content.split('\n')
    section_start = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('## ') and section_title in line:
            section_start = i
            break
    if section_start < 0:
        return []

    # 找到下一个 section 或文件末尾
    section_end = len(lines)
    for i in range(section_start + 1, len(lines)):
        if lines[i].strip().startswith('## '):
            section_end = i
            break

    # 在 section 范围内找表格起始行（以 | 开头的行）
    table_start = -1
    for i in range(section_start + 1, section_end):
        stripped = lines[i].strip()
        if stripped.startswith('|'):
            table_start = i
            break

    if table_start < 0:
        return []

    # 从表格起始行开始解析
    table_content = '\n'.join(lines[table_start:section_end])
    return parse_md_table(table_content, 0)


def escape_js_string(s):
    """转义 JavaScript 字符串中的特殊字符"""
    s = s.replace('\\', '\\\\')
    s = s.replace('`', '\\`')
    s = s.replace('${', '\\${')
    # 不转义单双引号，因为用反引号模板字符串
    return s


# ═══════════════════════════════════════════════════════
# 解析器：SYSTEM_STATE.md
# ═══════════════════════════════════════════════════════

def parse_system_state(aos_root):
    """解析 00_BOOT/SYSTEM_STATE.md"""
    path = aos_root / "00_BOOT" / "SYSTEM_STATE.md"
    content = read_file(path)
    if not content:
        return {}, [], [], []

    # 系统信息
    sys_info = {}
    for row in parse_md_tables_from_section(content, '系统信息'):
        field = row.get('字段', '')
        value = row.get('值', '')
        if '版本' in field:
            sys_info['version'] = value
        elif '内核状态' in field:
            sys_info['kernel_status'] = value
        elif '初始化时间' in field:
            sys_info['init_time'] = value
        elif '最后更新' in field:
            sys_info['last_update'] = value

    # 组件状态
    components = []
    for row in parse_md_tables_from_section(content, '组件状态'):
        name = row.get('组件', '')
        status = row.get('状态', '').lower()
        desc = row.get('说明', '')
        if name:
            components.append({
                'name': name,
                'status': status if status in ('active', 'ready', 'error') else 'ready',
                'desc': desc
            })

    # 运行时统计
    stats = []
    for row in parse_md_tables_from_section(content, '运行时统计'):
        label = row.get('指标', '')
        value_str = row.get('值', '0')
        if label:
            try:
                value = int(re.sub(r'[^\d]', '', value_str))
            except ValueError:
                value = 0
            stats.append({'label': label, 'value': value})

    # 事件日志
    events = []
    for row in parse_md_tables_from_section(content, '事件日志'):
        time = row.get('时间', '')
        etype = row.get('事件类型', '')
        desc = row.get('描述', '')
        if time:
            events.append({
                'time': time,
                'type': etype.lower() if etype else 'info',
                'desc': desc
            })

    return sys_info, components, stats, events


# ═══════════════════════════════════════════════════════
# 解析器：SKILL_REGISTRY.md
# ═══════════════════════════════════════════════════════

def parse_skill_registry(aos_root):
    """解析 00_BOOT/SKILL_REGISTRY.md"""
    path = aos_root / "00_BOOT" / "SKILL_REGISTRY.md"
    content = read_file(path)
    if not content:
        return []

    skills = []
    # Skill 注册表
    for row in parse_md_tables_from_section(content, '注册表'):
        sid = row.get('Skill ID', '')
        name = row.get('名称', '')
        trigger = row.get('触发条件', '')
        version = row.get('版本', '')
        status = row.get('状态', '')
        spath = row.get('路径', '')
        if sid:
            # 尝试读取 SKILL.md 获取更多信息
            skill_md_path = aos_root / spath / "SKILL.md"
            skill_md = read_file(skill_md_path)

            # 读取 gotchas.md
            gotchas_path = aos_root / spath / "gotchas.md"
            gotchas = read_file(gotchas_path)

            skills.append({
                'id': sid,
                'name': name,
                'version': version,
                'status': status,
                'trigger': trigger,
                'path': spath,
                'structure': [],
                'callCount': 0,
                'lastExec': '',
                'evolution': [],
                'skillMd': skill_md,
                'gotchas': gotchas,
            })

    # 演化记录
    evo_rows = parse_md_tables_from_section(content, '演化记录')
    if not evo_rows:
        evo_rows = parse_md_tables_from_section(content, 'Skill 演化记录')
    for erow in evo_rows:
        sid = erow.get('Skill ID', '')
        for s in skills:
            if s['id'] == sid:
                s['evolution'].append({
                    'time': erow.get('时间', ''),
                    'type': erow.get('变更类型', ''),
                    'desc': erow.get('描述', '')
                })

    # 扫描 Skill 目录结构
    skills_dir = aos_root / "03_TOOLS" / "skills"
    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            existing = [s for s in skills if skill_dir.name in s['path']]
            if existing:
                existing[0]['structure'] = [f.name for f in skill_dir.iterdir() if not f.name.startswith('.')]

    return skills


# ═══════════════════════════════════════════════════════
# 解析器：01_PROJECTS/
# ═══════════════════════════════════════════════════════

def parse_projects(aos_root):
    """扫描 01_PROJECTS/ 下所有项目"""
    projects_dir = aos_root / "01_PROJECTS"
    if not projects_dir.exists():
        return []

    projects = []
    for proj_dir in sorted(projects_dir.iterdir()):
        if not proj_dir.is_dir():
            continue
        if proj_dir.name.startswith('.') or proj_dir.name == '__pycache__':
            continue

        project = parse_single_project(proj_dir, aos_root)
        if project:
            projects.append(project)

    return projects


def parse_single_project(proj_dir, aos_root):
    """解析单个项目目录"""
    name = proj_dir.name

    # 读取 AGENTS.md
    agents_content = read_file(proj_dir / "AGENTS.md")

    # 读取 README.md
    readme_content = read_file(proj_dir / "README.md")

    # 读取 STATUS.md
    status_content = read_file(proj_dir / "STATUS.md")

    # 从 AGENTS.md 提取项目信息
    project_info = extract_project_info(agents_content, name)

    # 从 STATUS.md 提取状态
    status = extract_project_status(status_content)

    # 从 README.md 提取描述
    desc = extract_project_desc(readme_content)

    # 检测项目类型（项目集 vs 单一项目）
    # 优先使用 AGENTS.md 中声明的项目类型，仅在未声明时按目录结构推断
    src_dir = proj_dir / "src"
    declared_type = project_info.get('type', '')
    # 检查 AGENTS.md 中是否有"子项目清单" section（项目集的明确标志）
    has_subproject_list = bool(agents_content) and ('子项目清单' in agents_content or '## 子项目' in agents_content)
    if has_subproject_list or '项目集' in declared_type or '插件集' in declared_type or '微服务' in declared_type:
        project_type = "项目集"
    elif declared_type and '项目集' not in declared_type:
        # 有明确类型声明但不是"项目集"，检查 src/ 下是否有插件式子项目
        # 如 game_server 类型但 src/ 下有多个 *_plugin_* 目录 → 实际是项目集
        project_type = "单一项目"
        if src_dir.exists():
            sub_dirs = [d for d in src_dir.iterdir() if d.is_dir() and not d.name.startswith('.') and not d.name.startswith('__')]
            plugin_dirs = [d for d in sub_dirs if '_plugin_' in d.name.lower() or '_module_' in d.name.lower()]
            if len(plugin_dirs) >= 2:
                project_type = "项目集"
    else:
        # 未在 AGENTS.md 中声明类型，按目录结构推断
        project_type = "单一项目"
        if src_dir.exists():
            # 检查 src 下是否有子目录（项目集模式）
            sub_dirs = [d for d in src_dir.iterdir() if d.is_dir() and not d.name.startswith('.') and not d.name.startswith('__')]
            if len(sub_dirs) >= 2:
                # 可能是项目集，但需排除常见代码模块目录
                code_module_names = {'extension', 'extensions', 'native-host', 'native_host', 'config',
                                     'utils', 'helpers', 'lib', 'core', 'scripts', 'assets', 'static',
                                     'templates', 'tests', 'test', 'docs', 'styles', 'public', 'dist', 'build',
                                     'electron', 'dist-electron', 'node_modules', '.git', '.github', '.githooks'}
                real_subprojects = [d for d in sub_dirs if d.name.lower() not in code_module_names]
                if len(real_subprojects) >= 2:
                    project_type = "项目集"

    plugins = []
    modules = []
    if project_type == "项目集" and src_dir.exists():
        sub_dirs = [d for d in src_dir.iterdir() if d.is_dir() and not d.name.startswith('.') and not d.name.startswith('__')]
        for sd in sub_dirs:
            plugin_info = extract_plugin_info(sd, name)
            if plugin_info:
                plugins.append(plugin_info)

    # 检查是否有 modules（如 clash_omega 的 modules 字段）
    if agents_content and 'modules:' in agents_content.lower():
        # 尝试从 AGENTS.md 提取 modules
        modules = extract_modules_from_agents(agents_content)

    # 检查文件完整性
    has_agents = (proj_dir / "AGENTS.md").exists()
    has_readme = (proj_dir / "README.md").exists()
    has_status = (proj_dir / "STATUS.md").exists()

    # 目录结构
    structure = []
    for item in sorted(proj_dir.iterdir()):
        if item.name.startswith('.') or item.name == '__pycache__':
            continue
        structure.append(item.name + ('/' if item.is_dir() else ''))

    # 技术栈（从 AGENTS.md 提取）
    tech_stack = extract_tech_stack(agents_content)

    return {
        'name': name,
        'title': project_info.get('title', name),
        'type': project_info.get('type', ''),
        'status': status,
        'createdAt': project_info.get('created_at', ''),
        'path': f"01_PROJECTS/{name}/",
        'desc': desc,
        'techStack': tech_stack,
        'hasAgents': has_agents,
        'hasReadme': has_readme,
        'hasStatus': has_status,
        'structure': structure,
        'projectType': project_type,
        'plugins': plugins,
        'modules': modules,
        'agentsContent': agents_content,
        'readmeContent': readme_content,
        'statusContent': status_content,
    }


def extract_project_info(agents_content, name):
    """从 AGENTS.md 提取项目基本信息"""
    info = {}
    if not agents_content:
        return info

    # 优先从"项目基本信息" section 提取表格
    tables = parse_md_tables_from_section(agents_content, '项目基本信息')
    if not tables:
        # fallback: 尝试从全文第一个表格提取
        tables = parse_md_table(agents_content, 0)

    for row in tables:
        field = row.get('字段', row.get('项目', ''))
        value = row.get('值', '')
        if '项目名称' in field or '名称' in field:
            info['title'] = value
        elif '项目类型' in field:
            info['type'] = value
        elif '创建时间' in field:
            info['created_at'] = value
        elif '技术栈' in field:
            info['tech_stack'] = value

    # 从标题提取项目名称
    title_match = re.search(r'^#\s+(.+?)(?:\s*—|\s*$)', agents_content, re.MULTILINE)
    if title_match and 'title' not in info:
        info['title'] = title_match.group(1).strip()

    return info


def extract_project_status(status_content):
    """从 STATUS.md 提取项目状态。

    解析优先级：
    1. 元信息表中的"状态"字段（如 "| 状态 | ACTIVE |"）
    2. 元信息表中的"当前阶段"字段（如"发布准备"→ACTIVE，"核心开发"→PENDING）
    3. 阶段状态统计（全部 ✅ completed → ACTIVE，有 pending → PENDING）
    4. 默认 UNKNOWN
    """
    if not status_content:
        return 'UNKNOWN'

    # 优先级1：匹配元信息表中的"状态"字段
    status_match = re.search(r'\|\s*状态\s*\|\s*(\w+)\s*\|', status_content, re.IGNORECASE)
    if status_match:
        status_val = status_match.group(1).upper()
        if status_val in ('ACTIVE', 'PENDING', 'READY', 'PAUSED', 'ARCHIVED', 'ERROR'):
            return status_val

    # 优先级2：匹配元信息表中的"当前阶段"字段
    phase_match = re.search(r'\|\s*当前阶段\s*\|\s*([^|]+)\s*\|', status_content)
    if phase_match:
        phase = phase_match.group(1).strip()
        # 发布准备/已完成/交付 → ACTIVE
        if any(kw in phase for kw in ['发布', '完成', '交付', 'ACTIVE']):
            return 'ACTIVE'
        # 核心开发/开发中/进行中 → PENDING
        if any(kw in phase for kw in ['开发', '进行', 'pending', 'PENDING']):
            return 'PENDING'

    # 优先级3：统计阶段状态（仅匹配表格行中的阶段状态，排除状态图例）
    # 支持多种格式：
    #   - 有 emoji：| ✅ completed |、| ⏳ pending |、| 🔄 in_progress |
    #   - 有 emoji + 中文：| ✅ 完成 |、| ⏳ 待办 |、| 🔄 进行中 |
    #   - 无 emoji：| completed |、| pending |、| in_progress |
    #   - 无 emoji + 中文：| 完成 |、| 待办 |、| 进行中 |
    completed_count = len(re.findall(r'\|\s*(?:✅\s*)?(?:completed|完成)\s*\|', status_content, re.IGNORECASE))
    pending_count = len(re.findall(r'\|\s*(?:⏳\s*)?(?:pending|待办|待处理)\s*\|', status_content, re.IGNORECASE))
    in_progress_count = len(re.findall(r'\|\s*(?:🔄\s*)?(?:in_progress|进行中)\s*\|', status_content, re.IGNORECASE))

    # 项目已启动且在运行（有已完成阶段）→ ACTIVE（活跃中，可能正在迭代）
    # 全部待办（无已完成、无进行中）→ PENDING
    if completed_count > 0 or in_progress_count > 0:
        return 'ACTIVE'  # 项目已启动，有进展，视为活跃中
    if pending_count > 0:
        return 'PENDING'  # 全部待办 → PENDING

    # 优先级4：回退到全文搜索（仅匹配非图例行）
    # 排除"状态图例"section 中的内容
    lines = status_content.split('\n')
    non_legend_lines = []
    in_legend = False
    for line in lines:
        if '状态图例' in line:
            in_legend = True
            continue
        if in_legend and line.strip().startswith('#'):
            in_legend = False
        if not in_legend:
            non_legend_lines.append(line)

    non_legend_content = '\n'.join(non_legend_lines)
    fallback_patterns = [
        r'状态[：:]\s*(ACTIVE|PENDING|PHASE_\d+|READY|PAUSED|ARCHIVED|ERROR)',
        r'\b(ACTIVE|READY|PAUSED|ARCHIVED|ERROR)\b',
    ]
    for pattern in fallback_patterns:
        match = re.search(pattern, non_legend_content, re.IGNORECASE)
        if match:
            return match.group(1).upper()

    return 'UNKNOWN'


def extract_project_desc(readme_content):
    """从 README.md 提取项目描述。

    提取规则：
    1. 跳过标题行（# 开头）
    2. 跳过引用块（> 开头）
    3. 跳过分割线（---）
    4. 跳过徽章行（[![ 开头）和图片行（![ 开头）
    5. 跳过目录行（- [ 开头）
    6. 跳过表格行（| 开头）
    7. 跳过代码块（``` 开头）及其内部内容
    8. 取第一个完整段落（到空行为止）
    9. 截断到 300 字符
    """
    if not readme_content:
        return ''

    lines = readme_content.split('\n')
    desc_lines = []
    in_paragraph = False
    in_code_block = False
    for line in lines:
        stripped = line.strip()
        # 代码块状态跟踪
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue  # 跳过代码块内的内容
        # 跳过空行（段落分隔符）
        if not stripped:
            if in_paragraph and desc_lines:
                break  # 段落结束
            continue
        # 跳过标题
        if stripped.startswith('#'):
            continue
        # 跳过引用块
        if stripped.startswith('>'):
            continue
        # 跳过分割线
        if stripped.startswith('---'):
            continue
        # 跳过徽章和图片
        if stripped.startswith('[![') or stripped.startswith('!['):
            continue
        # 跳过目录项
        if stripped.startswith('- ['):
            continue
        # 跳过表格行
        if stripped.startswith('|'):
            continue

        in_paragraph = True
        desc_lines.append(stripped)

    desc = ' '.join(desc_lines)
    # 清理 markdown 语法
    desc = re.sub(r'`([^`]+)`', r'\1', desc)  # 行内代码
    desc = re.sub(r'\*\*([^*]+)\*\*', r'\1', desc)  # 粗体
    desc = desc[:300]

    return desc if desc else ''


def extract_plugin_info(plugin_dir, project_name):
    """从插件目录提取信息（增强版：支持 metadata.yaml / manifest.json / README.md 多源提取）"""
    name = plugin_dir.name
    # 尝试读取 metadata.yaml（AstrBot 插件标准）
    metadata_path = plugin_dir / "metadata.yaml"
    metadata = read_file(metadata_path)

    # 尝试读取 README.md
    readme = read_file(plugin_dir / "README.md")

    # 尝试读取 manifest.json（Chrome 扩展标准）
    manifest_path = plugin_dir / "manifest.json"
    manifest = read_file(manifest_path)

    # 从 metadata.yaml 提取基本信息
    info = {
        'name': name,
        'status': 'active',
        'version': '',
        'author': '',
        'desc': '',
        'display_name': '',
        'metadata': metadata or '',
        'readme': readme or '',
        'manifest': manifest or '',
        'structure': [],
    }

    # 优先从 metadata.yaml 提取
    if metadata:
        for line in metadata.split('\n'):
            line = line.strip()
            # 清理 YAML 行内注释（# 后面的内容，但需避免误清理 URL 中的 #）
            # 简单规则：只清理冒号后值部分的 # 注释
            def clean_yaml_value(val):
                val = val.strip().strip('"').strip("'")
                # 清理行内注释（# 前有空格的视为注释）
                if ' #' in val:
                    val = val.split(' #')[0].strip()
                return val

            if line.startswith('desc:'):
                info['desc'] = clean_yaml_value(line.split(':', 1)[1])
            elif line.startswith('version:'):
                info['version'] = clean_yaml_value(line.split(':', 1)[1])
            elif line.startswith('author:'):
                info['author'] = clean_yaml_value(line.split(':', 1)[1])
            elif line.startswith('display_name:'):
                info['display_name'] = clean_yaml_value(line.split(':', 1)[1])
            elif line.startswith('name:'):
                # metadata.yaml 中的 name 字段可能含注释，需清理
                raw_name = clean_yaml_value(line.split(':', 1)[1])
                if raw_name and not info.get('display_name'):
                    info['display_name'] = raw_name

    # fallback: 从 manifest.json 提取（Chrome 扩展）
    if manifest and not info['version']:
        try:
            manifest_data = json.loads(manifest)
            info['version'] = manifest_data.get('version', '')
            info['display_name'] = info['display_name'] or manifest_data.get('name', '')
            info['desc'] = info['desc'] or manifest_data.get('description', '')
            # author 可能存在于 author 字段
            if not info['author'] and 'author' in manifest_data:
                author_data = manifest_data['author']
                if isinstance(author_data, dict):
                    info['author'] = author_data.get('email', '') or author_data.get('name', '')
                else:
                    info['author'] = str(author_data)
        except (json.JSONDecodeError, TypeError):
            pass

    # fallback: 从 README.md 提取描述（第一段非标题文本）
    if not info['desc'] and readme:
        info['desc'] = extract_project_desc(readme)

    # fallback: 从 README.md 提取 display_name（第一个 # 标题）
    if not info['display_name'] and readme:
        for line in readme.split('\n'):
            line = line.strip()
            if line.startswith('# '):
                info['display_name'] = line[2:].strip()
                break

    # 收集目录结构（最多 20 项，避免过大）
    try:
        items = sorted(plugin_dir.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        for item in items:
            if item.name.startswith('.') or item.name == '__pycache__':
                continue
            info['structure'].append(item.name + ('/' if item.is_dir() else ''))
            if len(info['structure']) >= 20:
                break
    except (PermissionError, OSError):
        pass

    return info


def extract_modules_from_agents(agents_content):
    """从 AGENTS.md 提取模块信息（如 clash_omega 的 modules）"""
    modules = []
    # 简单提取：查找模块相关表格
    for row in parse_md_table(agents_content, 0):
        module_name = row.get('模块', row.get('名称', ''))
        if module_name:
            modules.append({
                'name': module_name,
                'desc': row.get('说明', row.get('描述', '')),
                'files': []
            })
    return modules


def extract_tech_stack(agents_content):
    """从 AGENTS.md 提取技术栈"""
    if not agents_content:
        return []

    # 查找技术栈行
    for row in parse_md_table(agents_content, 0):
        field = row.get('字段', '')
        value = row.get('值', '')
        if '技术栈' in field:
            return [t.strip() for t in value.split(',') if t.strip()]

    return []


# ═══════════════════════════════════════════════════════
# 解析器：04_MEMORY/
# ═══════════════════════════════════════════════════════

def parse_memory(aos_root):
    """扫描 04_MEMORY/ 下的记忆数据"""
    memory_dir = aos_root / "04_MEMORY"
    if not memory_dir.exists():
        return {}

    # 解析 INDEX.md
    index_path = memory_dir / "INDEX.md"
    index_content = read_file(index_path)

    memories = {
        'user': [],
        'feedback': [],
        'reference': [],
        'project': []
    }

    if not index_content:
        return memories

    # 按分类解析索引
    current_cat = None
    for line in index_content.split('\n'):
        line = line.strip()
        if line.startswith('## '):
            cat_name = line[3:].strip().lower()
            if cat_name in memories:
                current_cat = cat_name
            continue

        if not current_cat:
            continue

        # 解析索引行：- [title](path) — hook
        match = re.match(r'-\s+\[([^\]]+)\]\(([^)]+)\)\s*—?\s*(.*)', line)
        if match:
            title = match.group(1)
            path = match.group(2)
            hook = match.group(3).strip()

            # 读取完整内容
            full_path = memory_dir / path
            content = read_file(full_path)

            # 判断类型
            mem_type = '记录型'
            if current_cat in ('user', 'project'):
                mem_type = '状态型'

            memories[current_cat].append({
                'title': title,
                'path': path,
                'hook': hook,
                'type': mem_type,
                'content': content
            })

    return memories


# ═══════════════════════════════════════════════════════
# 解析器：09_REFERENCE/
# ═══════════════════════════════════════════════════════

def parse_references(aos_root):
    """扫描 09_REFERENCE/ 下的知识库数据"""
    ref_dir = aos_root / "09_REFERENCE"
    if not ref_dir.exists():
        return []

    # 解析 _index.md
    index_path = ref_dir / "_index.md"
    index_content = read_file(index_path)

    references = []

    if not index_content:
        return references

    # 解析索引表
    for row in parse_md_tables_from_section(index_content, '索引表'):
        slug = row.get('Slug', '')
        title = row.get('标题', '')
        tags_str = row.get('标签', '')
        source = row.get('来源', '')
        confidence = row.get('可信度', '1.0')
        ref_path = row.get('路径', '')

        if not slug:
            continue

        tags = [t.strip() for t in tags_str.split(',') if t.strip()]

        # 判断分类
        category = 'web'
        if 'system/' in ref_path or source == 'AOS内部设计':
            category = 'system'

        # 读取完整内容：直接用 slug.md 在对应子目录查找
        content = ''
        for subdir in ['system', 'web']:
            candidate = ref_dir / subdir / f"{slug}.md"
            if candidate.exists():
                content = read_file(candidate)
                break

        # 也读取 metadata.json
        metadata_json = ''
        for subdir in ['system', 'web']:
            candidate = ref_dir / subdir / f"{slug}.metadata.json"
            if candidate.exists():
                metadata_json = read_file(candidate)
                break

        try:
            conf_float = float(confidence)
        except ValueError:
            conf_float = 1.0

        references.append({
            'slug': slug,
            'title': title,
            'tags': tags,
            'source': source,
            'confidence': conf_float,
            'category': category,
            'content': content,
            'metadata': metadata_json,
        })

    return references


# ═══════════════════════════════════════════════════════
# 生成 data.js
# ═══════════════════════════════════════════════════════

def _strip_large_fields(data):
    """从 AOS_DATA 中剥离大文本字段，返回 (精简数据, 大字段数据)

    精简数据保留所有结构，大文本字段值设为空字符串
    大字段数据保持相同结构，仅含大文本字段
    """
    import copy
    slim = copy.deepcopy(data)
    content = {
        'memories': {},
        'references': [],
        'skills': [],
        'projects': [],
    }

    # memories: 每条含 content
    for cat, items in (slim.get('memories') or {}).items():
        content['memories'][cat] = []
        for item in items:
            content['memories'][cat].append({
                'title': item.get('title', ''),
                'content': item.get('content', '')
            })
            item['content'] = ''

    # references: 每条含 content + metadata
    for i, ref in enumerate(slim.get('references') or []):
        content['references'].append({
            'slug': ref.get('slug', ''),
            'content': ref.get('content', ''),
            'metadata': ref.get('metadata', '')
        })
        ref['content'] = ''
        ref['metadata'] = ''

    # skills: 每条含 skillMd + gotchas
    for s in slim.get('skills') or []:
        content['skills'].append({
            'id': s.get('id', ''),
            'skillMd': s.get('skillMd', ''),
            'gotchas': s.get('gotchas', '')
        })
        s['skillMd'] = ''
        s['gotchas'] = ''

    # projects: 每条含 agentsContent + readmeContent + statusContent
    for p in slim.get('projects') or []:
        content['projects'].append({
            'name': p.get('name', ''),
            'agentsContent': p.get('agentsContent', ''),
            'readmeContent': p.get('readmeContent', ''),
            'statusContent': p.get('statusContent', '')
        })
        p['agentsContent'] = ''
        p['readmeContent'] = ''
        p['statusContent'] = ''

    return slim, content


def _strip_subproject_large_fields(subproject_data):
    """从 SUBPROJECT_DATA 中剥离大文本字段，返回 (精简数据, 大字段数据)"""
    import copy
    slim = copy.deepcopy(subproject_data)
    content = {}
    for name, entry in slim.items():
        content[name] = {
            'metadata': entry.get('metadata', ''),
            'readme': entry.get('readme', '')
        }
        entry['metadata'] = ''
        entry['readme'] = ''
    return slim, content


def generate_data_js(aos_root, output_path):
    """生成 data.js 文件（仅元数据）+ data_content.js（大文本字段）"""
    print(f"扫描 AOS 目录: {aos_root}")

    # 1. 解析系统状态
    print("  解析 SYSTEM_STATE.md...")
    sys_info, components, stats, events = parse_system_state(aos_root)

    # 2. 解析 Skill 注册表
    print("  解析 SKILL_REGISTRY.md...")
    skills = parse_skill_registry(aos_root)

    # 3. 解析项目
    print("  扫描 01_PROJECTS/...")
    projects = parse_projects(aos_root)

    # 4. 解析记忆
    print("  扫描 04_MEMORY/...")
    memories = parse_memory(aos_root)

    # 5. 解析知识库
    print("  扫描 09_REFERENCE/...")
    references = parse_references(aos_root)

    # 6. 构建完整数据对象
    full_data = {
        'version': sys_info.get('version', '1.1.0'),
        'kernelStatus': sys_info.get('kernel_status', 'ACTIVE'),
        'initTime': sys_info.get('init_time', ''),
        'lastUpdate': sys_info.get('last_update', ''),
        'components': components,
        'stats': stats,
        'events': events,
        'skills': skills,
        'projects': projects,
        'memories': memories,
        'references': references,
        # Loop 和 Agent 模块暂无实际数据源，保留前端兼容的默认结构
        'loops': {
            'types': [
                {'name': '自检循环', 'desc': '系统启动时自动执行完整性检查', 'active': 0},
                {'name': '同步循环', 'desc': '定时同步工作目录与 GitHub 仓库', 'active': 0},
                {'name': '迁移循环', 'desc': '批量处理历史内容迁移', 'active': 0},
            ]
        },
        'agents': {
            'modes': [
                {'name': 'PLAN', 'desc': '只读探索+生成计划', 'trigger': '/spec 或 /plan'},
                {'name': 'EXECUTE', 'desc': '读写操作+工具调用', 'trigger': '默认模式'},
                {'name': 'VERIFY', 'desc': '只读验证+输出报告', 'trigger': '新会话中发起'},
            ],
            'protocols': ['Maker/Checker 分离', '状态更新是步骤的一部分', '事前声明优于事后记录', '文件是唯一的跨会话通道']
        },
        'logs': {
            'systemEvents': events if events else [],
        },
    }

    # 7. 生成 SUBPROJECT_DATA（完整版，含大文本）
    full_subproject = json.loads(generate_subproject_data(projects))

    # 8. 拆分：精简数据 + 大字段数据
    slim_data, content_data = _strip_large_fields(full_data)
    slim_subproject, content_subproject = _strip_subproject_large_fields(full_subproject)

    # 9. 生成 data.js（精简元数据）
    print(f"  生成 {output_path}...")
    slim_json = json.dumps(slim_data, ensure_ascii=False, indent=2)
    slim_sub_json = json.dumps(slim_subproject, ensure_ascii=False, indent=2)

    data_js_content = f"""// ═══════════════════════════════════════════════════════
// AOS Viewer Data — 自动生成（元数据，不含大文本字段）
// 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// 生成脚本: 03_TOOLS/scripts/aos_generate_data.py
// ⚠ 此文件由脚本自动生成，请勿手动修改
// ⚠ 大文本字段（content/skillMd/gotchas/agentsContent 等）存放在 data_content.js
// ═══════════════════════════════════════════════════════

const AOS_DATA = {slim_json};

// ═══════════════════════════════════════════════════════
// 子项目元数据（不含 metadata/readme 大文本字段）
// ═══════════════════════════════════════════════════════
const SUBPROJECT_DATA = {slim_sub_json};
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(data_js_content)

    # 10. 生成 data_content.js（大文本字段）
    content_path = output_path.parent / "data_content.js"
    print(f"  生成 {content_path}...")

    content_combined = {
        'memories': content_data['memories'],
        'references': content_data['references'],
        'skills': content_data['skills'],
        'projects': content_data['projects'],
        'subprojects': content_subproject,
    }
    content_json = json.dumps(content_combined, ensure_ascii=False, indent=2)

    content_js_content = f"""// ═══════════════════════════════════════════════════════
// AOS Viewer Data Content — 自动生成（大文本字段）
// 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// 生成脚本: 03_TOOLS/scripts/aos_generate_data.py
// ⚠ 此文件由脚本自动生成，请勿手动修改
// ⚠ 此文件包含 memories/references/skills/projects/subprojects 的大文本字段
// ⚠ app.js 初始化时会将此数据合并回 AOS_DATA 和 SUBPROJECT_DATA
// ═══════════════════════════════════════════════════════

const AOS_DATA_CONTENT = {content_json};
"""

    with open(content_path, 'w', encoding='utf-8') as f:
        f.write(content_js_content)

    # 统计
    print(f"\n生成完成！")
    print(f"  组件: {len(components)} 个")
    print(f"  Skill: {len(skills)} 个")
    print(f"  项目: {len(projects)} 个")
    print(f"  记忆: {sum(len(v) for v in memories.values())} 条")
    print(f"  知识库: {len(references)} 条")
    print(f"  事件: {len(events)} 条")
    print(f"\n输出文件:")
    print(f"  元数据: {output_path} ({output_path.stat().st_size / 1024:.1f} KB)")
    print(f"  大文本: {content_path} ({content_path.stat().st_size / 1024:.1f} KB)")


def generate_subproject_data(projects):
    """生成 SUBPROJECT_DATA 对象（使用 JSON 序列化，更健壮）"""
    sub_data = {}
    for p in projects:
        plugins = p.get('plugins', [])
        if not plugins:
            continue
        for plugin in plugins:
            name = plugin.get('name', '')
            if not name:
                continue
            entry = {}
            if plugin.get('metadata'):
                entry['metadata'] = plugin['metadata']
            if plugin.get('readme'):
                entry['readme'] = plugin['readme']
            sub_data[name] = entry

    return json.dumps(sub_data, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════

if __name__ == '__main__':
    aos_root = find_aos_root()

    # 确定输出路径
    if len(sys.argv) > 2:
        output_path = Path(sys.argv[2])
    else:
        output_path = aos_root / "03_TOOLS" / "aos_viewer" / "prototype" / "js" / "data.js"

    generate_data_js(aos_root, output_path)
