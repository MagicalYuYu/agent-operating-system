"""插件基类与事件总线模块。

本模块定义了聊天机器人插件集的统一接口：
- PluginBase：所有插件必须继承的抽象基类
- EventBus：插件间通信的事件总线

设计原则：
1. 插件间禁止直接调用，必须通过 EventBus 通信
2. 所有插件实现统一的接口，便于框架统一管理
3. 抽象方法强制子类实现，保证接口完整性
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional


class PluginBase(ABC):
    """插件抽象基类。

    所有聊天机器人插件必须继承此类，并实现以下抽象方法：
    - on_message：处理接收到的消息
    - on_command：处理命令
    - on_load：插件加载时触发
    - on_unload：插件卸载时触发

    属性：
        name: 插件名称，子类必须覆盖
        event_bus: 共享的事件总线实例，用于插件间通信
        config: 插件配置字典
    """

    def __init__(self, event_bus: Optional["EventBus"] = None, config: Optional[Dict[str, Any]] = None) -> None:
        """初始化插件实例。

        参数：
            event_bus: 共享的事件总线实例。若未提供则插件无法与其他插件通信。
            config: 插件配置字典，可选
        """
        self.name: str = "base_plugin"
        self.event_bus: Optional[EventBus] = event_bus
        self.config: Dict[str, Any] = config or {}

    @abstractmethod
    def on_message(self, message: Dict[str, Any]) -> Optional[str]:
        """处理接收到的消息。

        参数：
            message: 消息字典，至少包含以下字段：
                - text: 消息文本内容
                - user: 发送者标识

        返回：
            若插件处理了该消息，返回响应字符串；否则返回 None
        """
        raise NotImplementedError("子类必须实现 on_message 方法")

    @abstractmethod
    def on_command(self, command: str, args: List[str]) -> Optional[str]:
        """处理命令。

        参数：
            command: 命令名称（不含斜杠，如 "weather"）
            args: 命令参数列表

        返回：
            命令处理结果字符串，若不处理该命令返回 None
        """
        raise NotImplementedError("子类必须实现 on_command 方法")

    @abstractmethod
    def on_load(self) -> None:
        """插件加载时触发。

        子类应在此方法中完成资源初始化、事件注册等工作。
        """
        raise NotImplementedError("子类必须实现 on_load 方法")

    @abstractmethod
    def on_unload(self) -> None:
        """插件卸载时触发。

        子类应在此方法中完成资源释放、事件注销等工作。
        """
        raise NotImplementedError("子类必须实现 on_unload 方法")

    def emit_event(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        """通过事件总线发送事件。

        参数：
            event_name: 事件名称
            *args: 位置参数
            **kwargs: 关键字参数
        """
        if self.event_bus is not None:
            self.event_bus.emit(event_name, *args, **kwargs)

    def register_event(self, event_name: str, handler: Callable[..., Any]) -> None:
        """注册事件处理器。

        参数：
            event_name: 事件名称
            handler: 事件处理函数
        """
        if self.event_bus is not None:
            self.event_bus.register(event_name, handler)


class EventBus:
    """事件总线，用于插件间通信。

    设计原则：
    - 插件间禁止直接调用，必须通过事件总线通信
    - 支持一个事件对应多个处理器，按注册顺序触发
    - 处理器异常不影响其他处理器执行

    用法示例：
        bus = EventBus()
        bus.register("weather.updated", on_weather_updated)
        bus.emit("weather.updated", city="北京", temp=25)
    """

    def __init__(self) -> None:
        """初始化事件总线。"""
        # 事件处理器映射表：{事件名: [处理器函数列表]}
        self._handlers: Dict[str, List[Callable[..., Any]]] = {}

    def register(self, event_name: str, handler: Callable[..., Any]) -> None:
        """注册事件处理器。

        参数：
            event_name: 事件名称
            handler: 事件处理函数

        说明：
            同一事件可注册多个处理器，按注册顺序触发。
            同一处理器重复注册会被忽略。
        """
        if not isinstance(event_name, str) or not event_name:
            raise ValueError("事件名称必须为非空字符串")
        if not callable(handler):
            raise TypeError("事件处理器必须为可调用对象")

        if event_name not in self._handlers:
            self._handlers[event_name] = []

        # 避免重复注册同一处理器
        if handler not in self._handlers[event_name]:
            self._handlers[event_name].append(handler)

    def unregister(self, event_name: str, handler: Callable[..., Any]) -> bool:
        """注销事件处理器。

        参数：
            event_name: 事件名称
            handler: 要注销的处理函数

        返回：
            注销成功返回 True，未找到返回 False
        """
        if event_name not in self._handlers:
            return False

        if handler in self._handlers[event_name]:
            self._handlers[event_name].remove(handler)
            # 若该事件已无处理器，清理空列表
            if not self._handlers[event_name]:
                del self._handlers[event_name]
            return True
        return False

    def emit(self, event_name: str, *args: Any, **kwargs: Any) -> List[Any]:
        """触发事件。

        参数：
            event_name: 事件名称
            *args: 位置参数，传递给处理器
            **kwargs: 关键字参数，传递给处理器

        返回：
            所有处理器返回值的列表（按注册顺序）

        说明：
            单个处理器异常会被捕获并打印错误信息，不影响其他处理器执行。
        """
        if event_name not in self._handlers:
            return []

        results: List[Any] = []
        for handler in self._handlers[event_name]:
            try:
                result = handler(*args, **kwargs)
                results.append(result)
            except Exception as exc:  # noqa: BLE001
                # 捕获异常打印，不影响其他处理器
                print(f"[EventBus] 事件 '{event_name}' 处理器 '{getattr(handler, '__name__', repr(handler))}' 异常: {exc}")
        return results

    def clear(self) -> None:
        """清空所有事件处理器。"""
        self._handlers.clear()

    def list_events(self) -> List[str]:
        """列出所有已注册的事件名称。

        返回：
            事件名称列表
        """
        return list(self._handlers.keys())

    def handler_count(self, event_name: str) -> int:
        """获取指定事件的处理器数量。

        参数：
            event_name: 事件名称

        返回：
            处理器数量，事件不存在返回 0
        """
        return len(self._handlers.get(event_name, []))
