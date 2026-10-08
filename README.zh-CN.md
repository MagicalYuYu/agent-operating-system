# AOS — Agent Operating System

**运行在类 Claude Code agent harness 上的个人文件治理层。**

[![Release](https://img.shields.io/badge/Release-v2.0.0--rc.1-blue.svg)](https://github.com/MagicalYuYu/agent-operating-system/releases)
[![Runtime](https://img.shields.io/badge/Runtime-DeepSeek_Harness-6E40C9.svg)](https://github.com/deepseek-ai/deepseek-harness)
[![Standard](https://img.shields.io/badge/Standard-AGENTS.md-2EA44F.svg)](https://agents.md/)
[![License: MIT](https://img.shields.io/badge/License-MIT--Additional-informational.svg)](LICENSE)

[English](README.md) · [官网](https://aos.magicalyu.online)

AI 编程工具能写代码、跑命令，但不管你的文件：交付物散在工作目录里、知识存了三份彼此矛盾、会话一压缩约束就丢。AOS 解决的是这一层的问题，它给工具一套关于"东西放哪、知识存哪、状态记哪"的约定，并且这些约定可以被脚本检查。

只要对话发生在 AOS 的工作路径内，无论操作的是哪个项目、甚至在授权后操作其他设备上的文件，你的 AI 都会遵守这套秩序。一次部署，处处生效。

形象点讲，AOS 的定位类似《钢铁侠》里的贾维斯：战衣换了几代，贾维斯一直都在。这就意味着，即便未来 AI 工具不时更换，秩序和记忆也可以持续跟着走。

---

## 它提供什么

**目录宪章**：8 个编号目录，每个目录一行职责和几条约束，写在 AGENTS.md 里。AI 在创建任何文件之前先查约定，你不再需要反复纠正"这个文件不要放这里"。具体到每类文件放哪、目录怎么命名，有一套可程序化判断的细则，见 [docs/file-conventions.md](docs/file-conventions.md)。附带的校验脚本（`scripts/check_placement.py`）能扫出违反约定的散落文件、非标命名、结构漂移，机器管机器。

**指针表记忆**：`04_MEMORY/INDEX.md` 一行一指针加一段短描述，配 32KB 的单文件上限。状态类记忆（项目进展、个人偏好）覆盖旧值并留变更注释；记录类记忆（经验、坑点）只追加。长出来的历史剪切进日志目录，不丢。

**双层日志**：过程细节交给平台自带的会话档案；治理层面的大事（巡检、事故、决策、交付）写入人类可直接阅读的 06_LOGS。换平台时，叙事层日志可以整体搬走。

**治理 skills**：文件落位判定、知识入库检查、子代理调度决策、巡检流程等，各自是一个按需加载的技能文件，带实战沉淀的 gotchas 段落。犯错沉淀进对应 skill，比在提示词里纠正更持久。

**环境对齐**：一份 manifest 登记所有依赖组件，换机器或迁移环境时跑一个脚本即可检测缺什么。

这些机制怎么协同运转、一个任务从指令到交付经过哪些环节，见 [架构参考](docs/architecture.md)。

## 平台支持

| 层 | 覆盖范围 | 说明 |
|---|---|---|
| 完整适配 | [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)（DSH） | skills 自动发现与按需加载、上下文压缩锚点、会话索引脚本等全部能力 |
| 通用适配 | 任何读取 `AGENTS.md` 约定的工具（Claude Code、Codex 等） | 目录宪章、指针表记忆、落位约定、校验脚本 |

v2 的实测在 DSH 上完成。通用适配也不意味着二手体验：把仓库交给你的 AI 工具，它读一遍约定，就能把这些规则适配成自己平台的形式（比如把 `.dsh/skills/` 的内容改写成对应平台的技能格式），不需要手动改。

## 如何上手

最直接的方式：把这句话发给你正在用的 AI 工具（DSH、Claude Code、Codex 等均可），让它替你完成：

> 部署 AOS：克隆 https://github.com/MagicalYuYu/agent-operating-system 到 <你的目标路径>，阅读仓库根目录的 AGENTS.md 理解目录约定，运行 `python scripts/check_placement.py` 验证结构、有报错按提示修复，最后告诉我使用时需要注意的约定要点。

想手动完成的话：

1. 环境要求：读取 `AGENTS.md` 约定的工具即为通用适配（目录宪章/脚本可用）；完整适配（skills 自动加载等）需 DSH，其他平台参照 `.dsh/skills/` 改写。脚本需要 Python 3.10+。
2. 把本仓库放在任意路径（下称 `{AOS_ROOT}`），路径无硬编码要求。
3. 校验结构：`python scripts/check_placement.py`。根目录按脚本位置自动推导，也可用 `--root` 显式指定；退出码 1 表示有 error 级违规。
4. 对齐环境（可选）：按你的实际依赖编辑 `.dsh/skill-manifest.json`，再跑 `python scripts/align_environment.py` 检测缺失组件，加 `--apply` 可补装。
5. 建第一个项目：参照 `01_PROJECTS/_example_cli_tool/` 的两件套（AGENTS.md + README.md），或直接复制任一 `_example_*` 目录改名起步。示例项目自带可运行的测试命令。
6. 读内核：`AGENTS.md`（约 90 行），含目录宪章、4 条铁律、落位速查、行为不变量。

---

## 目录速览

| 目录 | 职责 |
|---|---|
| `01_PROJECTS/` | 项目隔离存放（附 3 个示例项目：CLI 工具 / 游戏本地化 / 插件集） |
| `04_MEMORY/` | 唯一状态持久化中心（`INDEX.md` 一行一指针） |
| `05_CACHE/` | Agent 中间产物垃圾场（可再生；唯一副本禁入） |
| `06_LOGS/` | 运行日志，平台无关叙事层（只追加） |
| `07_EXPORTS/` | 交付物唯一出口（按项目分层） |
| `08_INBOX/` | 重量级外部输入中转区（处理完归位留指针） |
| `09_REFERENCE/` | 唯一参考知识库（知识只存一份） |
| `99_ARCHIVE/` | 不可修改历史归档（只读只增） |
| `.dsh/skills/` | 7 个治理 / 功能 skills（file-placement、knowledge-ingest、subagent-dispatch、inspection、project-init、exa-search、dual-machine） |
| `scripts/` | check_placement / align_environment / session_analyzer / session_index_update |
| `docs/` | 设计文档与迁移指南 |

## 文档

- [架构参考](docs/architecture.md)——系统由哪些部分组成、每个机制怎么运转、一次典型任务的完整流转
- [设计思路](docs/design-rationale.md)——完整的设计论证：十个模块各自是什么、为什么这样设计、依据与数据、其他技术方向为什么没有采用
- [文件落位约定](docs/file-conventions.md)——每类文件放哪、目录怎么命名、轻量任务与项目的分界
- [从 v1 迁移](docs/MIGRATION.md)——v1 用户升级指南，含让 AI 代为部署的提示词

## 反馈

使用中遇到问题或有建议，欢迎开 [Issue](https://github.com/MagicalYuYu/agent-operating-system/issues) 或到 [Discussions](https://github.com/MagicalYuYu/agent-operating-system/discussions) 交流。

## License

MIT + 附加条款（禁止单独封装商用售卖），详见 [LICENSE](LICENSE)。
