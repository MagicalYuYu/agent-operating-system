# AOS v1.1.0 — 04_MEMORY

唯一状态持久化中心，所有状态必须写入此目录。

## 应放什么
- INDEX.md — 记忆索引（硬上限200行/25KB）
- user/ — 用户画像（长期）
- feedback/ — 行为纠偏（中期，每条含规则+Why+How to apply）
- reference/ — 外部系统指针（中期，只存路径不存内容）
- project/ — 项目动态事实（短期，相对日期必须转绝对日期）
- agent_pool/ — 多会话协同状态
- skill_memory/ — Skill 持久记忆
- loop_memory/ — Loop 持久记忆

## 禁止放什么
- 可推导信息（代码模式、Git历史、Debug方案）
- AGENTS.md 已有内容（避免冗余）
- 临时任务细节

## 记忆四类体系
| 类型 | 时效 | 维护者 |
|------|------|--------|
| user | 长期 | 用户+Agent观察 |
| feedback | 中期 | Agent自动积累 |
| reference | 中期 | Agent自动积累 |
| project | 短期 | Agent自动积累 |
