# 压缩锚点（模板版：context-imports 类插件在压缩后自动重注入；≤30 行）

> 使用说明：本文件是工作区常驻锚点，存放压缩后仍需记住的不变量。以下均为示例内容，按你的环境改写后删除本说明行。

## 子代理三铁律
1. 批量/枚举/统计/文本 → 优先 workflow 子代理 + 低成本批量模型 provider；裸 subagent = 主模型全价
2. 委派文件创建 → prompt 内联目标路径（子代理落位遵守率不稳定，实测约半数）
3. 产出后 `python scripts/check_placement.py` 兜底

## 文件操作铁律
1. 中文内容文件只准 write/edit 工具（或 python 显式 utf-8），禁用 shell 管道/重定向写入
2. JSON/YAML 写入 UTF-8 带 BOM；读取用 `utf-8-sig`
3. YAML description 以 `[` 开头必须加引号；含反斜杠路径用单引号串
4. 修改 skill-manifest.json 等结构化文件 → 禁用 shell 字符串替换，只准 write/edit/python json

## 多机协同
可选扩展：见 docs/design-rationale.md「多机协同扩展点」（本模板不含实现）。

## 调研渠道
先验搜索渠道归属与质量；关键结论回原文（read_page/web_fetch）核对；单一来源 = 待验证。

## 上下文管理
- token 预算紧张时：主动将当前任务关键事实写入 04_MEMORY 或项目记忆（防压缩丢失）

## 快速索引
校验器 `scripts/check_placement.py` · 对齐器 `scripts/align_environment.py` · 会话分析 `scripts/session_analyzer.py` · 清单 `.dsh/skill-manifest.json`
