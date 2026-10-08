# AOS 2.0 — Agent Operating System

@.dsh/context-anchor.md

> 版本 2.0.0-rc.1 | 2026-10-07 | 本文件硬上限 200 行，溢出内容必须降级为 skill
> 前身：AOS v1（已冻结归档）

## 定位

AOS 是运行在类 Claude Code agent harness 上的个人文件治理层：**harness 提供运行时（调度、编排、沙箱、记忆通道），AOS 提供数据治理与工作流约定**。规则只写不变量，一切按需知识通过指针表和 skills 检索。

## 铁律（4 条，平台无关）

1. **记忆分型**：记录型（feedback/经验/坑点/日志）只追加；状态型（画像/项目事实/配置）覆盖旧值并留变更注释（如"React（2026-06-15 更新，原为 Vue）"）
2. **输出隔离**：交付物一律经 `07_EXPORTS/{project}/` 导出，禁止散落在工作目录
3. **Reference 唯一化**：每份知识只存一处，他处只写路径引用；禁止复制内容
4. **项目不复制知识**：01_PROJECTS 内只能引用 04_MEMORY / 09_REFERENCE 的路径

## 目录宪章（8 个）

| 目录 | 职责 | 关键约束 |
|---|---|---|
| 01_PROJECTS | 项目隔离存放 | 项目模板两件套：AGENTS.md + README.md |
| 04_MEMORY | 唯一状态持久化中心 | 状态型文件单文件 ≤32KB，超限剪切历史至 06_LOGS/{project}/memory_history.md 并留指针 |
| 05_CACHE | Agent 中间产物垃圾场 | ①唯一副本禁入（备份去 99_ARCHIVE 或异地）②两级分层：项目/日期③创建时间超 90 天由巡检 skill 出清理清单④禁止任何长期引用指向此目录 |
| 06_LOGS | 运行日志（平台无关叙事层） | 只追加；治理事件（巡检/事故/发布/决策）+ 项目关键节点（立项/阶段切换/交付）必写一行；重要会话一行入 `/aos/session_index.md`；跨平台迁移时本目录随迁（过程细节层归 harness 会话档案）；/memory_history.md 承接状态文件剪切的历史（裁剪前必须先归档，顺序不可倒） |
| 07_EXPORTS | 输出导出 | 按项目分层 |
| 08_INBOX | 重量级输入鲁棒入口 | ①中转区语义：处理完必须迁往真正归宿，原处只留去向指针②按 YYYYMMDD 分层③收到 INBOX 路径 → 读取 → 处理 → 主动归位 → 留去向记录 |
| 09_REFERENCE | 唯一参考知识库 | 知识只存一份；research/ 存调研成果 |
| 99_ARCHIVE | 不可修改历史归档 | 只读；只增不减 |

## 记忆体系

- **Semantic**（状态）：`04_MEMORY/INDEX.md`（一行一指针+150 字 hook，≤200 行）→ user/project/credentials
- **Episodic**（记录）：双层——细节层 = harness 会话档案 + goal 事件流（最全、平台绑定）；叙事层 = 06_LOGS 追加（人类可读、平台无关，跨平台迁移保险）
- **Procedural**（程序性）：`.dsh/skills/*/SKILL.md` 的 gotchas 段落，犯错沉淀到对应 skill，不只靠提示词纠正
- **Working**：harness 会话上下文，不手工维护
- 记忆写作纪律：经验条目三要素（规则+Why+How to apply）；能从现有规则推导的内容不入库（防冗余腐化）

## 落位速查（高频规则内联；细则见 file-placement skill）

| 产出什么 | 放哪 |
|---|---|
| 项目交付物 | `07_EXPORTS/{project}/`；无项目的轻量任务 → `07_EXPORTS/quicktasks/{YYYYMMDD}_{slug}/` |
| 临时/中间产物 | `05_CACHE/{project|quicktask}/{YYYYMMDD}/`（唯一副本禁入） |
| 外部给的大文件 | `08_INBOX/{YYYYMMDD}/`（处理完迁往归宿留指针） |
| 长期知识 | `09_REFERENCE/{domain}/` + INDEX 钩子 |
| 状态/偏好 | `04_MEMORY/`；日志与历史 → `06_LOGS/`；废弃不删 → `99_ARCHIVE/` |
| 项目内文件 | 按 file-placement skill §2 骨架；根层禁止代码/脚本散放 |
| 第三方组件 | 用户级 `~/.agents/skills` / harness profile，**不入 AOS**（自研才进 `.dsh/skills`） |

判定存疑（quicktask 阈值/建项目条件/项目内细分/判别式）→ 读 file-placement skill。

## 文件操作铁律（无条件生效）

1. 中文内容文件**只准 write/edit 工具**（或 python 显式 utf-8），禁用 shell 管道/重定向写入
2. JSON/YAML 写入 UTF-8 带 BOM；读取按 `utf-8-sig`
3. YAML description 以 `[` 开头必须加引号；含反斜杠路径用单引号串
4. 结构化文件（manifest 等）修改禁用 shell 字符串替换，只准 write/edit/python json

## 指针表（需要 X 时查 Y）

| 需要 | 查 |
|---|---|
| 用户偏好/画像 | `04_MEMORY/user/user_profile.md` |
| 项目动态 | `04_MEMORY/project/proj_{name}.md`（经 INDEX.md 定位） |
| 凭据 | `04_MEMORY/credentials.json`（引用 id，不复制 value；禁止上传公开仓库） |
| 知识入库/调研方法 | skill: knowledge-ingest |
| 子代理调度判断 | skill: subagent-dispatch |
| 新建项目 | skill: project-init |
| 文件放哪/轻量任务归档/是否建项目 | skill: file-placement |
| 多机协同（可选扩展） | skill: dual-machine（扩展点说明，见 docs/design-rationale.md） |

## 行为不变量

1. **对抗审查**：重大方案/高风险改动必须以独立上下文（fork 子代理或审查团队 review）做红队；写码者不认证自己的 diff
2. **两次纠正**：同一错误两次纠正失败 → 写 3-5 行简报，建议新会话贴入。载体是 feedback 同名条目：条目**第二次**更新时，回复必须附「建议新会话」提示；纠正计数不依赖模型记忆
3. **模型路由**：低推理批量任务（枚举/统计/文本整理/识图）路由低成本批量模型；强推理与决策用主模型
4. **批量清理**：批量模型产 manifest → 主会话复核 → 用户终审；唯一副本先异地备份+哈希校验
5. **运行时数据禁区**：生产服务运行时数据、数据库、日志内容绝不动
6. **AGENTS.md 防蠕变**：本文件 ≤200 行；季度检查，新增规则优先考虑写成 skill
7. **对外发布门禁**：公开仓库 push / Release / 任何公开渠道发布必须用户当次显式批准；计划批准不等于发布授权
8. **落盘前查路由**：创建/移动任何文件前，先查上方"落位速查"表；表格未覆盖或存疑时读 skill: file-placement 细则（高频规则内联、低频细则下沉）

## 多机协同（可选扩展；不需要可整段删除，不影响其余部分）

AOS 单机即可完整运行。跨机协作按扩展点对待：状态以 06_LOGS 叙事层与同步目录保持一致；命令走受控通道；部署前核对目标机约束。本发布包不附带跨机实现，设计讨论见 docs/design-rationale.md。

## 压缩保留项

压缩会话时保留：任务目标与验收标准、修改过的文件路径、未解决错误、架构决策及理由、用户明确约束。

压缩后恢复 4 步（防旧事件误判）：① 读 summary 的 Current Work → ② 读用户最新消息 → ③ 两者一致则继续 → ④ 不一致（质问旧事/新需求）先确认意图再行动。
