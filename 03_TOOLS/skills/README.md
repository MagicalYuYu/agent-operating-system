# AOS v1.1.0 — 03_TOOLS/skills

Skill 定义目录，每个 Skill 一个独立文件夹。

## 当前已注册 Skill
- web_knowledge_ingestion/ — 网页知识入库（SK_0001）
- legacy_migration/ — 存量内容迁移（SK_0002）

## Skill 文件夹标准结构
每个 Skill 必须包含：
- SKILL.md — 核心指令（description 写触发条件而非摘要）
- gotchas.md — 坑点清单（持续积累）
- config.json — Skill 配置

可选：
- scripts/ — 可执行脚本
- templates/ — 输出模板
- references/ — 参考资料

## 新建 Skill 流程
详见 00_BOOT/SKILL_REGISTRY.md
