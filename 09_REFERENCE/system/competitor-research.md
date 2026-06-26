# 竞品调研：Agent 操作系统与规则框架

> 来源：2026-06-21 全网调研 | 置信度：高

---

## TL;DR

- AOS 是目前唯一纯文件系统方案（零代码依赖），竞品均需 Python/Node 运行时
- PilotDeck 的白盒记忆和 Smart Routing 设计理念值得借鉴，但不引入代码依赖
- CLAUDE.md 最佳实践建议控制在 60 行以内，AOS 的 AGENTS.md 约 190 行需关注
- AOS 的差异化优势：零门槛部署、文件即状态、规则即代码

---

## 竞品对比

| 维度 | AOS | PilotDeck | claude-code-best-practice | OpenHands |
|------|-----|-----------|--------------------------|-----------|
| 定位 | 文件规范+规则体系 | Agent 操作系统 | CLAUDE.md 最佳实践 | 软件工程 Agent |
| 代码依赖 | 零（纯文件） | Python | 零（纯文件） | Python |
| 项目隔离 | 01_PROJECTS/ 目录 | WorkSpace 级 | 无原生支持 | 沙箱隔离 |
| 记忆系统 | 04_MEMORY/ 四类 | 白盒可追溯+Dream Mode | CLAUDE.local.md | Condenser 压缩 |
| Skill 系统 | 03_TOOLS/skills/ | WorkSpace Skill 集 | .claude/skills/ | 工具注册 |
| 模型路由 | 无 | Smart Routing（省77%成本） | 无 | 无 |
| 后台执行 | 无（单次触发） | Always-on | 无 | 后台运行 |
| Stars | — | 2,500+ | 57,000+ | 36,000+ |
| 许可证 | MIT+补充条款 | AGPL 3.0 | MIT | MIT |

---

## 可借鉴理念（不引入代码依赖）

### 1. 白盒记忆（来自 PilotDeck）

**理念**：记忆全程可追溯、可编辑、可回滚
**AOS 现状**：04_MEMORY/ 已实现文件级可追溯（文件可手动编辑），但缺少版本回滚和自动去噪
**借鉴方式**：记录此理念，后续可考虑在 04_MEMORY/ 中增加变更日志（changelog）机制

### 2. Smart Routing（来自 PilotDeck）

**理念**：按任务难度自动匹配模型，简单任务用轻量模型，复杂任务用旗舰模型
**AOS 现状**：无模型路由能力
**借鉴方式**：记录此理念，依赖 Trae 后续支持多模型切换功能

### 3. CLAUDE.md 精简原则（来自 claude-code-best-practice）

**理念**：CLAUDE.md 控制在 60 行以内，硬上限 300 行；只放 AI 可能忽略的规则
**AOS 现状**：AGENTS.md 约 190 行，已接近建议上限
**借鉴方式**：1.0 保持现状，后续版本考虑拆分

### 4. 记忆压缩与去噪（来自 PilotDeck Dream Mode / OpenHands Condenser）

**理念**：空闲时自动整合记忆，去除冗余，保持信噪比
**AOS 现状**：04_MEMORY/INDEX.md 有硬上限（200行/25KB），但无自动去噪
**借鉴方式**：记录此理念，可通过 `/aos-learn` 命令手动触发记忆整理

---

## AOS 差异化优势

1. **零代码依赖**：纯文件系统方案，克隆即用，无需安装 Python/Node
2. **文件即状态**：所有状态写入磁盘，不依赖运行时内存，跨会话天然保持
3. **规则即代码**：AGENTS.md + Trae Rules 双层规则体系，规则修改即时生效
4. **可视化执行**：每步操作向用户展示，不后台静默运行
5. **迁移系统**：内置存量内容迁移能力，其他竞品无此功能
