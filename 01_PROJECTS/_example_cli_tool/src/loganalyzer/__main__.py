"""LogAnalyzer 命令行入口模块。

使用 argparse 解析命令行参数，编排 解析 → 过滤 → 报告 的完整流程。
"""

import argparse
import sys
from pathlib import Path

from loganalyzer.parser import LogParser
from loganalyzer.filters import LogFilter
from loganalyzer.reporter import Reporter


def build_arg_parser():
    """构建命令行参数解析器。

    返回:
        argparse.ArgumentParser: 配置完成的参数解析器实例。
    """
    parser = argparse.ArgumentParser(
        prog="loganalyzer",
        description="LogAnalyzer 日志分析工具 — 统计日志级别、过滤条目、生成报告",
    )
    # 位置参数：日志文件路径（必填）
    parser.add_argument(
        "logfile",
        type=str,
        help="待分析的日志文件路径",
    )
    # 可选参数：按级别过滤
    parser.add_argument(
        "--level",
        choices=["INFO", "WARN", "ERROR"],
        default=None,
        help="按日志级别过滤（仅统计/展示该级别）",
    )
    # 可选参数：报告输出文件路径
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="报告输出文件路径（默认输出到控制台）",
    )
    # 可选参数：报告格式
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="报告格式，默认 text",
    )
    # 可选参数：显示前 N 个高频错误
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="显示前 N 个高频错误（默认 5）",
    )
    return parser


def main(argv=None):
    """命令行主入口函数。

    参数:
        argv: 命令行参数列表，为 None 时从 sys.argv 读取。

    返回:
        int: 退出码，0 表示成功，1 表示失败。
    """
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    # 校验日志文件是否存在
    log_path = Path(args.logfile)
    if not log_path.is_file():
        print(f"错误：日志文件不存在或不是文件：{args.logfile}", file=sys.stderr)
        return 1

    # 步骤 1：解析日志文件
    log_parser = LogParser()
    entries, skipped = log_parser.parse_file(args.logfile)

    # 步骤 2：按级别过滤（若指定）
    if args.level is not None:
        entries = LogFilter.by_level(entries, args.level)

    # 步骤 3：生成报告
    reporter = Reporter()
    stats = {
        "logfile": args.logfile,
        "entries": entries,
        "skipped": skipped,
        "level_filter": args.level,
    }

    # 根据格式生成报告内容
    if args.format == "json":
        report_content = reporter.generate_json_report(stats)
    else:
        report_content = reporter.generate_text_report(stats)

    # 追加高频错误（top 为 0 时不输出）
    if args.top > 0:
        top_errors = reporter.get_top_errors(entries, args.top)
        if args.format == "json":
            # JSON 报告已包含 top_errors 字段，此处无需重复追加
            pass
        else:
            # 文本报告追加高频错误部分
            report_content += reporter.format_top_errors(top_errors)

    # 步骤 4：输出报告
    if args.output:
        # 写入文件
        output_path = Path(args.output)
        try:
            output_path.write_text(report_content, encoding="utf-8")
            print(f"报告已写入：{args.output}")
        except OSError as exc:
            print(f"错误：无法写入输出文件 {args.output}：{exc}", file=sys.stderr)
            return 1
    else:
        # 输出到控制台
        print(report_content)

    return 0


if __name__ == "__main__":
    sys.exit(main())
