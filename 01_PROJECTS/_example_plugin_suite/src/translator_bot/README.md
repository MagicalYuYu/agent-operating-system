# TranslatorBot 翻译插件

> 聊天机器人插件集 — 文本翻译子插件

---

## 功能介绍

TranslatorBot 提供文本翻译功能，支持中、英、日三种语言的互译。本插件使用内置词典进行词级替换，**仅用于演示翻译插件的概念**，并非生产级翻译引擎。

本插件演示：
- 继承 `PluginBase` 抽象基类
- 命令参数解析与多种调用模式
- 词典最长匹配策略
- 翻译结果缓存
- 通过 `EventBus` 提供翻译服务

---

## 使用方法

### 1. 直接调用

```python
from translator_bot import TranslatorBot
from shared.plugin_base import EventBus

bus = EventBus()
translator = TranslatorBot(event_bus=bus)
translator.on_load()

# 翻译文本
result = translator.on_message({"text": "/translate en zh hello", "user": "user_001"})
print(result)
# 输出：en->zh：hello = 你好
```

### 2. 通过事件总线调用

其他插件可通过 `translate.request` 事件请求翻译：

```python
# 在其他插件中
results = self.event_bus.emit("translate.request", source_lang="en", target_lang="zh", text="hello")
# results = ["你好"]
```

---

## 命令列表

| 命令 | 说明 | 示例 |
|------|------|------|
| `/translate [源语言] [目标语言] [文本]` | 指定语言方向翻译 | `/translate en zh good morning` |
| `/translate [文本]` | 自动检测源语言，翻译为默认目标语言 | `/translate hello world` |
| `/translate langs` | 列出所有支持的翻译语言对 | `/translate langs` |

### 命令输出示例

```
> /translate en zh hello world
en->zh：hello world = 你好世界

> /translate zh->en 你好
zh->en：你好 = hello

> /translate hello
en->zh：hello = 你好

> /translate langs
共支持 4 个翻译方向：
  - English(en) -> 中文(zh)，27 个词条
  - 中文(zh) -> English(en)，23 个词条
  - 中文(zh) -> 日本語(ja)，8 个词条
  - English(en) -> 日本語(ja)，7 个词条
```

---

## 支持的语言对

| 源语言 | 目标语言 | 词条数 |
|--------|----------|--------|
| English (en) | 中文 (zh) | 27 |
| 中文 (zh) | English (en) | 23 |
| 中文 (zh) | 日本語 (ja) | 8 |
| English (en) | 日本語 (ja) | 7 |

### 语言代码

| 代码 | 语言名称 |
|------|----------|
| `en` | English |
| `zh` | 中文 |
| `ja` | 日本語 |
| `auto` | 自动检测（仅作源语言） |

---

## 配置说明

在 `config/bot_config.example.json` 的 `plugin_configs.translator_bot` 节点中配置：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `default_source_lang` | str | "auto" | 默认源语言（auto 表示自动检测） |
| `default_target_lang` | str | "zh" | 默认目标语言 |
| `cache_enabled` | bool | true | 是否启用翻译缓存 |

示例配置：

```json
{
  "default_source_lang": "auto",
  "default_target_lang": "zh",
  "cache_enabled": true
}
```

---

## 事件

### 发送的事件

| 事件名称 | 触发时机 | 参数 |
|----------|----------|------|
| `translate.completed` | 翻译完成后 | `source_lang`, `target_lang`, `original`, `translated` |

### 监听的事件

| 事件名称 | 用途 |
|----------|------|
| `translate.request` | 响应其他插件的翻译请求，返回译文 |

---

## 翻译原理

本插件采用**词典词级替换 + 最长匹配**策略：

1. **词典查找**：根据源/目标语言选择对应词典
2. **最长匹配**：按词条长度降序排列，优先匹配长词组（避免 "good" 干扰 "good morning"）
3. **逐词替换**：将原文中匹配到的词条替换为译文
4. **结果缓存**：相同输入直接返回缓存结果

> ⚠ 本翻译方法仅适用于演示。生产环境请使用专业翻译 API（如 Google Translate、DeepL）。

---

## 文件结构

```
translator_bot/
├── __init__.py    # 包初始化，导出 TranslatorBot
├── main.py        # TranslatorBot 类实现
└── README.md      # 本文件
```
