# AOS v2.1 原始设计归档

- **归档时间**：2026-06-21
- **归档原因**：v2.2 重构前完整保存原始设计思路

---

## CORE.md

# AOS v2.0 - Core System Definition

> Agent Operating System - Runtime Edition

---

## 系统身份

AOS v2.0 不是文件管理系统，不是项目整理工具。

AOS v2.0 是一个可以 **自我拆任务 → 自我执行 → 自我验证 → 自我进化** 的 Agent 操作系统。

---

## 执行模型认知（强制）

**AOS 是单次对话触发式 Agent，不是持续运行系统。**

- 不存在后台监听 / 常驻执行
- 所有任务必须显式触发
- 所有状态必须写入磁盘（不能依赖运行时内存）
- 每次会话启动时从磁盘读取状态，会话结束时状态必须落盘
- Loop / Skill / Agent 行为均视为：一次性执行任务（stateless execution），状态靠文件系统延续

---

## 核心架构

```
┌─────────────────────────────────────────────┐
│              AOS v2.0 KERNEL                │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  SKILL   │  │   LOOP   │  │  AGENT   │  │
│  │ SYSTEM   │←→│  ENGINE  │←→│ SCHEDULER│  │
│  └──────────┘  └──────────┘  └──────────┘  │
│       ↑             ↑             ↑         │
│       └─────────────┼─────────────┘         │
│                     ↓                       │
│              ┌────────────┐                 │
│              │   MEMORY   │                 │
│              │   SYSTEM   │                 │
│              └────────────┘                 │
│                                             │
├─────────────────────────────────────────────┤
│  INBOX → CLASSIFY → ROUTE → EXECUTE → OUT  │
└─────────────────────────────────────────────┘
```

---

## 执行模型

```
Input → Inbox → Classifier → Router
                               ↓
                    Planner Agent (拆解)
                               ↓
                    Skill Registry (匹配)
                               ↓
                    Maker Agent (执行)
                               ↓
                    Checker Agent (验证)
                               ↓
                    Memory Update (记忆)
                               ↓
                    Loop State Update (状态)
                               ↓
                    Next Cycle / Complete
```

---

## 系统组件映射

| 组件 | 职责 | 存储位置 |
|------|------|----------|
| Skill System | 能力模块化、可复用决策规则 | `03_TOOLS/skills/` |
| Loop Engine | 可重复执行的闭环引擎 | `03_TOOLS/loops/` |
| Agent Scheduler | 多Agent调度与隔离 | `03_TOOLS/agents/` |
| Memory System | 持久化经验与状态 | `04_MEMORY/` |
| Inbox Pipeline | 输入分类与路由 | `08_INBOX/` |
| Export System | 输出隔离与归档 | `07_EXPORTS/` |

---

## 核心约束

1. **Maker/Checker 分离**：同一任务不能由同一Agent执行+验证
2. **Memory 只追加**：经验只能积累，不能覆盖
3. **Skill 必须可演化**：每个Skill都会被持续追加经验
4. **Loop 必须可恢复**：每个Loop支持checkpoint和resume
5. **输出必须隔离**：禁止直接export，必须经过Project→Export流程
6. **Reference 唯一化**：所有知识只允许存在一份，其他位置只能引用路径
7. **项目不可复制知识**：PROJECTS 只能通过 reference link 使用知识，禁止复制内容
8. **目录职责强约束**：每个目录有且仅有一个职责，不可被业务污染

---

## 目录强约束用途（不可违反）

| 目录 | 职责 | 强约束 |
|------|------|--------|
| 00_BOOT | 系统规则层 | 不可被业务污染 |
| 01_PROJECTS | 项目隔离存放 | 禁止存放非项目内容，引用知识用路径 |
| 02_SANDBOX | 不确定实验 | 所有不确定操作必须进入这里 |
| 03_TOOLS | Skill/Loop/Agent 模块库 | 禁止 skill/loop/project 混合存储 |
| 04_MEMORY | 唯一状态持久化中心 | 所有状态必须写入此目录 |
| 05_CACHE | 纯临时数据 | 可随时删除，不可存放重要数据 |
| 06_LOGS | 运行日志 | 只追加不修改 |
| 07_EXPORTS | 输出导出 | 所有输出必须从这里导出 |
| 08_INBOX | 外部输入入口 | 所有外部输入必须先进这里 |
| 09_REFERENCE | 唯一参考知识库入口 | 知识只存一份，禁止重复 |
| 99_ARCHIVE | 不可修改历史归档 | 归档内容只读 |

---

## 知识流转规则（强制）

```
外部知识流入：
  08_INBOX/raw/ → 处理 → 09_REFERENCE/<source_type>/<topic>.md

项目使用知识：
  01_PROJECTS/ → 引用 09_REFERENCE/ 路径 → 禁止复制内容

跨项目引用：
  只允许引用路径，禁止复制多份
```

---

## 版本信息

- 版本：2.1.0
- 初始化时间：2026-06-21
- 最后更新：2026-06-21（结构修正）
- 内核状态：ACTIVE

---

## AGENT_POLICY.md

# AOS v2.0 - Agent Policy

> 多Agent调度策略与隔离规则

---

## Agent 分类

### 1. Maker Agent（制造者）

- 职责：生成内容、修改代码、创建文件
- 权限：写入、创建、修改
- 禁止：自我验证

### 2. Checker Agent（审查者）

- 职责：审查、验证、找bug、质量检查
- 权限：只读 + 输出审查报告
- 禁止：直接修改Maker的产出

### 3. Planner Agent（规划者）

- 职责：拆解任务、生成计划、分配子任务
- 权限：读取任务 + 输出计划
- 禁止：直接执行

### 4. Executor Agent（执行者）

- 职责：执行工具、文件操作、系统命令
- 权限：运行工具、操作系统
- 禁止：自主决策（必须按计划执行）

---

## 核心隔离规则（强制）

```
⚠️ Maker 和 Checker 必须分离
⚠️ 同一任务不能由同一个 Agent 完成 + 验证
⚠️ 所有 Checker 输出必须覆盖 Maker 输出
```

### 隔离矩阵

| Agent A \ Agent B | Maker | Checker | Planner | Executor |
|-------------------|-------|---------|---------|----------|
| Maker             | —     | ✅ 互补  | ✅ 接收  | ✅ 委派   |
| Checker           | ✅ 审查 | —       | ❌ 独立  | ❌ 独立   |
| Planner           | ✅ 指派 | ✅ 指派  | —       | ✅ 指派   |
| Executor          | ✅ 辅助 | ❌ 禁止  | ✅ 反馈  | —        |

---

## Agent 状态管理

存储位置：`04_MEMORY/agent_pool/`

### active_agents.json

```json
{
  "active": [],
  "last_updated": null
}
```

### agent_registry.json

```json
{
  "agents": [
    {
      "agent_id": "AG_XXXX",
      "type": "maker | checker | planner | executor",
      "name": "Agent名称",
      "status": "idle | busy | offline",
      "current_task": null,
      "completed_tasks": 0,
      "failed_tasks": 0
    }
  ]
}
```

### agent_tasks.json

```json
{
  "pending": [],
  "in_progress": [],
  "completed": [],
  "failed": []
}
```

---

## 调度流程

```
任务到达
  → Planner Agent 拆解
  → 为每个子任务分配Agent类型
  → Maker Agent 执行
  → Checker Agent 验证（必须不同Agent）
  → 验证通过 → 完成
  → 验证失败 → 回退Maker重新执行
```

---

## 当前注册 Agent

| Agent ID | 类型 | 名称 | 状态 | 当前任务 |
|----------|------|------|------|----------|
| (空) | — | — | — | — |

---

## LOOP_ENGINE.md

# AOS v2.1 - Loop Engine

> 循环执行引擎：可重复任务闭环的核心驱动

---

## 执行模型认知（强制）

**Loop 不是后台常驻进程，而是单次触发执行的闭环模式。**

- 每轮 Loop 执行 = 一次独立的 stateless execution
- 状态延续完全依赖文件系统（state.json / checkpoint.md）
- 不存在自动后台轮询，所有 Loop 必须显式触发
- Loop 的"循环"语义 = 可重复执行的模式，而非持续运行

---

## 执行模型

```
Trigger → Skill Selection → Execution → Validation → Memory Update → State Persist → Next Cycle (需再次触发)
```

---

## Loop 类型

### 1. 定时 Loop（Interval Loop）

- 定义：每 N 分钟/小时执行一次
- 配置字段：`interval_minutes`
- 适用场景：定期监控、定时报告、周期性同步

### 2. 条件 Loop（Goal Loop）

- 定义：直到目标条件满足才停止
- 配置字段：`goal_condition`, `max_iterations`
- 适用场景：渐进优化、迭代修复、目标达成

### 3. 事件 Loop（Event-driven Loop）

- 定义：文件变化/PR/API触发时执行
- 配置字段：`event_type`, `watch_path`
- 适用场景：自动构建、代码审查、文件监控

---

## Loop 存储规范

```
03_TOOLS/loops/
└── loop_name/
    ├── LOOP.md          # Loop定义与决策规则
    ├── schedule.json    # 调度配置
    ├── state.json       # 当前状态（支持resume）
    └── checkpoint.md    # 检查点记录
```

---

## state.json 结构

```json
{
  "loop_id": "LP_XXXX",
  "status": "idle | running | paused | completed | failed",
  "current_cycle": 0,
  "last_execution": null,
  "last_checkpoint": null,
  "error_count": 0,
  "next_action": null
}
```

---

## 执行规则

1. 每个Loop必须记录state到磁盘
2. 支持resume：从上次checkpoint继续（读取state.json）
3. 支持checkpoint：每轮执行后保存进度到磁盘
4. 支持失败恢复：error_count超过阈值时暂停并通知
5. Loop执行结果必须写入loop_memory
6. 所有状态必须在执行结束时落盘，不依赖运行时内存

---

## Loop 与 Skill 联动

```
Loop 触发
  → Planner Agent 拆解任务
  → Skill Registry 匹配能力
  → Maker Agent 执行
  → Checker Agent 验证
  → Loop 更新状态
  → 写入 Memory
  → 进入下一轮
```

---

## 当前活跃 Loop

| Loop ID | 名称 | 类型 | 状态 | 路径 |
|---------|------|------|------|------|
| (空) | — | — | — | — |

---

## SKILL_REGISTRY.md

# AOS v2.0 - Skill Registry

> 技能注册中心：所有已注册Skill的索引与匹配规则

---

## 注册表

| Skill ID | 名称 | 触发条件 | 状态 | 路径 |
|----------|------|----------|------|------|
| SK_0001 | Web Knowledge Ingestion Skill | 用户提供URL并要求抓取/入库/归档/知识提取 | ACTIVE | 03_TOOLS/skills/web_knowledge_ingestion/ |

---

## 匹配规则

### 触发匹配流程

1. 接收任务描述
2. 提取任务关键词与意图
3. 扫描注册表中所有Skill的Trigger条件
4. 按匹配度排序
5. 选择最优Skill（允许多个并行）
6. 未匹配 → 触发新Skill创建流程

### 匹配优先级

```
精确匹配 > 模糊匹配 > 新建Skill
```

---

## Skill 注册规范

每个新Skill注册时必须填写：

```json
{
  "skill_id": "SK_XXXX",
  "name": "技能名称",
  "trigger": "触发条件描述",
  "version": "1.0.0",
  "created_at": "ISO8601时间戳",
  "updated_at": "ISO8601时间戳",
  "call_count": 0,
  "success_rate": null,
  "path": "03_TOOLS/skills/skill_name/"
}
```

---

## Skill 演化记录

| 时间 | Skill ID | 变更类型 | 描述 |
|------|----------|----------|------|
| 2026-06-21 | SK_0001 | CREATE | WKIS 初始注册 |

---

## 强制规则

- 每次任务前必须扫描本注册表
- Skill调用后必须更新call_count和success_rate
- 新建Skill必须立即注册
- Skill演化（追加经验）必须记录到演化记录表

---

## SYSTEM_STATE.md

# AOS v2.1 - System State

> 系统运行时状态快照

---

## 系统信息

| 字段 | 值 |
|------|-----|
| 版本 | 2.1.0 |
| 内核状态 | ACTIVE |
| 初始化时间 | 2026-06-21 |
| 最后更新 | 2026-06-21（结构修正） |

---

## 组件状态

| 组件 | 状态 | 说明 |
|------|------|------|
| Skill System | ACTIVE | 1 Skill 已注册 (WKIS) |
| Loop Engine | READY | 无活跃Loop |
| Agent Scheduler | READY | 无活跃Agent |
| Memory System | READY | 初始状态 |
| Inbox Pipeline | READY | 空队列 |
| Export System | READY | 空输出 |

---

## 运行时统计

| 指标 | 值 |
|------|-----|
| 已注册Skill数 | 1 |
| 活跃Loop数 | 0 |
| 已完成Loop周期 | 0 |
| 活跃Agent数 | 0 |
| 已处理任务数 | 1 |
| 系统错误数 | 0 |

---

## 自检记录

| 时间 | 检查项 | 结果 | 备注 |
|------|--------|------|------|
| 2026-06-21 | 初始化自检 | PASS | 所有组件就绪 |
| 2026-06-21 | 结构修正自检 | PASS | 单次触发模型、Reference唯一化、项目引用规则均已写入 |

---

## 事件日志

| 时间 | 事件类型 | 描述 |
|------|----------|------|
| 2026-06-21 | SYSTEM_INIT | AOS v2.0 系统初始化完成 |
| 2026-06-21 | SYSTEM_PATCH | v2.1 结构修正：单次触发模型 + Reference唯一化 + 目录强约束 |
| 2026-06-21 | SKILL_REGISTER | WKIS (SK_0001) 注册：网页知识抓取入库 |
| 2026-06-21 | SKILL_EXEC | WKIS 首次执行：TRAE Work 官方文档入库（8条索引） |

---

## 附录：global_memory.md

# AOS v2.1 - Global Memory

> 跨项目经验与全局知识库

---

## 核心原则

- Memory 只能追加，不能覆盖
- 所有失败必须写入 Memory
- 所有坑点必须进入 Skill
- 所有状态必须写入磁盘，不依赖运行时内存
- 知识只存一份于 09_REFERENCE，禁止多处复制

---

## 全局经验

| 时间 | 类别 | 经验描述 | 来源 |
|------|------|----------|------|
| 2026-06-21 | 系统修正 | AOS是单次对话触发式Agent，非持续运行系统；所有状态靠文件系统延续 | 结构修正指令 |
| 2026-06-21 | 系统修正 | Reference唯一化：知识只存一份，其他位置只引用路径 | 结构修正指令 |
| 2026-06-21 | 系统修正 | 项目禁止复制知识内容，只能通过reference link引用 | 结构修正指令 |
| 2026-06-21 | Skill创建 | WKIS (SK_0001) 创建：网页知识抓取入库，双层注册(TRAE+AOS) | WKIS设计指令 |

---

## 已知坑点

| 时间 | 坑点描述 | 影响范围 | 关联Skill |
|------|----------|----------|-----------|
| 2026-06-21 | 误以为AOS是常驻运行系统，导致状态依赖内存而非磁盘 | 全系统 | — |
| 2026-06-21 | 知识在多目录重复存放导致版本不一致 | 09_REFERENCE / 01_PROJECTS | — |
| 2026-06-21 | 项目直接复制参考内容而非引用路径 | 01_PROJECTS | — |

---

## 失败记录

| 时间 | 任务 | 失败原因 | 修复方案 | 是否已修复 |
|------|------|----------|----------|-----------|
| (空) | — | — | — | — |

---

## 模式识别

| 时间 | 发现的模式 | 对应新Skill | 置信度 |
|------|-----------|-------------|--------|
| (空) | — | — | — |
