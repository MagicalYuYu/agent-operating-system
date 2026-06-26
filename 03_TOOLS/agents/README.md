# AOS v1.1.0 — 03_TOOLS/agents

> Agent定义与配置的存储根目录

---

## 目录规范

```
03_TOOLS/agents/
└── agent_name/
    ├── AGENT.md       # Agent定义、能力、约束
    ├── config.json    # Agent配置
    └── prompts/       # Agent专用提示词模板
```

---

## Agent 类型

| 类型 | 职责 | 核心约束 |
|------|------|----------|
| Maker | 生成内容/修改代码 | 禁止自我验证 |
| Checker | 审查/验证/找bug | 禁止直接修改产出 |
| Planner | 拆解任务/生成计划 | 禁止直接执行 |
| Executor | 执行工具/文件操作 | 必须按计划执行 |

---

## 当前注册 Agent

（空 — 等待任务触发创建）
