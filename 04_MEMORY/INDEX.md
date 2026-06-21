# AOS Memory Index

> 记忆索引 — 一行一条 topic 指针 + 150 字 hook 描述
> 硬上限：200 行 / 25KB，超出两阶段截断

---

## user
- [user-profile](user/user_profile.md) — 游戏本地化专家，中文沟通，技术洁癖，要求脱敏处理，CODE模式为主

## feedback
- [fb-harness-fixes](feedback/fb_harness_fixes.md) — Agent犯错时必须工程化修复沉淀到环境，不能只靠提示词纠正；修复方式：规则类→AGENTS.md，坑点类→gotchas.md，流程类→SKILL.md
- [fb-context-strategy](feedback/fb_context_strategy.md) — 上下文到60-70%时主动压缩；纠正两次失败后建议新会话；压缩时保留任务目标+修改文件+错误消息+架构决策+用户约束
- [fb-skill-trigger](feedback/fb_skill_trigger.md) — Skill的description必须写触发条件而非摘要；单个description不超过250字符；验证类Skill回报最大
- [fb-runtime-iron-rules](feedback/fb_runtime_iron_rules.md) — 用户是唯一调度器；状态更新是Skill步骤的一部分而非事后动作；事前声明优于事后记录；禁止假设Agent会自觉更新文件

## reference
- [ref-trae-settings](reference/ref_trae_settings.md) — Trae CODE模式设置：AGENTS.md开启、MCP自动运行、命令自动运行（沙箱外）、内置浏览器、记忆已开启

## project
- [proj-aos-v1-status](project/proj_aos_v2_status.md) — AOS v1.0.0 GitHub首发版，截至2026-06-21有1个Skill(WKIS)已注册，0个活跃Loop，0个活跃Agent
- [proj-example-project](project/proj__example_project.md) — 示例项目（游戏本地化），展示AOS项目目录标准结构，6个阶段均pending
