# AOS v1.0 - Inbox Pipeline

外部输入入口，所有外部输入必须先进这里。

## 应放什么
- raw/ — 原始抓取文件（WKIS 产出）
- migration/ — 迁移中转文件（采集/分类/入库的中间结果）

## 禁止放什么
- 已处理完毕的文件（处理后应迁移到正式目录或删除）
- 非输入类内容

## 处理流程
1. 外部内容进入 08_INBOX/
2. Agent 或脚本处理
3. 处理结果迁移到正式目录（09_REFERENCE/、01_PROJECTS/ 等）
4. 原始文件保留在 08_INBOX/raw/ 作为溯源依据

## 分层规则
- `raw/` 按日期分层存放：`08_INBOX/raw/{YYYYMMDD}/`
- `migration/` 按迁移批次存放：`08_INBOX/migration/`（已有结构）
