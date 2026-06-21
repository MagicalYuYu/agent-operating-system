# AOS v1.0 - Core System Definition

> Agent Operating System - Runtime Edition

---

## 系统身份

AOS v1.0 不是文件管理系统，不是项目整理工具。

AOS v1.0 是一个可以 **自我拆任务 → 自我执行 → 自我验证 → 自我进化** 的 Agent 操作系统。

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
│              AOS v1.0 KERNEL                │
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

- 版本：1.0.0
- 初始化时间：2026-06-21
- 最后更新：2026-06-21（v1.0.0 GitHub首发版）
- 内核状态：ACTIVE
- 详细设计文档：09_REFERENCE/system/aos-*.md
