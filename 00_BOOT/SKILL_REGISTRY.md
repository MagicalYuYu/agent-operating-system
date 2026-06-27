# AOS v1.1.0 — Skill Registry

> 技能注册中心：所有已注册 Skill 的索引与匹配规则

---

## 注册表

| Skill ID | 名称 | 触发条件 | 版本 | 状态 | 路径 |
|----------|------|----------|------|------|------|
| SK_0001 | Web Knowledge Ingestion Skill | 当用户提供URL并要求抓取/入库/归档/知识提取时使用 | 2.0.0 | ACTIVE | 03_TOOLS/skills/web_knowledge_ingestion/ |
| SK_0002 | Legacy Migration Skill | 当用户要求迁移/导入历史项目、对话记录、存量内容到AOS时使用 | 1.0.0 | ACTIVE | 03_TOOLS/skills/legacy_migration/ |
| SK_0003 | Ponytail Code Quality Skill | 当用户要求编写/修改代码时使用：6级决策阶梯（YAGNI→stdlib→原生→已装依赖→一行→最小实现），默认full强度 | 1.0.0 | ACTIVE | 03_TOOLS/skills/ponytail_code_quality/ |

---

## 匹配规则

### 触发匹配流程

1. 接收任务描述
2. 提取任务关键词与意图
3. 扫描注册表中所有 Skill 的 Trigger 条件
4. 按匹配度排序
5. 选择最优 Skill（允许多个并行）
6. 未匹配 → 触发新 Skill 创建流程

### 匹配优先级

```
精确匹配 > 模糊匹配 > 新建Skill
```

---

## Skill 注册规范

每个新 Skill 注册时必须填写：

```json
{
  "skill_id": "SK_XXXX",
  "name": "技能名称",
  "trigger": "触发条件（什么场景下用我，不超过250字符）",
  "version": "1.0.0",
  "created_at": "ISO8601时间戳",
  "updated_at": "ISO8601时间戳",
  "call_count": 0,
  "success_rate": null,
  "path": "03_TOOLS/skills/skill_name/",
  "trae_skill_path": ".trae/skills/skill-name/SKILL.md",
  "structure_version": "1.0",
  "has_gotchas": false,
  "has_scripts": false,
  "has_templates": false,
  "has_references": false
}
```

---

## Skill 文件夹标准结构

```
03_TOOLS/skills/{skill_name}/
├── SKILL.md              ← 核心指令（description 在前250字符写清触发条件）
├── gotchas.md            ← 坑点清单（持续积累，含金量最高）
├── scripts/              ← 可执行脚本（可选）
├── templates/            ← 输出模板（可选）
├── references/           ← 参考资料正文放不下的细节（可选）
└── memory/               ← Skill 持久记忆
```

---

## Skill 演化记录

| 时间 | Skill ID | 变更类型 | 描述 |
|------|----------|----------|------|
| 2026-06-21 | SK_0001 | CREATE | WKIS 初始注册 |
| 2026-06-21 | SK_0001 | 1.0.0-dev3 | 重构：description改为触发条件式；新增gotchas.md；新增可视化执行规范 |
| 2026-06-21 | SK_0001 | PATCH | 1.0.0-rc1：运行时铁律适配——状态更新嵌入Skill步骤 |
| 2026-06-21 | SK_0002 | CREATE | Legacy Migration Skill 初始注册 |
| 2026-06-21 | SK_0002 | EXEC | 示例项目迁移：6个插件(5活跃+1归档)+15个ZIP备份+2个教程文档迁入AOS |
| 2026-06-27 | SK_0003 | CREATE | ponytail_code_quality Skill 注册：源自 DietrichGebert/ponytail（18.4k star），6级决策阶梯，默认full强度，所有模型通用 |

---

## 强制规则

- 每次任务前必须扫描本注册表
- Skill 调用后必须更新 call_count 和 success_rate
- 新建 Skill 必须立即注册
- Skill 演化（追加经验/坑点）必须记录到演化记录表
- description 必须写触发条件而非摘要，不超过 250 字符
- 每个 Skill 必须包含 gotchas.md 坑点清单
- Skill 步骤序列的最后一步必须是状态更新（更新 STATUS.md / agent_tasks.json / SKILL_REGISTRY.md），不可省略
- 优先建设验证类 Skill（让 Agent 能自己确认工作成果）
