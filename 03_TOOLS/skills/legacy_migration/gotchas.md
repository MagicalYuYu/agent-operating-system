# SK_0002 坑点清单 — Legacy Migration

> 持续积累——每次 Agent 踩坑就补入

---

## 采集阶段

| # | 坑点 | 原因 | 规避方式 | 发现时间 |
|---|------|------|----------|----------|
| 1 | Trae对话无法通过API批量导出 | Trae无对话导出API | 用户需逐个窗口粘贴预设提示词，手动复制结果 | 2026-06-21 |
| 2 | 对话上下文过长导致提取不完整 | Agent可能截断长对话 | 分段提取，每段不超过2000字 | 2026-06-21 |
| 3 | 项目目录含大量node_modules等依赖 | 扫描耗时且无价值 | 排除常见依赖目录（node_modules/.git/venv等） | 2026-06-21 |

## 分类阶段

| # | 坑点 | 原因 | 规避方式 | 发现时间 |
|---|------|------|----------|----------|
| 4 | 同一知识在多个对话中重复出现 | 多次讨论同一主题 | 去重合并，保留最完整版本 | 2026-06-21 |
| 5 | 分类边界模糊 | 经验和知识难以区分 | 不确定的放入02_SANDBOX/migration_pending/ | 2026-06-21 |

## 入库阶段

| # | 坑点 | 原因 | 规避方式 | 发现时间 |
|---|------|------|----------|----------|
| 6 | 敏感信息遗漏 | 脱敏规则不完整 | 使用正则+关键词双重扫描 | 2026-06-21 |
| 7 | 目标路径已存在文件 | 迁移内容与现有内容冲突 | 不覆盖，向用户确认后合并或重命名 | 2026-06-21 |

## 跨平台

| # | 坑点 | 原因 | 规避方式 | 发现时间 |
|---|------|------|----------|----------|
| 8 | Claude Code的CLAUDE.md与AOS的AGENTS.md格式不同 | 不同系统的规则格式差异 | 统一转为AOS格式，规则写入Trae Rules | 2026-06-21 |
| 9 | ChatGPT对话无法直接提取 | 无API，纯Web界面 | 用户手动复制对话内容到08_INBOX/migration/ | 2026-06-21 |

## Windows 服务与 Docker

| # | 坑点 | 原因 | 规避方式 | 发现时间 |
|---|------|------|----------|----------|
| 10 | NSSM服务注册表路径未更新 | 迁移后Windows服务ImagePath仍指向旧目录 | 使用`nssm edit <service>`或修改注册表`HKLM\SYSTEM\CurrentControlSet\Services\<service>`下的ImagePath/Application/AppDirectory，需管理员权限 | 2026-06-21 |
| 11 | Docker bind mount绝对路径硬编码 | 容器的-v参数中主机路径是绝对路径，迁移后路径变更 | 必须`docker stop <container> && docker rm <container>`后重新`docker run`，更新-v参数中的主机路径部分 | 2026-06-21 |
| 12 | Docker Compose工作目录切换 | `docker compose down`必须在docker-compose.yml所在旧目录执行 | 先在旧目录执行`docker compose down`，确认容器停止后，在新目录执行`docker compose up -d` | 2026-06-21 |
| 13 | PowerShell 5.1默认GBK编码 | Windows PowerShell 5.1的$OutputEncoding默认为GBK，含中文的脚本输出乱码 | 脚本文件使用纯ASCII或UTF-8 BOM编码；运行前执行`$OutputEncoding = [System.Text.Encoding]::UTF8`；或使用PowerShell 7+ | 2026-06-21 |
| 14 | $ErrorActionPreference="Stop"与Docker CLI冲突 | Docker CLI将进度信息输出到stderr，PowerShell误判为终止错误 | 对Docker命令单独设置`$ErrorActionPreference = "Continue"`，或使用`2>$null`重定向stderr | 2026-06-21 |
| 15 | NSSM服务需提权脚本批量更新 | 多个NSSM服务的注册表路径需逐一修改，手动操作易遗漏 | 编写提权PowerShell脚本批量扫描并更新所有NSSM服务的ImagePath/Application/AppDirectory字段 | 2026-06-21 |
