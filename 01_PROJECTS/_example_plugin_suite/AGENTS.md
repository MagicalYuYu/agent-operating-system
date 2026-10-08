# 插件集示例 — 项目配置

> 本文件由 AOS 管理，Agent 操作本项目时自动加载

> 状态：项目集全部阶段完成，3 个子插件均 ACTIVE 就绪 ｜ 更新 2026-10
> 插件基类 + 事件总线架构定稿，weather_bot / translator_bot / accounting_bot 三插件开发、集成测试与文档全部完成。项目集作为 AOS 项目集结构范例展示，无活跃任务。

---

## 项目基本信息

| 字段 | 值 |
|------|-----|
| 项目名称 | 插件集示例 |
| 项目类型 | plugin_suite |
| 技术栈 | Python 3.10+, JSON, Markdown |
| 创建时间 | 2026-06-25 |
| AOS 项目路径 | 01_PROJECTS/_example_plugin_suite/ |

---

## 状态记录

| 项 | 值 |
|----|-----|
| 状态载体 | 本文件头部「状态摘要」节（v2 项目两件套：AGENTS.md + README.md，不设独立状态文件） |
| 更新规则 | 阶段切换或关键节点时覆盖更新摘要；过程历史追加至 `06_LOGS/{project}/` |

---

## 命令地图
- 构建命令: 无构建（纯 Python 标准库插件集）
- 测试命令: `python -c "import sys;sys.path.insert(0,'src');import weather_bot.main,translator_bot.main,accounting_bot.main,shared.plugin_base;print('import OK')"`（导入冒烟；无 unittest 用例）
- 运行命令: 无可执行入口（各 main.py 均无 `if __name__ == '__main__'` 块）；插件经 `src/shared/plugin_base.py` 的 EventBus 装配使用，配置模板 `config/bot_config.example.json`

## 项目专属约束

- 所有插件必须实现统一的插件接口（PluginBase）
- 插件间通信通过事件总线（EventBus）进行，禁止直接调用
- 配置文件统一使用 JSON 格式
- 每个插件必须有独立的 README.md

---

## 子项目清单

| 子项目名称 | 路径 | 状态 | 说明 |
|------------|------|------|------|
| weather_bot | src/weather_bot/ | ACTIVE | 天气查询插件 |
| translator_bot | src/translator_bot/ | ACTIVE | 翻译插件 |
| accounting_bot | src/accounting_bot/ | ACTIVE | 记账插件 |

---

## 敏感信息（迁移时重点关注）

> ⚠ 以下信息在迁移、部署、环境切换时必须重点核查

| 类型 | 内容 | 说明 | 迁移注意事项 |
|------|------|------|-------------|
| 端口 | 无 | 本项目为插件集，无独立服务端口 | — |
| 接口 | 无 | 本项目无 API 接口 | — |
| 路径 | src/ | 子项目存放目录 | 各子项目路径需保持一致 |
| 环境变量 | 无 | 本项目无环境变量 | — |
| 依赖服务 | 无 | 本项目无外部依赖 | — |
| 定时任务 | 无 | 本项目无定时任务 | — |

---

## 关联项目

| 关联项目 | 关系 | 说明 |
|----------|------|------|
| 无 | — | — |

---

## 知识引用（禁止复制内容，只引用路径）

- 无
