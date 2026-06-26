// ═══════════════════════════════════════════════════════
// AOS Viewer Data — 示例数据（上传版，含 3 个示例项目）
// ⚠ 此文件为 GitHub 上传版，仅包含示例项目数据
// ⚠ 用户首次运行 aos_generate_data.py 后将自动覆盖为真实数据
// ═══════════════════════════════════════════════════════

const AOS_DATA = {
  "version": "1.1.0",
  "kernelStatus": "ACTIVE",
  "initTime": "2026-06-21",
  "lastUpdate": "2026-06-XX（1.1.0 发布版：新增 AOS Viewer 可视化界面）",
  "components": [
    {
      "name": "Skill System",
      "status": "active",
      "desc": "0 Skill 已注册 (WKIS v1.0, Migration v1.0)，文件夹结构标准化"
    },
    {
      "name": "Loop Engine",
      "status": "ready",
      "desc": "3 种 Loop 类型已定义（Goal/Scheduled/Event），0 个活跃 Loop"
    },
    {
      "name": "Agent Scheduler",
      "status": "ready",
      "desc": "3 种执行模式（PLAN/EXECUTE/VERIFY），多会话协同协议已设计"
    },
    {
      "name": "Memory System",
      "status": "active",
      "desc": "INDEX.md + 四类记忆（user/feedback/reference/project）已建立"
    },
    {
      "name": "Inbox Pipeline",
      "status": "ready",
      "desc": "空队列"
    },
    {
      "name": "Export System",
      "status": "ready",
      "desc": "空输出"
    },
    {
      "name": "Harness Framework",
      "status": "active",
      "desc": "六层架构已定义，犯错工程化修复流程已建立"
    }
  ],
  "stats": [
    {
      "label": "已注册 Skill 数",
      "value": 0
    },
    {
      "label": "活跃 Loop 数",
      "value": 0
    },
    {
      "label": "已完成 Loop 周期",
      "value": 0
    },
    {
      "label": "活跃 Agent 数",
      "value": 0
    },
    {
      "label": "已处理任务数",
      "value": 0
    },
    {
      "label": "系统错误数",
      "value": 0
    },
    {
      "label": "记忆索引条目数",
      "value": 0
    },
    {
      "label": "反馈记录数",
      "value": 0
    }
  ],
  "events": [
    {
      "time": "2026-06-21",
      "type": "system_init",
      "desc": "AOS 1.0.0-dev1 系统初始化完成"
    },
    {
      "time": "2026-06-21",
      "type": "system_patch",
      "desc": "1.0.0-dev2 结构修正：单次触发模型 + Reference唯一化 + 目录强约束"
    },
    {
      "time": "2026-06-21",
      "type": "skill_register",
      "desc": "WKIS (SK_0001) 注册：网页知识抓取入库"
    },
    {
      "time": "2026-06-21",
      "type": "skill_exec",
      "desc": "WKIS 首次执行：TRAE Work 官方文档入库（8条索引）"
    },
    {
      "time": "2026-06-21",
      "type": "system_refactor",
      "desc": "1.0.0-dev3 全面重构：规则分层+记忆四类+Skill标准化+Loop适配+Harness六层+可视化规范"
    },
    {
      "time": "2026-06-21",
      "type": "archive",
      "desc": "1.0.0-dev2 原始设计归档至 99_ARCHIVE/aos-v1.0.0-dev2-original-design.md"
    },
    {
      "time": "2026-06-21",
      "type": "system_patch",
      "desc": "1.0.0-rc1 修正：运行时铁律（用户唯一调度器+事前声明+禁止假设自觉更新）、版本一致性规则、全部README版本号同步、AGENTS.md引用表修复"
    },
    {
      "time": "2026-06-21",
      "type": "tool_create",
      "desc": "aos_check.py 自检脚本创建（4项检查：版本号一致性/引用完整性/索引对应性/目录合规性）"
    },
    {
      "time": "2026-06-21",
      "type": "tool_create",
      "desc": ".gitignore 白名单模式创建（默认不上传，只允许特定文件）"
    },
    {
      "time": "2026-06-21",
      "type": "system_release",
      "desc": "v1.0.0 GitHub首发版：版本号统一调整，全部文件同步更新"
    },
    {
      "time": "2026-06-21",
      "type": "skill_register",
      "desc": "Migration (SK_0002) 注册：存量内容迁移接入"
    },
    {
      "time": "2026-06-21",
      "type": "tool_create",
      "desc": "迁移脚本三件套创建（aos_migrate_collect/classify/ingest.py）"
    },
    {
      "time": "2026-06-21",
      "type": "system_patch",
      "desc": "新增项目识别与配置加载机制、新建项目流程、项目级AGENTS.md模板"
    },
    {
      "time": "2026-06-21",
      "type": "skill_patch",
      "desc": "SK_0002 新增Phase 0环境调研与安全准备、操作安全铁律、敏感信息模板、回滚方案"
    },
    {
      "time": "2026-06-21",
      "type": "project_create",
      "desc": "游戏本地化示例(_example_game_localization)创建：含AGENTS.md/README.md/STATUS.md及示例翻译文件"
    },
    {
      "time": "2026-06-21",
      "type": "system_patch",
      "desc": "铁律2修正：Memory区分记录型(追加)与状态型(覆盖+变更注释)；新增用户画像更新规则、项目状态同步规则、文件分层规则、功能触发机制一览表；项目内标准结构(docs/src/config)"
    },
    {
      "time": "2026-06-21",
      "type": "readme_patch",
      "desc": "6个目录README更新：01_PROJECTS项目标准结构、06_LOGS外部组件日志+分层、07_EXPORTS分层、08_INBOX分层、loop_memory低频标注、05_CACHE低频标注"
    },
    {
      "time": "2026-06-21",
      "type": "bugfix",
      "desc": "INDEX.md空洞引用修复：补全8个缺失文件（user/feedback/reference/project目录下），修复proj_aos_v2→v1文件名"
    },
    {
      "time": "2026-06-21",
      "type": "bugfix",
      "desc": "aos_check.py修复：schema_version类型假设（isinstance前置检查）+版本号正则误匹配（排除01_PROJECTS/05_CACHE/02_SANDBOX）"
    },
    {
      "time": "2026-06-21",
      "type": "skill_patch",
      "desc": "SK_0002补充Windows/Docker/PowerShell坑点：NSSM服务注册表、Docker bind mount、Compose工作目录、PS编码、EA冲突"
    },
    {
      "time": "2026-06-21",
      "type": "system_patch",
      "desc": "AGENTS.md新增：导入已有项目流程、凭据管理规则、06_LOGS按项目分层规则"
    },
    {
      "time": "2026-06-21",
      "type": "feature",
      "desc": "credentials.json创建：凭据集中管理schema定义，项目AGENTS.md敏感信息表改为引用路径"
    },
    {
      "time": "2026-06-23",
      "type": "system_patch",
      "desc": "AGENTS.md 项目内标准结构更新：明确\"单一项目\"和\"项目集\"两种类型，禁止 src/ 下嵌套同名目录"
    },
    {
      "time": "2026-06-25",
      "type": "spec_create",
      "desc": "DAILY_INSPECTION.md 每日开工前巡检流程规范正式发布（v1.0.0），定义分层巡检模式（系统级+项目级）、5阶段流程、四类文件分类标准、路径层级规范"
    },
    {
      "time": "2026-06-25",
      "type": "bugfix",
      "desc": "修复LS工具可靠性问题：所有文件存在性检查改用PowerShell Test-Path/Get-ChildItem -Force验证，避免误报"
    },
    {
      "time": "2026-06-25",
      "type": "refactor",
      "desc": "巡检规范拆分：DAILY_INSPECTION.md 拆分为 SYSTEM_INSPECTION.md（系统级）+ PROJECT_INSPECTION.md（项目级），AGENTS.md 引用从启动自检流程移至详细规则引用表（标注Layer 3手动触发）"
    }
  ],
  "skills": [
    {
      "id": "SK_0001",
      "name": "Web Knowledge Ingestion Skill",
      "version": "2.0.0",
      "status": "ACTIVE",
      "trigger": "当用户提供URL并要求抓取/入库/归档/知识提取时使用",
      "path": "03_TOOLS/skills/web_knowledge_ingestion/",
      "structure": [
        "config.json",
        "gotchas.md",
        "SKILL.md"
      ],
      "callCount": 0,
      "lastExec": "",
      "evolution": [
        {
          "time": "2026-06-21",
          "type": "CREATE",
          "desc": "WKIS 初始注册"
        },
        {
          "time": "2026-06-21",
          "type": "1.0.0-dev3",
          "desc": "重构：description改为触发条件式；新增gotchas.md；新增可视化执行规范"
        },
        {
          "time": "2026-06-21",
          "type": "PATCH",
          "desc": "1.0.0-rc1：运行时铁律适配——状态更新嵌入Skill步骤"
        }
      ],
      "skillMd": "",
      "gotchas": ""
    },
    {
      "id": "SK_0002",
      "name": "Legacy Migration Skill",
      "version": "1.0.0",
      "status": "ACTIVE",
      "trigger": "当用户要求迁移/导入历史项目、对话记录、存量内容到AOS时使用",
      "path": "03_TOOLS/skills/legacy_migration/",
      "structure": [
        "config.json",
        "gotchas.md",
        "GUIDE.md",
        "SKILL.md",
        "templates"
      ],
      "callCount": 0,
      "lastExec": "",
      "evolution": [
        {
          "time": "2026-06-21",
          "type": "CREATE",
          "desc": "Legacy Migration Skill 初始注册"
        }
      ],
      "skillMd": "",
      "gotchas": ""
    }
  ],
  "projects": [
    {
      "name": "_example_cli_tool",
      "title": "CLI 工具示例",
      "type": "cli_tool",
      "status": "ACTIVE",
      "createdAt": "2026-06-25",
      "path": "01_PROJECTS/_example_cli_tool/",
      "desc": "一个日志分析 CLI 工具示例项目，展示 Python 命令行工具的标准结构（argparse + setuptools + 单元测试）。 - 技术栈：Python 3.10+, argparse, setuptools",
      "techStack": ["Python 3.10+", "argparse", "setuptools", "unittest"],
      "hasAgents": true,
      "hasReadme": true,
      "hasStatus": true,
      "structure": [
        "AGENTS.md",
        "README.md",
        "STATUS.md",
        "docs/",
        "src/"
      ],
      "projectType": "单一项目",
      "plugins": [],
      "modules": [],
      "agentsContent": "",
      "readmeContent": "",
      "statusContent": ""
    },
    {
      "name": "_example_plugin_suite",
      "title": "插件集示例",
      "type": "plugin_suite",
      "status": "ACTIVE",
      "createdAt": "2026-06-25",
      "path": "01_PROJECTS/_example_plugin_suite/",
      "desc": "一个聊天机器人插件集示例项目，展示 AOS 项目集（多子项目）标准结构，含 3 个独立子插件（天气查询/翻译/记账）。 - 技术栈：Python 3.10+, JSON, EventBus",
      "techStack": ["Python 3.10+", "JSON", "EventBus", "Markdown"],
      "hasAgents": true,
      "hasReadme": true,
      "hasStatus": true,
      "structure": [
        "AGENTS.md",
        "README.md",
        "STATUS.md",
        "config/",
        "docs/",
        "src/"
      ],
      "projectType": "项目集",
      "plugins": [
        {"name": "weather_bot", "path": "src/weather_bot/", "status": "ACTIVE", "desc": "天气查询插件"},
        {"name": "translator_bot", "path": "src/translator_bot/", "status": "ACTIVE", "desc": "翻译插件"},
        {"name": "accounting_bot", "path": "src/accounting_bot/", "status": "ACTIVE", "desc": "记账插件"}
      ],
      "modules": [],
      "agentsContent": "",
      "readmeContent": "",
      "statusContent": ""
    },
    {
      "name": "_example_game_localization",
      "title": "游戏本地化示例",
      "type": "game_localization",
      "status": "ACTIVE",
      "createdAt": "2026-06-21",
      "path": "01_PROJECTS/_example_game_localization/",
      "desc": "一个游戏本地化示例项目，展示 AOS 单一项目目录的标准结构（含翻译文件目录结构示例）。 - 源语言：English → 目标语言：简体中文 - 技术栈：JSON, Markdown",
      "techStack": ["JSON", "Markdown"],
      "hasAgents": true,
      "hasReadme": true,
      "hasStatus": true,
      "structure": [
        "AGENTS.md",
        "lang/",
        "README.md",
        "STATUS.md"
      ],
      "projectType": "单一项目",
      "plugins": [],
      "modules": [],
      "agentsContent": "",
      "readmeContent": "",
      "statusContent": ""
    }
  ],
  "memories": {
    "user": [],
    "feedback": [],
    "reference": [
      {
        "title": "ref-trae-settings",
        "path": "reference/ref_trae_settings.md",
        "hook": "Trae CODE模式设置：AGENTS.md开启、MCP自动运行、命令自动运行（沙箱外）、内置浏览器、记忆已开启",
        "type": "记录型",
        "content": ""
      }
    ],
    "project": [
      {
        "title": "proj-aos-v1-status",
        "path": "project/proj_aos_v1_status.md",
        "hook": "AOS v1.0.0 GitHub首发版，截至2026-06-21有2个Skill(WKIS+Migration)已注册，0个活跃Loop，0个活跃Agent",
        "type": "状态型",
        "content": ""
      },
      {
        "title": "proj-example-cli-tool",
        "path": "project/proj__example_cli_tool.md",
        "hook": "CLI工具示例项目（日志分析工具），展示Python命令行工具标准结构，含argparse/setuptools/单元测试，5个阶段completed+1个pending",
        "type": "状态型",
        "content": ""
      },
      {
        "title": "proj-example-plugin-suite",
        "path": "project/proj__example_plugin_suite.md",
        "hook": "插件集示例项目（聊天机器人插件集），展示项目集多子项目结构，含3个独立子插件（天气/翻译/记账），全部阶段completed",
        "type": "状态型",
        "content": ""
      },
      {
        "title": "proj-example-game-localization",
        "path": "project/proj__example_game_localization.md",
        "hook": "游戏本地化示例项目，展示AOS单一项目标准结构（含翻译文件目录），6个阶段均completed",
        "type": "状态型",
        "content": ""
      }
    ]
  },
  "references": [
    {
      "slug": "trae-work-commands-workflow",
      "title": "TRAE Work 命令与工作流",
      "tags": [
        "trae",
        "work",
        "commands",
        "spec",
        "plan",
        "workflow"
      ],
      "source": "https://docs.trae.cn/solo_slash-commands",
      "confidence": 1.0,
      "category": "system",
      "content": "",
      "metadata": ""
    },
    {
      "slug": "trae-work-features",
      "title": "TRAE Work 功能集",
      "tags": [
        "trae",
        "work",
        "features",
        "github",
        "feishu",
        "sandbox",
        "automation"
      ],
      "source": "https://docs.trae.cn/solo",
      "confidence": 1.0,
      "category": "system",
      "content": "",
      "metadata": ""
    },
    {
      "slug": "trae-work-mcp",
      "title": "TRAE Work MCP",
      "tags": [
        "trae",
        "work",
        "mcp",
        "protocol"
      ],
      "source": "https://docs.trae.cn/solo_mcp-overview",
      "confidence": 1.0,
      "category": "system",
      "content": "",
      "metadata": ""
    },
    {
      "slug": "trae-work-models",
      "title": "TRAE Work 模型",
      "tags": [
        "trae",
        "work",
        "models",
        "llm"
      ],
      "source": "https://docs.trae.cn/solo_models",
      "confidence": 1.0,
      "category": "system",
      "content": "",
      "metadata": ""
    },
    {
      "slug": "trae-work-overview",
      "title": "TRAE Work 概述",
      "tags": [
        "trae",
        "work",
        "overview",
        "agent",
        "cloud"
      ],
      "source": "https://docs.trae.cn/solo_what-is-trae-solo",
      "confidence": 1.0,
      "category": "system",
      "content": "",
      "metadata": ""
    },
    {
      "slug": "trae-work-quickstart",
      "title": "TRAE Work 快速开始",
      "tags": [
        "trae",
        "work",
        "quickstart",
        "web",
        "desktop",
        "mobile"
      ],
      "source": "https://docs.trae.cn/solo_trae-solo-quickstart",
      "confidence": 1.0,
      "category": "system",
      "content": "",
      "metadata": ""
    },
    {
      "slug": "trae-work-rules",
      "title": "TRAE Work 规则",
      "tags": [
        "trae",
        "work",
        "rules",
        "agents-md"
      ],
      "source": "https://docs.trae.cn/solo_rules",
      "confidence": 1.0,
      "category": "system",
      "content": "",
      "metadata": ""
    },
    {
      "slug": "trae-work-skills",
      "title": "TRAE Work 技能",
      "tags": [
        "trae",
        "work",
        "skills",
        "skill-md"
      ],
      "source": "https://docs.trae.cn/solo_skills",
      "confidence": 1.0,
      "category": "system",
      "content": "",
      "metadata": ""
    },
    {
      "slug": "aos-agent-execution-model",
      "title": "AOS Agent执行模式与多会话协同",
      "tags": [
        "aos",
        "agent",
        "execution-model",
        "multi-session",
        "collaboration"
      ],
      "source": "AOS内部设计",
      "confidence": 1.0,
      "category": "system",
      "content": "",
      "metadata": ""
    },
    {
      "slug": "aos-loop-engine-v2",
      "title": "AOS Loop Engine v2",
      "tags": [
        "aos",
        "loop",
        "engine",
        "scheduled",
        "goal",
        "visualization"
      ],
      "source": "AOS内部设计",
      "confidence": 1.0,
      "category": "system",
      "content": "",
      "metadata": ""
    },
    {
      "slug": "aos-harness-framework",
      "title": "AOS Harness 六层架构",
      "tags": [
        "aos",
        "harness",
        "reliability",
        "engineering",
        "safety"
      ],
      "source": "AOS内部设计",
      "confidence": 1.0,
      "category": "system",
      "content": "",
      "metadata": ""
    },
    {
      "slug": "competitor-research",
      "title": "竞品调研：Agent操作系统与规则框架",
      "tags": [
        "aos",
        "competitor",
        "pilotdeck",
        "openhands",
        "claude-md"
      ],
      "source": "2026-06全网调研",
      "confidence": 0.9,
      "category": "system",
      "content": "",
      "metadata": ""
    },
    {
      "slug": "web-template-specification",
      "title": "网页模板规范文档",
      "tags": [
        "web",
        "template",
        "css",
        "animation",
        "glassmorphism",
        "aurora",
        "aos",
        "lingxi"
      ],
      "source": "AOS+灵犀网站开发经验",
      "confidence": 1.0,
      "category": "web",
      "content": "",
      "metadata": ""
    }
  ],
  "loops": {
    "types": [
      {
        "name": "自检循环",
        "desc": "系统启动时自动执行完整性检查",
        "active": 0
      },
      {
        "name": "同步循环",
        "desc": "定时同步工作目录与 GitHub 仓库",
        "active": 0
      },
      {
        "name": "迁移循环",
        "desc": "批量处理历史内容迁移",
        "active": 0
      }
    ]
  },
  "agents": {
    "modes": [
      {
        "name": "PLAN",
        "desc": "只读探索+生成计划",
        "trigger": "/spec 或 /plan"
      },
      {
        "name": "EXECUTE",
        "desc": "读写操作+工具调用",
        "trigger": "默认模式"
      },
      {
        "name": "VERIFY",
        "desc": "只读验证+输出报告",
        "trigger": "新会话中发起"
      }
    ],
    "protocols": [
      "Maker/Checker 分离",
      "状态更新是步骤的一部分",
      "事前声明优于事后记录",
      "文件是唯一的跨会话通道"
    ]
  },
  "logs": {
    "systemEvents": [
      {
        "time": "2026-06-21",
        "type": "system_init",
        "desc": "AOS 1.0.0-dev1 系统初始化完成"
      },
      {
        "time": "2026-06-21",
        "type": "system_patch",
        "desc": "1.0.0-dev2 结构修正：单次触发模型 + Reference唯一化 + 目录强约束"
      },
      {
        "time": "2026-06-21",
        "type": "skill_register",
        "desc": "WKIS (SK_0001) 注册：网页知识抓取入库"
      },
      {
        "time": "2026-06-21",
        "type": "skill_exec",
        "desc": "WKIS 首次执行：TRAE Work 官方文档入库（8条索引）"
      },
      {
        "time": "2026-06-21",
        "type": "system_refactor",
        "desc": "1.0.0-dev3 全面重构：规则分层+记忆四类+Skill标准化+Loop适配+Harness六层+可视化规范"
      },
      {
        "time": "2026-06-21",
        "type": "archive",
        "desc": "1.0.0-dev2 原始设计归档至 99_ARCHIVE/aos-v1.0.0-dev2-original-design.md"
      },
      {
        "time": "2026-06-21",
        "type": "system_patch",
        "desc": "1.0.0-rc1 修正：运行时铁律（用户唯一调度器+事前声明+禁止假设自觉更新）、版本一致性规则、全部README版本号同步、AGENTS.md引用表修复"
      },
      {
        "time": "2026-06-21",
        "type": "tool_create",
        "desc": "aos_check.py 自检脚本创建（4项检查：版本号一致性/引用完整性/索引对应性/目录合规性）"
      },
      {
        "time": "2026-06-21",
        "type": "tool_create",
        "desc": ".gitignore 白名单模式创建（默认不上传，只允许特定文件）"
      },
      {
        "time": "2026-06-21",
        "type": "system_release",
        "desc": "v1.0.0 GitHub首发版：版本号统一调整，全部文件同步更新"
      },
      {
        "time": "2026-06-21",
        "type": "skill_register",
        "desc": "Migration (SK_0002) 注册：存量内容迁移接入"
      },
      {
        "time": "2026-06-21",
        "type": "tool_create",
        "desc": "迁移脚本三件套创建（aos_migrate_collect/classify/ingest.py）"
      },
      {
        "time": "2026-06-21",
        "type": "system_patch",
        "desc": "新增项目识别与配置加载机制、新建项目流程、项目级AGENTS.md模板"
      },
      {
        "time": "2026-06-21",
        "type": "skill_patch",
        "desc": "SK_0002 新增Phase 0环境调研与安全准备、操作安全铁律、敏感信息模板、回滚方案"
      },
      {
        "time": "2026-06-21",
        "type": "project_create",
        "desc": "游戏本地化示例(_example_game_localization)创建：含AGENTS.md/README.md/STATUS.md及示例翻译文件"
      },
      {
        "time": "2026-06-21",
        "type": "system_patch",
        "desc": "铁律2修正：Memory区分记录型(追加)与状态型(覆盖+变更注释)；新增用户画像更新规则、项目状态同步规则、文件分层规则、功能触发机制一览表；项目内标准结构(docs/src/config)"
      },
      {
        "time": "2026-06-21",
        "type": "readme_patch",
        "desc": "6个目录README更新：01_PROJECTS项目标准结构、06_LOGS外部组件日志+分层、07_EXPORTS分层、08_INBOX分层、loop_memory低频标注、05_CACHE低频标注"
      },
      {
        "time": "2026-06-21",
        "type": "bugfix",
        "desc": "INDEX.md空洞引用修复：补全8个缺失文件（user/feedback/reference/project目录下），修复proj_aos_v2→v1文件名"
      },
      {
        "time": "2026-06-21",
        "type": "bugfix",
        "desc": "aos_check.py修复：schema_version类型假设（isinstance前置检查）+版本号正则误匹配（排除01_PROJECTS/05_CACHE/02_SANDBOX）"
      },
      {
        "time": "2026-06-21",
        "type": "skill_patch",
        "desc": "SK_0002补充Windows/Docker/PowerShell坑点：NSSM服务注册表、Docker bind mount、Compose工作目录、PS编码、EA冲突"
      },
      {
        "time": "2026-06-21",
        "type": "system_patch",
        "desc": "AGENTS.md新增：导入已有项目流程、凭据管理规则、06_LOGS按项目分层规则"
      },
      {
        "time": "2026-06-21",
        "type": "feature",
        "desc": "credentials.json创建：凭据集中管理schema定义，项目AGENTS.md敏感信息表改为引用路径"
      },
      {
        "time": "2026-06-23",
        "type": "system_patch",
        "desc": "AGENTS.md 项目内标准结构更新：明确\"单一项目\"和\"项目集\"两种类型，禁止 src/ 下嵌套同名目录"
      },
      {
        "time": "2026-06-25",
        "type": "spec_create",
        "desc": "DAILY_INSPECTION.md 每日开工前巡检流程规范正式发布（v1.0.0），定义分层巡检模式（系统级+项目级）、5阶段流程、四类文件分类标准、路径层级规范"
      },
      {
        "time": "2026-06-25",
        "type": "bugfix",
        "desc": "修复LS工具可靠性问题：所有文件存在性检查改用PowerShell Test-Path/Get-ChildItem -Force验证，避免误报"
      },
      {
        "time": "2026-06-25",
        "type": "refactor",
        "desc": "巡检规范拆分：DAILY_INSPECTION.md 拆分为 SYSTEM_INSPECTION.md（系统级）+ PROJECT_INSPECTION.md（项目级），AGENTS.md 引用从启动自检流程移至详细规则引用表（标注Layer 3手动触发）"
      }
    ]
  }
};

// ═══════════════════════════════════════════════════════
// 子项目元数据（示例版为空）
// ═══════════════════════════════════════════════════════
const SUBPROJECT_DATA = {};

window.AOS_DATA = AOS_DATA;
window.SUBPROJECT_DATA = SUBPROJECT_DATA;