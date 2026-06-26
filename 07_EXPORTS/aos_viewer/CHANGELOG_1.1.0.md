# AOS 1.1.0 变更日志

> 发布日期：2026-06-25
> 上一版本：1.0.0（2026-06-21 GitHub 首发版）

---

## 新增功能

### AOS Viewer 可视化界面

AOS 1.1.0 引入了全新的可视化前端 **AOS Viewer**，提供 Liquid Glass 玻璃拟态风格的 OS 感操作体验。

| 特性 | 说明 |
|------|------|
| 系统总览 | 版本 / 内核状态 / 组件状态 / 运行时统计 / 事件日志时间线 |
| Skill 管理 | 已注册 Skill 清单 + 调用次数 + 演化记录 |
| 项目工作区 | 项目卡片网格 + AGENTS/README/STATUS 内容预览 |
| 记忆中心 | 用户画像 / 反馈记录 / 参考 / 项目（四类记忆） |
| 知识库 | 参考知识库（系统 / 网页分类） |
| Loop 监控 | Loop 类型定义 + 活跃 Loop（预留） |
| Agent 任务池 | Agent 任务认领（预留） |
| 日志查看器 | 运行日志浏览 |
| 控制台 | 脚本触发器（自检 / 同步 / 迁移采集 / 迁移分类 / 迁移入库） |

### i18n 国际化

- 内置 zh-CN（简体中文） / en-US（English）双语切换
- 所有界面文本均支持 i18n 字典管理
- 控制台欢迎语 / 菜单项 / 模块标题 / 状态标签全覆盖

### PyWebView 桌面模式

- 无边框窗口 + 自定义窗口控制（最小化 / 最大化 / 关闭）
- 菜单栏拖拽移动窗口
- 启动动画（Boot Screen + 进度条）
- 动态背景光晕效果

### HTTP API 实时数据

- `/api/data` 端点：返回完整 AOS 数据 JSON
- `/api/refresh` 端点：触发数据重新扫描
- 数据源指示器：本地 data.js（静态）↔ API（实时）切换

### Spotlight 全局搜索

- 搜索模块 / Skill / 项目 / 记忆 / 知识
- 关键词高亮
- 精准跳转
- MD 正文搜索（可在偏好设置开启）

### 数据生成脚本

新增 `03_TOOLS/scripts/aos_generate_data.py`：
- 扫描 AOS 文件系统（00_BOOT / 03_TOOLS / 04_MEMORY / 09_REFERENCE）
- 生成 `prototype/js/data.js` 供 AOS Viewer 加载
- 纯 Python 标准库实现，无第三方依赖
- 支持 PyInstaller 打包环境

### 主题系统

- 深色（默认）/ 浅色 / 极简 三种主题
- 缩放控制（放大 / 缩小 / 重置）

---

## 修改与增强

### AGENTS.md

- **新增**：项目内标准结构定义（类型一单一项目 / 类型二项目集）
- **新增**：禁止 `src/` 下嵌套同名目录的约束
- **新增**：双机环境章节（仅工作目录版本，GitHub 上传版自动剥离）

### 同步脚本 aos_sync_github.py

- **增强**：四层过滤机制（EXCLUDE_DIRS + EXTRA_EXCLUDE_FILES + DESENSITIZE_FILES + SENSITIVE_PATTERNS）
- **新增**：`agents_dual_machine` 脱敏类型（剥离双机环境章节）
- **新增**：`system_state` 脱敏类型（统计归零 + 事件过滤 + 自检记录清理）
- **新增**：`index` 脱敏类型增强（保留 proj-aos-v1-status 模板描述）
- **新增**：`proj_aos_status` 脱敏类型（版本更新 + 移除开发过程描述）
- **新增**：data.js 替换步骤（example_data.js → GitHub 目录 data.js）
- **新增**：AOS_Viewer/ 和 release/ 目录排除

### 巡检规范

- **新增**：`00_BOOT/SYSTEM_INSPECTION.md`（系统级巡检规范）
- **新增**：`00_BOOT/PROJECT_INSPECTION.md`（项目级巡检规范）
- **变更**：原 DAILY_INSPECTION.md 拆分为系统级 + 项目级两个文件
- **变更**：AGENTS.md 引用从启动自检流程移至详细规则引用表（标注 Layer 3 手动触发）

### 版本号同步

系统版本号统一从 `1.0.0` → `1.1.0`，涉及文件：

| 文件 | 修改内容 |
|------|----------|
| `00_BOOT/SYSTEM_STATE.md` | 版本字段 + 最后更新描述 + v1.1.0 发布事件 |
| `00_BOOT/CORE.md` | 版本字段 |
| `README.md` | 版本徽章 |
| `04_MEMORY/INDEX.md` | proj-aos-v1-status 描述 |
| `04_MEMORY/project/proj_aos_v1_status.md` | 版本 + GitHub 发布状态 + AOS Viewer 状态 |
| `03_TOOLS/aos_viewer/prototype/index.html` | title + 版本显示 |
| `03_TOOLS/aos_viewer/prototype/js/i18n.js` | console.welcome |
| `03_TOOLS/aos_viewer/prototype/js/app.js` | fallback version |
| `03_TOOLS/aos_viewer/aos_viewer_server.py` | fallback version |
| `03_TOOLS/aos_viewer/prototype/previews/*.html` | 系统版本（3 文件） |
| `docs/index.html` | hero.badge（zh-CN + en-US） |
| `docs/AOS_creative_proposal.html` | hero.badge（zh-CN + en-US） |
| `09_REFERENCE/web/web-template-specification.md` | 示例版本号 |
| `03_TOOLS/scripts/aos_generate_data.py` | fallback version |

---

## 修复

- 修复 LS 工具可靠性问题：所有文件存在性检查改用 PowerShell `Test-Path` / `Get-ChildItem -Force` 验证，避免误报
- 修复同步脚本中 proj_aos_v1_status.md 脱敏逻辑的版本匹配问题（改为正则通用匹配）

---

## 已知问题

| 问题 | 严重度 | 状态 |
|------|--------|------|
| 凭据管理无加密 | 中 | 待实现（credentials.json 明文存储） |
| Loop Engine 未实现 | 高 | 待实现（3 种类型已定义，0 个活跃） |
| agent_pool 任务认领机制 | 中 | 待实现（schema 已定义，0 个活跃） |
| AOS Viewer 响应式适配 | 低 | 1.2.0 规划 |
| AOS Viewer 工具链集成 | 低 | 1.2.0 规划 |

---

## 下载

- **GitHub Release**：[v1.1.0](https://github.com/MagicalYuYu/agent-operating-system/releases/tag/v1.1.0)
- **发布包内容**：
  - `AOS_Viewer_v1.1.0.zip`（PyInstaller 打包的桌面应用，约 50MB）
  - `aos-1.1.0-source.zip`（源码包，含完整框架文件）
  - `AOS_UPDATE_PROMPT_1.1.0.md`（Agent 辅助更新提示词）
  - `ReleaseNotes_1.1.0.md`（本文件）

---

## 升级方式

详见 `MIGRATION_GUIDE_1.1.0.md`，提供 3 种升级方案：

1. **Agent 辅助更新**（推荐）：粘贴 `AOS_UPDATE_PROMPT_1.1.0.md` 到 Agent 对话框
2. **自动合并脚本**（备选）：运行 `aos_migrate_to_1.1.0.py`（1.2.0 提供）
3. **手动合并**（兜底）：按 `MIGRATION_GUIDE_1.1.0.md` 步骤操作

---

*AOS 1.1.0 · MIT License · 2026-06-25*
