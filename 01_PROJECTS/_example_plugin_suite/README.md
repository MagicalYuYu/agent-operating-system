# 插件集示例（Example Plugin Suite）

> AOS 项目集标准结构示例 — 聊天机器人插件集（ChatBot Suite）

---

## 项目简介

本项目是一个聊天机器人插件集合示例，用于演示 AOS 项目集（plugin_suite）的标准目录结构与协作模式。项目集由 3 个独立的聊天机器人插件组成，所有插件实现统一的 `PluginBase` 接口，通过 `EventBus` 事件总线进行插件间通信。

本示例面向 AOS 初次使用者，展示：
- 项目集目录结构规范（`src/` 下存放多个子项目）
- 子项目独立目录与共享模块的协作方式
- 统一插件接口与事件总线设计模式
- JSON 配置文件的统一管理

---

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    ChatBot Framework                    │
│  ┌───────────────────────────────────────────────────┐  │
│  │                   EventBus 事件总线                 │  │
│  │   register() / emit() / unregister()              │  │
│  └───────▲───────────────▲───────────────▲───────────┘  │
│          │               │               │              │
│   ┌──────┴──────┐ ┌──────┴──────┐ ┌──────┴──────┐       │
│   │ WeatherBot  │ │TranslatorBot│ │AccountingBot│       │
│   │  天气查询   │ │   翻译      │ │   记账      │       │
│   └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────────────────────────────────────────┘
```

### 插件接口（PluginBase）

所有插件必须继承 `PluginBase` 抽象基类，实现以下方法：

| 方法 | 类型 | 说明 |
|------|------|------|
| `on_message(message)` | 抽象方法 | 处理接收到的消息 |
| `on_command(command, args)` | 抽象方法 | 处理命令 |
| `on_load()` | 抽象方法 | 插件加载时触发 |
| `on_unload()` | 抽象方法 | 插件卸载时触发 |

### 事件总线（EventBus）

插件间通信通过事件总线进行，禁止插件之间直接调用：

| 方法 | 说明 |
|------|------|
| `register(event_name, handler)` | 注册事件处理器 |
| `emit(event_name, *args, **kwargs)` | 触发事件 |
| `unregister(event_name, handler)` | 注销事件处理器 |

---

## 子项目列表

| 子项目名称 | 路径 | 功能 | 命令示例 |
|------------|------|------|----------|
| weather_bot | [src/weather_bot/](src/weather_bot/) | 天气查询 | `/weather 北京` |
| translator_bot | [src/translator_bot/](src/translator_bot/) | 文本翻译 | `/translate en zh hello` |
| accounting_bot | [src/accounting_bot/](src/accounting_bot/) | 个人记账 | `/account add 50 午餐` |

---

## 安装方式

### 环境要求

- Python 3.10+
- 无第三方依赖（仅使用标准库）

### 安装步骤

1. 克隆或复制项目目录到 AOS 工作区：
   ```bash
   # 项目应位于 AOS 的 01_PROJECTS/ 下
   01_PROJECTS/_example_plugin_suite/
   ```

2. 将 `src/` 加入 Python 路径（或在该目录下运行）：
   ```powershell
   # Windows PowerShell
   $env:PYTHONPATH = "$PWD\src;$env:PYTHONPATH"
   ```

3. 复制配置文件并按需修改：
   ```powershell
   Copy-Item config\bot_config.example.json config\bot_config.json
   ```

---

## 使用示例

### 启动单个插件

```python
from weather_bot import WeatherBot
from shared.plugin_base import EventBus

# 创建事件总线
event_bus = EventBus()

# 加载天气插件
weather = WeatherBot(event_bus=event_bus)
weather.on_load()

# 模拟接收消息
result = weather.on_message({"text": "/weather 北京", "user": "user_001"})
print(result)
# 输出：北京 当前天气：晴，温度 25°C，湿度 45%，风力 3 级
```

### 启动多个插件（事件总线协作）

```python
from weather_bot import WeatherBot
from translator_bot import TranslatorBot
from accounting_bot import AccountingBot
from shared.plugin_base import EventBus

# 创建共享事件总线
event_bus = EventBus()

# 加载所有插件
plugins = [
    WeatherBot(event_bus=event_bus),
    TranslatorBot(event_bus=event_bus),
    AccountingBot(event_bus=event_bus),
]
for p in plugins:
    p.on_load()

# 模拟消息分发
messages = [
    {"text": "/weather 上海", "user": "user_001"},
    {"text": "/translate en zh good morning", "user": "user_002"},
    {"text": "/account add 30 咖啡", "user": "user_001"},
]
for msg in messages:
    for p in plugins:
        response = p.on_message(msg)
        if response:
            print(f"[{p.name}] {response}")
            break
```

---

## 目录结构说明

```
_example_plugin_suite/
├── AGENTS.md                          # 项目专属配置（AOS 必需）
├── README.md                          # 项目说明（本文件）
├── STATUS.md                          # 项目状态跟踪（AOS 必需）
├── docs/
│   └── plugin_dev_guide.md            # 插件开发指南
├── config/
│   └── bot_config.example.json       # 配置示例
└── src/
    ├── shared/
    │   └── plugin_base.py             # 插件基类 + 事件总线
    ├── weather_bot/
    │   ├── __init__.py
    │   ├── main.py
    │   └── README.md
    ├── translator_bot/
    │   ├── __init__.py
    │   ├── main.py
    │   └── README.md
    └── accounting_bot/
        ├── __init__.py
        ├── main.py
        └── README.md
```

| 目录 | 职责 |
|------|------|
| `docs/` | 项目文档（开发指南、设计文档） |
| `config/` | 项目配置文件 |
| `src/shared/` | 共享模块（基类、工具） |
| `src/<plugin_name>/` | 各子插件独立目录 |

---

## 开发新插件指南

详细的插件开发流程请参考 [docs/plugin_dev_guide.md](docs/plugin_dev_guide.md)。

### 快速开始

1. 在 `src/` 下创建新的插件目录，例如 `src/my_bot/`
2. 创建 `__init__.py` 导出插件类
3. 创建 `main.py` 实现 `PluginBase` 抽象方法
4. 创建 `README.md` 说明插件功能
5. 在项目根目录的 `AGENTS.md` 子项目清单中登记

### 最小插件示例

```python
from shared.plugin_base import PluginBase, EventBus

class MyBot(PluginBase):
    name = "my_bot"

    def on_load(self):
        print(f"{self.name} 已加载")

    def on_unload(self):
        print(f"{self.name} 已卸载")

    def on_message(self, message):
        # 处理消息逻辑
        return None

    def on_command(self, command, args):
        # 处理命令逻辑
        return None
```

---

## 许可证

本示例项目仅用于演示 AOS 项目集结构，无商业用途限制。

---

## 维护信息

| 字段 | 值 |
|------|-----|
| 创建日期 | 2026-06-25 |
| 维护者 | AOS Framework |
| 最后更新 | 2026-06-25 |
