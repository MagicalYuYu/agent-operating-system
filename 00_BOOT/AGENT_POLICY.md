# AOS v1.1.0 — Agent 执行模式

> 单次触发式 Agent 的三种执行模式与多会话协同协议

---

## 执行模型认知（强制）

**Trae CODE 模式下，同一会话仅存在一个 Agent 实例。** 不同会话的独立 Agent 实例通过文件系统交互，实现变相并行。

---

## 三种执行模式

| 模式 | 触发条件 | 行为 | 约束 | 对应命令 |
|------|----------|------|------|----------|
| PLAN | 复杂任务、架构决策、新项目启动 | 只读探索+生成计划+写入 `.trae/specs/` | 不执行修改操作 | `/spec` 或 `/plan` |
| EXECUTE | 计划确认后、简单直接任务 | 读写操作+工具调用+文件修改 | 按计划执行，自主决策限于实现细节 | 默认模式 |
| VERIFY | 任务完成前、用户要求审查 | 只读验证+输出审查报告 | 不修改任何文件 | **必须在新会话中发起** |

---

## VERIFY 模式关键规则

- 验证必须在**新会话**中执行，确保审查者不共享制作者的上下文
- 审查报告写入 `06_LOGS/` 或 `07_EXPORTS/`
- 审查结果更新 `04_MEMORY/agent_pool/agent_tasks.json` 中对应任务状态

---

## 多会话协同协议

不同会话的 Agent 通过 `04_MEMORY/agent_pool/agent_tasks.json` 交互：

1. **任务声明**：Agent A 在 agent_tasks.json 中声明任务（status: pending）
2. **任务认领**：Agent B（新会话）读取并认领任务（status: in_progress）
3. **结果写入**：Agent B 完成后写入结果（status: completed/failed）
4. **结果消费**：后续会话读取结果继续工作

---

## 详细设计

完整的多会话协同协议、任务 JSON 结构、冲突处理机制见：
`09_REFERENCE/system/aos-agent-execution-model.md`
