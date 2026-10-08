# 07_EXPORTS — 输出导出

一切交付物的**唯一出口**（铁律 2：输出隔离），按项目分层；无项目的轻量任务放 `quicktasks/{YYYYMMDD}_{slug}/`。

根层只允许 README.md 与 release_notes* 文件，其余散放会被 `scripts/check_placement.py` 报违规。

示例：
- `07_EXPORTS/myproject/report_v2.md`（项目交付物）
- `07_EXPORTS/quicktasks/20261007_data-cleanup/`（轻量任务归档）
