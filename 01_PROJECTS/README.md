# AOS v1.1.0 — 01_PROJECTS

项目隔离存放区，每个项目一个独立子目录。

## 应放什么

- 每个项目一个子目录：`01_PROJECTS/{project_name}/`
- 每个项目必须包含：`AGENTS.md`（项目配置） + `README.md`（项目说明） + `STATUS.md`（状态跟踪）
- 项目专属文档放 `docs/`，源代码放 `src/`，配置放 `config/`

## 禁止放什么

- 非项目内容
- 知识内容副本（应放 09_REFERENCE/，这里只引用路径）
- 全局状态文件（应放 04_MEMORY/）

## 项目类型

AOS 支持两种项目类型，通过 AGENTS.md 的"项目类型"字段区分：

### 类型一：单一项目

适用于独立项目（如浏览器扩展、单机应用、工具脚本）。`src/` 直接存放源代码文件。

```
01_PROJECTS/{name}/
├── AGENTS.md               ← 项目专属配置（必须）
├── README.md               ← 项目基本信息（必须）
├── STATUS.md               ← 项目状态跟踪（必须）
├── docs/                   ← 项目文档（讨论记录、开发规划、设计文档）
├── src/                    ← 源代码 / 工作文件（直接存放代码文件）
├── config/                 ← 项目配置
└── reference_links.md      ← 知识引用路径（不复制内容）
```

### 类型二：项目集

适用于包含多个子项目的集合（如插件集、微服务集、多模块项目）。`src/` 存放多个子项目目录，每个子项目有独立的结构。

```
01_PROJECTS/{name}/
├── AGENTS.md               ← 项目专属配置（必须，含子项目清单）
├── README.md               ← 项目基本信息（必须）
├── STATUS.md               ← 项目状态跟踪（必须）
├── docs/                   ← 项目文档（共享开发规范、教程）
├── src/                    ← 源代码 / 工作文件（存放多个子项目）
│   ├── sub_project_1/      ← 子项目1（独立目录）
│   ├── sub_project_2/      ← 子项目2（独立目录）
│   └── sub_project_3/      ← 子项目3（独立目录）
├── config/                 ← 项目配置
└── reference_links.md      ← 知识引用路径（不复制内容）
```

## 示例项目

AOS 内置 3 个精心制作的示例项目，演示不同项目类型的标准结构：

| 示例项目 | 类型 | 说明 |
|----------|------|------|
| [_example_cli_tool](../01_PROJECTS/_example_cli_tool/) | 单一项目 | CLI 工具示例（Python 日志分析工具） |
| [_example_game_localization](../01_PROJECTS/_example_game_localization/) | 单一项目 | 游戏本地化示例（翻译文件 + 流程文档） |
| [_example_plugin_suite](../01_PROJECTS/_example_plugin_suite/) | 项目集 | 插件集示例（聊天机器人插件集合） |

## 新建项目流程

1. 在 `01_PROJECTS/{name}/` 下创建目录
2. 创建 `AGENTS.md`（项目专属配置）
3. 创建 `README.md`（项目基本信息）
4. 创建 `STATUS.md`（项目状态跟踪）
5. 更新 `04_MEMORY/project/proj_{name}.md`
6. 更新 `04_MEMORY/INDEX.md`

## 导入已有项目流程

对于已有运行服务的项目导入（非从零创建），需额外执行：

1. 服务发现与采集（NSSM 服务 / Docker 容器 / 端口监听）
2. 凭据提取（自动填入 AGENTS.md 敏感信息表 + credentials.json）
3. 依赖关系推断（端口连接关系 / 配置文件引用 / 环境变量）
4. 执行标准 6 步新建项目流程
