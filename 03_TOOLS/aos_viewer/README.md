# AOS Viewer — 系统桌面环境

> AOS 操作系统的桌面环境 · v1.1.0

## 定位

AOS Viewer 是 AOS 操作系统的**桌面环境**——就像 macOS 之于 Darwin 内核、Windows 桌面之于 Windows NT。

它不是"给 AOS 加的可视化插件"，而是 v1.1.0 系统形态的核心组成：让 AOS 从"一组文件"进化为"一套可见、可控、可操作的操作系统"。用户通过它看见系统全貌、控制脚本执行，AI 通过它获得数据源。

### 三大核心价值

| 价值 | 说明 |
|:-----|:-----|
| 👁️ **可见性** | 系统总览 / Skill / 项目 / 记忆 / 知识库 / 日志，一眼全览，不再靠 `find` 和记忆 |
| 🎛️ **可控性** | 控制台一键触发自检 / 同步 / 迁移，进度实时可见，不用记命令 |
| 🖥️ **系统感** | Liquid Glass 玻璃拟态桌面 + 菜单栏 + Spotlight 搜索 + 通知中心 |

### 设计原则

- **只读不写**：AOS Viewer 不修改任何 AOS 系统文件，所有操作通过显式脚本触发
- **数据实时**：通过 `aos_generate_data.py` 扫描文件系统，或 HTTP API 实时读取
- **零侵入**：不影响 AOS 内核运行时行为，可随时关闭

---

## 桌面特性

| 特性 | 说明 |
|------|------|
| 启动动画 | Boot Screen 欢迎画面 + 动态背景光晕 |
| 菜单栏 | 文件 / 视图 / 工具 / 帮助 四大下拉菜单 |
| Spotlight 搜索 | 全局搜索模块 / Skill / 项目 / 记忆 / 知识，关键词高亮 |
| 通知中心 | 操作完成实时弹窗反馈 |
| 右键菜单 | 选中文字复制 / 联动 Spotlight 搜索 |
| 三种主题 | 深色（默认）/ 浅色 / 极简 |
| 玻璃强度 | 弱 / 标准 / 强 三档可调 |
| UI 缩放 | 0.8x – 1.4x 全局缩放 |
| i18n 国际化 | zh-CN / en-US 双语无缝切换 |
| 数据源切换 | 本地 data.js ↔ HTTP API 实时读取 |
| 设置持久化 | WebView 数据持久化到 %APPDATA%\AOS_Viewer\ |

---

## 快速开始

### 方式一：打包 EXE（推荐普通用户）

从 GitHub Release 下载 `AOS Viewer.exe`，双击即可启动——无需 Python 环境，自带 Liquid Glass 桌面界面。

- 启动后自动打开桌面窗口
- 自动扫描 AOS 文件系统生成实时数据
- 关闭窗口即退出
- 设置持久化到 `%APPDATA%\AOS_Viewer\`，重启不丢失

> 打包 EXE 内置 example_data.js 作为示例数据。首次启动时如检测到 AOS 根目录，会自动调用 `aos_generate_data.py` 生成实时数据。

### 方式二：桌面窗口模式（开发者）

```bash
# 默认启动 PyWebView 桌面窗口
python aos_viewer_server.py

# 指定端口 + 桌面模式
python aos_viewer_server.py --port 8765 --desktop
```

### 方式三：浏览器 + HTTP API 模式（开发者调试）

```bash
# 启动 HTTP 服务器并自动打开浏览器
python aos_viewer_server.py --port 8765 --browser
```

> 浏览器模式仅作为开发者调试选项，普通用户推荐使用打包 EXE。

### 生成实时数据

```bash
# 扫描 AOS 文件系统，生成 prototype/js/data.js
python ../scripts/aos_generate_data.py
```

---

## 模块清单

AOS Viewer 桌面包含 9 大模块，覆盖 AOS 系统的每一个角落：

| 模块 | 说明 |
|------|------|
| 🖥️ 系统总览 | 版本 / 内核状态 / 组件状态 / 运行时统计 / 事件日志时间线 |
| 🔧 Skill 管理 | 已注册 Skill 清单 + 调用次数 + 演化记录 |
| 📁 项目工作区 | 项目卡片网格 + AGENTS/README/STATUS 内容预览 |
| 🧠 记忆中心 | 用户画像 / 反馈记录 / 参考 / 项目（四类记忆） |
| 📚 知识库 | 参考知识库（系统 / 网页分类） |
| 🔄 Loop 监控 | Loop 类型定义 + 活跃 Loop（预留） |
| 🤖 Agent 任务池 | Agent 任务认领（预留） |
| 📝 日志查看器 | 运行日志浏览 |
| 🎛️ 控制台 | 脚本触发器（自检 / 同步 / 迁移采集 / 迁移分类 / 迁移入库） |

---

## 技术栈

| 层 | 选型 | 状态 |
|----|------|------|
| 前端 | HTML + CSS + JS（原生，零依赖） | ✅ 已实现 |
| 桌面壳 | PyWebView | ✅ 已集成 |
| 打包 | PyInstaller（onefile 模式，自包含 EXE） | ✅ 已集成 |
| 数据解析 | aos_generate_data.py | ✅ 已实现 |
| 国际化 | i18n.js（zh-CN / en-US） | ✅ 已实现 |
| 视觉风格 | Liquid Glass 玻璃拟态 | ✅ 已实现 |

---

## 数据流

```
AOS 文件系统（00_BOOT/ 03_TOOLS/ 04_MEMORY/ 09_REFERENCE/ ...）
        ↓ aos_generate_data.py 扫描
prototype/js/data.js（元数据） + data_content.js（大文本缓存）
        ↓ app.js 加载 + mergeDataContent() 合并
AOS Viewer 前端渲染
        ↓（可选）
aos_viewer_server.py HTTP API（/api/data /api/refresh）
        ↓
浏览器 / PyWebView 桌面窗口 / 打包 EXE
```

---

## 目录结构

```
03_TOOLS/aos_viewer/
├── README.md                    ← 本文件
├── aos_viewer_server.py         ← 后端服务 + PyWebView 入口
├── aos_viewer.spec              ← PyInstaller 打包配置（onefile 模式）
├── aos_viewer.ico               ← 应用图标
├── version_info.txt             ← EXE 元信息（版本号/公司/描述）
└── prototype/                   ← 前端原型（已生产化）
    ├── index.html               ← 主入口
    ├── favicon.ico
    ├── css/
    │   └── style.css            ← 主样式（Liquid Glass 风格）
    ├── js/
    │   ├── app.js               ← 交互逻辑
    │   ├── data.js              ← 运行时数据（aos_generate_data.py 生成）
    │   ├── data_content.js      ← 大文本内容缓存
    │   └── i18n.js              ← 国际化字典
    └── previews/                ← 备用美学方向归档
        ├── README.md
        ├── a_cyber_archive.html
        ├── b_terminal_organism.html
        └── c_oriental_void.html
```

---

## 依赖

```bash
# 桌面模式必需
pip install pywebview

# 打包构建
pip install pyinstaller
```

> 打包 EXE 模式无需任何依赖，双击即用。

---

## 与 AOS 内核的关系

AOS Viewer 是 AOS 操作系统的**桌面环境层**，位于五层 OS 架构的最顶层：

```
🖥️ 桌面环境层（AOS Viewer）  ← 你在这里看见和操作系统
       ↓ 调用
📦 应用层（Skills）           ← 触发脚本执行
       ↓ 遵循
🧠 内核层（AGENTS.md）        ← 规则约束
       ↓ 组织
📁 文件系统层（10 个目录）    ← 文件存储
       ↓ 持久化
💾 存储层（04_MEMORY）        ← 记忆中心
```

- AOS Viewer 是**只读仪表盘 + 控制台**，不修改任何 AOS 文件
- 数据通过 `aos_generate_data.py` 扫描生成，与 AOS 文件系统一致
- 控制台脚本触发依赖 `03_TOOLS/scripts/` 下的脚本
- 不影响 AOS 内核运行时行为
