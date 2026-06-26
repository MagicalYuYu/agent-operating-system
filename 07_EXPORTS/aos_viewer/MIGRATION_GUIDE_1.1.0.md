# AOS 1.1.0 手动升级指南

> 本指南适用于无法使用 Agent 辅助更新（方案一）的用户，手动完成从 1.0.0 到 1.1.0 的升级。

---

## 前置准备

### 1. 备份当前 AOS

```bash
# 在 AOS 根目录下执行
mkdir 99_ARCHIVE\pre_update_1.1.0_YYYYMMDD
xcopy /E /I /H /Y 00_BOOT 99_ARCHIVE\pre_update_1.1.0_YYYYMMDD\00_BOOT
xcopy /E /I /H /Y 03_TOOLS 99_ARCHIVE\pre_update_1.1.0_YYYYMMDD\03_TOOLS
xcopy /E /I /H /Y 04_MEMORY 99_ARCHIVE\pre_update_1.1.0_YYYYMMDD\04_MEMORY
copy AGENTS.md 99_ARCHIVE\pre_update_1.1.0_YYYYMMDD\
copy README.md 99_ARCHIVE\pre_update_1.1.0_YYYYMMDD\
```

### 2. 下载 1.1.0 发布包

从 GitHub Release 下载 `aos-1.1.0-source.zip`，解压到临时目录 `05_CACHE\aos_1.1.0_update\`。

### 3. 确认 Python 环境

```bash
python --version  # 需 3.8+
```

---

## 升级步骤

### 步骤 1：新增文件（直接复制）

以下文件在 1.0.0 中不存在，直接从发布包复制到对应位置：

| 源路径（发布包） | 目标路径（你的 AOS） |
|------------------|---------------------|
| `03_TOOLS/aos_viewer/` | `03_TOOLS/aos_viewer/`（整个目录） |
| `03_TOOLS/scripts/aos_generate_data.py` | `03_TOOLS/scripts/aos_generate_data.py` |
| `07_EXPORTS/aos_viewer/example_data.js` | `07_EXPORTS/aos_viewer/example_data.js` |

```bash
# 示例（Windows）
xcopy /E /I /H /Y 05_CACHE\aos_1.1.0_update\03_TOOLS\aos_viewer 03_TOOLS\aos_viewer
copy 05_CACHE\aos_1.1.0_update\03_TOOLS\scripts\aos_generate_data.py 03_TOOLS\scripts\
```

### 步骤 2：合并 AGENTS.md

**关键变更**：新增"项目内标准结构"定义。

打开你的 `AGENTS.md`，找到"项目内标准结构"章节（如有），替换为以下内容：

```markdown
## 项目内标准结构

AOS 支持两种项目类型，通过 AGENTS.md 的"项目类型"字段区分：

### 类型一：单一项目

适用于独立项目（如浏览器扩展、单机应用、工具脚本）。`src/` 直接存放源代码文件。

（详见 1.1.0 官方版 AGENTS.md）

### 类型二：项目集

适用于包含多个子项目的集合（如插件集、微服务集、多模块项目）。`src/` 存放多个子项目目录，每个子项目有独立的结构。

（详见 1.1.0 官方版 AGENTS.md）

### 规范说明

- 子目录按需创建，非强制
- `docs/` 存放项目相关的讨论文档、开发规划等 MD 文件
- `src/` 存放实际工作文件：单一项目直接存放代码，项目集存放子项目目录
- `config/` 存放项目专属配置
- 项目集的 AGENTS.md 必须包含子项目清单（名称/路径/状态/说明）
- 禁止在 src/ 下再嵌套与项目同名的目录（如 `src/{name}/`），避免冗余层级
```

**注意**：保留你的自定义规则，只替换"项目内标准结构"章节。如果你添加了"双机环境"章节，**保留它**（这是你的私有配置，GitHub 上传版会自动剥离）。

### 步骤 3：更新 SYSTEM_STATE.md

打开 `00_BOOT/SYSTEM_STATE.md`：

1. **更新版本号**：
   ```markdown
   | 版本 | 1.1.0 |
   ```

2. **更新最后更新字段**：
   ```markdown
   | 最后更新 | 2026-06-XX（v1.1.0 发布：新增 AOS Viewer 可视化界面 + i18n 国际化 + 巡检规范拆分） |
   ```

3. **保留**你的运行时统计数字和事件日志（不要删除任何用户事件）

4. **追加** v1.1.0 发布事件到事件日志末尾：
   ```markdown
   | 2026-06-XX | SYSTEM_RELEASE | v1.1.0 发布：新增 AOS Viewer 可视化界面（Liquid Glass 风格+i18n 国际化+PyWebView 桌面模式+HTTP API），新增 aos_generate_data.py 数据生成脚本，同步脚本增强脱敏逻辑 |
   ```

### 步骤 4：更新 INDEX.md

打开 `04_MEMORY/INDEX.md`：

1. **保留**你的所有记忆索引条目（不删除任何条目）
2. **更新** `proj-aos-v1-status` 条目的描述（版本号 1.0.0 → 1.1.0）

### 步骤 5：更新 proj_aos_v1_status.md

打开 `04_MEMORY/project/proj_aos_v1_status.md`：

1. **更新版本号**：
   ```markdown
   | 版本 | 1.1.0 | 2026-06-XX（原为 1.0.0 首发，升级为 1.1.0 新增可视化界面） |
   ```

2. **更新 GitHub 发布状态**：
   ```markdown
   | GitHub 发布状态 | v1.1.0 发布 | 2026-06-XX（原为 v1.0.0 首发） |
   ```

3. **追加 AOS Viewer 状态字段**到动态事实表：
   ```markdown
   | AOS Viewer 状态 | v1.1.0 新增可视化界面（Liquid Glass 风格 + i18n 国际化 + PyWebView 桌面模式 + HTTP API） | 2026-06-XX |
   | AOS Viewer 功能 | Spotlight搜索+精准跳转+关键词高亮+MD正文搜索+菜单栏+下拉菜单+动效+无边框桌面窗口 | 2026-06-XX |
   ```

4. **保留**你的其他动态事实（已注册 Skill 数、记忆索引数等）

### 步骤 6：更新 README.md

打开根目录 `README.md`，更新版本徽章 `1.0.0` → `1.1.0`。

### 步骤 7：版本号同步

扫描以下文件中的 `1.0.0` 版本引用，更新为 `1.1.0`：

| 文件 | 修改内容 |
|------|----------|
| `00_BOOT/CORE.md` | 版本字段 |
| `docs/index.html` | hero.badge（zh-CN + en-US，共 3 处） |
| `docs/AOS_creative_proposal.html` | hero.badge（zh-CN + en-US，共 3 处） |
| `09_REFERENCE/web/web-template-specification.md` | 示例版本号 |

**保留不动的场景**：
- Skill 自身版本号（`config.json` 中的 `"version": "1.0.0"` 是 Skill 版本，非系统版本）
- 历史事件记录中的版本引用（如 `v1.0.0 GitHub首发版` 是历史事实）
- 归档文件（`99_ARCHIVE/`）

### 步骤 8：生成 data.js

```bash
python 03_TOOLS\scripts\aos_generate_data.py
```

确认 `03_TOOLS/aos_viewer/prototype/js/data.js` 生成成功，且 `"version"` 字段为 `"1.1.0"`。

### 步骤 9：一致性自检

```bash
python 03_TOOLS\scripts\aos_check.py
```

修复所有不一致项。

### 步骤 10：验证 AOS Viewer

```bash
# 桌面窗口模式（需安装 pywebview）
pip install pywebview
python 03_TOOLS\aos_viewer\aos_viewer_server.py
```

---

## 清理

- 删除临时目录 `05_CACHE\aos_1.1.0_update\`
- 保留备份目录 `99_ARCHIVE\pre_update_1.1.0_YYYYMMDD\`（验证成功后可手动删除）

---

## 回滚

如果升级失败：

1. 从 `99_ARCHIVE\pre_update_1.1.0_YYYYMMDD\` 恢复备份文件
2. 删除新增文件：
   - `03_TOOLS\aos_viewer\`（整个目录）
   - `03_TOOLS\scripts\aos_generate_data.py`
3. 运行 `aos_check.py` 验证回滚结果

---

## 常见问题

### Q: data.js 生成失败？

- 确认 Python 3.8+
- 确认在 AOS 根目录下执行
- 检查 `00_BOOT/SYSTEM_STATE.md` 是否存在且格式正确
- `aos_generate_data.py` 无第三方依赖，纯标准库实现

### Q: AOS Viewer 启动后白屏？

- 检查 `prototype/js/data.js` 是否存在且为有效 JSON
- 检查终端是否有 Python 报错
- 尝试重新运行 `aos_generate_data.py`

### Q: PyWebView 桌面模式无法启动？

- 确认已安装：`pip install pywebview`
- Windows 需要 WebView2 Runtime（Win10/11 通常已预装）
- 查看终端错误输出

### Q: 版本号同步遗漏？

- 运行 `aos_check.py` 检测不一致项
- 手动检查 `99_ARCHIVE/` 是否被误改（应保留历史版本号）
- 第三方项目中的 `1.0.0` 不应被修改（`aos_check.py` 已排除 `01_PROJECTS/`）

---

*AOS 1.1.0 手动升级指南 · MIT License · 2026-06-25*
