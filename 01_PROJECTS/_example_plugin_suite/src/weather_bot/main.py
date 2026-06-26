"""WeatherBot 天气查询插件。

本插件演示如何实现一个完整的聊天机器人插件：
- 继承 PluginBase 抽象基类
- 通过事件总线与其他插件通信
- 使用预设的模拟天气数据（不调用真实 API）

支持的命令：
    /weather [城市]        查询指定城市的天气
    /weather list          列出所有支持查询的城市
"""

from typing import Any, Dict, List, Optional

from shared.plugin_base import EventBus, PluginBase


# 预设的城市天气模拟数据
# 实际项目中应替换为真实天气 API 调用
_MOCK_WEATHER_DATA: Dict[str, Dict[str, Any]] = {
    "北京": {
        "condition": "晴",
        "temperature": 25,
        "humidity": 45,
        "wind": 3,
        "aqi": 60,
    },
    "上海": {
        "condition": "多云",
        "temperature": 28,
        "humidity": 70,
        "wind": 2,
        "aqi": 55,
    },
    "广州": {
        "condition": "雷阵雨",
        "temperature": 31,
        "humidity": 85,
        "wind": 4,
        "aqi": 48,
    },
    "深圳": {
        "condition": "阵雨",
        "temperature": 30,
        "humidity": 80,
        "wind": 3,
        "aqi": 42,
    },
    "成都": {
        "condition": "阴",
        "temperature": 24,
        "humidity": 75,
        "wind": 1,
        "aqi": 88,
    },
    "杭州": {
        "condition": "晴转多云",
        "temperature": 27,
        "humidity": 65,
        "wind": 2,
        "aqi": 50,
    },
    "武汉": {
        "condition": "晴",
        "temperature": 29,
        "humidity": 60,
        "wind": 2,
        "aqi": 70,
    },
    "西安": {
        "condition": "多云",
        "temperature": 26,
        "humidity": 50,
        "wind": 3,
        "aqi": 95,
    },
}


class WeatherBot(PluginBase):
    """天气查询插件。

    通过 /weather 命令查询指定城市的天气信息。
    数据来源为预设的模拟数据，演示插件接口与事件总线用法。
    """

    def __init__(self, event_bus: Optional[EventBus] = None, config: Optional[Dict[str, Any]] = None) -> None:
        """初始化天气查询插件。

        参数：
            event_bus: 共享事件总线实例
            config: 插件配置，支持以下字段：
                - default_city: 默认城市，未指定城市时使用
                - data_source: 数据来源标识（仅用于日志）
                - units: 温度单位（metric/imperial），目前仅用于显示
        """
        super().__init__(event_bus, config)
        self.name = "weather_bot"
        # 默认城市，当用户未指定城市时使用
        self._default_city: str = self.config.get("default_city", "北京")
        # 数据来源标识
        self._data_source: str = self.config.get("data_source", "mock")
        # 温度单位
        self._units: str = self.config.get("units", "metric")

    def on_load(self) -> None:
        """插件加载时触发。

        注册事件处理器，便于其他插件监听天气查询事件。
        """
        print(f"[{self.name}] 天气查询插件已加载（数据来源：{self._data_source}）")
        # 注册事件：当其他插件需要天气数据时可通过此事件获取
        self.register_event("weather.query", self._handle_weather_query)

    def on_unload(self) -> None:
        """插件卸载时触发。

        注销事件处理器，释放资源。
        """
        print(f"[{self.name}] 天气查询插件已卸载")
        if self.event_bus is not None:
            self.event_bus.unregister("weather.query", self._handle_weather_query)

    def on_message(self, message: Dict[str, Any]) -> Optional[str]:
        """处理接收到的消息。

        解析消息文本，若为 /weather 命令则交由 on_command 处理。
        """
        text: str = message.get("text", "").strip()
        if not text.startswith("/weather"):
            return None

        # 解析命令与参数
        parts: List[str] = text.split()
        # parts[0] = "/weather"
        args = parts[1:]
        return self.on_command("weather", args)

    def on_command(self, command: str, args: List[str]) -> Optional[str]:
        """处理 /weather 命令。

        支持的子命令：
            /weather [城市]    查询城市天气
            /weather list      列出所有支持的城市
            /weather           使用默认城市查询
        """
        if command != "weather":
            return None

        # 无参数：使用默认城市
        if not args:
            return self._query_weather(self._default_city)

        # /weather list：列出支持的城市
        if args[0].lower() == "list":
            return self._list_supported_cities()

        # /weather [城市]：查询指定城市
        # 用空格拼接参数，支持城市名带空格的情况（如 "New York"）
        city = " ".join(args)
        return self._query_weather(city)

    def _query_weather(self, city: str) -> str:
        """查询指定城市的天气。

        参数：
            city: 城市名称

        返回：
            格式化的天气信息字符串
        """
        city = city.strip()
        if not city:
            return "请提供城市名称，用法：/weather [城市]"

        # 查询模拟数据
        data = _MOCK_WEATHER_DATA.get(city)
        if data is None:
            supported = "、".join(_MOCK_WEATHER_DATA.keys())
            return f"暂不支持查询「{city}」的天气。\n目前支持的城市：{supported}"

        # 格式化天气信息
        temp = data["temperature"]
        # 温度单位转换（仅显示，不影响逻辑）
        temp_display = f"{temp}°C" if self._units == "metric" else f"{int(temp * 9 / 5 + 32)}°F"

        result = (
            f"{city} 当前天气：{data['condition']}，"
            f"温度 {temp_display}，"
            f"湿度 {data['humidity']}%，"
            f"风力 {data['wind']} 级，"
            f"空气质量指数 {data['aqi']}"
        )

        # 通过事件总线通知其他插件天气已查询
        self.emit_event(
            "weather.updated",
            city=city,
            condition=data["condition"],
            temperature=temp,
        )

        return result

    def _list_supported_cities(self) -> str:
        """列出所有支持查询的城市。"""
        cities = list(_MOCK_WEATHER_DATA.keys())
        header = f"共支持 {len(cities)} 个城市："
        body = "\n".join(f"  - {name}" for name in cities)
        return f"{header}\n{body}"

    def _handle_weather_query(self, city: str) -> Dict[str, Any]:
        """事件处理器：响应 weather.query 事件。

        供其他插件通过事件总线获取天气数据。

        参数：
            city: 城市名称

        返回：
            天气数据字典，若城市不存在返回空字典
        """
        data = _MOCK_WEATHER_DATA.get(city)
        if data is None:
            return {}
        return {"city": city, **data}
