# AOS v1.1.0 — 可视化界面发布

> **Agent Operating System** · 2026-06-25 · MIT License

---

## 版本亮点

**AOS Viewer** — 全新的可视化前端，为 AOS 装上"眼睛"和"遥控器"。

从 1.0.0 的纯文件系统，到 1.1.0 的可视化操作台，AOS 现在可以"看"了。

### 核心新功能

| 功能 | 说明 |
|------|------|
| **AOS Viewer** | Liquid Glass 玻璃拟态风格的可视化仪表盘，9 大模块（系统总览 / Skill / 项目 / 记忆 / 知识 / Loop / Agent / 日志 / 控制台） |
| **i18n 国际化** | 内置中英双语切换，所有界面文本均支持 i18n |
| **PyWebView 桌面模式** | 无边框窗口 + 自定义窗口控制，原生桌面应用体验 |
| **HTTP API** | `/api/data` + `/api/refresh` 端点，支持本地↔API 数据源切换 |
| **Spotlight 搜索** | 全局搜索模块 / Skill / 项目 / 记忆 / 知识，含关键词高亮 |
| **数据生成脚本** | `aos_generate_data.py` 扫描 AOS 文件系统自动生成 data.js |
| **三种主题** | 深色（默认）/ 浅色 / 极简 |
| **巡检规范拆分** | 系统级 + 项目级分层巡检，职责更清晰 |

---

## 截图预览

（发布后补充）

---

## 下载

| 文件 | 说明 | 大小 |
|------|------|------|
| `AOS_Viewer_v1.1.0.zip` | PyInstaller 打包的桌面应用（开箱即用） | ~50MB |
| `aos-1.1.0-source.zip` | 源码包（含完整框架文件） | ~2MB |
| `AOS_UPDATE_PROMPT_1.1.0.md` | Agent 辅助更新提示词（方案一） | <1KB |
| `ReleaseNotes_1.1.0.md` | 本发布说明 | <1KB |

---

## 升级方式（3 选 1）

### 方案一：Agent 辅助更新（推荐） ⭐⭐⭐

**适用**：Trae / Claude Code / Codex 用户

1. 下载 `AOS_UPDATE_PROMPT_1.1.0.md`
2. 打开你的 Agent，加载 AOS 工作目录
3. 将提示词内容粘贴到对话框
4. Agent 自动执行 8 步更新流程（扫描 / 备份 / 拉取 / 合并 / 同步 / 生成 / 自检 / 清理）
5. 遇到冲突时 Agent 会弹窗询问

**优点**：最贴合 AOS 使用习惯，智能处理冲突，全程可视化

### 方案二：自动合并脚本（备选） ⭐⭐

**适用**：希望纯自动化，不依赖 Agent 交互的用户

```bash
python aos_migrate_to_1.1.0.py --aos-root /path/to/aos
```

> 注：自动合并脚本将在 1.2.0 提供，1.1.0 请使用方案一或方案三。

### 方案三：手动合并（兜底） ⭐

**适用**：技术用户或特殊情况

详见 `MIGRATION_GUIDE_1.1.0.md`，按 10 步操作指南手动完成升级。

---

## 完整变更日志

详见 `CHANGELOG_1.1.0.md`。

### 新增文件（24 个）

- `03_TOOLS/aos_viewer/`（整个目录，16 个文件）
- `03_TOOLS/scripts/aos_generate_data.py`
- `00_BOOT/SYSTEM_INSPECTION.md` + `00_BOOT/PROJECT_INSPECTION.md`（巡检规范拆分）
- `07_EXPORTS/aos_viewer/`（发布物料，6 个文件）

### 修改文件（10 个）

- `AGENTS.md`（项目内标准结构 + 双机环境章节）
- `00_BOOT/SYSTEM_STATE.md` + `00_BOOT/CORE.md`（版本号）
- `README.md`（版本徽章）
- `04_MEMORY/INDEX.md` + `04_MEMORY/project/proj_aos_v1_status.md`
- `03_TOOLS/scripts/aos_generate_data.py`（fallback 版本号）
- `docs/index.html` + `docs/AOS_creative_proposal.html`（版本徽章）
- `09_REFERENCE/web/web-template-specification.md`（示例版本号）

### 删除文件（1 个）

- `00_BOOT/DAILY_INSPECTION.md`（拆分为系统级 + 项目级两个文件）

---

## 已知问题

- 凭据管理无加密（credentials.json 明文存储，1.2.0 引入加密）
- Loop Engine 未实现（3 种类型已定义，1.2.0 实现首批）
- agent_pool 任务认领机制未实现（1.2.0 规划）
- AOS Viewer 响应式适配（1.2.0 规划）

---

## 1.2.0 路线图

- 响应式适配（窄屏布局）
- 工具链集成（GitHub 同步 / 一致性自检按钮连接实际功能）
- Loop Engine 首批实现
- 应用内版本检查
- 增量更新机制（方案四）

---

## 致谢

感谢所有 AOS 用户在 1.0.0 阶段的反馈和实践经验，1.1.0 的所有改进都源于真实使用场景。

---

**AOS** · Agent Operating System · 让 AI 助手不再失忆，让多项目互不串台，让经验持续积累。

*MIT License · 2026-06-25*
