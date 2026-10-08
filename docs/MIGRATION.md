# 从 AOS v1 迁移到 v2

v1（2026 年中发布，TRAE 平台）已冻结在 tag `v1.1.0`。v2 是一次重写：底层从 TRAE 迁移到 DeepSeek Harness（DSH），目录结构精简，运行方式有较大变化。本文帮你完成迁移。

## v2 与 v1 的核心区别

v1 的思路是"用文件模拟一个操作系统"：启动自检目录（00_BOOT）、沙箱目录（02_SANDBOX）、工具模块库（03_TOOLS），因为当时的平台不提供调度、状态管理和技能发现。v2 所依托的 DSH 原生提供了这些能力，因此模拟层被整体拆除，AOS 回归为一个纯粹的**文件治理层**：约定东西放哪、知识存哪、状态记哪，并提供可程序化检查的脚本。

v1 的思路在当时的条件下是合理的：无原生运行时的平台上，那套补偿设计有其必要。换了平台，设计随之变化。

## 目录结构对照

| v1 | v2 | 说明 |
|---|---|---|
| 00_BOOT/ | 已移除 | 系统状态→分布式状态+日志；技能注册表→平台原生发现；循环引擎→goal 自动续跑 |
| 01_PROJECTS/ | 01_PROJECTS/ | 保留，项目模板从四件套简化为两件套（AGENTS.md + README.md） |
| 02_SANDBOX/ | 已移除 | 由 DSH 原生沙箱承担 |
| 03_TOOLS/ | 已移除 | 第三方组件→用户级 skills；自研脚本→仓库 scripts/ |
| 04_MEMORY/ | 04_MEMORY/ | 保留，INDEX.md 改为指针表并新增分组 |
| 05_CACHE/ 06_LOGS/ 07_EXPORTS/ 08_INBOX/ 09_REFERENCE/ 99_ARCHIVE/ | 同名保留 | 职责约定基本延续，细节见 AGENTS.md 目录宪章 |

## 部署 v2

### 路径一：让 AI 帮你完成（任何工具通用）

把下面这段话直接发给你在用的 AI 工具（DSH、Claude Code、Codex 等均可）：

> 请帮我部署 AOS 2.0 个人文件治理框架：
> 1. 克隆 https://github.com/MagicalYuYu/agent-operating-system 到我的工作目录（或我指定的路径）
> 2. 阅读仓库根目录的 AGENTS.md，理解目录宪章与落位约定
> 3. 运行 `python scripts/check_placement.py` 验证结构，如有报错按提示修复
> 4. 告诉我后续使用时需要注意的约定要点（不超过 5 条）
> 如果我在旧版 AOS（v1，TRAE 平台）上有数据，请先阅读仓库的 docs/MIGRATION.md 再操作。

从 v1 迁移且有旧数据的，保留最后一句，AI 会按本指南处理。

### 路径二：DSH 手动部署（完整体验）

1. 安装 DSH Desktop（[官方下载](https://www.deepseek.com/en/harness/)）
2. `git clone https://github.com/MagicalYuYu/agent-operating-system.git`（或下载 Release 包）到任意路径
3. 用 DSH 打开该目录，AGENTS.md 与 `.dsh/skills/` 会被自动发现加载
4. 跑一次 `python scripts/check_placement.py` 确认结构完整

DSH 用户额外获得：治理 skills 自动发现与按需加载、上下文压缩锚点、会话索引脚本。

### 路径三：其他 AI 工具手动部署（核心体验）

v2 的核心，目录宪章、指针表记忆、文件落位约定、校验脚本，不依赖任何特定平台。使用其他支持 `AGENTS.md` 约定的工具（Claude Code、Codex 等）时：

1. clone 或下载本仓库到你的工作路径
2. 工具会读取 AGENTS.md，核心治理约定即可生效
3. `.dsh/skills/` 下的技能是 DSH 目录格式；其他平台可参照其内容把规则改写为自己的技能/命令格式，或借助 rulesync 一类工具生成
4. 校验脚本需要 Python 3.10+

## v1 旧数据处理

- **04_MEMORY（记忆）**：大部分兼容。INDEX.md 需要按 v2 的指针表格式重排（一行一指针 + 短描述，可参照仓库内模板），状态文件迁移时建议顺手做一次瘦身（单文件 ≤32KB，超出的历史剪切到 06_LOGS）
- **项目数据（01_PROJECTS）**：直接保留。项目内的 STATUS.md / PROGRESS.md 在 v2 中由项目 AGENTS.md 头部摘要替代，可让 AI 帮你把两者的关键信息合并进项目 AGENTS.md
- **00_BOOT / 02_SANDBOX / 03_TOOLS 内容**：v2 中无对应物，建议归档留存而不是删除
- **v1 官网与文档**：保留在 tag `v1.1.0`，随时可查

## 常见问题

**v1 还能用吗？** 能。v1.1.0 是完整可用的版本，TRAE 平台用户可以继续使用，只是不再更新。

**必须换 DSH 吗？** 核心治理约定不依赖 DSH（见路径二）。但 v2 的完整体验（skills 自动加载、上下文锚点等）目前围绕 DSH 设计，其他平台需要少量适配。

**我的 v1 记忆数据能直接搬吗？** 见上节"v1 旧数据处理"，大部分可以，让 AI 帮你做最省事。
