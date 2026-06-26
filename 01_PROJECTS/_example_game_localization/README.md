# 游戏本地化示例（Game Localization Example）

> AOS 单一项目标准结构示例 — 演示游戏本地化（i18n）项目的目录结构与翻译流程

---

## 项目简介

本项目是一个游戏本地化示例，用于演示 AOS 单一项目（single-project）的标准目录结构，以及游戏本地化工程的典型流程。项目以一个虚构游戏的 UI 文本为例，展示从英文原文到简体中文翻译的完整结构。

本示例面向 AOS 初次使用者，展示：

- AOS 单一项目目录结构规范（`src/` 直接存放代码/资源文件）
- 游戏本地化项目的标准目录组织（`lang/{语言代码}/`）
- JSON 格式的语言文件规范（key-value 键值对）
- 源语言与目标语言的对照管理方式
- 翻译流程的阶段划分与状态跟踪

---

## 功能特性

| 特性 | 说明 |
|------|------|
| 双语言对照 | 英文原文（`lang/en/`）与简体中文翻译（`lang/zh-cn/`）并存 |
| JSON 键值对 | 采用 `key: value` 格式，便于程序加载与维护 |
| 模块化拆分 | 按 UI 模块组织文件（如 `ui.json`、`items.json`、`quests.json`） |
| UTF-8 编码 | 所有翻译文件统一使用 UTF-8 编码，避免乱码 |
| 术语一致性 | 通过术语表约束专有名词的统一翻译 |

---

## 目录结构说明

```
_example_game_localization/
├── AGENTS.md                 # 项目专属配置（AOS 必需）
├── README.md                 # 项目说明文档（本文件）
├── STATUS.md                 # 项目状态跟踪（AOS 必需）
└── lang/                     # 翻译文件目录
    ├── en/                   # 英文原文（源语言）
    │   └── ui.json           # UI 模块文本
    └── zh-cn/                # 简体中文翻译（目标语言）
        └── ui.json           # UI 模块文本（中文）
```

### 目录职责

| 目录/文件 | 职责 |
|-----------|------|
| `lang/` | 所有翻译文件的根目录，按语言代码分目录 |
| `lang/en/` | 源语言（英文）原文，作为翻译基准 |
| `lang/zh-cn/` | 目标语言（简体中文）翻译结果 |
| `*.json` | 语言文件，按模块命名（如 `ui.json`、`items.json`） |

### 为什么采用 `lang/{语言代码}/` 结构？

| 替代方案 | 缺点 | 本方案优势 |
|----------|------|------------|
| `lang/en.json` / `lang/zh-cn.json` | 模块多时文件爆炸，难以对照 | 同模块译文同目录名，对照清晰 |
| `i18n/en/ui.json` / `i18n/zh/ui.json` | 语言代码不统一（en vs zh） | 遵循 BCP 47 语言代码标准 |

---

## 文件格式规范

### JSON 语言文件格式

每个语言文件为标准 JSON，采用 `key: value` 键值对：

```json
{
  "menu.start": "Start Game",
  "menu.settings": "Settings",
  "menu.quit": "Quit",
  "dialog.welcome": "Welcome to the game!",
  "item.sword": "Iron Sword",
  "item.potion": "Health Potion"
}
```

### 命名规范

| 规范 | 说明 | 示例 |
|------|------|------|
| 键名层级 | 使用点号分隔模块与条目 | `menu.start`、`item.sword` |
| 键名小写 | 全小写，单词间用连字符 | `dialog.confirm-quit` |
| 模块前缀 | 键名以模块名开头 | `menu.*`、`item.*`、`quest.*` |
| 值不占位 | 值为纯文本，不包含变量占位符 | `"dialog.welcome": "欢迎来到游戏！"` |

### 编码要求

- 所有 `.json` 文件必须使用 **UTF-8 无 BOM** 编码
- 文件末尾保留一个换行符
- 缩进统一使用 2 空格

---

## 翻译流程示例

本项目的翻译流程分为 6 个阶段（对应 STATUS.md 中的阶段跟踪）：

### 阶段 1：术语表提取

从游戏源文件中提取专有名词，建立术语表：

| 英文原文 | 中文翻译 | 类型 | 备注 |
|----------|----------|------|------|
| Iron Sword | 铁剑 | 武器 | 基础武器 |
| Health Potion | 生命药水 | 消耗品 | 恢复 HP |

### 阶段 2：翻译规范建立

确定翻译风格与术语标准：

- **语气**：正式、简洁
- **数字**：阿拉伯数字
- **标点**：使用中文全角标点
- **专名**：与术语表保持一致

### 阶段 3：文本提取

从游戏源代码中提取所有可翻译文本，生成 `lang/en/*.json` 原文文件。

### 阶段 4：翻译执行

按模块逐个翻译，生成 `lang/zh-cn/*.json` 译文文件。

**原文**（`lang/en/ui.json`）：

```json
{
  "menu.start": "Start Game",
  "menu.settings": "Settings",
  "menu.quit": "Quit",
  "dialog.welcome": "Welcome to the game!",
  "item.sword": "Iron Sword",
  "item.potion": "Health Potion"
}
```

**译文**（`lang/zh-cn/ui.json`）：

```json
{
  "menu.start": "开始游戏",
  "menu.settings": "设置",
  "menu.quit": "退出",
  "dialog.welcome": "欢迎来到游戏！",
  "item.sword": "铁剑",
  "item.potion": "生命药水"
}
```

### 阶段 5：翻译验证

| 检查项 | 说明 |
|--------|------|
| 上下文检查 | 在游戏场景中验证译文是否符合语境 |
| 术语一致性 | 检查同一术语是否在各模块中翻译一致 |
| 键名对照 | 确保原文与译文的键名完全对应 |
| 格式检查 | 确认 JSON 格式有效、编码为 UTF-8 |

### 阶段 6：导出交付

导出最终翻译文件，交付给游戏开发团队集成。

---

## 使用示例

### 加载语言文件（Python 示例）

```python
import json
from pathlib import Path

def load_language(lang_code: str, module: str = "ui") -> dict:
    """加载指定语言的文本资源。

    参数：
        lang_code: 语言代码（如 "en"、"zh-cn"）
        module: 模块名（如 "ui"、"items"）

    返回：
        键值对字典
    """
    file_path = Path(__file__).parent / "lang" / lang_code / f"{module}.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# 加载中文 UI 文本
texts = load_language("zh-cn", "ui")
print(texts["menu.start"])  # 输出：开始游戏
```

### 切换语言

```python
class Localization:
    def __init__(self, lang_code: str = "en"):
        self.lang_code = lang_code
        self.texts = {}

    def load(self, module: str = "ui"):
        self.texts[module] = load_language(self.lang_code, module)

    def get(self, key: str, module: str = "ui") -> str:
        return self.texts.get(module, {}).get(key, key)

# 使用示例
loc = Localization("zh-cn")
loc.load("ui")
print(loc.get("dialog.welcome"))  # 输出：欢迎来到游戏！
```

---

## 扩展建议

| 扩展方向 | 实现方式 |
|----------|----------|
| 新增语言 | 在 `lang/` 下创建新语言目录（如 `lang/ja/`） |
| 新增模块 | 在各语言目录下创建新 JSON 文件（如 `items.json`） |
| 变量插值 | 在值中使用 `{name}` 占位符，运行时替换 |
| 复数处理 | 按 BCP 47 规范处理复数形式 |
| 自动校验 | 编写脚本检查原文与译文的键名一致性 |

---

## 注意事项

- 本项目为 **AOS 示例项目**，目录名以 `_` 开头。实际项目请使用项目真实名称作为目录名。
- 本示例仅展示结构与流程，实际游戏本地化项目规模会更大（数百至数千条文本）。
- 翻译文件为示例内容，可自由修改用于学习。

---

## 许可证

MIT License — 本项目为 AOS 示例项目，可自由学习与引用。

---

## 维护信息

| 字段 | 值 |
|------|-----|
| 创建日期 | 2026-06-21 |
| 维护者 | AOS Framework |
| 最后更新 | 2026-06-25 |
