# AOS v1.1.0 — Loop Engine

> 单次触发式 Agent 的循环执行引擎

---

## 执行模型认知（强制）

**Loop 不是后台常驻进程，而是单次触发执行的闭环模式。**

- 每轮 Loop 执行 = 一次独立的 stateless execution
- 状态延续完全依赖文件系统（state.json / checkpoint.md）
- 不存在自动后台轮询，所有 Loop 必须显式触发
- Loop 的"循环"语义 = 可重复执行的模式，而非持续运行

---

## 三种 Loop 类型

### 1. Goal Loop（目标循环）

- 定义：设定目标条件，单次会话内迭代执行直到达成
- 触发：用户设定目标
- 状态：state.json 记录进度，会话中断后可手动 resume
- 限制：max_iterations 防止无限循环（熔断机制）

### 2. Scheduled Loop（定时循环）

- 定义：通过 Trae Schedule 工具（cron）定时触发新会话
- 触发：cron 表达式（最小间隔 10 分钟）
- 状态：state.json 跨会话延续
- 每次触发 = 一次独立的 AOS 会话

### 3. Event Loop（事件循环）

- 定义：文件变化/条件触发时执行
- 触发：当前为手动触发（Trae 不支持 Hook 自动触发）
- 状态：state.json 记录上次执行时间和结果
- 未来：Trae 支持 Hook 后可自动触发

---

## 可视化执行规范（强制）

所有 Loop 执行必须向用户展示完整过程：

```
┌─ Loop: LP_0001 [Goal Loop] ──────────────────┐
│ 目标：所有 URL 处理完毕且索引已更新            │
│ 进度：3/5 轮 | 状态：执行中 ●                  │
│ 本轮：处理 reference-03-source-code.md          │
│ 耗时：已用 45s | 预计剩余：30s                 │
│ 产出：09_REFERENCE/system/reference-03-*.md     │
│ 熔断：max_iterations=10, error_count=0         │
└───────────────────────────────────────────────┘
```

---

## 熔断机制（强制）

- Goal Loop：max_iterations 上限，超出暂停并通知用户
- Scheduled Loop：error_count 超过阈值暂停，下次触发前检查
- 任何 Loop 连续 3 次失败必须暂停，等待用户确认

---

## 详细设计

完整的 state.json 结构、resume 机制、Scheduled Loop 配置方式见：
`09_REFERENCE/system/aos-loop-engine-v2.md`
