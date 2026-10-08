#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AOS v2 文件落位校验器 — file-placement skill §2.4 四禁令 + 顶层路由检查
用法: python scripts/check_placement.py [--root DIR] [--project {name}]
只读检查，绝不移动/删除。退出码 0=无 error（warn 不影响） 1=有 error
功能：①根层/落位合规 ②04_MEMORY 乱码(U+FFFD)检查 ③05_CACHE 超期检查(按 st_ctime，绝不用 mtime)
④scripts 全量 ast 语法自检（含本脚本自身）
输出分级：每条违规带 [error]/[warn] 前缀，结尾汇总 error=N warn=M
ROOT 默认按脚本自身位置推导（scripts/ 的上级目录），不依赖任何绝对路径；--root 可覆盖。
"""
import ast, os, re, sys, time
from pathlib import Path

ROOT = Path(sys.argv[sys.argv.index("--root") + 1]) if "--root" in sys.argv else Path(__file__).resolve().parent.parent
PROJECTS = ROOT / "01_PROJECTS"
MEDIA_EXT = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".ico"}
ARCHIVE_EXT = {".zip", ".7z", ".tar", ".gz"}
ROOT_ALLOWED_FILES = {"AGENTS.md", "README.md", "CHANGELOG.md", ".gitignore", "LICENSE",
                      "package.json", "package-lock.json", "tsconfig.json", "index.html", "requirements.txt",
                      "pyproject.toml", "setup.py", "Cargo.toml", "go.mod", "pnpm-lock.yaml", "yarn.lock",
                      "vite.config.ts", "vite.config.js", "electron-builder.yml", "Dockerfile", "docker-compose.yml"}
# v2 项目两件套：AGENTS.md + README.md；v1 的 STATUS.md/PROGRESS.md 已废除（状态入 AGENTS.md 头部摘要），不再入白名单
ROOT_ALLOWED_LOWER = {s.lower() for s in ROOT_ALLOWED_FILES}  # 白名单大小写不敏感（progress.md 误报教训）
DATE_OK = re.compile(r"^\d{8}(_[a-z0-9\-]+)?$")
SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build", "unpacked", "backup", "99_ARCHIVE"}

violations = []
def v(rule, path, hint="", sev="error"):
    """sev: error=阻断级（exit 1）/ warn=提示级（不影响退出码）"""
    violations.append(f"[{sev}] [{rule}] {path}" + (f"  → {hint}" if hint else ""))

def iter_files(base: Path, max_depth=4):
    base_depth = len(base.parts)
    stack = [base]
    while stack:
        d = stack.pop()
        try:
            for e in d.iterdir():
                if len(e.parts) - base_depth >= max_depth:
                    continue
                if e.is_dir():
                    if e.name not in SKIP_DIRS:
                        stack.append(e)
                        yield e
                else:
                    yield e
        except (PermissionError, OSError):
            pass

def check_project(pdir: Path):
    loose = [f for f in pdir.iterdir() if f.is_file() and f.name.lower() not in ROOT_ALLOWED_LOWER]
    if len(loose) >= 3:
        v("根层堆放", pdir, f"{len(loose)} 个散落文件 → 按类型入 docs/scripts/config/assets")
    for f in loose:
        if f.suffix.lower() in {".py", ".ps1", ".sh", ".bat"}:
            v("根层脚本", f, "→ scripts/{dev|deploy|verify}/（代码文件归 src/）")
    for e in iter_files(pdir, max_depth=5):
        if not e.is_file():
            if re.match(r"^\d{4}", e.name) and not DATE_OK.match(e.name) and e.parent not in (pdir, pdir / "src"):
                v("非标日期命名", e, "→ YYYYMMDD[_slug]")
            continue
        in_src = "src" in e.parts
        if in_src and e.suffix.lower() == ".log":
            v("src混入日志", e, "→ 06_LOGS/{project}/")
        elif in_src and e.suffix.lower() in MEDIA_EXT:
            is_runtime = e.parent.name.lower() in {"icons", "icon", "assets", "images"} or e.name.lower().startswith("logo") or "favicon" in e.name.lower()
            site_bundle = any((e.parent / m).exists() for m in ("index.html", "manifest.json", "CNAME"))  # 部署站点目录（静态站点/PWA bundle）内图片=运行时资产，豁免
            rel_parts = e.parts[e.parts.index("src") + 1:]
            looks_doc = e.parent.name.lower() == "docs" or re.match(r"^(ui-|screen|shot)", e.stem, re.I) or rel_parts[:-1] == ()
            if not is_runtime and not site_bundle and looks_doc:
                v("src混入文档图", e, "→ docs/media/（运行时图标/logo 豁免）")
        elif in_src and e.suffix.lower() in ARCHIVE_EXT:
            v("src混入压缩包", e, "→ backup/ 或解压后归位")
    ag = pdir / "AGENTS.md"
    if ag.exists():
        text = ag.read_text(encoding="utf-8", errors="ignore")
        if not re.search(r"(运行|启动|run).{0,40}(命令|`)", text, re.I):
            v("缺命令地图", ag, "→ AGENTS.md 应列 build/test/run 各一条命令")

def check_top():
    # AOS 根层唯一合法项（公开仓库根层标准文件：README/LICENSE/CHANGELOG/.github）
    allowed = {".dsh", ".uploads", ".github", "01_PROJECTS", "04_MEMORY", "05_CACHE", "06_LOGS", "07_EXPORTS",
               "08_INBOX", "09_REFERENCE", "99_ARCHIVE", "scripts", "docs",
               "AGENTS.md", "README.md", "LICENSE", "CHANGELOG.md"}
    for f in ROOT.iterdir():
        if f.name not in allowed:
            v("顶层散落", f, "→ 按归属入对应目录（仓库工件不入本目录树）")
    cache = ROOT / "05_CACHE"
    if cache.exists():
        for f in cache.iterdir():
            if f.is_file() and f.name != "README.md":  # 目录自述文件豁免
                v("CACHE根层散放", f, "→ 05_CACHE/{project}/{YYYYMMDD}/")
    exports = ROOT / "07_EXPORTS"
    if exports.exists():
        for f in exports.iterdir():  # 只查根层散放（子目录=项目分层区，合法）
            if f.is_file() and f.suffix.lower() == ".md":
                ok = f.name == "README.md" or f.stem.lower().startswith("release_notes")
                if not ok:
                    v("07孤立MD", f, "→ 移项目 docs/ 或 07_EXPORTS/{project}/")
    agents = ROOT / ".agents"
    if agents.exists():
        for g in agents.rglob(".git"):
            v("agents含git克隆", g.parent, "→ 第三方 skills 应装 ~/.agents/skills（用户级）")

def check_memory_encoding():
    """④ 04_MEMORY 乱码检查：递归扫全部 .md（含 INDEX.md），内容含 U+FFFD 替换符 → 每文件一条 [error]
    errors='replace' 使非 UTF-8 落盘的字节也折算为 U+FFFD，一并捕获（GBK 乱码坑）"""
    mem = ROOT / "04_MEMORY"
    if not mem.exists():
        return
    for f in sorted(mem.rglob("*.md")):
        if not f.is_file():
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except (PermissionError, OSError):
            continue
        n = text.count("\ufffd")
        if n:
            v("记忆乱码", f, f"含 {n} 处 U+FFFD → 编码已损坏，按源修复后重写落盘")

def check_cache_ttl():
    """⑤ 05_CACHE 超期检查：各顶层目录按 st_ctime（Windows=创建时间）统计创建超 90 天的文件数与总 MB
    ⚠ 绝不用 st_mtime——ROM/跨盘拷贝会保留源 mtime，实证误判事故
    跳过 _template（模板目录不计缓存）；只 [warn] 不 error——近期活跃数据不得误报"""
    cache = ROOT / "05_CACHE"
    if not cache.exists():
        return
    skip = {"_template"}
    cutoff = time.time() - 90 * 86400
    for d in sorted(cache.iterdir()):
        if not d.is_dir() or d.name in skip:
            continue
        stale, total = 0, 0
        stack = [str(d)]
        while stack:
            cur = stack.pop()
            try:
                with os.scandir(cur) as it:  # os.scandir 递归遍历，stat 免二次系统调用
                    for e in it:
                        try:
                            if e.is_dir(follow_symlinks=False):
                                stack.append(e.path)
                            elif e.is_file(follow_symlinks=False):
                                st = e.stat()  # Windows: st_ctime=创建时间（非 mtime）
                                if st.st_ctime < cutoff:
                                    stale += 1
                                    total += st.st_size
                        except OSError:
                            continue
            except OSError:
                continue
        if stale:
            v("CACHE超期", d, f"{stale} 个文件创建超 90 天，共 {total / 1048576:.1f} MB（按 st_ctime 判定）", sev="warn")

def check_scripts_smoke():
    """⑥ scripts 语法自检：每个 .py 过 ast.parse（含本脚本自身）
    脚本坏了机器当场报红，不等到调用时才炸"""
    sdir = ROOT / "scripts"
    if not sdir.exists():
        return
    for f in sorted(sdir.glob("*.py")):
        try:
            ast.parse(f.read_text(encoding="utf-8-sig", errors="replace"), filename=str(f))
        except SyntaxError as ex:
            v("脚本语法坏", f, f"ast.parse 失败：第 {ex.lineno} 行 {ex.msg}")

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # 修 GBK 控制台乱码
    except (AttributeError, OSError):
        pass
    if "--project" in sys.argv:
        targets = [PROJECTS / sys.argv[sys.argv.index("--project") + 1]]
    else:
        targets = [d for d in PROJECTS.iterdir() if d.is_dir()] if PROJECTS.exists() else []
    for p in targets:
        if p.exists():
            check_project(p)
    if "--project" not in sys.argv:
        check_top()
        check_memory_encoding()
        check_cache_ttl()
        check_scripts_smoke()
    n_err = sum(1 for x in violations if x.startswith("[error]"))
    n_warn = len(violations) - n_err
    print(f"检查 {len(targets)} 个项目 + 顶层")
    if violations:
        print(f"违规 {len(violations)} 项:")
        for line in violations:
            print(" ", line)
    else:
        print("全部通过")
    print(f"error={n_err} warn={n_warn}")  # 结尾汇总行
    sys.exit(1 if n_err else 0)  # 仅 error 触发退出码 1，warn 不影响

if __name__ == "__main__":
    main()
