# 项目状态 — 游戏本地化示例

> 状态型记忆 — 覆盖旧值，保留变更注释

---

## 基本信息

| 字段 | 值 | 更新日期 |
|------|-----|----------|
| 项目名 | _example_game_localization | 2026-06-25（2026-06-21 创建，原为 _example_project）|
| 类型 | 游戏本地化示例（game_localization，单一项目）| 2026-06-21 |
| 路径 | 01_PROJECTS/_example_game_localization/ | 2026-06-25（原为 01_PROJECTS/_example_project/）|
| 状态 | ACTIVE | 2026-06-25 |

## 项目结构

```
01_PROJECTS/_example_game_localization/
├── AGENTS.md           ← 项目专属配置
├── README.md           ← 项目基本信息（252 行，详尽文档）
├── STATUS.md           ← 项目状态跟踪（48 行，标准格式）
└── lang/
    ├── en/ui.json      ← 英文原文文件（6 个键值对）
    └── zh-cn/ui.json   ← 中文翻译文件（6 个键值对）
```

## 阶段状态

| 阶段 | 状态 | 说明 |
|------|------|------|
| 术语表提取 | ✅ completed | 已从示例游戏文件提取 6 个 UI 术语键值对 |
| 翻译规范建立 | ✅ completed | 确定翻译风格、标点规范、编码规范 |
| 文本提取 | ✅ completed | 生成 lang/en/ui.json 英文原文文件 |
| 翻译执行 | ✅ completed | 生成 lang/zh-cn/ui.json 简体中文译文文件 |
| 翻译验证 | ✅ completed | 键名对照通过、UTF-8 编码验证通过 |
| 导出交付 | ✅ completed | 示例翻译文件已就绪 |

## 用途

此项目为 AOS 单一项目目录标准结构的示例，展示游戏本地化项目的目录组织、JSON 语言文件规范、翻译流程。面向 AOS 初次使用者，可自由学习与引用。

## 变更历史

| 日期 | 变更 |
|------|------|
| 2026-06-21 | 项目初始化，创建目录结构与示例翻译文件 |
| 2026-06-25 | 巡检修复：移除 AGENTS.md 空洞引用、README 升级为 252 行详尽文档、STATUS 升级为标准格式 |
| 2026-06-25 | 项目重命名：_example_project → _example_game_localization（与其他示例项目命名格式一致）|
