# AOS v1.1.0 — 03_TOOLS

Skill / 脚本 / 适配器 / 可视化界面库，存放 AOS 的所有可执行工具。

## 应放什么

| 子目录 | 说明 |
|--------|------|
| skills/ | Skill 定义（每个 Skill 一个文件夹，含 SKILL.md + gotchas.md + 可选 scripts/templates/references） |
| scripts/ | 工具脚本（Python）：自检、数据生成、迁移采集/分类/入库、GitHub 同步 |
| aos_viewer/ | AOS Viewer 可视化界面（v1.1.0 新增）：前端原型 + PyWebView 桌面入口 + PyInstaller 打包配置 |
| adapters/ | 跨平台适配模板（Claude Code / Codex） |
| connectors/ | 外部连接器配置（预留） |
| agents/ | Agent 模板（预留） |
| loops/ | Loop 模板（预留） |

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

## AOS Viewer（v1.1.0 新增）

AOS Viewer 是 AOS 的可视化前端 + 脚本触发器，提供只读仪表盘和控制台。详见 [aos_viewer/README.md](aos_viewer/README.md)。

- **浏览器模式**：直接打开 `aos_viewer/prototype/index.html`
- **桌面窗口模式**：`python aos_viewer/aos_viewer_server.py --desktop`
- **打包 EXE**：使用 PyInstaller 打包为单文件可执行程序
