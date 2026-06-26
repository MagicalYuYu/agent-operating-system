"""TranslatorBot 翻译插件。

本插件演示如何实现一个文本翻译插件：
- 继承 PluginBase 抽象基类
- 通过事件总线与其他插件通信
- 使用简单的词典替换实现翻译功能（演示概念，非生产级翻译）

支持的命令：
    /translate [源语言] [目标语言] [文本]    翻译指定文本
    /translate langs                        列出支持的语言对
    /translate [文本]                        自动检测并翻译为中文

支持的语言代码：
    en - English
    zh - 中文
    ja - 日本語
"""

from typing import Any, Dict, List, Optional

from shared.plugin_base import EventBus, PluginBase


# 翻译词典：{(源语言, 目标语言): {源词: 目标词}}
# 仅包含少量示例词条，演示翻译概念
_DICTIONARIES: Dict[str, Dict[str, str]] = {
    # 英文 -> 中文
    "en->zh": {
        "hello": "你好",
        "world": "世界",
        "good": "好",
        "morning": "早上",
        "good morning": "早上好",
        "good night": "晚安",
        "thank": "谢谢",
        "thanks": "谢谢",
        "thank you": "谢谢",
        "yes": "是",
        "no": "不",
        "goodbye": "再见",
        "bye": "再见",
        "love": "爱",
        "friend": "朋友",
        "book": "书",
        "water": "水",
        "food": "食物",
        "computer": "电脑",
        "python": "Python",
        "code": "代码",
        "hello world": "你好世界",
        "i love you": "我爱你",
        "how are you": "你好吗",
        "i am fine": "我很好",
        "what is your name": "你叫什么名字",
        "my name is": "我的名字是",
    },
    # 中文 -> 英文
    "zh->en": {
        "你好": "hello",
        "世界": "world",
        "早上好": "good morning",
        "晚安": "good night",
        "谢谢": "thank you",
        "是": "yes",
        "不": "no",
        "再见": "goodbye",
        "爱": "love",
        "朋友": "friend",
        "书": "book",
        "水": "water",
        "食物": "food",
        "电脑": "computer",
        "代码": "code",
        "早上": "morning",
        "好": "good",
        "你好世界": "hello world",
        "我爱你": "i love you",
        "你好吗": "how are you",
        "我很好": "i am fine",
        "你叫什么名字": "what is your name",
        "我的名字是": "my name is",
    },
    # 中文 -> 日文
    "zh->ja": {
        "你好": "こんにちは",
        "谢谢": "ありがとう",
        "再见": "さようなら",
        "早上好": "おはよう",
        "晚安": "おやすみ",
        "爱": "愛",
        "朋友": "友達",
        "你好世界": "こんにちは世界",
    },
    # 英文 -> 日文
    "en->ja": {
        "hello": "こんにちは",
        "thank you": "ありがとう",
        "goodbye": "さようなら",
        "good morning": "おはよう",
        "good night": "おやすみ",
        "love": "愛",
        "friend": "友達",
    },
}

# 支持的语言代码与显示名映射
_LANGUAGE_NAMES: Dict[str, str] = {
    "en": "English",
    "zh": "中文",
    "ja": "日本語",
}


class TranslatorBot(PluginBase):
    """文本翻译插件。

    通过 /translate 命令翻译文本。
    使用内置词典进行词级替换，演示翻译插件的概念。
    """

    def __init__(self, event_bus: Optional[EventBus] = None, config: Optional[Dict[str, Any]] = None) -> None:
        """初始化翻译插件。

        参数：
            event_bus: 共享事件总线实例
            config: 插件配置，支持以下字段：
                - default_source_lang: 默认源语言（auto 表示自动检测）
                - default_target_lang: 默认目标语言
                - cache_enabled: 是否启用翻译缓存
        """
        super().__init__(event_bus, config)
        self.name = "translator_bot"
        self._default_source_lang: str = self.config.get("default_source_lang", "auto")
        self._default_target_lang: str = self.config.get("default_target_lang", "zh")
        self._cache_enabled: bool = self.config.get("cache_enabled", True)
        # 翻译缓存：{(源语言, 目标语言, 原文): 译文}
        self._cache: Dict[tuple, str] = {}

    def on_load(self) -> None:
        """插件加载时触发。

        注册事件处理器，便于其他插件调用翻译功能。
        """
        print(f"[{self.name}] 翻译插件已加载（缓存：{'启用' if self._cache_enabled else '禁用'}）")
        self.register_event("translate.request", self._handle_translate_request)

    def on_unload(self) -> None:
        """插件卸载时触发。

        清空缓存，注销事件处理器。
        """
        print(f"[{self.name}] 翻译插件已卸载（共翻译 {len(self._cache)} 条记录）")
        self._cache.clear()
        if self.event_bus is not None:
            self.event_bus.unregister("translate.request", self._handle_translate_request)

    def on_message(self, message: Dict[str, Any]) -> Optional[str]:
        """处理接收到的消息。

        解析消息文本，若为 /translate 命令则交由 on_command 处理。
        """
        text: str = message.get("text", "").strip()
        if not text.startswith("/translate"):
            return None

        parts: List[str] = text.split(maxsplit=1)
        # parts[0] = "/translate"
        args_str = parts[1] if len(parts) > 1 else ""
        # 将参数按空格拆分
        args = args_str.split() if args_str else []
        return self.on_command("translate", args)

    def on_command(self, command: str, args: List[str]) -> Optional[str]:
        """处理 /translate 命令。

        支持的子命令：
            /translate langs                            列出支持的语言对
            /translate [源语言] [目标语言] [文本]        翻译文本
            /translate [文本]                            自动检测并翻译为默认目标语言
        """
        if command != "translate":
            return None

        # /translate langs：列出支持的语言对
        if args and args[0].lower() == "langs":
            return self._list_supported_languages()

        # 无参数：提示用法
        if not args:
            return self._usage()

        # 判断参数模式
        # 模式1：前两个参数都是语言代码 -> /translate [源] [目标] [文本]
        # 模式2：直接翻译 -> /translate [文本]
        if len(args) >= 3 and self._is_lang_code(args[0]) and self._is_lang_code(args[1]):
            source_lang = args[0]
            target_lang = args[1]
            text_to_translate = " ".join(args[2:])
        else:
            # 默认语言：自动检测源语言，翻译为默认目标语言
            source_lang = self._default_source_lang
            target_lang = self._default_target_lang
            text_to_translate = " ".join(args)

        return self._translate(source_lang, target_lang, text_to_translate)

    def _translate(self, source_lang: str, target_lang: str, text: str) -> str:
        """执行翻译。

        参数：
            source_lang: 源语言代码（auto 表示自动检测）
            target_lang: 目标语言代码
            text: 待翻译文本

        返回：
            翻译结果字符串
        """
        text = text.strip()
        if not text:
            return "请提供待翻译的文本"

        # 自动检测源语言
        if source_lang == "auto":
            source_lang = self._detect_language(text)

        # 检查语言对是否支持
        dict_key = f"{source_lang}->{target_lang}"
        dictionary = _DICTIONARIES.get(dict_key)
        if dictionary is None:
            supported = "、".join(_DICTIONARIES.keys())
            return f"暂不支持 {source_lang} -> {target_lang} 翻译。\n支持的翻译方向：{supported}"

        # 检查缓存
        cache_key = (source_lang, target_lang, text)
        if self._cache_enabled and cache_key in self._cache:
            cached = self._cache[cache_key]
            return f"[缓存] {source_lang}->{target_lang}：{text} = {cached}"

        # 执行翻译（词级替换，按词典长度降序以优先匹配长词组）
        translated = self._do_translate(text, dictionary)

        # 写入缓存
        if self._cache_enabled:
            self._cache[cache_key] = translated

        # 通知其他插件翻译已完成
        self.emit_event(
            "translate.completed",
            source_lang=source_lang,
            target_lang=target_lang,
            original=text,
            translated=translated,
        )

        return f"{source_lang}->{target_lang}：{text} = {translated}"

    def _do_translate(self, text: str, dictionary: Dict[str, str]) -> str:
        """执行实际的词典替换翻译。

        采用最长匹配策略：优先匹配词典中最长的词条，避免短词干扰长词组。

        参数：
            text: 待翻译文本
            dictionary: 词典映射

        返回：
            翻译后的文本
        """
        result = text
        # 按词条长度降序排列，优先匹配长词组
        sorted_entries = sorted(dictionary.items(), key=lambda x: len(x[0]), reverse=True)
        for source_word, target_word in sorted_entries:
            if source_word in result:
                result = result.replace(source_word, target_word)
        return result

    def _detect_language(self, text: str) -> str:
        """简单检测文本语言。

        通过字符范围判断：含中文字符判定为 zh，否则为 en。

        参数：
            text: 待检测文本

        返回：
            语言代码（"zh" 或 "en"）
        """
        for char in text:
            # CJK 统一表意文字范围
            if "\u4e00" <= char <= "\u9fff":
                return "zh"
        return "en"

    def _list_supported_languages(self) -> str:
        """列出所有支持的翻译语言对。"""
        lines = [f"共支持 {len(_DICTIONARIES)} 个翻译方向："]
        for key in _DICTIONARIES.keys():
            source, target = key.split("->")
            source_name = _LANGUAGE_NAMES.get(source, source)
            target_name = _LANGUAGE_NAMES.get(target, target)
            word_count = len(_DICTIONARIES[key])
            lines.append(f"  - {source_name}({source}) -> {target_name}({target})，{word_count} 个词条")
        return "\n".join(lines)

    def _usage(self) -> str:
        """返回使用说明。"""
        return (
            "翻译插件用法：\n"
            "  /translate [源语言] [目标语言] [文本]    翻译指定文本\n"
            "  /translate [文本]                        自动检测并翻译为默认目标语言\n"
            "  /translate langs                        列出支持的语言对\n"
            "示例：\n"
            "  /translate en zh hello\n"
            "  /translate zh->en 你好\n"
            "  /translate hello world"
        )

    @staticmethod
    def _is_lang_code(token: str) -> bool:
        """判断 token 是否为有效的语言代码。

        参数：
            token: 待判断的字符串

        返回：
            是语言代码返回 True，否则返回 False
        """
        return token.lower() in _LANGUAGE_NAMES

    def _handle_translate_request(self, source_lang: str, target_lang: str, text: str) -> str:
        """事件处理器：响应 translate.request 事件。

        供其他插件通过事件总线调用翻译功能。

        参数：
            source_lang: 源语言代码（auto 表示自动检测）
            target_lang: 目标语言代码
            text: 待翻译文本

        返回：
            翻译结果字符串
        """
        return self._translate(source_lang, target_lang, text)
