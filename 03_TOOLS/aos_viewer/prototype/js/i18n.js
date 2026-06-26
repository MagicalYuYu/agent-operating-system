/* ═══════════════════════════════════════════════════════
   AOS Viewer i18n — 国际化系统
   支持语言：zh-CN（默认） / en-US
   用法：
     - HTML 静态文本：添加 data-i18n="key" 属性
     - HTML placeholder：添加 data-i18n-placeholder="key"
     - HTML title/tooltip：添加 data-i18n-title="key"
     - JS 动态文本：t('key') 或 t('key', arg1, arg2)
   ═══════════════════════════════════════════════════════ */

const I18N = {
  'zh-CN': {
    // ─── 启动画面 ───
    'boot.loading': '正在加载系统组件...',

    // ─── 菜单栏 ───
    'menu.file': '文件',
    'menu.view': '视图',
    'menu.tools': '工具',
    'menu.help': '帮助',

    // ─── 文件菜单 ───
    'menu.file.refresh': '刷新数据',
    'menu.file.export': '导出 JSON',
    'menu.file.close': '关闭面板',

    // ─── 视图菜单 ───
    'menu.view.switchModule': '切换模块',
    'menu.view.theme': '主题',
    'menu.view.zoomIn': '放大',
    'menu.view.zoomOut': '缩小',
    'menu.view.zoomReset': '重置缩放',

    // ─── 工具菜单 ───
    'menu.tools.spotlight': 'Spotlight 搜索',
    'menu.tools.check': '一致性自检',
    'menu.tools.sync': 'GitHub 同步',
    'menu.tools.migrate': '迁移采集',
    'menu.tools.settings': '偏好设置',

    // ─── 帮助菜单 ───
    'menu.help.about': '关于 AOS',
    'menu.help.shortcuts': '快捷键说明',
    'menu.help.settings': '偏好设置',

    // ─── 窗口控制 ───
    'window.minimize': '最小化',
    'window.maximize': '最大化',
    'window.close': '关闭',

    // ─── 数据源指示器 ───
    'datasource.local': '本地',
    'datasource.api': 'API',
    'datasource.local.title': '当前数据来源：本地 data.js（静态）。启动后端服务后可切换为 API 实时数据',
    'datasource.api.title': '当前数据来源：后端 API（实时数据，带 TTL 缓存）',

    // ─── 模块名称（菜单/Dock/模块头通用） ───
    'module.dashboard': '系统总览',
    'module.skills': 'Skill 管理',
    'module.projects': '项目工作区',
    'module.memory': '记忆中心',
    'module.reference': '知识库',
    'module.loop': 'Loop 监控',
    'module.agent': 'Agent 任务池',
    'module.logs': '日志查看器',
    'module.console': '控制台',

    // ─── Dock 短标签 ───
    'dock.dashboard': '总览',
    'dock.projects': '项目',
    'dock.memory': '记忆',
    'dock.reference': '知识',
    'dock.logs': '日志',
    'dock.console': '控制台',

    // ─── 主题 ───
    'theme.dark': '深色',
    'theme.light': '浅色',
    'theme.minimal': '极简',

    // ─── 玻璃强度 ───
    'glass.weak': '弱',
    'glass.normal': '标准',
    'glass.strong': '强',

    // ─── 系统总览模块 ───
    'dashboard.version': '版本',
    'dashboard.kernelStatus': '内核状态',
    'dashboard.initTime': '初始化时间',
    'dashboard.lastUpdate': '最后更新',
    'dashboard.components': '组件状态',
    'dashboard.runtimeStats': '运行时统计',
    'dashboard.eventLog': '事件日志',

    // ─── Skill 模块 ───
    'skills.registered': '已注册 Skill',
    'skill.callCount': '调用 {0} 次',
    'skill.viewDetail': '点击查看文件结构与演化记录 ›',
    'skill.collapse': '收起详情 ‹',
    'skill.evolution': '演化记录（{0}）',

    // ─── 项目模块 ───
    'projects.list': '项目列表',
    'project.viewDetail': '点击查看详情 ›',
    'project.detail.title': '项目详情',
    'project.expand': '向左扩展',
    'project.collapse': '向右收起',
    'project.description': '项目描述',
    'project.basicInfo': '基本信息',
    'project.type': '类型',
    'project.createdAt': '创建时间',
    'project.path': '路径',
    'project.status': '状态',
    'project.projectType': '项目类型',
    'project.techStack': '技术栈',
    'project.fileIntegrity': '文件完整性',
    'project.structure': '项目结构',
    'project.subprojects': '子项目',
    'project.sourceModules': '源码模块',
    'project.subprojectCount': '子项目（{0}）',
    'project.moduleCount': '源码模块（{0}）',
    'project.subprojectStats': '子项目统计',
    'project.total': '总数',
    'project.active': '活跃',
    'project.archived': '归档',
    'project.fileCount': '{0} 个文件',
    'project.clickSubproject': '点击左侧子项目标签可查看每个插件的详情',
    'project.expandHint': '点击左侧把手 ‹ 向左扩展查看项目级文件（AGENTS.md / STATUS.md / README.md），或点击左侧子项目卡片查看详情',
    'project.expandHintSingle': '点击左侧子项目卡片查看详情',
    'project.expandHintSimple': '点击左侧把手 ‹ 向左扩展查看项目级文件（AGENTS.md / STATUS.md / README.md）',
    'project.fileUnavailable': '{0} 暂不可用',
    'project.fileUnavailableDesc': '项目目录待创建，文件内容将在项目初始化后可用',
    'project.cardHint': '点击查看详情 ›',

    // ─── 子项目详情 ───
    'subproject.detail': '插件详情',
    'subproject.name': '名称',
    'subproject.version': '版本',
    'subproject.author': '作者',
    'subproject.status': '状态',
    'subproject.path': '路径',
    'subproject.fileStructure': '文件结构',
    'subproject.fileList': '文件列表',
    'subproject.pendingModeling': '详细数据（metadata.yaml / README.md / 文件结构）待建模',

    // ─── 模块详情 ───
    'module.detail': '模块详情',
    'module.name': '名称',
    'module.path': '路径',

    // ─── 全屏模式标签 ───
    'tab.projectLevel': '项目级',
    'tab.overview': '概览',

    // ─── 记忆模块 ───
    'memory.user': '用户画像',
    'memory.feedback': '反馈记录',
    'memory.reference': '参考',
    'memory.project': '项目',
    'memory.empty': '暂无记忆',
    'memory.pathHint': '完整内容请查看文件：04_MEMORY/{0}',
    'memory.readFull': '点击卡片可在右侧侧边栏阅读全文 ›',
    'memory.noContent': '内容待填充，暂不支持阅读',
    'memory.toggleHint': '点击阅读全文 / 展开详情 ›',
    'memory.toggleHintNoContent': '点击展开详情 ›',
    'memory.collapse': '收起 ‹',

    // ─── 知识库模块 ───
    'ref.all': '全部',
    'ref.system': '系统',
    'ref.web': '网页',
    'ref.confidence': '可信度',
    'ref.pathHint': '文件路径：09_REFERENCE/{0}/{1}.md',
    'ref.sourceLink': '访问原始来源 ↗',
    'ref.source': '来源：{0}',
    'ref.readFull': '点击卡片可在右侧侧边栏阅读全文 ›',
    'ref.noContent': '内容待填充，暂不支持阅读',
    'ref.toggleHint': '点击阅读全文 / 展开详情 ›',
    'ref.toggleHintNoContent': '点击展开详情 ›',
    'ref.collapse': '收起 ‹',
    'ref.viewDetail': '点击查看详情 ›',

    // ─── Loop 模块 ───
    'loop.types': 'Loop 类型定义',
    'loop.active': '活跃 Loop',
    'loop.empty.title': '暂无活跃 Loop',
    'loop.empty.desc': 'Loop 引擎已就绪，等待用户触发',
    'loop.unavailable': '暂不可使用',
    'loop.unavailable.title': '功能已定义，待 v1.1 实现',
    'loop.activeMeta': '活跃: {0} · 功能已定义，待后续版本实现',

    // ─── Agent 模块 ───
    'agent.modes': '执行模式',
    'agent.protocols': '协同协议',
    'agent.active': '活跃 Agent',
    'agent.empty.title': '暂无活跃 Agent',
    'agent.empty.desc': '多会话协同协议已就绪',
    'agent.unavailable': '暂不可使用',
    'agent.unavailable.title': '功能已定义，待 v1.1 实现',
    'agent.trigger': '触发: {0}',

    // ─── 日志模块 ───
    'logs.systemEvents': '系统事件日志',
    'logs.level.all': '全部',
    'logs.search.placeholder': '搜索日志...',
    'logs.col.time': '时间',
    'logs.col.level': '级别',
    'logs.col.source': '来源',
    'logs.col.message': '消息',
    'logs.empty': '无匹配日志',
    'logs.detail.time': '时间',
    'logs.detail.level': '级别',
    'logs.detail.source': '来源',
    'logs.detail.message': '消息',

    // ─── 控制台模块 ───
    'console.check': '一致性自检',
    'console.sync': 'GitHub 同步',
    'console.migrate': '迁移采集',
    'console.classify': '迁移分类',
    'console.ingest': '迁移入库',
    'console.terminalTitle': 'AOS Console — python',
    'console.welcome': 'AOS Console v1.1.0 — 输入命令或点击上方按钮执行脚本',

    // ─── Spotlight ───
    'spotlight.placeholder': '搜索模块、Skill、项目、知识...',
    'spotlight.hint.titleOnly': '仅搜索标题和标签 · 开启 MD 正文搜索请在偏好设置',
    'spotlight.hint.mdOn': '已开启 MD 正文搜索 · 搜索范围含项目配置、记忆、知识库完整正文',

    // ─── 设置面板 ───
    'settings.title': '偏好设置',
    'settings.theme': '外观主题',
    'settings.accessibility': '无障碍',
    'settings.animations': '启用动效',
    'settings.animationsDesc': '开启所有动画和过渡效果（关闭后界面完全静态）',
    'settings.scale': '界面缩放',
    'settings.fontSize': '字体大小',
    'settings.fontSizeDesc': '调整全局字体大小（80% - 140%）',
    'settings.glass': '玻璃效果',
    'settings.blur': '模糊强度',
    'settings.blurDesc': '调整玻璃拟态的模糊程度',
    'settings.developer': '开发者',
    'settings.debug': '调试面板',
    'settings.debugDesc': '开启后底部显示调试面板，实时监控 DOM 状态与函数调用日志（类似 F12 Console）',
    'settings.search': '搜索',
    'settings.mdSearch': 'MD 正文搜索',
    'settings.mdSearchDesc': '开启后 Spotlight 将搜索记忆和知识库的完整 Markdown 正文（默认关闭，MD 过多时增加性能消耗）',
    'settings.language': '语言',
    'settings.languageDesc': '切换界面语言',

    // ─── MD 阅读器 ───
    'mdReader.title': '文档预览',
    'mdReader.resize': '拖拽调整宽度',
    'mdReader.empty.title': '内容待填充',
    'mdReader.empty.desc': '该文件的完整内容尚未录入数据层',

    // ─── 调试面板 ───
    'debug.title': '调试面板 · Debug Console',
    'debug.refresh': '刷新状态',
    'debug.export': '导出日志',
    'debug.clear': '清空',
    'debug.close': '关闭面板',
    'debug.collapse': '收起调试面板',
    'debug.expand': '展开调试面板',
    'debug.domSnapshot': 'DOM 状态快照',
    'debug.domEmpty': '点击"刷新状态"查看 DOM 状态',
    'debug.callLog': '调用日志',

    // ─── 通知 ───
    'notif.ready': 'AOS 系统已就绪',
    'notif.readyDesc': 'v{0} 内核运行中 · {1} Skill · {2} 记忆索引 · {3} 知识库',
    'notif.refreshed': '数据已刷新',
    'notif.refreshedDesc': '组件 {0} · 项目 {1} · 知识库 {2}',
    'notif.refresh': '已刷新',
    'notif.refreshDesc': '系统总览数据已重新加载',
    'notif.closed': '已关闭',
    'notif.closedDesc': '所有浮层面板已收起',
    'notif.themeChanged': '主题已切换',
    'notif.themeChangedDesc': '当前主题：{0}',
    'notif.scaleChanged': '缩放已调整',
    'notif.scaleChangedDesc': '当前缩放：{0}%',
    'notif.exportSuccess': '导出成功',
    'notif.exportSuccessDesc': 'AOS 数据已导出为 JSON 文件',
    'notif.exportFail': '导出失败',
    'notif.exportFailDesc': '{0}',
    'notif.redirecting': '正在跳转',
    'notif.redirectingDesc': '已打开 AOS 官网',
    'notif.copied': '已复制',
    'notif.copiedDesc': '事件内容已复制到剪贴板',
    'notif.copyFail': '复制失败',
    'notif.copyFailDesc': '剪贴板访问被拒绝，请手动复制',
    'notif.moduleDev': '{0} 模块',
    'notif.moduleDevDesc': '该模块正在开发中，敬请期待',

    // ─── 右键菜单 ───
    'ctx.copyEvent': '复制事件',
    'ctx.copySelection': '复制选中文字',
    'ctx.searchSelection': '搜索选中文字',
    'ctx.refresh': '刷新',
    'ctx.refreshLog': '刷新日志',
    'ctx.spotlight': 'Spotlight 搜索',
    'ctx.dashboard': '系统总览',
    'ctx.console': '控制台',
    'ctx.settings': '偏好设置',

    // ─── 快捷键说明 ───
    'shortcuts.title': '快捷键说明',
    'shortcuts.desc': 'F5 刷新 · Ctrl+Space 搜索 · Ctrl+, 设置 · ESC 关闭浮层 · Ctrl+1/2 切换模块',

    // ─── Spotlight 搜索索引 ───
    'search.type.module': '模块',
    'search.type.script': '脚本',
    'search.type.project': '项目',
    'search.type.subproject': '子项目·{0}',
    'search.type.memory': '记忆·{0}',
    'search.type.reference': '知识·{0}',
    'search.desc.dashboard': '查看 AOS 系统状态',
    'search.desc.skills': '管理已注册 Skill',
    'search.desc.projects': '浏览 AOS 项目',
    'search.desc.memory': '查看记忆索引',
    'search.desc.reference': '浏览参考知识',
    'search.desc.loop': '查看 Loop 状态',
    'search.desc.agent': '查看 Agent 任务',
    'search.desc.logs': '查看运行日志',
    'search.desc.console': '执行 AOS 脚本',

    // ─── 通用 ───
    'common.active': 'ACTIVE',
    'common.ready': 'READY',
    'common.close': '关闭',
    'common.unknown': '未知错误',
  },

  'en-US': {
    // ─── Boot screen ───
    'boot.loading': 'Loading system components...',

    // ─── Menu bar ───
    'menu.file': 'File',
    'menu.view': 'View',
    'menu.tools': 'Tools',
    'menu.help': 'Help',

    // ─── File menu ───
    'menu.file.refresh': 'Refresh Data',
    'menu.file.export': 'Export JSON',
    'menu.file.close': 'Close Panel',

    // ─── View menu ───
    'menu.view.switchModule': 'Switch Module',
    'menu.view.theme': 'Theme',
    'menu.view.zoomIn': 'Zoom In',
    'menu.view.zoomOut': 'Zoom Out',
    'menu.view.zoomReset': 'Reset Zoom',

    // ─── Tools menu ───
    'menu.tools.spotlight': 'Spotlight Search',
    'menu.tools.check': 'Consistency Check',
    'menu.tools.sync': 'GitHub Sync',
    'menu.tools.migrate': 'Migration Collect',
    'menu.tools.settings': 'Settings',

    // ─── Help menu ───
    'menu.help.about': 'About AOS',
    'menu.help.shortcuts': 'Keyboard Shortcuts',
    'menu.help.settings': 'Settings',

    // ─── Window controls ───
    'window.minimize': 'Minimize',
    'window.maximize': 'Maximize',
    'window.close': 'Close',

    // ─── Data source indicator ───
    'datasource.local': 'Local',
    'datasource.api': 'API',
    'datasource.local.title': 'Data source: local data.js (static). Start the backend service to switch to live API data',
    'datasource.api.title': 'Data source: backend API (live data with TTL cache)',

    // ─── Module names ───
    'module.dashboard': 'Dashboard',
    'module.skills': 'Skills',
    'module.projects': 'Projects',
    'module.memory': 'Memory',
    'module.reference': 'Reference',
    'module.loop': 'Loop Engine',
    'module.agent': 'Agent Pool',
    'module.logs': 'Logs',
    'module.console': 'Console',

    // ─── Dock short labels ───
    'dock.dashboard': 'Home',
    'dock.projects': 'Projects',
    'dock.memory': 'Memory',
    'dock.reference': 'Library',
    'dock.logs': 'Logs',
    'dock.console': 'Console',

    // ─── Theme ───
    'theme.dark': 'Dark',
    'theme.light': 'Light',
    'theme.minimal': 'Minimal',

    // ─── Glass intensity ───
    'glass.weak': 'Subtle',
    'glass.normal': 'Normal',
    'glass.strong': 'Strong',

    // ─── Dashboard module ───
    'dashboard.version': 'Version',
    'dashboard.kernelStatus': 'Kernel',
    'dashboard.initTime': 'Initialized',
    'dashboard.lastUpdate': 'Last Update',
    'dashboard.components': 'Components',
    'dashboard.runtimeStats': 'Runtime Stats',
    'dashboard.eventLog': 'Event Log',

    // ─── Skills module ───
    'skills.registered': 'Registered Skills',
    'skill.callCount': '{0} calls',
    'skill.viewDetail': 'View file structure & evolution ›',
    'skill.collapse': 'Collapse ‹',
    'skill.evolution': 'Evolution ({0})',

    // ─── Projects module ───
    'projects.list': 'Projects',
    'project.viewDetail': 'View details ›',
    'project.detail.title': 'Project Details',
    'project.expand': 'Expand left',
    'project.collapse': 'Collapse right',
    'project.description': 'Description',
    'project.basicInfo': 'Basic Info',
    'project.type': 'Type',
    'project.createdAt': 'Created',
    'project.path': 'Path',
    'project.status': 'Status',
    'project.projectType': 'Project Type',
    'project.techStack': 'Tech Stack',
    'project.fileIntegrity': 'File Integrity',
    'project.structure': 'Structure',
    'project.subprojects': 'Subprojects',
    'project.sourceModules': 'Source Modules',
    'project.subprojectCount': 'Subprojects ({0})',
    'project.moduleCount': 'Source Modules ({0})',
    'project.subprojectStats': 'Subproject Stats',
    'project.total': 'Total',
    'project.active': 'Active',
    'project.archived': 'Archived',
    'project.fileCount': '{0} files',
    'project.clickSubproject': 'Click a subproject tab on the left to view plugin details',
    'project.expandHint': 'Click the left handle ‹ to expand project-level files (AGENTS.md / STATUS.md / README.md), or click a subproject card',
    'project.expandHintSingle': 'Click a subproject card on the left to view details',
    'project.expandHintSimple': 'Click the left handle ‹ to expand project-level files (AGENTS.md / STATUS.md / README.md)',
    'project.fileUnavailable': '{0} unavailable',
    'project.fileUnavailableDesc': 'Project directory pending creation. File contents will be available after initialization.',
    'project.cardHint': 'View details ›',

    // ─── Subproject detail ───
    'subproject.detail': 'Plugin Details',
    'subproject.name': 'Name',
    'subproject.version': 'Version',
    'subproject.author': 'Author',
    'subproject.status': 'Status',
    'subproject.path': 'Path',
    'subproject.fileStructure': 'File Structure',
    'subproject.fileList': 'Files',
    'subproject.pendingModeling': 'Detailed data (metadata.yaml / README.md / file structure) pending modeling',

    // ─── Module detail ───
    'module.detail': 'Module Details',
    'module.name': 'Name',
    'module.path': 'Path',

    // ─── Fullscreen tabs ───
    'tab.projectLevel': 'Project-level',
    'tab.overview': 'Overview',

    // ─── Memory module ───
    'memory.user': 'User Profile',
    'memory.feedback': 'Feedback',
    'memory.reference': 'Reference',
    'memory.project': 'Project',
    'memory.empty': 'No memories yet',
    'memory.pathHint': 'View full content: 04_MEMORY/{0}',
    'memory.readFull': 'Click card to read full text in sidebar ›',
    'memory.noContent': 'Content pending, reading unavailable',
    'memory.toggleHint': 'Read full text / Expand ›',
    'memory.toggleHintNoContent': 'Expand ›',
    'memory.collapse': 'Collapse ‹',

    // ─── Reference module ───
    'ref.all': 'All',
    'ref.system': 'System',
    'ref.web': 'Web',
    'ref.confidence': 'Confidence',
    'ref.pathHint': 'File: 09_REFERENCE/{0}/{1}.md',
    'ref.sourceLink': 'Open source ↗',
    'ref.source': 'Source: {0}',
    'ref.readFull': 'Click card to read full text in sidebar ›',
    'ref.noContent': 'Content pending, reading unavailable',
    'ref.toggleHint': 'Read full text / Expand ›',
    'ref.toggleHintNoContent': 'Expand ›',
    'ref.collapse': 'Collapse ‹',
    'ref.viewDetail': 'View details ›',

    // ─── Loop module ───
    'loop.types': 'Loop Type Definitions',
    'loop.active': 'Active Loops',
    'loop.empty.title': 'No active loops',
    'loop.empty.desc': 'Loop engine ready, awaiting user trigger',
    'loop.unavailable': 'Unavailable',
    'loop.unavailable.title': 'Feature defined, pending v1.1 implementation',
    'loop.activeMeta': 'Active: {0} · Feature defined, pending future implementation',

    // ─── Agent module ───
    'agent.modes': 'Execution Modes',
    'agent.protocols': 'Coordination Protocols',
    'agent.active': 'Active Agents',
    'agent.empty.title': 'No active agents',
    'agent.empty.desc': 'Multi-session coordination protocol ready',
    'agent.unavailable': 'Unavailable',
    'agent.unavailable.title': 'Feature defined, pending v1.1 implementation',
    'agent.trigger': 'Trigger: {0}',

    // ─── Logs module ───
    'logs.systemEvents': 'System Event Log',
    'logs.level.all': 'All',
    'logs.search.placeholder': 'Search logs...',
    'logs.col.time': 'Time',
    'logs.col.level': 'Level',
    'logs.col.source': 'Source',
    'logs.col.message': 'Message',
    'logs.empty': 'No matching logs',
    'logs.detail.time': 'Time',
    'logs.detail.level': 'Level',
    'logs.detail.source': 'Source',
    'logs.detail.message': 'Message',

    // ─── Console module ───
    'console.check': 'Consistency Check',
    'console.sync': 'GitHub Sync',
    'console.migrate': 'Migration Collect',
    'console.classify': 'Migration Classify',
    'console.ingest': 'Migration Ingest',
    'console.terminalTitle': 'AOS Console — python',
    'console.welcome': 'AOS Console v1.1.0 — Type a command or click a button above to run a script',

    // ─── Spotlight ───
    'spotlight.placeholder': 'Search modules, skills, projects, references...',
    'spotlight.hint.titleOnly': 'Searching titles & tags only · Enable MD full-text search in Settings',
    'spotlight.hint.mdOn': 'MD full-text search enabled · Includes project configs, memory, and reference content',

    // ─── Settings panel ───
    'settings.title': 'Settings',
    'settings.theme': 'Appearance',
    'settings.accessibility': 'Accessibility',
    'settings.animations': 'Enable Animations',
    'settings.animationsDesc': 'Enable all animations and transitions (disable for a fully static interface)',
    'settings.scale': 'Interface Scale',
    'settings.fontSize': 'Font Size',
    'settings.fontSizeDesc': 'Adjust global font size (80% - 140%)',
    'settings.glass': 'Glass Effect',
    'settings.blur': 'Blur Intensity',
    'settings.blurDesc': 'Adjust the blur intensity of the glassmorphism effect',
    'settings.developer': 'Developer',
    'settings.debug': 'Debug Panel',
    'settings.debugDesc': 'Show debug panel at the bottom to monitor DOM state and function call logs (like F12 Console)',
    'settings.search': 'Search',
    'settings.mdSearch': 'MD Full-text Search',
    'settings.mdSearchDesc': 'Enable Spotlight to search full Markdown content of memory and references (off by default for performance)',
    'settings.language': 'Language',
    'settings.languageDesc': 'Switch interface language',

    // ─── MD Reader ───
    'mdReader.title': 'Document Preview',
    'mdReader.resize': 'Drag to resize width',
    'mdReader.empty.title': 'Content pending',
    'mdReader.empty.desc': 'Full content of this file has not been ingested yet',

    // ─── Debug panel ───
    'debug.title': 'Debug Console',
    'debug.refresh': 'Refresh State',
    'debug.export': 'Export Logs',
    'debug.clear': 'Clear',
    'debug.close': 'Close Panel',
    'debug.collapse': 'Collapse debug panel',
    'debug.expand': 'Expand debug panel',
    'debug.domSnapshot': 'DOM State Snapshot',
    'debug.domEmpty': 'Click "Refresh State" to view DOM state',
    'debug.callLog': 'Call Log',

    // ─── Notifications ───
    'notif.ready': 'AOS system ready',
    'notif.readyDesc': 'v{0} kernel running · {1} Skills · {2} memory entries · {3} references',
    'notif.refreshed': 'Data refreshed',
    'notif.refreshedDesc': 'Components {0} · Projects {1} · References {2}',
    'notif.refresh': 'Refreshed',
    'notif.refreshDesc': 'Dashboard data reloaded',
    'notif.closed': 'Closed',
    'notif.closedDesc': 'All overlay panels collapsed',
    'notif.themeChanged': 'Theme switched',
    'notif.themeChangedDesc': 'Current theme: {0}',
    'notif.scaleChanged': 'Scale adjusted',
    'notif.scaleChangedDesc': 'Current scale: {0}%',
    'notif.exportSuccess': 'Export successful',
    'notif.exportSuccessDesc': 'AOS data exported as JSON file',
    'notif.exportFail': 'Export failed',
    'notif.exportFailDesc': '{0}',
    'notif.redirecting': 'Redirecting',
    'notif.redirectingDesc': 'Opening AOS website',
    'notif.copied': 'Copied',
    'notif.copiedDesc': 'Event content copied to clipboard',
    'notif.copyFail': 'Copy failed',
    'notif.copyFailDesc': 'Clipboard access denied, please copy manually',
    'notif.moduleDev': '{0} module',
    'notif.moduleDevDesc': 'This module is under development, stay tuned',

    // ─── Context menu ───
    'ctx.copyEvent': 'Copy Event',
    'ctx.copySelection': 'Copy Selection',
    'ctx.searchSelection': 'Search Selection',
    'ctx.refresh': 'Refresh',
    'ctx.refreshLog': 'Refresh Logs',
    'ctx.spotlight': 'Spotlight Search',
    'ctx.dashboard': 'Dashboard',
    'ctx.console': 'Console',
    'ctx.settings': 'Settings',

    // ─── Keyboard shortcuts ───
    'shortcuts.title': 'Keyboard Shortcuts',
    'shortcuts.desc': 'F5 Refresh · Ctrl+Space Search · Ctrl+, Settings · ESC Close overlay · Ctrl+1/2 Switch module',

    // ─── Spotlight search index ───
    'search.type.module': 'Module',
    'search.type.script': 'Script',
    'search.type.project': 'Project',
    'search.type.subproject': 'Subproject·{0}',
    'search.type.memory': 'Memory·{0}',
    'search.type.reference': 'Reference·{0}',
    'search.desc.dashboard': 'View AOS system status',
    'search.desc.skills': 'Manage registered skills',
    'search.desc.projects': 'Browse AOS projects',
    'search.desc.memory': 'View memory index',
    'search.desc.reference': 'Browse reference knowledge',
    'search.desc.loop': 'View loop status',
    'search.desc.agent': 'View agent tasks',
    'search.desc.logs': 'View runtime logs',
    'search.desc.console': 'Run AOS scripts',

    // ─── Common ───
    'common.active': 'ACTIVE',
    'common.ready': 'READY',
    'common.close': 'Close',
    'common.unknown': 'Unknown error',
  },
};

// ═══════════════════════════════════════════════════════
// i18n 核心函数
// ═══════════════════════════════════════════════════════

let _currentLang = 'zh-CN';

function getLang() {
  return _currentLang;
}

function setLang(lang) {
  if (!I18N[lang]) lang = 'zh-CN';
  _currentLang = lang;
  // 持久化到 prefs
  const prefs = loadPrefs();
  prefs.lang = lang;
  savePrefs(prefs);
  // 应用到 DOM
  applyI18n(lang);
  // 更新 html lang 属性
  document.documentElement.lang = lang;
}

/**
 * 翻译函数 — 用于 JS 动态文本
 * 支持占位符替换：t('key', arg1, arg2) → "text {0} {1}"
 */
function t(key, ...args) {
  const dict = I18N[_currentLang] || I18N['zh-CN'];
  let text = dict[key];
  if (text === undefined) {
    // 回退到 zh-CN
    text = I18N['zh-CN'][key];
    if (text === undefined) {
      return key; // 返回 key 本身作为最后手段
    }
  }
  // 替换占位符 {0}, {1}, ...
  if (args.length > 0) {
    text = text.replace(/\{(\d+)\}/g, (match, idx) => {
      return args[idx] !== undefined ? args[idx] : match;
    });
  }
  return text;
}

/**
 * 应用翻译到 DOM — 遍历 [data-i18n] 等属性
 */
function applyI18n(lang) {
  if (!I18N[lang]) lang = 'zh-CN';
  const dict = I18N[lang];

  // data-i18n: 替换 textContent
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const text = dict[key];
    if (text !== undefined) {
      el.textContent = text;
    }
  });

  // data-i18n-placeholder: 替换 placeholder
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    const text = dict[key];
    if (text !== undefined) {
      el.placeholder = text;
    }
  });

  // data-i18n-title: 替换 title
  document.querySelectorAll('[data-i18n-title]').forEach(el => {
    const key = el.getAttribute('data-i18n-title');
    const text = dict[key];
    if (text !== undefined) {
      el.title = text;
    }
  });

  // 更新 html lang 属性
  document.documentElement.lang = lang;
}

/**
 * 初始化 i18n — 从 prefs 加载语言并应用
 */
function initI18n() {
  const prefs = loadPrefs();
  _currentLang = prefs.lang || 'zh-CN';
  applyI18n(_currentLang);
}
