# LogAnalyzer 详细使用教程

> 本文档提供 LogAnalyzer 日志分析工具的完整使用指南，包含所有命令行参数说明、多种使用场景示例及输出格式说明。

---

## 目录

- [前置准备](#前置准备)
- [命令行参数详解](#命令行参数详解)
- [使用场景示例](#使用场景示例)
- [输出格式说明](#输出格式说明)
- [作为 Python 模块使用](#作为-python-模块使用)
- [常见问题](#常见问题)

---

## 前置准备

### 日志文件格式要求

LogAnalyzer 解析如下标准格式的日志文件：

```
[2026-06-25 10:30:45] [ERROR] Database connection timeout
[2026-06-25 10:31:02] [WARN]  Cache miss ratio exceeds 50%
[2026-06-25 10:31:30] [INFO]  Request processed in 120ms
[2026-06-25 10:32:00] [INFO]  User login successful
[2026-06-25 10:32:15] [ERROR] Failed to parse config file
```

**格式规范**：

| 字段 | 格式 | 说明 |
|------|------|------|
| 时间戳 | `[YYYY-MM-DD HH:MM:SS]` | 方括号包裹的标准日期时间 |
| 级别 | `[INFO]` / `[WARN]` / `[ERROR]` | 不区分大小写 |
| 消息 | 级别后的剩余文本 | 自动去除首尾空白 |

不符合格式的行将被跳过并计入 `skipped` 字段，不影响其他有效行解析。

### 准备示例日志文件

创建一个示例日志文件 `server.log` 用于后续演示：

```
[2026-06-25 09:00:00] [INFO]  Server started on port 8080
[2026-06-25 09:00:01] [INFO]  Loading configuration from config.yaml
[2026-06-25 09:00:02] [WARN]  Cache miss ratio exceeds 50%
[2026-06-25 09:01:30] [ERROR] Database connection timeout
[2026-06-25 09:02:00] [ERROR] Failed to parse config file
[2026-06-25 09:02:30] [INFO]  Request processed in 120ms
[2026-06-25 09:03:00] [ERROR] Database connection timeout
[2026-06-25 09:03:30] [WARN]  Disk space below threshold
[2026-06-25 09:04:00] [ERROR] Authentication failed for user admin
[2026-06-25 09:04:30] [INFO]  Backup completed successfully
```

---

## 命令行参数详解

```
usage: loganalyzer [-h] [--level {INFO,WARN,ERROR}] [--output OUTPUT]
                   [--format {text,json}] [--top TOP]
                   logfile

LogAnalyzer 日志分析工具

positional arguments:
  logfile               待分析的日志文件路径

options:
  -h, --help            显示帮助信息并退出
  --level {INFO,WARN,ERROR}
                        按日志级别过滤（仅统计/展示该级别）
  --output OUTPUT       报告输出文件路径（默认输出到控制台）
  --format {text,json}  报告格式，默认 text
  --top TOP             显示前 N 个高频错误（默认 5）
```

### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `logfile` | 字符串 | 是 | — | 日志文件路径（相对或绝对路径） |
| `--level` | 枚举 | 否 | 全部 | 过滤级别：`INFO` / `WARN` / `ERROR` |
| `--output` | 字符串 | 否 | 控制台 | 报告输出文件路径 |
| `--format` | 枚举 | 否 | `text` | 报告格式：`text` 或 `json` |
| `--top` | 整数 | 否 | `5` | 显示高频错误前 N 条 |

---

## 使用场景示例

### 场景一：基础分析

分析整个日志文件，输出统计摘要：

```bash
loganalyzer server.log
```

**输出示例**：

```
==============================
   LogAnalyzer 分析报告
==============================

日志文件：server.log
解析条目总数：10
跳过无效行：0

【级别统计】
  ERROR :   4 条 (40.00%)
  WARN  :   2 条 (20.00%)
  INFO  :   4 条 (40.00%)

【高频错误 Top 5】
  1. [2 次] Database connection timeout
  2. [1 次] Failed to parse config file
  3. [1 次] Authentication failed for user admin
```

### 场景二：按级别过滤

仅查看 ERROR 级别日志的统计：

```bash
loganalyzer server.log --level ERROR
```

**输出示例**：

```
==============================
   LogAnalyzer 分析报告
==============================

日志文件：server.log
解析条目总数：4
（已按级别过滤：ERROR）

【级别统计】
  ERROR :   4 条 (100.00%)

【高频错误 Top 5】
  1. [2 次] Database connection timeout
  2. [1 次] Failed to parse config file
  3. [1 次] Authentication failed for user admin
```

### 场景三：导出 JSON 报告

将分析结果以 JSON 格式导出到文件：

```bash
loganalyzer server.log --format json --output report.json
```

执行后 `report.json` 内容示例：

```json
{
    "logfile": "server.log",
    "total_entries": 10,
    "skipped_lines": 0,
    "level_stats": {
        "ERROR": 4,
        "WARN": 2,
        "INFO": 4
    },
    "level_percentages": {
        "ERROR": 40.0,
        "WARN": 20.0,
        "INFO": 40.0
    },
    "top_errors": [
        {"count": 2, "message": "Database connection timeout"},
        {"count": 1, "message": "Failed to parse config file"},
        {"count": 1, "message": "Authentication failed for user admin"}
    ]
}
```

### 场景四：查看高频错误 Top 10

```bash
loganalyzer server.log --top 10
```

### 场景五：组合使用

按 WARN 级别过滤 + JSON 格式 + 导出文件 + Top 20：

```bash
loganalyzer server.log --level WARN --format json --output warn_report.json --top 20
```

### 场景六：直接通过模块运行（未安装时）

```bash
cd src
python -m loganalyzer ../server.log --format json
```

---

## 输出格式说明

### 文本报告（text）

文本报告采用分节式布局，便于人工阅读：

- **头部**：分隔线 + 报告标题
- **概览**：日志文件名、解析条目数、跳过行数
- **级别统计**：各级别条目数与百分比
- **高频错误**：按出现次数降序排列的错误消息列表

### JSON 报告（json）

JSON 报告采用结构化字段，便于程序化处理：

| 字段 | 类型 | 说明 |
|------|------|------|
| `logfile` | string | 日志文件路径 |
| `total_entries` | int | 解析的有效条目总数 |
| `skipped_lines` | int | 跳过的无效行数 |
| `level_stats` | object | 各级别条目数字典 |
| `level_percentages` | object | 各级别百分比字典 |
| `top_errors` | array | 高频错误列表，每项含 `count` 与 `message` |

---

## 作为 Python 模块使用

LogAnalyzer 的各个模块也可独立调用，嵌入到其他 Python 脚本中：

```python
from loganalyzer.parser import LogParser
from loganalyzer.filters import LogFilter
from loganalyzer.reporter import Reporter

# 解析日志文件
parser = LogParser()
entries = parser.parse_file("server.log")

# 按级别过滤
error_entries = LogFilter.by_level(entries, "ERROR")

# 按关键词过滤
timeout_entries = LogFilter.by_keyword(entries, "timeout")

# 生成报告
reporter = Reporter()
text_report = reporter.generate_text_report({
    "logfile": "server.log",
    "entries": entries,
    "skipped": 0,
})
print(text_report)

# 获取高频错误
top_errors = reporter.get_top_errors(entries, n=5)
for item in top_errors:
    print(f"{item['count']} 次 - {item['message']}")
```

### LogEntry 对象属性

`LogParser.parse_line` 与 `parse_file` 返回的 `LogEntry` 对象包含以下属性：

| 属性 | 类型 | 说明 |
|------|------|------|
| `timestamp` | `datetime` | 日志时间戳 |
| `level` | `str` | 日志级别（大写） |
| `message` | `str` | 日志消息内容 |

---

## 常见问题

### Q1：日志文件中的非标准格式行如何处理？

不符合 `[YYYY-MM-DD HH:MM:SS] [LEVEL] message` 格式的行会被跳过，并计入报告中的 `skipped` / `skipped_lines` 字段，不会导致程序报错。

### Q2：日志级别是否区分大小写？

不区分。`[error]`、`[Error]`、`[ERROR]` 均会被识别为 `ERROR` 级别，统一转为大写存储。

### Q3：`--top` 参数为 0 会怎样？

`--top 0` 表示不显示高频错误部分，报告中会省略【高频错误】一节。

### Q4：输出文件已存在会覆盖吗？

会。`--output` 指定的文件若已存在将被覆盖，请提前备份重要文件。
