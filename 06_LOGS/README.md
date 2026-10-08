# 06_LOGS — 运行日志（平台无关叙事层）

只追加，不改写。两类必写：治理事件（巡检/事故/发布/决策）与项目关键节点（立项/阶段切换/交付），一行一条。

- 重要会话一行入 `aos/session_index.md`（可用 `python scripts/session_index_update.py` 自动追加）
- `{project}/memory_history.md` 承接 04_MEMORY 状态文件剪切的历史——**裁剪前必须先归档，顺序不可倒**
- 跨平台迁移时本目录随迁（过程细节层归 harness 会话档案，不在此目录）

示例：`06_LOGS/myproject/20261007_release.md`，内容一行：`2026-10-07 | v1.2 发布 | 交付物见 07_EXPORTS/myproject/`
