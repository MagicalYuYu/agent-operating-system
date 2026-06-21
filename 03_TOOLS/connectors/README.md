# AOS v1.0 - Connectors 目录

> 外部系统连接器的存储根目录

---

## 目录规范

```
03_TOOLS/connectors/
└── connector_name/
    ├── CONNECTOR.md    # 连接器定义与配置说明
    ├── config.json     # 连接参数（脱敏）
    └── scripts/        # 连接脚本
```

---

## 支持的连接器类型

| 类型 | 说明 | 示例 |
|------|------|------|
| API | REST/GraphQL接口 | GitHub API, Notion API |
| Database | 数据库连接 | PostgreSQL, MongoDB |
| File | 文件系统监控 | 本地目录, S3 |
| Message | 消息队列 | Webhook, SSE |

---

## 当前已配置 Connector

（空 — 等待需求触发创建）
