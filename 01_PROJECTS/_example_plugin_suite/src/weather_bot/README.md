# WeatherBot 天气查询插件

> 聊天机器人插件集 — 天气查询子插件

---

## 功能介绍

WeatherBot 提供城市天气查询功能，用户通过 `/weather` 命令查询指定城市的当前天气信息。

本插件使用预设的模拟天气数据（不调用真实 API），用于演示 AOS 项目集中插件的完整开发流程，包括：
- 继承 `PluginBase` 抽象基类
- 通过 `EventBus` 与其他插件通信
- 命令解析与参数处理
- 配置项读取

---

## 使用方法

### 1. 直接调用

```python
from weather_bot import WeatherBot
from shared.plugin_base import EventBus

bus = EventBus()
weather = WeatherBot(event_bus=bus)
weather.on_load()

# 查询天气
result = weather.on_message({"text": "/weather 北京", "user": "user_001"})
print(result)
# 输出：北京 当前天气：晴，温度 25°C，湿度 45%，风力 3 级，空气质量指数 60
```

### 2. 通过事件总线查询

其他插件可通过 `weather.query` 事件获取天气数据：

```python
# 在其他插件中
data = self.event_bus.emit("weather.query", city="北京")
# data = [{"city": "北京", "condition": "晴", "temperature": 25, ...}]
```

---

## 命令列表

| 命令 | 说明 | 示例 |
|------|------|------|
| `/weather [城市]` | 查询指定城市的天气 | `/weather 上海` |
| `/weather list` | 列出所有支持查询的城市 | `/weather list` |
| `/weather` | 使用默认城市查询（默认：北京） | `/weather` |

### 命令输出示例

```
> /weather 北京
北京 当前天气：晴，温度 25°C，湿度 45%，风力 3 级，空气质量指数 60

> /weather list
共支持 8 个城市：
  - 北京
  - 上海
  - 广州
  - 深圳
  - 成都
  - 杭州
  - 武汉
  - 西安

> /weather 巴黎
暂不支持查询「巴黎」的天气。
目前支持的城市：北京、上海、广州、深圳、成都、杭州、武汉、西安
```

---

## 配置说明

在 `config/bot_config.example.json` 的 `plugin_configs.weather_bot` 节点中配置：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `default_city` | str | "北京" | 默认查询城市 |
| `data_source` | str | "mock" | 数据来源标识（仅用于日志） |
| `units` | str | "metric" | 温度单位（metric=摄氏，imperial=华氏） |

示例配置：

```json
{
  "default_city": "上海",
  "data_source": "mock",
  "units": "metric"
}
```

---

## 事件

### 发送的事件

| 事件名称 | 触发时机 | 参数 |
|----------|----------|------|
| `weather.updated` | 天气查询成功后 | `city`, `condition`, `temperature` |

### 监听的事件

| 事件名称 | 用途 |
|----------|------|
| `weather.query` | 响应其他插件的天气数据请求，返回天气字典 |

---

## 文件结构

```
weather_bot/
├── __init__.py    # 包初始化，导出 WeatherBot
├── main.py        # WeatherBot 类实现
└── README.md      # 本文件
```
