# AOS — Agent Operating System

**A file governance layer for AI coding agents.**

[![Release](https://img.shields.io/badge/Release-v2.0.0--rc.1-blue.svg)](https://github.com/MagicalYuYu/agent-operating-system/releases)
[![Runtime](https://img.shields.io/badge/Runtime-DeepSeek_Harness-6E40C9.svg)](https://github.com/deepseek-ai/deepseek-harness)
[![Standard](https://img.shields.io/badge/Standard-AGENTS.md-2EA44F.svg)](https://agents.md/)
[![License: MIT](https://img.shields.io/badge/License-MIT--Additional-informational.svg)](LICENSE)

[中文文档](README.zh-CN.md) · [Website](https://aos.magicalyu.online)

AI coding tools write code and run commands, but they don't manage your files. Deliverables end up scattered across the workspace, knowledge gets saved in three contradictory copies, and constraints are lost when the session context is compressed. AOS addresses this layer: it gives your tools a set of conventions for where files go and where knowledge lives. These conventions are machine-checkable.

Your AI follows these rules inside an AOS workspace, regardless of which project it touches or which device it operates on once you authorize it. One deployment, everywhere.

Think of Jarvis in *Iron Man* — the suits change, Jarvis stays. Switch AI tools, and the structure and memory carry over.

## What it provides

**Directory charter**: 8 numbered directories, each with a one-line responsibility and key constraints written into AGENTS.md. Your AI checks the conventions before creating any file, so you stop repeating "don't put that there." Full rules for file placement and naming are in [docs/file-conventions.md](docs/file-conventions.md). A validator script (`scripts/check_placement.py`) scans for misplaced files, non-standard naming, and structural drift.

**Pointer-table memory**: `04_MEMORY/INDEX.md` maps every topic to a one-line pointer plus a short description, with a 32KB per-file cap. State-type memory (project facts, preferences) overwrites old values with change notes; record-type memory (experience, pitfalls) is append-only. History that outgrows the cap gets trimmed into the log directory with a pointer left behind.

**Dual-layer logs**: Process details live in your platform's session archives. Governance-level events (audits, incidents, decisions, deliveries) go into a human-readable log directory that moves with you across platforms.

**Governance skills**: File placement rules, knowledge intake checks, subagent dispatch decisions, inspection workflows — each is an on-demand skill file with gotchas distilled from real incidents. Mistakes get baked back into the relevant skill rather than corrected via prompts.

**Environment alignment**: A manifest registers all dependency components. Running one script on a new machine tells you what's missing and can auto-install it.

For how these mechanisms work together, from instruction to delivery, see the [architecture reference](docs/architecture.md).

## Platform support

| Tier | Coverage | What you get |
|---|---|---|
| Full adaptation | [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) (DSH) | Skills auto-discovery, context compression anchor, session indexing — everything |
| Generic adaptation | Any tool that reads `AGENTS.md` (Claude Code, Codex, etc.) | Directory charter, pointer-table memory, placement conventions, validator scripts |

v2 was tested on DSH. Generic adaptation doesn't mean a second-class experience: hand the repository to your AI tool, and it can adapt these rules to its platform's format (for example, rewriting `.dsh/skills/` entries into its own skill format).

## Getting started

The fastest path: send this message to your AI tool (DSH, Claude Code, Codex, or any other):

> Deploy AOS: clone https://github.com/MagicalYuYu/agent-operating-system to <your target path>, read the AGENTS.md at the repository root to understand the directory conventions, run `python scripts/check_placement.py` to validate the structure and fix any errors, then tell me the key conventions I should know about.

Prefer manual steps:

1. Requirements: any tool that reads `AGENTS.md` gives you generic adaptation (charter + scripts). Full adaptation (skills auto-loading) requires DSH; other platforms can adapt from `.dsh/skills/`. Scripts need Python 3.10+.
2. Place the repository anywhere (referred to as `{AOS_ROOT}`). No hardcoded paths.
3. Validate: `python scripts/check_placement.py`. Root is auto-derived from the script's location; override with `--root`. Exit code 1 means errors.
4. Align environment (optional): edit `.dsh/skill-manifest.json` for your dependencies, then run `python scripts/align_environment.py`. Add `--apply` to install missing components.
5. Create your first project: follow the two-file pattern (AGENTS.md + README.md) in `01_PROJECTS/_example_cli_tool/`, or copy any `_example_*` directory. Examples include runnable test commands.
6. Read the kernel: `AGENTS.md` (~90 lines) — charter, 4 iron rules, placement table, behavioral invariants.

## Directory overview

| Directory | Purpose |
|---|---|
| `01_PROJECTS/` | Project isolation (3 example projects included) |
| `04_MEMORY/` | Single source of truth for state (INDEX.md pointer table) |
| `05_CACHE/` | Agent intermediate artifacts (regenerable; never the sole copy) |
| `06_LOGS/` | Append-only logs, platform-independent narrative layer |
| `07_EXPORTS/` | Sole exit point for deliverables (per-project) |
| `08_INBOX/` | Staging area for large external inputs (processed → relocated, pointer left) |
| `09_REFERENCE/` | Single-copy knowledge base |
| `99_ARCHIVE/` | Immutable history (read-only, append-only) |
| `.dsh/skills/` | 7 governance skills |
| `scripts/` | check_placement / align_environment / session_analyzer / session_index_update |
| `docs/` | Documentation |

## Documentation

- [Architecture reference](docs/architecture.md) : how the system works, from components to end-to-end task flow
- [Design rationale](docs/design-rationale.md) : why each design decision was made, with data and references
- [File conventions](docs/file-conventions.md) : where every type of file goes, naming rules, lightweight vs. project tasks
- [Migration from v1](docs/MIGRATION.md) : upgrade guide for v1 users, with a prompt to let AI handle the deployment

Full documentation is in Chinese; this README and the architecture reference have English versions. Remaining docs are being translated over time.

## Feedback

Found a problem or have a suggestion? Open an [Issue](https://github.com/MagicalYuYu/agent-operating-system/issues) or start a [Discussion](https://github.com/MagicalYuYu/agent-operating-system/discussions).

## License

MIT + additional terms (no standalone commercial repackaging). See [LICENSE](LICENSE).
