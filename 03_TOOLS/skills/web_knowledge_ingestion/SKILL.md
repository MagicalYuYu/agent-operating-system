# Web Knowledge Ingestion Skill (WKIS)

> AOS Skill — 网页知识抓取与入库

---

## 决策规则

1. URL 抓取失败不阻塞其他 URL
2. 入库前必须检查 `_index.md` 防重复
3. 已存在文件不可静默覆盖，必须确认
4. 知识只存 `09_REFERENCE/`，项目通过索引引用
5. System Level 知识优先归类到 `09_REFERENCE/system/`
6. raw 层必须存完整原文（去HTML标签后），不允许压缩
7. 知识库层必须保留论证链条、代码示例、配置参数、坑点完整说明，禁止只留结论
8. 每个步骤必须可视化展示执行过程，禁止后台静默运行

---

## 坑点

| 坑点 | 规避方式 |
|------|----------|
| WebFetch 超时/拒绝 | 失败不阻塞，记录原因 |
| 内容截断 | 检查完整性，不完整时标注 |
| 重复入库 | 检查 _index.md 中 source_url |
| slug 冲突 | 加入 domain 前缀区分 |
| 图片链接失效 | 仅保留 URL 引用，不下载 |
| 过度压缩 | raw层存完整原文，知识库层保留论证链条和代码示例 |
| description写成摘要 | 必须写触发条件而非摘要，不超过250字符 |

---

## 输出路径映射

| 类型 | 路径 |
|------|------|
| 原始抓取 | `08_INBOX/raw/{YYYYMMDD}_{domain_slug}.md` |
| Web 知识 | `09_REFERENCE/web/{topic_slug}.md` |
| System 知识 | `09_REFERENCE/system/{topic_slug}.md` |
| 元数据 | `{target_dir}{topic_slug}.metadata.json` |
| 索引 | `09_REFERENCE/_index.md` |

---

## 演化记录

| 时间 | 变更类型 | 描述 |
|------|----------|------|
| 2026-06-21 | CREATE | Skill 初始创建 |
| 2026-06-21 | PATCH | 新增决策规则#6#7：raw层存完整原文，知识库层禁止过度压缩 |
| 2026-06-21 | V2.2 | 重构：description改为触发条件式；新增可视化执行规范；新增决策规则#8；新增坑点：description写成摘要 |
