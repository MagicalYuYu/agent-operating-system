# AOS Memory Index（模板）

> 记忆索引 — 一行一条 topic 指针 + 150 字 hook 描述
> 硬上限：200 行 / 25KB，超出两阶段截断
> 分组：活跃（进行中/30 天内有更新/基础设施在用）/ 低频 / 示例；分组核验随轻审刷新
> ⚠ 以下条目全部为示例值：替换为你的真实条目后删除本行

---

## user
- [user-profile](user/user_profile.md) — 示例：职业背景与主用平台、模型偏好（决策用主模型/批量用低成本模型）、交互风格（重细节/质量优先）、巡检边界约定（仅框架层不深入 src/）

## reference
（示例：研究成果见 09_REFERENCE/research/，此处只留指针；入库走 knowledge-ingest skill）

## feedback
- [fb-example](feedback/fb_example.md) — 示例：某规则两次纠正失败后的简报，三要素=规则+Why+How to apply

## project — 活跃
- [proj-example-active](project/proj_example_active.md) — 示例：一句话状态 + 当前阶段 + 交付物位置（07_EXPORTS/{name}/）
- [proj-example-service](project/proj_example_service.md) — 示例：常驻服务型项目，写明端口/部署方式/依赖（敏感值只引用 credentials.json id）

## project — 低频
- [proj-example-idle](project/proj_example_idle.md) — 示例：挂起项目，一句话说明阻塞点与恢复条件

## project — 示例
- [proj-example-game-localization](project/proj_example_game_localization.md) — 示例行：对应 01_PROJECTS/_example_game_localization/ 的项目记忆
- [proj-example-cli-tool](project/proj_example_cli_tool.md) — 示例行：对应 01_PROJECTS/_example_cli_tool/ 的项目记忆
- [proj-example-plugin-suite](project/proj_example_plugin_suite.md) — 示例行：对应 01_PROJECTS/_example_plugin_suite/ 的项目记忆
