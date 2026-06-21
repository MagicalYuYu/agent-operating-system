# AOS 跨平台适配说明

AOS 1.0 对 Trae 适配性最优，同时也支持 Claude Code 和 Codex。本目录提供各平台的适配模板和映射说明。

---

## 适配原理

AOS 的核心是一套文件目录 + 规则体系，不依赖特定平台的代码运行时。适配的关键是将 AOS 的规则映射到目标平台的原生配置格式：

| AOS 概念 | Trae | Claude Code | Codex |
|----------|------|-------------|-------|
| 系统规则 | AGENTS.md（根目录） | CLAUDE.md（根目录） | 系统提示词 |
| 项目规则 | 01_PROJECTS/{name}/AGENTS.md | 子目录 CLAUDE.md | 项目配置 |
| Skill | .trae/skills/ | .claude/skills/ | 工具定义 |
| 规则文件 | Trae Rules（设置中配置） | .claude/rules/ | 规则配置 |
| 自定义命令 | Trae 命令（设置中配置） | .claude/commands/ | 命令配置 |
| 记忆 | 04_MEMORY/ | CLAUDE.local.md + 记忆系统 | 会话状态 |

---

## Claude Code 适配

### 步骤1：创建 CLAUDE.md

将 AOS 根目录的 AGENTS.md 核心规则提取到 CLAUDE.md 中。建议控制在 60 行以内，详细规则通过引用指向 AOS 文件：

```markdown
# AOS v1.0 — Claude Code 适配

## 核心规则
- 执行模型、铁律、约束详见 AGENTS.md
- 项目识别规则详见 AGENTS.md
- Skill 规范详见 03_TOOLS/skills/{skill}/SKILL.md

## 目录约束
- 00_BOOT/ 系统规则，不可被业务污染
- 01_PROJECTS/ 项目隔离，引用知识用路径
- 04_MEMORY/ 状态持久化，区分记录型与状态型
- 09_REFERENCE/ 知识只存一份，禁止重复

## 记忆规则
- 读取 04_MEMORY/ 时遵循 aos-memory-rules
- 修改文件时遵循 aos-consistency-guard
```

### 步骤2：创建 Claude Code Rules

将 AOS 的 Trae Rules 转换为 `.claude/rules/` 下的文件：

- `.claude/rules/aos-skill-rules.md` ← 对应 Trae Rule 1
- `.claude/rules/aos-memory-rules.md` ← 对应 Trae Rule 2
- `.claude/rules/aos-consistency-guard.md` ← 对应 Trae Rule 3

### 步骤3：创建 Claude Code Commands

将 AOS 的自定义命令转换为 `.claude/commands/` 下的文件：

- `.claude/commands/aos-status.md`
- `.claude/commands/aos-ingest.md`
- `.claude/commands/aos-review.md`
- `.claude/commands/aos-learn.md`

---

## Codex 适配

### 步骤1：配置系统提示词

将 AGENTS.md 的核心规则配置到 Codex 的系统提示词中。

### 步骤2：配置工具定义

将 AOS Skill 的功能映射到 Codex 的工具定义格式。

### 步骤3：配置规则

将 AOS 的 Trae Rules 映射到 Codex 的规则配置中。

---

## 注意事项

- AOS 的文件目录结构在所有平台下保持一致，无需修改
- 规则内容相同，只是配置格式不同
- 当前仅提供模板和映射说明，完整自动化适配流程后续根据用户反馈开发
