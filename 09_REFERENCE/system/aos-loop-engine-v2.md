# AOS v1.0 Loop Engine 详细设计

> 来源：AOS内部设计
> 入库时间：2026-06-21T16:00:00+08:00
> 主题：Loop Engine 单次触发适配、三种Loop类型、状态延续与熔断机制
> 标签：aos, loop, engine, scheduled, goal, visualization
> 引用依据：相关参考（Loop Engineering）、相关参考（Query Loop）、相关参考（多Agent）、相关参考（Harness Engineering）

---

## TL;DR

- AOS Loop Engine 基于**单次触发式执行模型**：每次触发只执行一轮，状态靠文件系统（state.json）延续，不依赖运行时内存
- 三种 Loop 类型：**Goal Loop**（单次会话内迭代）、**Scheduled Loop**（Trae Schedule cron 跨会话触发）、**Event Loop**（当前手动触发，未来 Hook 适配）
- state.json 是 Loop 的唯一状态载体：记录 loop_id、loop_type、status、current_cycle、resume_context、next_action 等完整状态
- 可视化执行规范：每个步骤必须展示步骤编号/总数、操作名称、状态、目标、耗时、产出路径
- 熔断机制：max_iterations 上限、error_count 阈值、连续3次失败自动暂停
- Scheduled Loop 通过 Trae Schedule 工具配置 cron 表达式，message 字段携带完整上下文模板，实现跨会话状态延续
- Agent 会忘，文件不会——所有 Loop 状态必须落盘

---

## 核心概念

### 执行模型认知：单次触发式，状态靠文件系统延续

AOS 的 Loop Engine 不是传统意义上的"循环"——没有 while(true) 的持续运行循环。每次触发只执行**一轮迭代**，执行完毕后状态写入 state.json，等待下一次触发继续。这种设计适配 AOS 单次触发式 Agent 的本质。

**与传统 Loop 的区别**：

| 维度 | 传统 Loop | AOS Loop Engine |
|------|-----------|-----------------|
| 执行模型 | while(true) 持续运行 | 单次触发，状态落盘 |
| 状态存储 | 运行时内存 | 文件系统 state.json |
| 触发方式 | 自动循环 | 显式触发（cron/goal/event） |
| 上下文 | 单一会话持续 | 跨会话，每次从磁盘恢复 |
| 崩溃恢复 | 需要检查点机制 | 天然支持，状态已在磁盘 |

> 引用依据：相关参考 明确"Agent 会忘，文件不会——需要磁盘级状态文件记录进度，不能依赖上下文窗口"；相关参考 详解 Query Loop 是 while(true) + tool_use/end_turn 判断，但 AOS 的单次触发模型决定了不能复用这种持续循环模式。

### 三种 Loop 类型

#### Goal Loop：单次会话内迭代

**定义**：用户设定一个目标，Agent 在单次会话内反复迭代直到目标达成或达到上限。

**触发方式**：用户通过 `/goal` 命令或 AGENTS.md 中的 goal_condition 触发。

**执行流程**：
1. 创建 state.json，设定 goal_condition 和 max_iterations
2. 每轮迭代：检查 goal_condition → 执行操作 → 更新 state.json → 检查是否达成
3. 达成目标：status → completed，输出结果
4. 达到上限或失败：status → paused/failed，输出当前进度和 resume_context

**resume 机制**：当 Goal Loop 因上下文溢出或用户中断而暂停时，state.json 中的 resume_context 和 next_action 记录了"上次执行到哪里"和"下一步该做什么"。新会话启动时读取 state.json 即可从断点继续。resume 时用户需在新会话中明确指派（如："继续执行 LP_0001 Loop"），Agent 不会自动恢复。

**适用场景**：代码重构、批量文件修改、复杂调试等需要在单次会话内多次迭代的任务。

#### Scheduled Loop：通过 Trae Schedule cron 触发

**定义**：通过 Trae Schedule 工具配置 cron 表达式，定时触发 Agent 执行，实现跨会话状态延续。

**触发方式**：Trae Schedule 工具的 cron_expression 字段。

**执行流程**：
1. 首次配置：通过 Trae Schedule 创建定时任务，message 字段携带完整上下文模板
2. 每次触发：Schedule 工具按 cron 时间启动新会话，message 内容作为新会话的初始指令
3. 新会话启动：读取 state.json → 恢复上下文 → 执行一轮迭代 → 更新 state.json
4. 跨会话延续：每次触发都是新会话，但通过 state.json 实现状态无缝衔接

**适用场景**：每日代码审查、CI 监控与修复、技术债扫描、依赖升级检查等周期性任务。

#### Event Loop：当前手动触发，未来 Hook 适配

**定义**：由特定事件触发的 Loop，当前版本为手动触发，未来适配 Trae Hook 机制后可实现自动化。

**触发方式**：
- 当前：用户手动发起指令触发
- 未来：适配 Trae 的 Rules 机制（替代 Hook），在特定事件（如文件变更、Git 提交）时自动触发

**执行流程**：
1. 事件发生（当前为手动，未来为自动检测）
2. 读取对应 Loop 的 state.json
3. 执行一轮迭代
4. 更新 state.json

**适用场景**：代码提交后自动测试、Issue 创建时自动分析、文件变更时自动检查规范等事件驱动任务。

> 引用依据：相关参考 详解三种触发方式——定时触发（cron）、事件触发（hook）、目标触发（/goal）；相关参考 入门路径 Level 1 从 /goal 开始 → Level 2 加 hook 自动化 → Level 3 搭完整流水线。

---

## 运行时铁律（强制）

1. **状态更新是步骤的一部分**：Loop 的状态更新必须嵌入 Skill 步骤序列的最后一个强制步骤，不是可选的事后动作。Agent 不会"记得"在 Loop 结束后更新 state.json
2. **事前声明优于事后记录**：每轮 Loop 开始前声明"即将执行什么"并写入 state.json，执行本身就是完成证明
3. **禁止假设 Agent 会自觉更新**：如果设计依赖"Agent 在每轮 Loop 结束后主动更新 state.json"，则该设计不可靠。必须将状态更新作为 Skill 步骤的一部分
4. **Scheduled Loop 的 message 字段必须包含完整上下文**：因为每次 cron 触发都是全新会话，Agent 没有任何历史记忆

---

## 方法论 / 流程

### state.json 完整结构

```json
{
  "loop_id": "LP_0001",
  "loop_type": "goal",
  "status": "idle",
  "current_cycle": 0,
  "max_iterations": 10,
  "last_execution": null,
  "last_checkpoint": null,
  "error_count": 0,
  "resume_context": "上次执行到...",
  "next_action": "下一步操作...",
  "goal_condition": "目标条件描述",
  "artifacts": []
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| loop_id | string | Loop 唯一标识，格式 LP_XXXX |
| loop_type | string | Loop 类型：goal / scheduled / event |
| status | string | 当前状态：idle / running / paused / completed / failed |
| current_cycle | number | 当前迭代轮次，从 0 开始 |
| max_iterations | number | 最大迭代次数上限，默认 10 |
| last_execution | ISO8601|null | 上次执行时间 |
| last_checkpoint | ISO8601|null | 上次检查点时间 |
| error_count | number | 连续错误计数 |
| resume_context | string | 恢复上下文：描述上次执行到哪里 |
| next_action | string | 下一步操作：描述接下来该做什么 |
| goal_condition | string | 目标条件：描述达成目标的判定标准 |
| artifacts | string[] | 产出物路径列表 |

**状态转换规则**：

```
idle → running → completed
               → paused → running（恢复）
               → failed
```

- **idle → running**：Loop 被触发，开始执行
- **running → completed**：goal_condition 满足，或所有轮次执行完毕
- **running → paused**：用户中断、上下文溢出、或需要人工确认
- **paused → running**：恢复执行，从 resume_context 和 next_action 继续
- **running → failed**：error_count 达到阈值，或 max_iterations 用尽仍未完成

### 可视化执行规范

所有 Loop 操作必须向用户展示执行过程，禁止后台静默运行。每个步骤必须包含：步骤编号/总数、操作名称、状态、目标、耗时、产出路径。

**展示格式**：

```
┌─ [步骤 1/5] 网页抓取 ──────────────────────┐
│ 状态：执行中 ●                               │
│ 目标：https://example.com/article            │
│ 耗时：已用 12s                               │
│ 产出：08_INBOX/raw/20260621_example.md       │
└──────────────────────────────────────────────┘
```

**Loop 整体进度展示**：

```
┌─ Loop LP_0001 [Goal Loop] ──────────────────┐
│ 状态：running ●                              │
│ 进度：3/10 轮                                │
│ 目标：所有测试通过                            │
│ 上次执行：2026-06-21 10:30:00                │
│ 下一步：修复 auth 模块测试失败                │
│ 错误计数：0                                   │
└──────────────────────────────────────────────┘
```

> 引用依据：AGENTS.md 中"可视化执行规范"明确要求所有操作必须展示执行过程，每个步骤必须包含步骤编号/总数、操作名称、状态、目标、耗时、产出路径。

### 熔断机制

三层熔断保护，防止 Loop 在失败循环中空转烧钱：

**1. max_iterations 上限**：
- 每个 Loop 必须设定最大迭代次数，默认 10
- 达到上限后 status → paused，输出当前进度和 resume_context
- 用户可手动调整 max_iterations 后恢复

**2. error_count 阈值**：
- 每次执行失败 error_count +1，成功则重置为 0
- error_count ≥ 3 时 status → failed，输出失败分析报告
- 报告包含：失败模式分析、已尝试策略、建议修正方向

**3. 连续3次失败暂停**：
- 连续3次迭代均未推进目标（current_cycle 递增但 goal_condition 未趋近）
- 自动暂停，status → paused
- 输出简报：当前状态、失败模式、建议用户介入或调整策略

**熔断恢复**：
- 用户可手动重置 error_count 后恢复执行
- 或调整策略（修改 next_action / goal_condition）后恢复
- 恢复后 error_count 重置为 0，但 current_cycle 不重置

> 引用依据：相关参考 强调"没有熔断机制的 Loop 就是烧钱机器——Agent 调用有 bug 的 MCP 工具，5 分钟内重试 400 次。必须设置最大迭代次数"；相关参考 Harness Engineering 的失败恢复采用三级降级策略。

### Scheduled Loop 配置实操

#### Trae Schedule 工具配置

**cron 表达式格式**：5 字段 unix cron 格式 `minute hour day-of-month month day-of-week`

**常用配置示例**：

| 场景 | cron 表达式 | 说明 |
|------|-------------|------|
| 每天早上9点 | `0 9 * * *` | 每日代码审查 |
| 工作日16点 | `0 16 * * 1-5` | 工作日下班前检查 |
| 每周一9点 | `0 9 * * 1` | 周一技术债扫描 |
| 每月1号9点 | `0 9 1 * *` | 月度依赖升级检查 |
| 每30分钟 | `*/30 * * * *` | CI 监控（注意：最小间隔10分钟） |

**message 字段完整模板**：

```
你是一个 AOS Scheduled Loop 执行代理。请按以下指令执行：

## Loop 信息
- Loop ID：LP_0001
- Loop 类型：scheduled
- 目标：{goal_condition}

## 状态恢复
- 当前轮次：{current_cycle}
- 上次执行：{last_execution}
- 恢复上下文：{resume_context}
- 下一步操作：{next_action}

## 执行要求
1. 读取 04_MEMORY/loops/LP_0001/state.json 获取最新状态
2. 执行一轮迭代，推进目标
3. 更新 state.json（current_cycle +1，更新 resume_context 和 next_action）
4. 检查 goal_condition 是否达成
5. 按可视化执行规范展示每个步骤

## 熔断规则
- max_iterations：{max_iterations}
- 连续3次失败自动暂停
- error_count 达到3则停止

## 产出
- 更新 04_MEMORY/loops/LP_0001/state.json
- 日志追加至 06_LOGS/loop_LP_0001_YYYYMMDD.log
```

**timezone 设置**：
- 推荐使用用户本地时区，如 `Asia/Shanghai`
- 若省略则默认为空，按 UTC 执行

**创建示例**：

```
使用 Trae Schedule 工具创建 Scheduled Loop：
- name: "每日代码审查"
- cron_expression: "0 9 * * *"
- timezone: "Asia/Shanghai"
- message: [上述模板，填入实际值]
```

> 引用依据：相关参考 详解 Boris Cherny 的真实案例——每天早上9点定时任务自动启动，调"分诊"Skill 翻昨天的 CI 失败记录、Open Issue、最近的 commit，全程串起来的是一条状态文件；相关参考 入门路径 Level 2 加 hook 自动化。

---

## 关键坑点

- **Loop 当作持续循环使用**：AOS Loop 是单次触发式，不是 while(true)。每次触发只执行一轮，状态靠 state.json 延续。试图在单次会话中实现无限循环会触发熔断。
- **state.json 未及时更新**：每轮迭代结束后必须立即更新 state.json，不能等会话结束。会话可能随时中断，未落盘的状态会丢失。
- **max_iterations 设置过大**：没有上限的 Loop 是烧钱机器。默认 10 次，根据任务复杂度调整，但必须设上限。
- **Scheduled Loop 的 message 字段不完整**：message 是新会话的唯一上下文来源，必须包含完整的 Loop 信息、状态恢复指令和执行要求。信息缺失会导致新会话无法正确恢复。
- **error_count 未重置**：成功执行后必须重置 error_count 为 0。否则偶发失败会累积导致误触发熔断。
- **可视化执行规范被忽略**：后台静默运行是严重违规。每个步骤必须展示步骤编号/总数、操作名称、状态、目标、耗时、产出路径。
- **Goal Loop 跨会话使用**：Goal Loop 设计为单次会话内迭代。如需跨会话，应使用 Scheduled Loop。Goal Loop 会话中断后应转为 Scheduled Loop 继续。
- **cron 最小间隔限制**：Trae Schedule 工具要求最小间隔 10 分钟。`*/5 * * * *` 这种配置不被支持。

---

## 可迁移到 AOS 的规则

- AOS Loop Engine 基于单次触发式执行模型，状态靠 state.json 延续，不依赖运行时内存
- 三种 Loop 类型按场景选择：Goal Loop（单会话迭代）、Scheduled Loop（跨会话定时）、Event Loop（事件驱动）
- state.json 是 Loop 的唯一状态载体，每轮迭代结束后必须立即落盘
- 可视化执行规范强制执行：每个步骤展示编号/总数、操作名称、状态、目标、耗时、产出路径
- 熔断机制三层保护：max_iterations 上限 + error_count 阈值 + 连续3次失败暂停
- Scheduled Loop 通过 Trae Schedule 工具配置，message 字段必须携带完整上下文模板
- Goal Loop 会话中断后转为 Scheduled Loop 继续执行
- Agent 会忘，文件不会——所有 Loop 状态必须写入磁盘
- cron 最小间隔 10 分钟，不支持更高频调度
- Loop 场景选择原则：只在高频重复+规则明确+有自动化验证手段的场景启用
