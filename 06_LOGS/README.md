# AOS v1.1.0 — 06_LOGS

运行日志存放区，只追加不修改。

## 应放什么

- Agent 操作日志
- 巡检日志（系统级 / 项目级）
- 外部组件运行日志（如 Docker 容器日志、NSSM 服务日志）

## 禁止放什么

- 项目源代码
- 运行时状态（应放 04_MEMORY/）
- 临时数据（应放 05_CACHE/）
- 最终交付文件（应放 07_EXPORTS/）

## 分层规则

按"项目名 → 模块名 → 类型 → 日期"分层存放：

```
06_LOGS/
├── aos_system/                    ← 系统级日志
│   └── inspection/
│       └── {YYYYMMDD}_system.md   ← 系统级巡检日志
├── {project_name}/                ← 项目级日志（按项目名分层）
│   └── inspection/
│       └── {YYYYMMDD}_project.md  ← 项目级巡检日志
└── README.md
```

## 文件命名规范

- 日期格式：`YYYYMMDD`（如 `20260626`）
- 巡检日志：`{YYYYMMDD}_system.md` / `{YYYYMMDD}_project.md`
- 其他日志：`{YYYYMMDD}_{描述}.md`

## 注意

- 日志文件**只追加不修改**
- 文件名中的日期统一使用 `YYYYMMDD` 格式
- 系统级日志使用 `aos_system/` 作为第 2 层目录
