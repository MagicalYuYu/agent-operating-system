# AOS v1.0 - Loops 目录

> 可重复执行任务闭环的存储根目录

---

## 目录规范

每个Loop必须遵循以下结构：

```
03_TOOLS/loops/
└── loop_name/
    ├── LOOP.md          # Loop定义与决策规则
    ├── schedule.json    # 调度配置
    ├── state.json       # 当前状态（支持resume）
    └── checkpoint.md    # 检查点记录
```

---

## Loop 类型

| 类型 | 说明 | 触发方式 |
|------|------|----------|
| Interval | 定时循环 | 每 N 分钟/小时 |
| Goal | 目标循环 | 直到条件满足 |
| Event | 事件循环 | 文件变化/PR/API |

---

## 当前活跃 Loop

（空 — 等待任务触发创建）
