"""日志过滤规则模块。

提供 LogFilter 类，支持按级别、关键词、时间范围过滤日志条目。
"""

from datetime import datetime
from typing import List, Optional

from loganalyzer.parser import LogEntry


class LogFilter:
    """日志过滤器。

    所有方法均为静态方法，接收 LogEntry 列表并返回过滤后的列表。
    """

    @staticmethod
    def by_level(entries: List[LogEntry], level: str) -> List[LogEntry]:
        """按日志级别过滤。

        参数:
            entries: 日志条目列表。
            level: 目标级别（INFO / WARN / ERROR），不区分大小写。

        返回:
            list: 仅包含指定级别的日志条目。
        """
        target_level = level.upper()
        return [entry for entry in entries if entry.level == target_level]

    @staticmethod
    def by_keyword(entries: List[LogEntry], keyword: str) -> List[LogEntry]:
        """按关键词过滤（在消息内容中匹配）。

        参数:
            entries: 日志条目列表。
            keyword: 待匹配的关键词。

        返回:
            list: 消息内容包含关键词的日志条目。
        """
        if not keyword:
            return list(entries)
        return [entry for entry in entries if keyword in entry.message]

    @staticmethod
    def by_time_range(
        entries: List[LogEntry],
        start: Optional[datetime],
        end: Optional[datetime],
    ) -> List[LogEntry]:
        """按时间范围过滤。

        参数:
            entries: 日志条目列表。
            start: 起始时间（包含），为 None 表示不限制起始。
            end: 结束时间（包含），为 None 表示不限制结束。

        返回:
            list: 时间戳在 [start, end] 区间内的日志条目。
        """
        result = []
        for entry in entries:
            # 起始时间检查
            if start is not None and entry.timestamp < start:
                continue
            # 结束时间检查
            if end is not None and entry.timestamp > end:
                continue
            result.append(entry)
        return result
