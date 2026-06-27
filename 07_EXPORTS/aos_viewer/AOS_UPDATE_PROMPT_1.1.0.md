# AOS 1.1.0 更新指令（Agent 辅助）

> **用途**：在 Trae / Claude Code / Codex 对话框中输入"请读取 `07_EXPORTS/aos_viewer/AOS_UPDATE_PROMPT_1.1.0.md` 并执行其中的更新流程"，Agent 将自动执行从 1.0.0 到 1.1.0 的更新流程。
>
> **前置条件**：Agent 已加载 AOS 工作目录（含 `AGENTS.md`），Python 3.8+ 可用。
>
> **路径约定**：以下脚本中的 `$aosRoot` 变量表示 AOS 根目录。默认在 AOS 根目录下执行即可（`$aosRoot = "."`），也可由用户指定（如 `$aosRoot = "C:\Users\YourName\AOS"`）。
>
> **预计耗时**：15-30 分钟（取决于网络下载速度与合并冲突数量）

---

## 路径变量初始化（所有步骤的前提）

**执行命令**（PowerShell，在 AOS 根目录下执行）：
```powershell
# 设置 AOS 根目录（默认为当前目录，即 AOS 根目录）
# 如需指定其他路径，改为：$aosRoot = "C:\path\to\your\AOS"
$aosRoot = "."
```

---

## 任务说明

你正在协助用户将 AOS（Agent Operating System）从 **1.0.0** 更新到 **1.1.0**。

**1.1.0 核心变更**：
- 新增 AOS Viewer 可视化界面（Liquid Glass 风格 + i18n 国际化 + PyWebView 桌面模式 + HTTP API + Spotlight 全局搜索）
- 新增 `aos_generate_data.py` 数据生成脚本（扫描 AOS 文件系统生成 `data.js`）
- AGENTS.md 新增"项目内标准结构"（类型一单一项目 / 类型二项目集）+ 双机环境章节
- 巡检规范拆分：`DAILY_INSPECTION.md` → `SYSTEM_INSPECTION.md` + `PROJECT_INSPECTION.md`
- 版本号统一从 1.0.0 → 1.1.0（14 处文件位置）

**文件变更总览**（来源：`FILE_MANIFEST_1.1.0.json`）：

| 类别 | 数量 | 处理方式 |
|------|------|----------|
| 新增文件 | 24 | 直接覆盖（1.0.0 不存在） |
| 修改文件 | 12 | 智能合并（三向比对） |
| 删除文件 | 1 | 删除并迁移内容 |
| GitHub 排除 | 23 | 不参与更新（仅同步脚本参考） |

请严格按以下 8 个步骤执行，**每步完成后输出进度摘要**，遇到冲突时弹窗询问用户决策。

---

## 步骤 1：环境扫描

**目标**：确认当前版本、用户项目、自定义规则，为后续合并提供基线。

**执行命令**（PowerShell）：
```powershell
# 1.1 确认当前版本
Select-String -Path "$aosRoot\00_BOOT\SYSTEM_STATE.md" -Pattern "1\.0\.0" | Select-Object -First 3

# 1.2 列出用户项目（排除示例项目）
Get-ChildItem -Path "$aosRoot\01_PROJECTS\" -Directory | Where-Object { $_.Name -ne "_example_project" } | Select-Object Name

# 1.3 统计记忆索引条目数
(Get-Content "$aosRoot\04_MEMORY\INDEX.md" | Measure-Object -Line).Lines
```

**扫描清单**：
- [ ] 读取 `00_BOOT/SYSTEM_STATE.md` 确认版本号为 `1.0.0`（若不是，停止并询问用户）
- [ ] 列出 `01_PROJECTS/` 下所有用户项目（排除 `_example_project`）
- [ ] 扫描 `04_MEMORY/INDEX.md` 记录当前记忆索引条目数
- [ ] 扫描 `AGENTS.md` 检测是否含用户自定义规则（对比 1.0.0 官方版特征：无"项目内标准结构"章节、无"双机环境"章节）
- [ ] 检查 `00_BOOT/DAILY_INSPECTION.md` 是否存在（1.0.0 应存在，1.1.0 将删除）

**产出**：环境扫描报告（当前版本 / 用户项目清单 / 自定义规则检测结果 / DAILY_INSPECTION.md 存在性）

**进度摘要**：
```
┌─ [步骤 1/8] 环境扫描 ─────────────────────┐
│ 状态：完成 ✓                               │
│ 当前版本：1.0.0                            │
│ 用户项目数：N                              │
│ 自定义规则：检测到/未检测到                 │
│ DAILY_INSPECTION.md：存在/不存在           │
└────────────────────────────────────────────┘
```

---

## 步骤 2：备份

**目标**：备份所有将被修改或删除的文件，确保可回滚。

**执行命令**（PowerShell）：
```powershell
# 2.1 创建备份目录（YYYYMMDD 替换为当前日期）
$backupDir = "$aosRoot\99_ARCHIVE\pre_update_1.1.0_20260625"
New-Item -ItemType Directory -Path $backupDir -Force

# 2.2 备份将被修改的文件（保持相对路径结构）
$filesToBackup = @(
    "AGENTS.md",
    "00_BOOT\SYSTEM_STATE.md",
    "00_BOOT\CORE.md",
    "00_BOOT\DAILY_INSPECTION.md",
    "README.md",
    "04_MEMORY\INDEX.md",
    "04_MEMORY\project\proj_aos_v1_status.md",
    "09_REFERENCE\_index.md",
    "docs\index.html",
    "docs\AOS_creative_proposal.html",
    "09_REFERENCE\web\web-template-specification.md"
)
foreach ($file in $filesToBackup) {
    $src = "$aosRoot\$file"
    $dst = "$backupDir\$file"
    if (Test-Path $src) {
        New-Item -ItemType Directory -Path (Split-Path $dst) -Force | Out-Null
        Copy-Item -Path $src -Destination $dst -Force
        Write-Host "已备份: $file"
    } else {
        Write-Host "警告: 文件不存在，跳过: $file" -ForegroundColor Yellow
    }
}

# 2.3 生成备份清单（含 MD5）
Get-ChildItem -Path $backupDir -Recurse -File | ForEach-Object {
    $hash = (Get-FileHash -Path $_.FullName -Algorithm MD5).Hash
    [PSCustomObject]@{
        Path = $_.FullName.Replace($backupDir, "")
        MD5 = $hash
        BackupTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
} | ConvertTo-Json | Out-File -FilePath "$backupDir\backup_manifest.json" -Encoding utf8
```

**产出**：备份目录路径 `99_ARCHIVE/pre_update_1.1.0_YYYYMMDD/` + `backup_manifest.json`

**进度摘要**：
```
┌─ [步骤 2/8] 备份 ─────────────────────────┐
│ 状态：完成 ✓                               │
│ 备份路径：99_ARCHIVE/pre_update_1.1.0_...  │
│ 备份文件数：N                              │
│ 清单文件：backup_manifest.json             │
└────────────────────────────────────────────┘
```

---

## 步骤 3：获取 1.1.0 文件（三选一）

**目标**：获取 1.1.0 官方文件，为合并提供"1.1.0 官方版"参考。

⚠️ **请用户选择以下 3 种方式之一**（弹窗询问）：

### 方式 A：GitHub Release 下载（推荐，需联网）

**下载地址**：https://github.com/MagicalYuYu/agent-operating-system/releases/tag/v1.1.0

**发布包内容**：
- `AOS_Viewer_v1.1.0.zip`（PyInstaller 打包的桌面应用，约 50MB，可选）
- `aos-1.1.0-source.zip`（源码包，含完整框架文件，**必需**）
- `AOS_UPDATE_PROMPT_1.1.0.md`（本文件）
- `ReleaseNotes_1.1.0.md`（变更日志）

**执行命令**（PowerShell，下载源码包并解压）：
```powershell
# 3.A.1 下载源码包
$url = "https://github.com/MagicalYuYu/agent-operating-system/releases/download/v1.1.0/aos-1.1.0-source.zip"
$zipPath = "$aosRoot\05_CACHE\aos-1.1.0-source.zip"
New-Item -ItemType Directory -Path "$aosRoot\05_CACHE" -Force | Out-Null
Invoke-WebRequest -Uri $url -OutFile $zipPath

# 3.A.2 解压到临时目录
$updateDir = "$aosRoot\05_CACHE\aos_1.1.0_update"
Expand-Archive -Path $zipPath -DestinationPath $updateDir -Force
Write-Host "1.1.0 文件已解压到: $updateDir"
```

### 方式 B：git clone 命令（需 Git，可获取完整仓库）

**执行命令**（PowerShell）：
```powershell
# 3.B.1 浅克隆 v1.1.0 分支
$updateDir = "$aosRoot\05_CACHE\aos_1.1.0_update"
git clone --depth 1 --branch v1.1.0 https://github.com/MagicalYuYu/agent-operating-system.git $updateDir

# 3.B.2 验证克隆成功
if (Test-Path "$updateDir\AGENTS.md") {
    Write-Host "克隆成功: $updateDir"
} else {
    Write-Host "克隆失败，请检查网络或分支名" -ForegroundColor Red
}
```

### 方式 C：从本地已同步的 GitHub 目录读取（无需联网）

**适用场景**：用户已在本地 GitHub 目录同步过 1.1.0 版本。

**执行命令**（PowerShell）：
```powershell
# 3.C.1 检查本地 GitHub 目录（用户根据实际路径修改）
$githubDir = "C:\path\to\your\github\agent-operating-system"  # 替换为你的实际路径
if (Test-Path "$githubDir\AGENTS.md") {
    # 3.C.2 验证版本号
    $versionMatch = Select-String -Path "$githubDir\00_BOOT\SYSTEM_STATE.md" -Pattern "1\.1\.0"
    if ($versionMatch) {
        # 3.C.3 复制到临时目录（避免直接操作 GitHub 目录）
        $updateDir = "$aosRoot\05_CACHE\aos_1.1.0_update"
        New-Item -ItemType Directory -Path $updateDir -Force | Out-Null
        robocopy $githubDir $updateDir /E /XD .git /XF *.log
        Write-Host "已从本地 GitHub 目录复制到: $updateDir"
    } else {
        Write-Host "本地 GitHub 目录版本非 1.1.0，请先 git pull" -ForegroundColor Red
    }
} else {
    Write-Host "本地 GitHub 目录不存在: $githubDir" -ForegroundColor Red
}
```

**产出**：`05_CACHE/aos_1.1.0_update/` 目录（含 1.1.0 完整文件，作为"1.1.0 官方版"参考）

**进度摘要**：
```
┌─ [步骤 3/8] 获取 1.1.0 文件 ──────────────┐
│ 状态：完成 ✓                               │
│ 获取方式：A/B/C                            │
│ 临时目录：05_CACHE/aos_1.1.0_update/       │
│ 文件完整性：已验证/异常                    │
└────────────────────────────────────────────┘
```

---

## 步骤 4：合并修改文件（关键步骤，分级处理）

**目标**：按分级合并策略处理 24 新增 + 12 修改 + 1 删除文件。

### 4.1 分级合并策略总览

| 级别 | 处理方式 | 适用文件 | 数量 |
|------|----------|----------|------|
| L1 直接覆盖 | 从 1.1.0 临时目录复制（1.0.0 不存在） | 新增文件 | 24 |
| L2 智能合并 | 三向比对（用户版 / 1.0.0 官方版 / 1.1.0 官方版） | 1.0.0 已存在的修改文件 | 12 |
| L3 删除迁移 | 删除文件并确认内容已迁移 | 删除文件 | 1 |

### 4.2 L1 直接覆盖：24 个新增文件

**执行命令**（PowerShell）：
```powershell
$updateDir = "$aosRoot\05_CACHE\aos_1.1.0_update"
$aosRoot = "$aosRoot"

# 新增文件清单（相对路径）
$newFiles = @(
    "03_TOOLS\aos_viewer\README.md",
    "03_TOOLS\aos_viewer\aos_viewer_server.py",
    "03_TOOLS\aos_viewer\aos_viewer.spec",
    "03_TOOLS\aos_viewer\aos_viewer.ico",
    "03_TOOLS\aos_viewer\prototype\index.html",
    "03_TOOLS\aos_viewer\prototype\favicon.ico",
    "03_TOOLS\aos_viewer\prototype\css\style.css",
    "03_TOOLS\aos_viewer\prototype\js\app.js",
    "03_TOOLS\aos_viewer\prototype\js\data.js",
    "03_TOOLS\aos_viewer\prototype\js\data_content.js",
    "03_TOOLS\aos_viewer\prototype\js\i18n.js",
    "03_TOOLS\aos_viewer\prototype\previews\README.md",
    "03_TOOLS\aos_viewer\prototype\previews\a_cyber_archive.html",
    "03_TOOLS\aos_viewer\prototype\previews\b_terminal_organism.html",
    "03_TOOLS\aos_viewer\prototype\previews\c_oriental_void.html",
    "03_TOOLS\aos_viewer\prototype\previews\index.html",
    "03_TOOLS\scripts\aos_generate_data.py",
    "07_EXPORTS\aos_viewer\example_data.js",
    "07_EXPORTS\aos_viewer\AOS_UPDATE_PROMPT_1.1.0.md",
    "07_EXPORTS\aos_viewer\MIGRATION_GUIDE_1.1.0.md",
    "07_EXPORTS\aos_viewer\CHANGELOG_1.1.0.md",
    "07_EXPORTS\aos_viewer\FILE_MANIFEST_1.1.0.json",
    "00_BOOT\SYSTEM_INSPECTION.md",
    "00_BOOT\PROJECT_INSPECTION.md"
)

$copiedCount = 0
foreach ($file in $newFiles) {
    $src = "$updateDir\$file"
    $dst = "$aosRoot\$file"
    if (Test-Path $src) {
        New-Item -ItemType Directory -Path (Split-Path $dst) -Force | Out-Null
        Copy-Item -Path $src -Destination $dst -Force
        $copiedCount++
    } else {
        Write-Host "警告: 源文件缺失: $file" -ForegroundColor Yellow
    }
}
Write-Host "已复制 $copiedCount / 24 个新增文件"
```

**⚠️ 特殊处理**：
- `data.js`：1.1.0 临时目录中的 `data.js` 可能是脱敏版（`example_data.js` 内容），步骤 6 会用 `aos_generate_data.py` 重新生成真实数据覆盖
- `data_content.js`：GitHub 上传版可能不含此文件（被排除），步骤 6 会自动生成
- `AOS_UPDATE_PROMPT_1.1.0.md`：即本文件，若用户已粘贴本提示词则无需覆盖

### 4.3 L2 智能合并：12 个修改文件（三向比对）

对每个 1.0.0 已存在的修改文件，读取三方版本进行比对：
- **用户版**：`$aosRoot\{path}`（用户当前文件）
- **1.0.0 官方版**：从备份或 GitHub v1.0.0 tag 获取（可参考步骤 2 备份）
- **1.1.0 官方版**：`$aosRoot\05_CACHE\aos_1.1.0_update\{path}`

**合并原则**：
- 用户自定义内容（用户有但 1.0.0 官方版没有）→ **保留**
- 1.1.0 新增内容（1.1.0 有但 1.0.0 没有）→ **追加**
- 1.1.0 修改内容（1.0.0 → 1.1.0 变更）→ **采用 1.1.0 版**
- 冲突内容（用户自定义与 1.1.0 新增重叠）→ **弹窗询问用户**

#### 4.3.1 AGENTS.md（最复杂，必须用户确认）

- 识别用户自定义规则（用户有但 1.0.0 官方版没有的内容）
- 识别 1.1.0 新增章节：
  - "项目内标准结构"（类型一单一项目 / 类型二项目集）
  - "禁止 `src/` 下嵌套同名目录"约束
  - "双机环境"章节（仅工作目录版保留，GitHub 上传版自动剥离）
- **合并策略**：保留用户自定义规则 + 追加 1.1.0 新增章节
- **特别注意**：1.1.0 的"项目内标准结构"更新需替换 1.0.0 的旧版结构描述
- **输出合并差异报告供用户确认**（新增 / 删除 / 修改 / 冲突）

#### 4.3.2 00_BOOT/SYSTEM_STATE.md

- 保留用户的运行时统计数字（Skill 数、任务数、记忆索引数等）
- 保留用户的事件日志（**不删除任何用户事件**）
- 追加 1.1.0 框架级事件：
  ```
  | 2026-06-XX | SYSTEM_RELEASE | v1.1.0 发布：新增 AOS Viewer 可视化界面 |
  | 2026-06-XX | SYSTEM_UPDATE | 巡检规范拆分：DAILY_INSPECTION → SYSTEM_INSPECTION + PROJECT_INSPECTION |
  ```
- 更新版本号 `1.0.0` → `1.1.0`
- 更新"最后更新"字段为当前日期

#### 4.3.3 00_BOOT/CORE.md

- 更新版本号 `1.0.0` → `1.1.0`
- 更新"最后更新"描述

#### 4.3.4 04_MEMORY/INDEX.md

- 保留用户的所有记忆索引条目（**不删除任何条目**）
- 更新 `proj-aos-v1-status` 条目的描述：版本号 `1.0.0` → `1.1.0`

#### 4.3.5 04_MEMORY/project/proj_aos_v1_status.md

- 保留用户的动态事实（已注册 Skill 数、记忆索引数等）
- 追加 1.1.0 新增字段：
  ```
  | AOS Viewer 状态 | v1.1.0 新增可视化界面 | 2026-06-XX |
  | AOS Viewer 功能 | Spotlight搜索+精准跳转+关键词高亮+MD正文搜索+菜单栏+下拉菜单+动效+无边框桌面窗口 | 2026-06-XX |
  ```
- 更新版本号 `1.0.0` → `1.1.0`（保留变更注释：`原为 1.0.0 首发，升级为 1.1.0 新增可视化界面`）
- 更新 GitHub 发布状态为 `v1.1.0 发布`
- 更新已知缺陷标题 `v1.0.0` → `v1.1.0`

#### 4.3.6 README.md

- 更新版本徽章 `1.0.0` → `1.1.0`
- 保留用户自定义内容（如有）

#### 4.3.7 09_REFERENCE/_index.md

- 保留用户的所有索引条目
- 1.1.0 追加 15 条 `private-collection-*` 索引（若用户已有则跳过；若无则追加）
- 同步脚本脱敏时剥离 `private_collection` 行（私有收藏不上传 GitHub）

#### 4.3.8 03_TOOLS/scripts/aos_generate_data.py

- 此文件在 4.2 已作为新增文件复制，此处仅确认 `fallback version` 为 `1.1.0`
- 若已是 `1.1.0` 则跳过

#### 4.3.9 docs/index.html

- 更新 `hero.badge` 版本号 `v1.0.0` → `v1.1.0`（共 3 处：zh-CN HTML + zh-CN i18n + en-US i18n）

#### 4.3.10 docs/AOS_creative_proposal.html

- 更新 `hero.badge` 版本号 `v1.0.0` → `v1.1.0`（共 3 处：zh-CN HTML + zh-CN i18n + en-US i18n）

#### 4.3.11 09_REFERENCE/web/web-template-specification.md

- 更新示例版本号 `v1.0.0` → `v1.1.0`

### 4.4 L3 删除迁移：1 个删除文件

#### 00_BOOT/DAILY_INSPECTION.md

- **删除原因**：拆分为 `SYSTEM_INSPECTION.md` + `PROJECT_INSPECTION.md`（4.2 已新增）
- **执行命令**（PowerShell）：
  ```powershell
  # 确认内容已迁移（检查新文件是否存在）
  if ((Test-Path "$aosRoot\00_BOOT\SYSTEM_INSPECTION.md") -and (Test-Path "$aosRoot\00_BOOT\PROJECT_INSPECTION.md")) {
      Remove-Item -Path "$aosRoot\00_BOOT\DAILY_INSPECTION.md" -Force
      Write-Host "已删除 DAILY_INSPECTION.md（内容已迁移）"
  } else {
      Write-Host "新文件未就绪，跳过删除" -ForegroundColor Yellow
  }
  ```
- **更新引用**：`AGENTS.md` 中"详细规则引用表"的巡检规范引用需更新为新路径（4.3.1 已处理）

**产出**：合并差异报告 + 用户确认记录 + 文件操作日志

**进度摘要**：
```
┌─ [步骤 4/8] 合并修改 ─────────────────────┐
│ 状态：完成 ✓                               │
│ L1 直接覆盖：24/24                         │
│ L2 智能合并：12/12（冲突 N 处已用户确认）  │
│ L3 删除迁移：1/1                           │
│ 保留用户自定义：N 处                       │
└────────────────────────────────────────────┘
```

---

## 步骤 5：版本号同步

**目标**：扫描所有 `.md` 和 `.json` 文件中的 `1.0.0` 版本引用，逐一更新为 `1.1.0`。

**执行命令**（PowerShell）：
```powershell
# 5.1 扫描所有含 1.0.0 的文件（排除归档/项目/缓存/沙箱）
$excludePaths = @("99_ARCHIVE", "01_PROJECTS", "05_CACHE", "02_SANDBOX", ".git")
$matches = Get-ChildItem -Path "$aosRoot" -Recurse -Include "*.md", "*.json", "*.html", "*.js", "*.py" -File |
    Where-Object { $excludePaths -notcontains ($_.FullName.Split("\")[-2]) } |
    ForEach-Object {
        $content = Get-Content $_.FullName -Raw
        if ($content -match "1\.0\.0") {
            [PSCustomObject]@{
                Path = $_.FullName.Replace("$aosRoot\", "")
                MatchCount = ([regex]::Matches($content, "1\.0\.0")).Count
            }
        }
    }
$matches | Format-Table -AutoSize
```

**14 处必须同步的文件位置**：

| 序号 | 文件路径 | 修改内容 |
|------|----------|----------|
| 1 | `00_BOOT/SYSTEM_STATE.md` | 版本字段 + 最后更新描述 |
| 2 | `00_BOOT/CORE.md` | 版本字段 |
| 3 | `README.md` | 版本徽章 |
| 4 | `04_MEMORY/INDEX.md` | proj-aos-v1-status 描述 |
| 5 | `04_MEMORY/project/proj_aos_v1_status.md` | 版本 + GitHub 发布状态 + 已知缺陷标题 |
| 6 | `03_TOOLS/aos_viewer/prototype/index.html` | `<title>` + 版本显示 |
| 7 | `03_TOOLS/aos_viewer/prototype/js/i18n.js` | `console.welcome` |
| 8 | `03_TOOLS/aos_viewer/prototype/js/app.js` | fallback version |
| 9 | `03_TOOLS/aos_viewer/aos_viewer_server.py` | fallback version |
| 10 | `03_TOOLS/aos_viewer/prototype/previews/*.html` | 系统版本（3 文件：a_cyber_archive / b_terminal_organism / c_oriental_void） |
| 11 | `docs/index.html` | hero.badge（zh-CN HTML + zh-CN i18n + en-US i18n，共 3 处） |
| 12 | `docs/AOS_creative_proposal.html` | hero.badge（zh-CN HTML + zh-CN i18n + en-US i18n，共 3 处） |
| 13 | `09_REFERENCE/web/web-template-specification.md` | 示例版本号 |
| 14 | `03_TOOLS/scripts/aos_generate_data.py` | fallback version |

**⚠️ 保留不动的场景**（**禁止修改**）：
- Skill 自身版本号（`config.json` 中的 `"version": "1.0.0"` 是 Skill 版本，非系统版本）
- 历史事件记录中的版本引用（如 `v1.0.0 GitHub首发版` 是历史事实，**不可篡改**）
- 归档文件（`99_ARCHIVE/` 下的所有文件，只读）
- 第三方项目文件（`01_PROJECTS/` 下的项目自有版本号）

**执行命令**（PowerShell，批量替换，需人工复核）：
```powershell
# 5.2 批量替换（仅针对上述 14 处文件，先备份再替换）
$filesToUpdate = @(
    "00_BOOT\SYSTEM_STATE.md",
    "00_BOOT\CORE.md",
    "README.md",
    "04_MEMORY\INDEX.md",
    "04_MEMORY\project\proj_aos_v1_status.md",
    "03_TOOLS\aos_viewer\prototype\index.html",
    "03_TOOLS\aos_viewer\prototype\js\i18n.js",
    "03_TOOLS\aos_viewer\prototype\js\app.js",
    "03_TOOLS\aos_viewer\aos_viewer_server.py",
    "03_TOOLS\aos_viewer\prototype\previews\a_cyber_archive.html",
    "03_TOOLS\aos_viewer\prototype\previews\b_terminal_organism.html",
    "03_TOOLS\aos_viewer\prototype\previews\c_oriental_void.html",
    "docs\index.html",
    "docs\AOS_creative_proposal.html",
    "09_REFERENCE\web\web-template-specification.md",
    "03_TOOLS\scripts\aos_generate_data.py"
)
foreach ($file in $filesToUpdate) {
    $path = "$aosRoot\$file"
    if (Test-Path $path) {
        $content = Get-Content $path -Raw
        # 仅替换系统版本号引用，保留历史事件中的版本号（需人工复核）
        $newContent = $content -replace "(?<!v)1\.0\.0(?!\d)", "1.1.0"
        Set-Content -Path $path -Value $newContent -NoNewline -Encoding utf8
        Write-Host "已更新: $file"
    }
}
```

**产出**：版本号同步报告（14 处文件 + 保留场景清单）

**进度摘要**：
```
┌─ [步骤 5/8] 版本号同步 ───────────────────┐
│ 状态：完成 ✓                               │
│ 已同步文件：14                             │
│ 保留不动：Skill 版本/历史事件/归档          │
│ 待人工复核：N 处（历史事件中的版本引用）    │
└────────────────────────────────────────────┘
```

---

## 步骤 6：生成 data.js

**目标**：运行数据生成脚本，扫描 AOS 文件系统生成 `data.js` 供 AOS Viewer 加载。

**执行命令**（PowerShell）：
```powershell
# 6.1 运行数据生成脚本
Set-Location "$aosRoot"
python "03_TOOLS\scripts\aos_generate_data.py"

# 6.2 验证 data.js 生成
$dataJs = "$aosRoot\03_TOOLS\aos_viewer\prototype\js\data.js"
if (Test-Path $dataJs) {
    $content = Get-Content $dataJs -Raw
    if ($content -match '"version"\s*:\s*"1\.1\.0"') {
        Write-Host "data.js 生成成功，版本号正确: 1.1.0" -ForegroundColor Green
    } else {
        Write-Host "data.js 生成但版本号异常" -ForegroundColor Yellow
    }
} else {
    Write-Host "data.js 生成失败" -ForegroundColor Red
}
```

**产出**：`03_TOOLS/aos_viewer/prototype/js/data.js`（含真实 AOS 数据）

**进度摘要**：
```
┌─ [步骤 6/8] 生成 data.js ─────────────────┐
│ 状态：完成 ✓                               │
│ data.js 路径：03_TOOLS/aos_viewer/.../data.js │
│ 版本字段：1.1.0                            │
│ 数据条目：系统/Skill/项目/记忆/知识 N 条    │
└────────────────────────────────────────────┘
```

---

## 步骤 7：一致性自检

**目标**：运行自检脚本，修复所有不一致项。

**执行命令**（PowerShell）：
```powershell
# 7.1 运行一致性自检
Set-Location "$aosRoot"
python "03_TOOLS\scripts\aos_check.py"

# 7.2 若自检失败，根据报告修复
# 常见不一致项：
# - 版本号残留（步骤 5 遗漏）
# - 引用完整性（DAILY_INSPECTION.md 引用未更新）
# - 索引对应性（_index.md 与实际文件不一致）
# - 目录合规性（文件未按 AOS 目录约束存放）
```

**自检项清单**：
- [ ] 版本号一致性：扫描残留的 `1.0.0` 引用（排除 `99_ARCHIVE/`、`01_PROJECTS/`）
- [ ] 引用完整性：`DAILY_INSPECTION.md` 引用已更新为 `SYSTEM_INSPECTION.md` + `PROJECT_INSPECTION.md`
- [ ] 索引对应性：`09_REFERENCE/_index.md` 条目与实际文件一一对应
- [ ] 目录合规性：新增文件已按 AOS 目录约束存放（`aos_viewer/` 在 `03_TOOLS/`，`example_data.js` 在 `07_EXPORTS/`）
- [ ] Skill 注册：若 `aos_viewer` 作为 Skill 注册，需在 `00_BOOT/SKILL_REGISTRY.md` 添加条目

**产出**：自检报告（通过 / 失败 + 不一致项清单）

**进度摘要**：
```
┌─ [步骤 7/8] 一致性自检 ───────────────────┐
│ 状态：PASS / FAIL                          │
│ 不一致项：N（已修复 / 待修复）             │
│ 自检报告路径：05_CACHE/aos_check_report.txt │
└────────────────────────────────────────────┘
```

---

## 步骤 8：清理与验证

**目标**：清理临时文件，验证 AOS Viewer 正常工作，输出更新摘要。

### 8.1 清理临时目录

**执行命令**（PowerShell）：
```powershell
# 8.1.1 删除临时下载目录
Remove-Item -Path "$aosRoot\05_CACHE\aos_1.1.0_update" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$aosRoot\05_CACHE\aos-1.1.0-source.zip" -Force -ErrorAction SilentlyContinue
Write-Host "临时目录已清理"

# 8.1.2 保留备份目录（用户可手动清理）
Write-Host "备份目录保留: 99_ARCHIVE\pre_update_1.1.0_20260625\"
```

### 8.2 验证 AOS Viewer 正常工作

**执行命令**（PowerShell）：

```powershell
# 安装依赖（首次使用）
pip install pywebview

# 启动桌面应用
Set-Location "$aosRoot"
python "03_TOOLS\aos_viewer\aos_viewer_server.py" --mode desktop
# 验证：窗口启动后，确认标题栏/版本号显示 1.1.0
```

**验证清单**：
- [ ] AOS Viewer 启动无报错
- [ ] 版本号显示 `1.1.0`（标题栏 / 系统总览页）
- [ ] 系统总览页加载 data.js 数据正常（项目数 / Skill 数 / 记忆索引数）
- [ ] Spotlight 搜索功能可用（搜索"AOS Viewer"应能命中）
- [ ] 中英文切换正常（i18n）
- [ ] 控制台欢迎语显示 `v1.1.0`

### 8.3 输出更新摘要

**最终摘要**：
```
┌─ AOS 1.1.0 更新完成 ──────────────────────┐
│ 新增文件：24                               │
│ 修改文件：12                               │
│ 删除文件：1                                │
│ 保留用户自定义：N 处                       │
│ 版本号同步：14 处文件                      │
│ 备份路径：99_ARCHIVE/pre_update_1.1.0_...  │
│ 自检结果：PASS                             │
│ AOS Viewer：正常 / 异常                    │
│                                            │
│ 启动方式：                                 │
│   python 03_TOOLS/aos_viewer/aos_viewer_server.py --mode desktop │
└────────────────────────────────────────────┘
```

---

## 风险提示（Agent 必须向用户说明）

1. **AGENTS.md 合并冲突**：用户自定义规则与 1.1.0 新规则位置重叠时，需用户确认合并方向（保留用户版 / 采用 1.1.0 版 / 手动合并）
2. **版本号同步遗漏**：第三方项目中的 `1.0.0` 字符串可能被误改，`aos_check.py` 已排除 `01_PROJECTS/` 但需用户复核
3. **历史事件版本号**：SYSTEM_STATE.md 等文件中历史事件记录的 `v1.0.0 GitHub首发版` 是历史事实，**禁止修改**，仅修改当前版本字段
4. **Python 环境异常**：`aos_generate_data.py` 可能因 Python 版本 / 依赖缺失失败，需排查方向：
   - Python 3.8+ 要求
   - 无第三方依赖（纯标准库）
   - 路径权限
5. **备份空间**：备份目录占用磁盘空间，建议用户验证更新成功后定期清理 `99_ARCHIVE/` 下的旧备份
6. **AOS Viewer 依赖**：桌面模式需 `pip install pywebview`
7. **data.js 脱敏**：1.1.0 临时目录中的 `data.js` 可能是脱敏版，必须运行步骤 6 重新生成真实数据
8. **双机环境章节**：AGENTS.md 的"双机环境"章节仅工作目录版保留，更新时需保留此章节

---

## 用户确认环节（Agent 必须执行）

以下决策点必须弹窗询问用户，**不可自动决策**：

1. **步骤 3**：选择文件获取方式（A：GitHub Release / B：git clone / C：本地 GitHub 目录）
2. **步骤 4.3.1**：AGENTS.md 合并差异报告 → 用户确认是否接受合并结果
3. **步骤 4.3.5**：`proj_aos_v1_status.md` 是否保留用户的"1.1.0 发布策略"行（含内部报告引用，建议删除）
4. **步骤 5**：版本号同步后，人工复核历史事件中的版本引用是否被误改
5. **步骤 7**：自检失败时 → 用户确认是否手动修复或回滚

---

## 回滚方案

如果更新失败或用户不满意：

**执行命令**（PowerShell）：
```powershell
# 1. 停止所有 AOS Viewer 进程
Get-Process -Name "python*" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "aos_viewer" } | Stop-Process -Force

# 2. 从备份恢复
$backupDir = "$aosRoot\99_ARCHIVE\pre_update_1.1.0_20260625"
$filesToRestore = @(
    "AGENTS.md",
    "00_BOOT\SYSTEM_STATE.md",
    "00_BOOT\CORE.md",
    "00_BOOT\DAILY_INSPECTION.md",
    "README.md",
    "04_MEMORY\INDEX.md",
    "04_MEMORY\project\proj_aos_v1_status.md",
    "09_REFERENCE\_index.md",
    "docs\index.html",
    "docs\AOS_creative_proposal.html",
    "09_REFERENCE\web\web-template-specification.md"
)
foreach ($file in $filesToRestore) {
    $src = "$backupDir\$file"
    $dst = "$aosRoot\$file"
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $dst -Force
        Write-Host "已恢复: $file"
    }
}

# 3. 删除新增文件
Remove-Item -Path "$aosRoot\03_TOOLS\aos_viewer" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$aosRoot\03_TOOLS\scripts\aos_generate_data.py" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$aosRoot\00_BOOT\SYSTEM_INSPECTION.md" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$aosRoot\00_BOOT\PROJECT_INSPECTION.md" -Force -ErrorAction SilentlyContinue
# 07_EXPORTS/aos_viewer/ 下的发布文档可保留或删除

# 4. 运行自检验证回滚
python "$aosRoot\03_TOOLS\scripts\aos_check.py"
```

**回滚检查清单**：
- [ ] 所有修改文件已恢复到 1.0.0 状态
- [ ] 新增文件已删除
- [ ] `DAILY_INSPECTION.md` 已恢复
- [ ] `aos_check.py` 自检通过（版本号回 1.0.0）

---

## 兼容性说明

| Agent 平台 | 兼容性 | 说明 |
|------------|--------|------|
| Trae CODE 模式 | ✅ 最佳 | AOS 1.1.0 主适配平台，工具链完整 |
| Claude Code | ✅ 兼容 | 需手动指定 AOS 根目录 |
| Codex | ✅ 兼容 | 需手动指定 AOS 根目录 |
| 其他 Agent | ⚠️ 需验证 | 需支持文件读写 + 命令执行 + 弹窗交互能力 |

**环境要求**：
- Python 3.8+（`aos_generate_data.py` / `aos_check.py` / `aos_viewer_server.py`）
- PowerShell 5.1+（命令示例基于 PowerShell）
- Git（仅方式 B 需要）
- pywebview（AOS Viewer 桌面模式必需）

---

## 附：完整文件清单参考

详细文件清单见 `07_EXPORTS/aos_viewer/FILE_MANIFEST_1.1.0.json`，本提示词已嵌入关键信息。如需查看每个文件的脱敏方式和具体变更，请参考该 JSON 文件。

---

*本提示词由 AOS 1.1.0 发布包提供，随版本更新维护。*
*GitHub：https://github.com/MagicalYuYu/agent-operating-system/releases/tag/v1.1.0*
