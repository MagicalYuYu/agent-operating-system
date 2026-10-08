#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AOS 会话索引自动化。
扫描 DSH 会话档案（~/.dsh/sessions/{workspace}/*/session.v3.jsonl.zstd），筛选重要会话
（压缩体积 ≥512KB 或内容含 goal/change 事件），生成一行摘要追加到
06_LOGS/aos/session_index.md 的『### 未归档会话（自动索引）』小节。
幂等：文件中任何位置已出现 [id前8位] 的会话不再追加；单次上限 30 行；无新增不改文件。
只允许写自动小节，绝不触碰文件其余部分。

路径全部参数化：
  --sessions DIR   会话档案根目录，默认 ~/.dsh/sessions
  --workspace NAME 工作区会话子目录名；缺省按脚本位置自动推导（AOS 根路径编码为
                   会话目录名，例 C:\\Work\\AOS → --C-Work-AOS--：去冒号、路径分隔符
                   替换为 -、两侧加 --；推导失败退回会话根目录，需显式 --workspace）
  --index FILE     目标索引文件，默认 {AOS_ROOT}/06_LOGS/aos/session_index.md
                   （AOS_ROOT = scripts/ 的上级目录，按脚本位置推导，不依赖绝对路径）
"""
import argparse
import io
import json
import os
import re
from datetime import datetime
from pathlib import Path

import zstandard

AOS_ROOT = Path(__file__).resolve().parent.parent
SECT_TITLE = "### 未归档会话（自动索引）"
SIZE_THRESHOLD = 512 * 1024   # 重要阈值：压缩体积 ≥512KB
MAX_ADD = 30                  # 单次追加行数上限
# 首条用户消息里的系统噪声前缀（非真人输入），命中则跳过继续找下一条
NOISE_PREFIX = ("<system-reminder", "current runtime context", "[file-mount:", "[file:")


def derive_sessions_dir(sessions_root: Path) -> Path:
    """按脚本位置推导本工作区的会话子目录；推导失败退回会话根目录。"""
    encoded = str(AOS_ROOT).replace(":", "").replace("\\", "-").replace("/", "-")
    cand = sessions_root / f"--{encoded}--"
    return cand if cand.is_dir() else sessions_root


def id8_of(dirname):
    """会话 id 前 8 位：目录名去掉可选 session- 前缀后取前 8 字符。"""
    name = dirname[8:] if dirname.startswith("session-") else dirname
    return name[:8].lower()


def extract_user_text(data):
    """从 user 类记录的 data.content 提取首段可用 text；插件通知与噪声文本返回 None。"""
    src = data.get("source") or {}
    if src.get("kind") == "plugin":
        return None
    content = data.get("content")
    if not isinstance(content, list):
        return None
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            txt = str(block.get("text", "")).strip()
            if txt and not txt.lower().startswith(NOISE_PREFIX):
                return re.sub(r"\s+", " ", txt)
    return None


def scan_session(zst_path, size_bytes):
    """流式解压逐行扫描：返回 (首条用户文本, goal名, 是否含 goal/change, 首条时间ms)。全程坏行跳过。"""
    first_user, goal_name, has_goal, first_ms = None, None, False, None
    try:
        with open(zst_path, "rb") as f:
            reader = io.TextIOWrapper(
                zstandard.ZstdDecompressor().stream_reader(f),
                encoding="utf-8", errors="replace")
            for line in reader:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue          # 坏行跳过
                if first_ms is None and isinstance(obj.get("time"), (int, float)):
                    first_ms = obj["time"]
                t = str(obj.get("type", ""))
                if not has_goal and "goal/change" in t:
                    has_goal = True
                    d = obj.get("data") or {}
                    goal_name = d.get("objective") or d.get("name") or goal_name
                if first_user is None and "user" in t:
                    first_user = extract_user_text(obj.get("data") or {})
                if first_user is not None and (has_goal or size_bytes >= SIZE_THRESHOLD):
                    break              # 摘要与重要性均已确定，提前结束
    except Exception:
        pass                            # 解压失败按空会话处理
    return first_user, goal_name, has_goal, first_ms


def main():
    ap = argparse.ArgumentParser(description="AOS 会话索引自动化（06_LOGS/aos/session_index.md）")
    ap.add_argument("--sessions", default=os.path.join(os.path.expanduser("~"), ".dsh", "sessions"),
                    help="会话档案根目录（默认 ~/.dsh/sessions）")
    ap.add_argument("--workspace", default=None,
                    help="工作区会话子目录名（缺省按脚本位置自动推导）")
    ap.add_argument("--index", default=None,
                    help="目标索引文件（默认 {AOS_ROOT}/06_LOGS/aos/session_index.md）")
    args = ap.parse_args()

    index_md = Path(args.index) if args.index else AOS_ROOT / "06_LOGS" / "aos" / "session_index.md"
    sessions_root = Path(args.sessions)
    base = sessions_root / args.workspace if args.workspace else derive_sessions_dir(sessions_root)
    if not base.is_dir():
        ap.error(f"会话目录不存在: {base}（用 --sessions/--workspace 指定）")

    rows = []                           # (日期, id8, 描述, 压缩KB)
    for dirname in os.listdir(base):
        zst = os.path.join(base, dirname, "session.v3.jsonl.zstd")
        if not os.path.isfile(zst):
            continue
        try:
            size = os.path.getsize(zst)
        except OSError:
            continue
        kb = size // 1024
        first_user, goal_name, has_goal, first_ms = scan_session(zst, size)
        if size < SIZE_THRESHOLD and not has_goal:
            continue                     # 既不达标也无 goal/change → 非重要会话
        desc = (first_user or goal_name or "—")[:60].replace("|", "／")  # 竖线会破坏表格
        ts = first_ms / 1000 if first_ms else os.path.getmtime(zst)
        rows.append((datetime.fromtimestamp(ts).strftime("%Y-%m-%d"), id8_of(dirname), desc, kb))

    if not index_md.exists():
        index_md.parent.mkdir(parents=True, exist_ok=True)
        index_md.write_text("# AOS 会话索引\n\n", encoding="utf-8")  # 首次运行自动建档
    with open(index_md, "rb") as f:      # 先按原始字节探测 BOM，写回保持原样
        raw = f.read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    rows = sorted(r for r in rows if f"[{r[1]}]" not in text)   # 幂等 + 日期升序
    rows = rows[:MAX_ADD]
    if not rows:
        print("无新增")
        return
    new_lines = [f"| {d} [{i}] | （自动：{desc}） | {kb} |" for d, i, desc, kb in rows]
    lines = text.split("\n")
    try:                                   # 定位自动小节（存在则追加到小节末尾）
        head = lines.index(SECT_TITLE)
        end = len(lines)
        for k in range(head + 1, len(lines)):
            if lines[k].lstrip().startswith("#"):
                end = k
                break
        insert_at = end
        while insert_at > head + 1 and lines[insert_at - 1].strip() == "":
            insert_at -= 1                 # 不在段落尾部空行间插行
        lines[insert_at:insert_at] = new_lines
    except ValueError:                     # 小节不存在：文件末尾创建小节标题+表头
        if lines and lines[-1].strip() != "":
            lines.append("")
        lines += [SECT_TITLE, "", "| 日期 [id] | 主题 | 压缩KB |", "|---|---|---|"] + new_lines
    out = "\n".join(lines)
    if not out.endswith("\n"):
        out += "\n"
    with open(index_md, "w", encoding="utf-8" + ("-sig" if bom else ""), newline="") as f:
        f.write(out)
    print(f"新增 {len(new_lines)} 行：")
    for ln in new_lines:
        print("  " + ln)


if __name__ == "__main__":
    main()
