# AOS v1.0 — 00_BOOT

系统规则层，存放 AOS 的核心定义和运行时配置。

## 应放什么
- CORE.md — 系统身份定义、架构、执行模型
- AGENT_POLICY.md — Agent 执行模式与多会话协同协议
- LOOP_ENGINE.md — Loop Engine 定义与执行规范
- SKILL_REGISTRY.md — Skill 注册中心
- SYSTEM_STATE.md — 系统运行时状态快照

## 禁止放什么
- 项目相关内容
- 临时数据
- 日志文件

## 注意
此目录是 AOS 的"BIOS"，Agent 每次启动时首先读取此目录。不可被业务逻辑污染。
