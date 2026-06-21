# AOS v1.0 — 03_TOOLS

Skill/脚本/模板库，存放 AOS 的所有可执行工具。

## 应放什么
- skills/ — Skill 定义（每个 Skill 一个文件夹，含 SKILL.md + gotchas.md + 可选 scripts/templates/references）
- scripts/ — 工具脚本（Python）
- connectors/ — 外部连接器配置
- agents/ — Agent 模板
- loops/ — Loop 模板

## 禁止放什么
- 项目数据
- 运行时状态
- 知识内容

## Skill 文件夹标准结构
```
03_TOOLS/skills/{skill_name}/
├── SKILL.md       ← 核心指令（必须）
├── gotchas.md     ← 坑点清单（必须）
├── scripts/       ← 可执行脚本（可选）
├── templates/     ← 输出模板（可选）
└── references/    ← 参考资料（可选）
```

## 新建 Skill
1. 创建文件夹 03_TOOLS/skills/{name}/
2. 编写 SKILL.md（description 必须写触发条件，不超过250字符）
3. 创建 gotchas.md（坑点清单）
4. 在 00_BOOT/SKILL_REGISTRY.md 注册
5. 在 .trae/skills/ 下创建对应的 Trae Skill 入口
