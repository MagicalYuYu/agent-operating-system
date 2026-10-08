# 文件落位约定

AGENTS.md 内核里的"落位速查表"是高频规则的内联版；本文是完整细则，覆盖每类文件的归宿、目录命名、轻量任务与项目的分界。DSH 用户不需要单独读它，仓库内的 file-placement skill 是同一约定的运行时形态，会按需自动加载；其他平台的工具按本文执行即可。

## 判定顺序

对任何新文件依次过三道闸：

```
闸1 归属：属于某个项目？ → 是 → 按项目内结构落位
                    → 否 → 按顶层路由落位
闸2 寿命：临时（可再生产物）？ → 是 → 进 05_CACHE
                          → 否 → 永久区（项目/导出/参考/归档）
闸3 副本：是唯一副本？ → 是 → 禁止进 05_CACHE，必须永久区并另做备份
```

## 顶层路由（非项目文件）

| 内容 | 去向 | 说明 |
|---|---|---|
| 交付物/输出 | `07_EXPORTS/{project}/` | 无项目的轻量任务用 `07_EXPORTS/quicktasks/`，见下文 |
| Agent 中间产物 | `05_CACHE/{project|quicktask}/{YYYYMMDD}/` | 两级分层强制 |
| 重量级外部输入 | `08_INBOX/{YYYYMMDD}/` | 中转区：处理完迁往真正归宿，原处留去向指针 |
| 知识（长期有效） | `09_REFERENCE/{domain}/{topic}.md` | 配索引钩子，按领域分层 |
| 用户/项目状态 | `04_MEMORY/` | 状态记忆，经 INDEX 指针表定位 |
| 运行日志/历史 | `06_LOGS/{project}/` | 只追加 |
| 废弃但不可删 | `99_ARCHIVE/{批次名}/` | 只增 |

## 项目内结构

> 本节只治理非代码产物的落位；代码内部分层遵循各语言生态惯例（Python src-layout、Go 平铺、Rust 由 Cargo 强制、JS monorepo 用 apps/packages），不由本表强制。

### 标准骨架（两件套强制，其余按需生长）

```
{name}/
├── AGENTS.md            ← 根层只允许：两件套 + .gitignore + CHANGELOG.md
│                          应列出 build/test/run 各一条命令
├── README.md
├── docs/                ← 一切项目文档
│   ├── design/          设计文档、架构决策
│   ├── reports/         调研报告、验证报告
│   ├── archive/         过期文档
│   └── media/           文档配图
├── src/                 ← 源代码（单一项目）；项目集放子项目
├── scripts/             ← 项目脚本（dev/ deploy/ verify/）
├── config/              ← 配置文件（密钥只引用 id，不落明文）
├── assets/              ← 静态资源（images/ fonts/ audio/ data/）
├── tests/               ← 测试与夹具
├── tools/               ← 项目专用工具
└── backup/              ← 项目内备份（唯一备份禁放缓存区）
```

按需启用：小项目最少只需 `docs/` + `src/` 加两件套；config/scripts/assets/tests/tools/backup 有对应文件才建。单文件不建目录。

### 文件类型 → 路径映射

| 类型 | 特征 | 路径 |
|---|---|---|
| 文档 | `*.md`（非两件套） | `docs/{design|reports}/` |
| 代码 | `*.py *.ts *.js *.go *.rs` 等 | `src/` |
| 脚本 | `*.ps1 *.sh *.bat` 或 `check_* verify_* deploy_*` | `scripts/{dev|deploy|verify}/` |
| 配置 | `*.json *.yaml *.toml *.env*` | `config/` |
| 图片 | `*.png *.jpg *.svg` 等 | 文档配图→`docs/media/`；资源图→`assets/images/` |
| 数据集 | `*.csv *.parquet *.jsonl *.db` | `assets/data/`（运行时可变数据走项目运行目录） |
| 压缩包 | `*.zip *.7z *.tar.gz` | 解压后归位；包本身→`backup/` 或删除 |
| 测试 | `test_* *_test.*` | `tests/` |
| 日志 | `*.log` | `06_LOGS/{project}/`（禁止留在项目内） |
| 临时输出 | 生成即弃 | `05_CACHE/{project}/{YYYYMMDD}/` |

### 禁止事项（校验脚本按此扫描）

- 项目根层堆放 3 个以上非两件套文件
- `src/` 内出现日志、截图、压缩包
- 同一目录混放 4 种以上类型
- 层级超过 4 级仍未到达文件
- 日期命名一律 `YYYYMMDD`；禁止"final/最终版/新建文件夹"。日期只作事务性分层键，主题词必须并列（`YYYYMMDD_{slug}`），纯日期轴在实践中难以检索

## 轻量任务与新建项目的分界

不是所有工作都值得开项目。判定：任务无部署物、无独立 repo、产出少于 10 个文件且预计单会话完成 → 按轻量任务（quicktask）归档，不建项目。

| 产出 | 去向 |
|---|---|
| 有交付物（报告/脚本/图） | `07_EXPORTS/quicktasks/{YYYYMMDD}_{slug}/`（slug 用 kebab-case，不超过 3 词） |
| 仅中间过程文件 | `05_CACHE/quicktasks/{YYYYMMDD}_{slug}/` |
| 结论有长期价值 | 提炼进 `09_REFERENCE/`，原目录留指针 |
| 纯问答 | 不归档；值得记的偏好进用户记忆 |

quicktask 目录一旦命名不可改（跨会话续用靠它匹配）。

何时升级为项目（任一命中即可考虑）：同主题 quicktask 累计 3 个以上；单任务产出 10 个文件以上或超过 50MB；需要独立部署物（建服务、开 repo、装依赖树）。原则是提醒而非强制。

## 组件存放边界（自研与第三方）

能力边界不等于文件夹边界。第三方插件与 skills 在会话中照常可用，文件不在 AOS 目录内是设计而非例外：

| 组件 | 位置 | 判定 |
|---|---|---|
| 自研 skills（承载治理语义） | 项目级 skills 目录（DSH 为 `.dsh/skills/`） | 换一个工作区就失去意义 |
| 第三方 skills（通用能力） | 用户级目录（如 `~/.agents/skills/`） | 换任何工作区都有用 |
| 第三方插件 | 各平台自己的管理路径 | AOS 只声明依赖，不复制文件 |

多套工具并用时，把第三方 skills 放进仓库随仓库走是一种合法权衡（跨机免配置），代价是仓库膨胀与上游脱钩。

## 依据来源（公开）

- 浅层可预测结构、AGENTS.md 列 build/test/run：[Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)、[agents.md 标准](https://agents.md/)
- 按需生长、反对过度结构化：Go 与 Rust 官方社区实践
- 文档四象限：[Diátaxis](https://diataxis.fr/)；数据分层 raw/interim/processed：[Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/)
- 个人组织体系对照：PARA、Johnny Decimal；08_INBOX 的中转+指针模式与 agent 文件整理工作流的趋势同构
