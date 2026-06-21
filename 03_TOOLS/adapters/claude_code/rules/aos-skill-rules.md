# AOS Skill 规则（Claude Code 版本）

适用范围：当读取或修改 03_TOOLS/skills/ 目录下的文件时

1. Skill 必须是文件夹结构，包含 SKILL.md（必须）+ gotchas.md（必须）+ 可选的 scripts/templates/references
2. SKILL.md 的 description 必须写触发条件而非摘要，不超过250字符
3. 每个 Skill 必须有 gotchas.md 坑点清单，持续积累
4. 新建 Skill 必须立即在 00_BOOT/SKILL_REGISTRY.md 注册
5. Skill 调用后必须更新 SKILL_REGISTRY.md 的 call_count
6. Skill 步骤序列的最后一步必须是状态更新（更新 STATUS.md / agent_tasks.json / SKILL_REGISTRY.md），不可省略
