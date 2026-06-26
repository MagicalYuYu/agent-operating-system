# AccountingBot 记账插件

> 聊天机器人插件集 — 个人记账子插件

---

## 功能介绍

AccountingBot 提供个人记账功能，支持新增支出记录、查看记录列表、汇总统计、清空记录。所有账目数据持久化到 JSON 文件中，重启后不丢失。

本插件演示：
- 继承 `PluginBase` 抽象基类
- JSON 文件持久化存储
- 多子命令解析与分发
- 通过 `EventBus` 与其他插件通信
- 数据加载与保存的生命周期管理

---

## 使用方法

### 1. 直接调用

```python
from accounting_bot import AccountingBot
from shared.plugin_base import EventBus

bus = EventBus()
accounting = AccountingBot(event_bus=bus)
accounting.on_load()

# 新增记录
accounting.on_message({"text": "/account add 50 午餐", "user": "user_001"})
accounting.on_message({"text": "/account add 12.5 咖啡", "user": "user_001"})

# 查看列表
print(accounting.on_message({"text": "/account list", "user": "user_001"}))

# 汇总统计
print(accounting.on_message({"text": "/account summary", "user": "user_001"}))
```

### 2. 通过事件总线获取统计

其他插件可通过 `account.summary` 事件获取账目统计：

```python
# 在其他插件中
results = self.event_bus.emit("account.summary")
# results = [{"count": 5, "total": 187.5, "currency": "CNY"}]
```

---

## 命令列表

| 命令 | 说明 | 示例 |
|------|------|------|
| `/account add [金额] [描述]` | 新增一笔支出记录 | `/account add 50 午餐` |
| `/account list` | 列出所有账目记录 | `/account list` |
| `/account summary` | 汇总账目统计信息 | `/account summary` |
| `/account clear` | 清空所有账目记录 | `/account clear` |
| `/account help` | 显示帮助信息 | `/account help` |

### 命令输出示例

```
> /account add 50 午餐
记账成功 [#1]：CNY 50.00 - 午餐

> /account add 12.5 咖啡
记账成功 [#2]：CNY 12.50 - 咖啡

> /account list
共 2 条账目记录：
   ID        金额  时间                  描述
------------------------------------------------------------
  #1     CNY 50.00  2026-06-25 14:30:00  午餐
  #2     CNY 12.50  2026-06-25 15:45:00  咖啡

> /account summary
═══ 账目汇总 ═══
记录总数：2 条
总支出：CNY 62.50
平均每笔：CNY 31.25
最大单笔：CNY 50.00 - 午餐
最小单笔：CNY 12.50 - 咖啡

─── 按日期统计 ───
  2026-06-25：CNY 62.50
```

---

## 数据存储说明

### 存储格式

账目数据保存为 JSON 文件，默认路径为 `src/accounting_bot/accounting_data.json`。

文件结构示例：

```json
{
  "currency": "CNY",
  "count": 2,
  "records": [
    {
      "id": 1,
      "amount": 50.0,
      "description": "午餐",
      "currency": "CNY",
      "timestamp": "2026-06-25 14:30:00"
    },
    {
      "id": 2,
      "amount": 12.5,
      "description": "咖啡",
      "currency": "CNY",
      "timestamp": "2026-06-25 15:45:00"
    }
  ]
}
```

### 记录字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 记录唯一 ID，自增 |
| `amount` | float | 金额 |
| `description` | str | 描述 |
| `currency` | str | 货币单位 |
| `timestamp` | str | 记录时间（YYYY-MM-DD HH:MM:SS） |

### 生命周期

| 时机 | 行为 |
|------|------|
| `on_load` | 从 JSON 文件加载历史记录到内存 |
| `on_unload` | 将内存中的记录保存到 JSON 文件 |
| 每次新增记录 | 立即保存到文件（防止数据丢失） |

---

## 配置说明

在 `config/bot_config.example.json` 的 `plugin_configs.accounting_bot` 节点中配置：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `data_file` | str | "accounting_data.json" | 数据存储文件名 |
| `currency` | str | "CNY" | 货币单位 |
| `max_records` | int | 10000 | 最大记录数 |

示例配置：

```json
{
  "data_file": "accounting_data.json",
  "currency": "CNY",
  "max_records": 10000
}
```

---

## 事件

### 发送的事件

| 事件名称 | 触发时机 | 参数 |
|----------|----------|------|
| `account.recorded` | 新增记账记录后 | `amount`, `desc`, `record_id` |

### 监听的事件

| 事件名称 | 用途 |
|----------|------|
| `account.summary` | 响应其他插件的统计请求，返回统计字典 |

---

## 文件结构

```
accounting_bot/
├── __init__.py                # 包初始化，导出 AccountingBot
├── main.py                    # AccountingBot 类实现
├── README.md                  # 本文件
└── accounting_data.json       # 运行时自动生成的数据文件
```

> ⚠ `accounting_data.json` 在首次运行插件时自动生成，不属于代码文件，可在 `.gitignore` 中排除。
