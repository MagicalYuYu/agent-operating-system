# AOS v1.0 - Loop Memory

Loop 持久记忆，每个 Loop 一个文件。

## 应放什么
- LP_XXXX_memory.md — 对应 Loop 的执行记录、checkpoint、resume 上下文

## 命名规则
LP_{编号}_memory.md

## 注意
- Loop 必须可恢复，支持 checkpoint 和 resume
- state.json 记录当前进度，resume_context 字段让新会话 Agent 快速理解中断位置

## 实际使用频率
⚠ 低频目录。Trae CODE 模式为单次触发式，Loop 实际通过 Schedule 或单会话迭代实现，loop_memory/ 使用频率较低。保留此目录以备后续 Trae 功能升级时使用。
