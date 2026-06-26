"""报告生成器模块。

提供 Reporter 类，用于生成文本/JSON 格式的分析报告，并统计高频错误。
"""

import json
from collections import Counter
from typing import Dict, List

from loganalyzer.parser import LogEntry


class Reporter:
    """报告生成器。

    根据解析后的日志数据生成可读的报告内容。
    """

    def generate_text_report(self, stats: Dict) -> str:
        """生成文本格式报告。

        参数:
            stats: 统计数据字典，需包含以下字段：
                - logfile: 日志文件路径
                - entries: LogEntry 列表
                - skipped: 跳过的行数
                - level_filter: 级别过滤标识（可为 None）

        返回:
            str: 文本格式报告内容。
        """
        entries: List[LogEntry] = stats.get("entries", [])
        total = len(entries)
        skipped = stats.get("skipped", 0)
        logfile = stats.get("logfile", "unknown")
        level_filter = stats.get("level_filter")

        # 统计各级别条目数
        level_counts = self._count_by_level(entries)

        # 构建报告文本
        lines = []
        lines.append("=" * 30)
        lines.append("   LogAnalyzer 分析报告")
        lines.append("=" * 30)
        lines.append("")
        lines.append(f"日志文件：{logfile}")
        lines.append(f"解析条目总数：{total}")
        lines.append(f"跳过无效行：{skipped}")

        # 若指定了级别过滤，追加提示
        if level_filter is not None:
            lines.append(f"（已按级别过滤：{level_filter}）")

        lines.append("")
        lines.append("【级别统计】")
        for level in ("ERROR", "WARN", "INFO"):
            count = level_counts.get(level, 0)
            percent = (count / total * 100) if total > 0 else 0.0
            lines.append(f"  {level:<5}: {count:>4} 条 ({percent:6.2f}%)")

        # 高频错误部分由调用方通过 format_top_errors 追加
        return "\n".join(lines) + "\n"

    def generate_json_report(self, stats: Dict) -> str:
        """生成 JSON 格式报告。

        参数:
            stats: 统计数据字典，需包含以下字段：
                - logfile: 日志文件路径
                - entries: LogEntry 列表
                - skipped: 跳过的行数
                - level_filter: 级别过滤标识（可为 None）

        返回:
            str: JSON 格式报告内容（格式化缩进）。
        """
        entries: List[LogEntry] = stats.get("entries", [])
        total = len(entries)
        skipped = stats.get("skipped", 0)
        logfile = stats.get("logfile", "unknown")

        # 统计各级别条目数与百分比
        level_counts = self._count_by_level(entries)
        level_percentages = {
            level: (level_counts.get(level, 0) / total * 100) if total > 0 else 0.0
            for level in ("ERROR", "WARN", "INFO")
        }

        # 统计高频错误（默认取全部 ERROR 的前 5）
        top_errors = self.get_top_errors(entries, n=5)

        # 组装报告字典
        report = {
            "logfile": logfile,
            "total_entries": total,
            "skipped_lines": skipped,
            "level_stats": {
                "ERROR": level_counts.get("ERROR", 0),
                "WARN": level_counts.get("WARN", 0),
                "INFO": level_counts.get("INFO", 0),
            },
            "level_percentages": {
                "ERROR": round(level_percentages["ERROR"], 2),
                "WARN": round(level_percentages["WARN"], 2),
                "INFO": round(level_percentages["INFO"], 2),
            },
            "top_errors": top_errors,
        }

        return json.dumps(report, ensure_ascii=False, indent=4)

    def get_top_errors(self, entries: List[LogEntry], n: int) -> List[Dict]:
        """获取前 N 个高频错误。

        参数:
            entries: 日志条目列表。
            n: 返回的错误条目数。

        返回:
            list: 高频错误列表，每项含 count 与 message 字段，按次数降序排列。
        """
        if n <= 0:
            return []

        # 仅统计 ERROR 级别
        error_entries = [e for e in entries if e.level == "ERROR"]

        # 按消息内容计数
        counter = Counter(entry.message for entry in error_entries)

        # 取前 N 个
        result = []
        for message, count in counter.most_common(n):
            result.append({"count": count, "message": message})
        return result

    def format_top_errors(self, top_errors: List[Dict]) -> str:
        """格式化高频错误为文本段落（供追加到文本报告）。

        参数:
            top_errors: get_top_errors 返回的列表。

        返回:
            str: 格式化的高频错误文本。
        """
        if not top_errors:
            return ""

        lines = ["", "【高频错误 Top %d】" % len(top_errors)]
        for idx, item in enumerate(top_errors, start=1):
            count = item["count"]
            message = item["message"]
            lines.append(f"  {idx}. [{count:>2} 次] {message}")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _count_by_level(entries: List[LogEntry]) -> Dict[str, int]:
        """统计各级别条目数。

        参数:
            entries: 日志条目列表。

        返回:
            dict: 键为级别，值为条目数。
        """
        counts: Dict[str, int] = {"ERROR": 0, "WARN": 0, "INFO": 0}
        for entry in entries:
            if entry.level in counts:
                counts[entry.level] += 1
            else:
                # 未知级别也计入，避免数据丢失
                counts[entry.level] = counts.get(entry.level, 0) + 1
        return counts
