# 09_REFERENCE — 唯一参考知识库

每份知识只存一份（铁律 3：Reference 唯一化），他处只写路径引用，禁止复制内容；`research/` 存调研成果。

入库走 knowledge-ingest skill：文件头部写来源 URL、抓取日期、可信度备注；`_index.md` 加一行指针（主题 + 一句话 hook），超 200 行启用父子索引。

示例：`09_REFERENCE/web/http-caching.md` + `_index.md` 一行：`- [http-caching](web/http-caching.md) — 缓存策略速查（官方文档核对，2026-10）`
