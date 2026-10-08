#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AOS 环境对齐器 — 读 .dsh/skill-manifest.json，检测缺失组件，支持一键补装

用法:
  python scripts/align_environment.py            # 检测模式：报告缺失，不动手
  python scripts/align_environment.py --apply    # 执行模式：对缺失项运行 install 命令
AOS 根按脚本自身位置推导（scripts/ 的上级目录），不依赖任何绝对路径。
检测方式（无 API 依赖，纯文件系统）:
  project-skill → <AOS>/.dsh/skills/{name}/SKILL.md
  dsh-plugin    → ~/.dsh/profiles/*/node_modules/{name}
  user-skill    → ~/.agents/skills/{name}/SKILL.md
退出码: 0=全部就绪 2=有缺失（--apply 后仍缺）
"""
import json, os, subprocess, sys
from pathlib import Path

AOS = Path(__file__).resolve().parent.parent
MANIFEST = AOS / ".dsh" / "skill-manifest.json"

def detect(kind: str, name: str, detect_expr: str) -> bool:
    expr = detect_expr.replace("%USERPROFILE%", os.path.expanduser("~")).replace("/", os.sep)
    # 相对路径锚定到 AOS 根（不依赖 cwd）
    p = Path(expr)
    if not p.is_absolute():
        expr = str(AOS / expr)
    import glob
    return any(glob.glob(expr))

def main():
    apply = "--apply" in sys.argv
    data = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    missing, broken = [], []
    for c in data["components"] + data.get("user_skills", []):
        if detect(c["kind"], c["name"], c["detect"]):
            print(f"[OK]        {c['name']} ({c['kind']})")
        elif not c.get("required", True) or c.get("status") == "retired":
            # optional（required:false）与已退役（status:retired）组件未安装不计缺失
            print(f"[SKIP]      {c['name']} ({c['kind']}) — optional/retired，未装不计缺失")
        else:
            tag = "MISSING" if c.get("install") else "BROKEN"
            (missing if c.get("install") else broken).append(c)
            print(f"[{tag:<7}] {c['name']} ({c['kind']})  install: {c.get('install')}")
    # 能力抽检（在场≠可用）
    print("--- capability checks ---")
    cred = AOS / "04_MEMORY" / "credentials.json"
    try:
        json.loads(cred.read_text(encoding="utf-8-sig"))
        print("[CAP-OK]   credentials.json parses (utf-8-sig)")
    except Exception as e:
        print(f"[CAP-FAIL] credentials.json: {e}")
        broken.append({"name": "capability:credentials-parse"})
    if os.environ.get("EXA_API_KEY"):
        print("[CAP-OK]   EXA_API_KEY present in env")
    else:
        print("[CAP-WARN] EXA_API_KEY not in current env (user级环境变量需新进程读取)")
    if broken:
        print(f"\n!! {len(broken)} 个 project-skill 缺失且无 install 命令（应随 AOS 仓库存在，检查同步完整性）")
    if not missing and not broken:
        print("\n环境对齐：全部就绪"); sys.exit(0)
    print(f"\n缺失 {len(missing)} 项 / 异常 {len(broken)} 项")
    if apply and missing:
        for c in missing:
            print(f">>> 执行: {c['install']}")
            try:
                r = subprocess.run(c["install"], shell=True, capture_output=True, text=True, timeout=600)
                print(f"    exit={r.returncode} {r.stdout[-200:] if r.stdout else r.stderr[-200:]}")
            except subprocess.TimeoutExpired:
                print(f"    [TIMEOUT] 安装超过 600s，请手动执行: {c['install']}")
        print("安装后请重跑本脚本（不带 --apply）复核，并更新 manifest 的 pin 字段")
    elif not apply:
        print("（检测模式。补装: 加 --apply；project-skill 异常请同步 AOS 仓库）")
    sys.exit(2)

if __name__ == "__main__":
    main()
