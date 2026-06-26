# LogAnalyzer — 日志分析命令行工具

> 一个轻量级、零依赖的 Python 命令行日志分析工具，用于统计服务器日志中的错误、警告、信息级别出现次数，支持过滤与多格式报告导出。

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-zero-success.svg)](#)

---

## 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [安装方式](#安装方式)
- [使用示例](#使用示例)
- [目录结构说明](#目录结构说明)
- [开发指南](#开发指南)

---

## 项目简介

LogAnalyzer 是一个面向运维与开发人员的命令行日志分析工具。它能够快速解析标准格式的时间戳日志文件，按日志级别（INFO / WARN / ERROR）进行统计，并支持关键词过滤、时间范围筛选以及高频错误排序。工具采用 Python 标准库实现，**零外部依赖**，开箱即用。

### 适用场景

- 服务器运行日志的日常巡检
- 故障排查时快速定位高频错误
- 生成可归档的日志统计报告（文本 / JSON）
- CI/CD 流水线中的日志质量检测

---

## 功能特性

| 功能 | 说明 |
|------|------|
| 级别统计 | 自动统计 INFO / WARN / ERROR 各级别出现次数与占比 |
| 级别过滤 | 按 `--level` 参数筛选指定级别的日志条目 |
| 关键词过滤 | 内置 `LogFilter.by_keyword` 方法，支持消息内容匹配 |
| 时间范围筛选 | 支持按起止时间过滤日志区间 |
| 高频错误排序 | `--top N` 输出出现频次最高的 N 条错误信息 |
| 多格式报告 | 支持文本报告（`--format text`）与 JSON 报告（`--format json`） |
| 文件输出 | `--output` 参数可将报告写入文件，默认输出到控制台 |
| 零依赖 | 仅使用 Python 标准库，无需 pip 安装第三方包 |

---

## 安装方式

### 方式一：开发模式安装（推荐）

适用于希望直接使用 `loganalyzer` 命令的开发者：

```bash
cd src
pip install -e .
```

安装后即可在任意位置调用：

```bash
loganalyzer /var/log/server.log
```

### 方式二：直接运行（无需安装）

无需安装，直接通过 Python 模块方式运行：

```bash
cd src
python -m loganalyzer /var/log/server.log
```

### 环境要求

- Python 3.10 及以上版本
- 无需任何第三方依赖

---

## 使用示例

### 基础用法：分析整个日志文件

```bash
loganalyzer /var/log/server.log
```

输出示例：

```
==============================
   LogAnalyzer 分析报告
==============================

日志文件：server.log
解析条目总数：1520

【级别统计】
  ERROR :   42 条 ( 2.76%)
  WARN  :  158 条 (10.39%)
  INFO  : 1320 条 (86.84%)

【高频错误 Top 5】
  1. [42 次] Database connection timeout
  2. [18 次] Failed to parse config file
  3. [ 9 次] Authentication failed for user admin
  4. [ 6 次] Disk space below threshold
  5. [ 3 次] Scheduled task crashed
```

### 按级别过滤

仅查看 ERROR 级别日志：

```bash
loganalyzer /var/log/server.log --level ERROR
```

### 导出 JSON 报告到文件

```bash
loganalyzer /var/log/server.log --format json --output report.json
```

### 显示高频错误 Top 10

```bash
loganalyzer /var/log/server.log --top 10
```

### 组合使用：筛选 + 导出

```bash
loganalyzer /var/log/server.log --level WARN --format json --output warn_report.json --top 20
```

---

## 目录结构说明

```
_example_cli_tool/
├── AGENTS.md                       # 项目专属配置（AOS 管理）
├── README.md                       # 项目说明文档（本文件）
├── STATUS.md                       # 项目状态跟踪
├── docs/
│   └── usage.md                    # 详细使用教程
└── src/
    ├── setup.py                    # 分发配置（setuptools）
    ├── loganalyzer/                # 核心源码包
    │   ├── __init__.py             # 包信息与版本声明
    │   ├── __main__.py             # 命令行入口（argparse）
    │   ├── parser.py               # 日志解析器 LogParser
    │   ├── filters.py              # 过滤规则 LogFilter
    │   └── reporter.py             # 报告生成器 Reporter
    └── tests/
        └── test_parser.py          # 单元测试（unittest）
```

### 模块职责

| 模块 | 职责 |
|------|------|
| `__main__.py` | 解析命令行参数，编排解析→过滤→报告流程 |
| `parser.py` | 解析日志行与日志文件，返回 `LogEntry` 对象 |
| `filters.py` | 提供按级别、关键词、时间范围的过滤方法 |
| `reporter.py` | 生成文本/JSON 报告，统计高频错误 |

---

## 开发指南

### 运行单元测试

```bash
cd src
python -m unittest discover tests
```

### 支持的日志格式

工具解析如下标准格式日志：

```
[2026-06-25 10:30:45] [ERROR] Database connection timeout
[2026-06-25 10:31:02] [WARN]  Cache miss ratio exceeds 50%
[2026-06-25 10:31:30] [INFO]  Request processed in 120ms
```

格式规范：

- 时间戳：`[YYYY-MM-DD HH:MM:SS]`
- 级别：`[INFO]` / `[WARN]` / `[ERROR]`（不区分大小写）
- 消息：级别后的剩余文本，自动去除首尾空白

### 扩展建议

- 新增日志级别：在 `parser.py` 的 `LEVEL_PATTERN` 中扩展正则
- 新增报告格式：在 `reporter.py` 中实现新的 `generate_*_report` 方法
- 新增过滤维度：在 `filters.py` 中添加对应的 `by_*` 静态方法

### 代码规范

- 遵循 [PEP 8](https://peps.python.org/pep-0008/) 编码规范
- 所有公共函数与类必须包含 docstring
- 使用 4 空格缩进，行宽不超过 100 字符

---

## 许可证

MIT License — 本项目为 AOS 示例项目，可自由学习与引用。
