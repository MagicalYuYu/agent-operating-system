#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DSH 会话档案分析器 — 解压 session.v3.jsonl.zstd，输出 token/工具/错误/耗时结构摘要

用法:
  python scripts/session_analyzer.py [--sessions DIR] [--workspace NAME] [会话目录名]
  --sessions DIR    会话档案根目录，默认 ~/.dsh/sessions
  --workspace NAME  工作区会话子目录名；缺省时按脚本位置自动推导（AOS 根路径编码为
                    会话目录名，例 C:\\Work\\AOS → --C-Work-AOS--：去冒号、路径分隔符
                    替换为 -、两侧加 --；推导失败退回会话根目录，需显式 --workspace）
  会话目录名        省略时取压缩体积最大的会话
依赖: pip install zstandard
"""
import argparse
import json
import os
from collections import Counter
from pathlib import Path

import zstandard


def derive_sessions_dir(sessions_root: Path) -> Path:
    """按脚本位置推导本工作区的会话子目录；推导失败退回会话根目录。"""
    aos_root = Path(__file__).resolve().parent.parent
    encoded = str(aos_root).replace(":", "").replace("\\", "-").replace("/", "-")
    cand = sessions_root / f"--{encoded}--"
    return cand if cand.is_dir() else sessions_root


def main():
    ap = argparse.ArgumentParser(description="DSH 会话档案结构分析器")
    ap.add_argument("--sessions", default=os.path.join(os.path.expanduser("~"), ".dsh", "sessions"),
                    help="会话档案根目录（默认 ~/.dsh/sessions）")
    ap.add_argument("--workspace", default=None,
                    help="工作区会话子目录名（缺省按脚本位置自动推导）")
    ap.add_argument("session", nargs="?", default=None,
                    help="会话目录名（缺省取压缩体积最大的会话）")
    args = ap.parse_args()

    sessions_root = Path(args.sessions)
    sess_dir = sessions_root / args.workspace if args.workspace else derive_sessions_dir(sessions_root)
    if not sess_dir.is_dir():
        ap.error(f"会话目录不存在: {sess_dir}（用 --sessions/--workspace 指定）")

    sessions = []
    for d in os.listdir(sess_dir):
        full = os.path.join(sess_dir, d, "session.v3.jsonl.zstd")
        if os.path.exists(full):
            sessions.append((os.path.getsize(full), d, full))
    if not sessions:
        print(f"该目录下没有会话档案: {sess_dir}")
        return
    sessions.sort(reverse=True)

    target = args.session if args.session else sessions[0][1]

    zst_path = os.path.join(sess_dir, target, "session.v3.jsonl.zstd")
    if not os.path.exists(zst_path):
        print(f"会话不存在: {zst_path}")
        return
    dctx = zstandard.ZstdDecompressor()
    with open(zst_path, 'rb') as f:
        raw = dctx.stream_reader(f).read()
    lines = raw.decode('utf-8', errors='replace').strip().split('\n')

    tool_calls = []
    reasoning_blocks = []
    token_usage = []
    step_times = []
    errors = []
    goals = []

    for line in lines:
        try:
            obj = json.loads(line)
            etype = obj.get('type', '')

            if etype == 'tool/call':
                data = obj.get('data', {})
                inp = data.get('input', {})
                tool_calls.append({
                    'name': data.get('name', '?'),
                    'input_preview': str(inp)[:100] if inp else '',
                })
            elif etype == 'tool/result':
                data = obj.get('data', {})
                if data.get('isError') or data.get('is_error'):
                    errors.append(f"{data.get('name','?')}: {str(data.get('content',''))[:100]}")
            elif etype == 'assistant/message':
                data = obj.get('data', {})
                msg = data.get('message', {})
                usage = data.get('usage', {})
                if usage:
                    token_usage.append(usage)
                content = msg.get('content', [])
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict):
                            if block.get('type') == 'reasoning':
                                reasoning_blocks.append(str(block.get('text', ''))[:300])
            elif etype == 'goal/change':
                goals.append(obj.get('data', {}))
            elif etype == 'step/end':
                d = obj.get('data', {})
                step_times.append(d.get('durationMs', 0))
        except Exception:
            pass

    # 汇总输出
    print(f"Session: {target[:20]}...")
    print(f"Events: {len(lines)} | Steps: {len(step_times)} | Tool calls: {len(tool_calls)} | Errors: {len(errors)}")

    print("\n=== Token 使用 ===")
    total_in = sum(u.get('inputTokens', 0) for u in token_usage)
    total_out = sum(u.get('outputTokens', 0) for u in token_usage)
    total_cache = sum(u.get('cacheReadTokens', 0) for u in token_usage)
    print(f"Input: {total_in:,} | Output: {total_out:,} | CacheRead: {total_cache:,} | Total: {total_in+total_out:,}")
    if token_usage:
        print(f"单步平均 input: {total_in//max(1,len(token_usage)):,} | 最大单步: {max(u.get('inputTokens',0) for u in token_usage):,}")

    print("\n=== 工具分布 ===")
    for name, count in Counter(t['name'] for t in tool_calls).most_common(15):
        print(f"  {name}: {count}")

    print(f"\n=== 错误 ({len(errors)}) ===")
    for e in errors[:5]:
        print(f"  {e}")

    print(f"\n=== 思考样本 ({len(reasoning_blocks)} blocks) ===")
    for i, r in enumerate(reasoning_blocks[:2]):
        print(f"  [{i+1}] {r[:200]}...")

    print(f"\n=== Goal 变化 ({len(goals)}) ===")
    for g in goals[:3]:
        print(f"  {str(g)[:100]}")

    print("\n=== 步骤耗时 ===")
    if step_times:
        times = [t for t in step_times if t]
        print(f"  平均: {sum(times)//len(times)}ms | 最长: {max(times)}ms | 总耗时: {sum(times)//1000}s")


if __name__ == "__main__":
    main()
