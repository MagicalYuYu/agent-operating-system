# 05_CACHE — Agent 中间产物垃圾场

存放 agent 工作过程中的临时/可再生文件，一切内容都应视为**随时可删**。约束：

1. 唯一副本禁入（备份去 99_ARCHIVE 或异地）
2. 两级分层：`{project|quicktask}/{YYYYMMDD}/`
3. mtime>90 天的条目由巡检（inspection skill）出清理清单，用户确认后清理
4. 禁止任何长期引用指向此目录

示例：`05_CACHE/myproject/20261007/tmp_scan.json`（当天中间产物，次日可再生）
