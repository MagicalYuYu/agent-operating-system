# AOS — Agent Operating System

> 给 AI 一个规范的工作台，而不是一个空聊天框

如果你用过 AI 编程工具，可能遇到过这些情况：

- 手上同时跑着好几个项目，文件散落各处，找东西靠搜索
- AI 帮你改了代码，但改了哪些、为什么改，过两天就忘了
- 想让 AI 按固定流程干活，但每次都要从头描述一遍
- 项目之间有依赖关系，迁移时总漏掉端口、配置、环境变量
- 对话一关，AI 之前做的所有事情就"失忆"了

AOS 就是来解决这些问题的。

它不是又一个 AI 框架，而是一套标准化的文件目录 + 规则体系。你把项目放进 AOS，AI 就知道文件该放哪、流程该怎么走、状态该怎么记。对话关了没关系，下次打开，AI 从磁盘读取状态，接着上次的进度继续。

---

## AOS 适合谁

AOS 面向有一定开发经验、但缺少标准化流程的开发者。如果你项目越做越多、管理越来越乱，想让 AI 稳定可靠地帮你干活而不是每次从零开始，又不想花大量时间自研 Agent 系统——AOS 可能适合你。

---

## 快速开始

### 1. 获取 AOS

两种方式任选其一：

**方式一：Git 克隆**（推荐，方便后续更新）

```bash
git clone https://github.com/MagicalYuYu/agent-operating-system.git
```

**方式二：下载压缩包**

在 GitHub 仓库页面点击「Code → Download ZIP」，解压到任意位置即可。AOS 是纯文件结构，无需安装任何依赖。

### 2. 在 AI 工具中打开

**TRAE Work（最优适配）**

1. 打开 TRAE Work
2. 点击「打开文件夹」，选择 AOS 目录
3. 切换到 **Code 模式**（TRAE Work 右上角或左侧面板切换）
4. TRAE Work 会自动读取根目录的 `AGENTS.md`，AOS 的规则即开始生效

**其他平台（Claude Code / Codex 等）**

将 AOS 目录设为对应平台的工作区根目录，参照 [03_TOOLS/adapters/](03_TOOLS/adapters/) 中的适配模板完成配置。AOS 规则体系基于 TRAE Work Code 模式设计，其他平台需自行完成适配调整。

### 3. 配置 Rules

AOS 需要 3 条 Rules 才能完整运行。配置路径：**TRAE Work 设置 → 规则与记忆 → 本地 → 规则 → 点击「+ 创建」**

| 规则名 | 路径限定 | 作用 |
|--------|----------|------|
| aos-skill-rules | `03_TOOLS/skills/` | Skill 创建和调用规范 |
| aos-memory-rules | `04_MEMORY/` | 记忆存储规范 |
| aos-consistency-guard | （留空，全局生效） | 文件修改时的一致性保障 |

每条规则的具体内容见 [TRAE Work 配置指南](docs/trae-setup-guide.md)，文档包含完整的操作步骤和规则全文，可直接复制粘贴。

### 4. 配置自定义命令（可选）

AOS 提供 3 条自定义命令，配置路径：**TRAE Work 设置 → 命令 → 本地 → 点击「+ 创建」**

| 命令名 | 作用 |
|--------|------|
| /aos-status | 查看 AOS 当前系统状态 |
| /aos-ingest | 触发网页知识入库流程 |
| /aos-review | 对当前会话工作执行审查 |

每条命令的具体内容见 [TRAE Work 配置指南](docs/trae-setup-guide.md)。

### 5. 验证安装

```bash
python 03_TOOLS/scripts/aos_check.py
```

输出 `一致性验证：通过` 即表示安装成功。

---

## 它是怎么工作的

AOS 的核心思路很简单：**所有状态都写在文件里，AI 每次启动时从文件读取，结束时写回文件。**

```
你发指令 → AI 读取规则和状态 → 执行任务 → 写回状态 → 你关掉对话
                                                    ↓
下次打开 → AI 再次读取状态 → 接着上次的进度继续
```

每个项目有独立的配置文件，AI 会根据你的指令自动识别当前项目，加载对应的规则。你不需要手动告诉 AI"我在做哪个项目"。

---

## 目录结构

```
agent-operating-system/
├── AGENTS.md              ← 系统规则（TRAE Work 自动加载）
├── 00_BOOT/               ← 核心规则和系统状态
├── 01_PROJECTS/           ← 你的项目（每个项目一个文件夹）
├── 02_SANDBOX/            ← 实验、不确定的东西放这里
├── 03_TOOLS/              ← Skill 和工具脚本
├── 04_MEMORY/             ← AI 的记忆（跨会话保持）
├── 05_CACHE/              ← 临时数据（可随时清空）
├── 06_LOGS/               ← 运行日志
├── 07_EXPORTS/            ← 最终输出文件
├── 08_INBOX/              ← 外部输入中转
├── 09_REFERENCE/          ← 参考知识库
└── 99_ARCHIVE/            ← 历史归档（只读）
```

每个目录都有明确的职责和约束，文件不会乱放，AI 也不会把日志写到项目目录里。

---

## 内置功能

### 网页知识入库（WKIS）

给一个 URL，自动提取结构化知识并存入参考知识库。支持技术文章、官方文档、架构分析等内容的自动压缩、重组和索引。

### 存量内容迁移

把散落各处的历史项目、对话记录、工作流程迁移到 AOS 体系。支持从 TRAE Work、Claude Code、ChatGPT、本地文件等多种来源迁移，包含完整的安全准备、脱敏处理和回滚机制。

迁移流程分为三个阶段：

```
Phase 0: 环境调研与安全准备
  → 服务状态检测、健康检查、安全备份、敏感信息提取、回滚方案
Phase 1: 采集（Collect）
  → 将原始内容收集到 08_INBOX/migration/
Phase 2: 分类（Classify）
  → 使用决策树将内容分类到对应目录
Phase 3: 入库（Ingest）
  → 按类型写入 AOS 目录结构，更新索引和状态
```

详细的迁移操作指南见 [迁移指南](03_TOOLS/skills/legacy_migration/GUIDE.md)。

### 项目级配置

每个项目独立规则，AI 自动识别并加载。

### 一致性自检

内置脚本验证文件引用、版本号、索引是否一致。

### 可视化执行

AI 每步操作都展示进度，不会后台静默运行。

---

## 适配平台

AOS 1.0 对 **TRAE Work** 适配性最优（规则体系、Skill 机制均基于 TRAE Work Code 模式设计），同时也支持 **Claude Code** 和 **Codex**。用户下载部署后，将 AOS 目录设为对应平台的根目录即可快速完成适配。

跨平台适配模板和映射说明见 [03_TOOLS/adapters/](03_TOOLS/adapters/)，包含 Claude Code 的 CLAUDE.md 模板、Rules 模板和配置映射表。

---

## 适用场景

AOS 适配各类开发与运维场景——无论你是做项目开发、内容管理、知识库构建还是系统运维，只要需要 AI 按规范流程稳定执行任务，AOS 都能提供标准化的文件组织和规则体系支撑。

---

## 文档索引

| 文档 | 位置 | 内容 |
|------|------|------|
| TRAE Work 配置指南 | [docs/trae-setup-guide.md](docs/trae-setup-guide.md) | Rules 和命令的完整配置步骤，可直接复制 |
| 迁移指南 | [03_TOOLS/skills/legacy_migration/GUIDE.md](03_TOOLS/skills/legacy_migration/GUIDE.md) | 存量内容迁移的完整操作流程 |
| 系统规则 | [AGENTS.md](AGENTS.md) | 执行模型、铁律、约束、触发机制一览 |
| 核心定义 | [00_BOOT/](00_BOOT/) | Agent 策略、Loop 引擎、Skill 注册、系统状态 |
| Skill 开发 | [03_TOOLS/skills/](03_TOOLS/skills/) | 每个 Skill 的完整指令、坑点、模板 |
| 工具脚本 | [03_TOOLS/scripts/](03_TOOLS/scripts/) | 自检、迁移采集/分类/入库脚本 |
| 记忆体系 | [04_MEMORY/](04_MEMORY/) | 索引、用户画像、反馈、项目状态 |
| 参考知识 | [09_REFERENCE/](09_REFERENCE/) | 系统设计文档、Web 知识库 |
| 项目模板 | [01_PROJECTS/_example_project/](01_PROJECTS/_example_project/) | 完整示例项目 |
| 迁移模板 | [03_TOOLS/skills/legacy_migration/templates/](03_TOOLS/skills/legacy_migration/templates/) | 项目 AGENTS.md 模板、对话提取提示词 |

每个目录下的 `README.md` 都有详细的"应放什么/禁止放什么"说明。

---

## 致谢

致敬互联网开放精神与每一位乐于分享的知识贡献者。

---

## 许可证

[MIT License with Additional Terms](LICENSE)

个人使用无任何限制。禁止将 AOS 单独封装后商用售卖。衍生项目鼓励标注来源，但不强制。
