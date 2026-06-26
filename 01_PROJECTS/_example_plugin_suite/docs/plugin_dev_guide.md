# 插件开发指南

> 本文档详细说明如何为 ChatBot Suite 开发新插件。

---

## 目录

1. [插件接口说明](#1-插件接口说明)
2. [事件总线使用方法](#2-事件总线使用方法)
3. [配置文件格式](#3-配置文件格式)
4. [最小插件示例](#4-最小插件示例)
5. [完整开发流程](#5-完整开发流程)

---

## 1. 插件接口说明

所有插件必须继承 `PluginBase` 抽象基类（位于 `src/shared/plugin_base.py`），并实现以下四个抽象方法。

### 1.1 PluginBase 类定义

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class PluginBase(ABC):
    def __init__(self, event_bus=None, config=None):
        self.name: str = "base_plugin"      # 子类必须覆盖
        self.event_bus = event_bus           # 共享事件总线
        self.config: Dict[str, Any] = config or {}
```

### 1.2 必须实现的抽象方法

#### `on_message(message) -> Optional[str]`

处理接收到的消息。这是插件的核心入口，框架将每条消息分发给所有已加载的插件。

| 参数 | 类型 | 说明 |
|------|------|------|
| message | Dict[str, Any] | 消息字典，包含 `text`（文本）、`user`（发送者）字段 |
| 返回值 | Optional[str] | 若插件处理了该消息，返回响应字符串；否则返回 None 让其他插件处理 |

#### `on_command(command, args) -> Optional[str]`

处理命令。框架解析出命令后调用此方法。

| 参数 | 类型 | 说明 |
|------|------|------|
| command | str | 命令名称（不含斜杠，如 `"weather"`） |
| args | List[str] | 命令参数列表 |
| 返回值 | Optional[str] | 命令处理结果字符串，若不处理该命令返回 None |

#### `on_load() -> None`

插件加载时触发。子类应在此方法中完成资源初始化、事件注册等工作。

#### `on_unload() -> None`

插件卸载时触发。子类应在此方法中完成资源释放、事件注销等工作。

### 1.3 辅助方法（基类已实现）

| 方法 | 说明 |
|------|------|
| `emit_event(event_name, *args, **kwargs)` | 通过事件总线发送事件 |
| `register_event(event_name, handler)` | 注册事件处理器 |

---

## 2. 事件总线使用方法

事件总线（`EventBus`）是插件间通信的唯一通道。**禁止插件之间直接调用**。

### 2.1 核心方法

| 方法 | 说明 |
|------|------|
| `register(event_name, handler)` | 注册事件处理器 |
| `emit(event_name, *args, **kwargs)` | 触发事件，返回所有处理器返回值列表 |
| `unregister(event_name, handler)` | 注销事件处理器 |

### 2.2 事件命名规范

事件名称采用 `模块.动作` 的点分格式，例如：

| 事件名称 | 触发场景 |
|----------|----------|
| `weather.updated` | 天气数据更新 |
| `account.recorded` | 新增记账记录 |
| `translate.completed` | 翻译完成 |

### 2.3 使用示例

**发送方插件（accounting_bot）：**

```python
def on_command(self, command, args):
    if command == "account" and args and args[0] == "add":
        # 记账逻辑...
        # 通过事件总线通知其他插件
        self.emit_event("account.recorded", amount=amount, desc=desc)
        return "记账成功"
```

**接收方插件（weather_bot）：**

```python
def on_load(self):
    # 注册事件处理器
    self.register_event("account.recorded", self._on_account_recorded)

def _on_account_recorded(self, amount, desc):
    print(f"[WeatherBot] 收到记账通知：{amount} - {desc}")
```

### 2.4 异常隔离

事件总线会捕获单个处理器的异常并打印错误信息，不会影响其他处理器的执行。因此插件无需为自己的事件处理器添加 try/except，但建议在关键业务中自行处理。

---

## 3. 配置文件格式

所有配置文件统一使用 JSON 格式。参考 `config/bot_config.example.json`。

### 3.1 顶层结构

```json
{
  "bot_name": "ChatBot",
  "platform": "terminal",
  "plugins": ["weather_bot", "translator_bot", "accounting_bot"],
  "event_bus": {
    "enabled": true,
    "log_events": false
  }
}
```

### 3.2 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `bot_name` | str | 机器人名称 |
| `platform` | str | 运行平台（terminal/qq/wechat） |
| `plugins` | List[str] | 启用的插件名称列表 |
| `event_bus.enabled` | bool | 是否启用事件总线 |
| `event_bus.log_events` | bool | 是否记录事件日志 |

### 3.3 插件级配置

插件可通过 `config` 参数接收专属配置：

```python
class MyBot(PluginBase):
    def __init__(self, event_bus=None, config=None):
        super().__init__(event_bus, config)
        self.name = "my_bot"
        # 从 config 读取插件配置
        self.api_key = self.config.get("api_key", "")
        self.timeout = self.config.get("timeout", 30)
```

---

## 4. 最小插件示例

以下是一个完整可运行的最小插件示例：

```python
"""问候插件示例。"""

from typing import Any, Dict, List, Optional
from shared.plugin_base import PluginBase, EventBus


class GreetBot(PluginBase):
    """问候插件，演示最小可运行插件结构。"""

    def __init__(self, event_bus: Optional[EventBus] = None, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(event_bus, config)
        self.name = "greet_bot"
        self._greet_count = 0

    def on_load(self) -> None:
        """插件加载时初始化。"""
        print(f"[{self.name}] 插件已加载")
        # 注册事件处理器
        self.register_event("user.joined", self._on_user_joined)

    def on_unload(self) -> None:
        """插件卸载时清理。"""
        print(f"[{self.name}] 插件已卸载，共问候 {self._greet_count} 次")

    def on_message(self, message: Dict[str, Any]) -> Optional[str]:
        """处理消息。"""
        text = message.get("text", "")
        user = message.get("user", "unknown")

        # 处理 /greet 命令
        if text.startswith("/greet"):
            return self.on_command("greet", text.split()[1:])

        # 处理普通问候
        if "你好" in text or "hello" in text.lower():
            self._greet_count += 1
            return f"你好，{user}！我是问候插件。"
        return None

    def on_command(self, command: str, args: List[str]) -> Optional[str]:
        """处理命令。"""
        if command != "greet":
            return None

        target = args[0] if args else "朋友"
        self._greet_count += 1
        return f"你好，{target}！很高兴见到你。"

    def _on_user_joined(self, user: str) -> None:
        """事件处理器：用户加入。"""
        print(f"[{self.name}] 欢迎 {user} 加入聊天！")
```

---

## 5. 完整开发流程

### 5.1 创建插件目录

在 `src/` 下创建新的插件目录：

```
src/my_bot/
├── __init__.py    # 包初始化，导出插件类
├── main.py        # 插件主逻辑
└── README.md      # 插件说明文档
```

### 5.2 实现 __init__.py

```python
"""my_bot 插件包。"""
from .main import MyBot

__all__ = ["MyBot"]
```

### 5.3 实现 main.py

1. 继承 `PluginBase`
2. 实现 4 个抽象方法
3. 在 `on_load` 中注册事件
4. 在 `on_unload` 中注销事件

### 5.4 编写 README.md

每个插件必须有独立的 README.md，包含：
- 功能介绍
- 使用方法
- 命令列表
- 配置说明（如有）

### 5.5 在 AGENTS.md 中登记

在项目根目录的 `AGENTS.md` 的"子项目清单"中添加一行：

```
| my_bot | src/my_bot/ | ACTIVE | 我的插件说明 |
```

### 5.6 测试插件

```python
from shared.plugin_base import EventBus
from my_bot import MyBot

bus = EventBus()
bot = MyBot(event_bus=bus)
bot.on_load()

result = bot.on_message({"text": "/my_command arg1", "user": "test"})
print(result)

bot.on_unload()
```

---

## 附录：常见问题

### Q1：插件间如何共享数据？

通过事件总线传递。一个插件 `emit_event`，另一个插件 `register_event` 接收。禁止直接访问其他插件的内部状态。

### Q2：插件配置从哪里读取？

通过 `config` 参数传入，由框架在加载插件时从配置文件读取并传递。

### Q3：插件抛出异常会怎样？

`on_message` / `on_command` 中的异常会冒泡到框架，由框架捕获并记录日志，不影响其他插件。事件总线中的处理器异常会被自动捕获并打印。
