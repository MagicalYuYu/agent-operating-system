"""日志解析器模块。

提供 LogParser 类与 LogEntry 数据类，用于解析标准格式的日志行与日志文件。
"""

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

# 标准日志行正则：[2026-06-25 10:30:45] [ERROR] message here
# 分组说明：
#   group 1 — 时间戳文本：2026-06-25 10:30:45
#   group 2 — 日志级别：INFO / WARN / ERROR（不区分大小写）
#   group 3 — 消息内容
# 使用 re.IGNORECASE 标志，使 [warn] / [Warn] 等小写/混合写法均可匹配
LOG_LINE_PATTERN = re.compile(
    r"^\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]\s*\[(INFO|WARN|ERROR)\]\s*(.*)$",
    re.IGNORECASE,
)

# 时间戳解析格式
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


@dataclass
class LogEntry:
    """日志条目数据类。

    属性:
        timestamp: 日志时间戳。
        level: 日志级别（大写形式，如 INFO / WARN / ERROR）。
        message: 日志消息内容。
    """

    timestamp: datetime
    level: str
    message: str


class LogParser:
    """日志解析器。

    解析标准格式的日志行与日志文件，返回 LogEntry 对象。
    标准格式：[2026-06-25 10:30:45] [ERROR] message here
    """

    def parse_line(self, line: str) -> LogEntry:
        """解析单行日志，返回 LogEntry 对象。

        参数:
            line: 单行日志文本。

        返回:
            LogEntry: 解析得到的日志条目。

        Raises:
            ValueError: 当行不符合标准日志格式时抛出。
        """
        # 去除行尾换行符与首尾空白
        stripped_line = line.strip()

        # 正则匹配
        match = LOG_LINE_PATTERN.match(stripped_line)
        if not match:
            raise ValueError(f"无法解析的日志行格式：{stripped_line!r}")

        timestamp_str, level_str, message_str = match.groups()

        # 解析时间戳
        try:
            timestamp = datetime.strptime(timestamp_str, TIMESTAMP_FORMAT)
        except ValueError as exc:
            raise ValueError(f"无效的时间戳格式：{timestamp_str!r}") from exc

        # 级别统一转为大写
        return LogEntry(
            timestamp=timestamp,
            level=level_str.upper(),
            message=message_str.strip(),
        )

    def parse_file(self, filepath: str) -> Tuple[List[LogEntry], int]:
        """解析整个日志文件，返回 LogEntry 列表与跳过行数。

        参数:
            filepath: 日志文件路径。

        返回:
            tuple: (entries, skipped)
                - entries: 成功解析的 LogEntry 列表
                - skipped: 跳过的无效行数

        Raises:
            FileNotFoundError: 当文件不存在时抛出。
        """
        path = Path(filepath)
        if not path.is_file():
            raise FileNotFoundError(f"日志文件不存在：{filepath}")

        entries: List[LogEntry] = []
        skipped = 0

        # 逐行读取并解析
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for raw_line in f:
                # 跳过空行
                if not raw_line.strip():
                    skipped += 1
                    continue
                try:
                    entry = self.parse_line(raw_line)
                    entries.append(entry)
                except ValueError:
                    # 不符合格式的行计入跳过数，不中断解析
                    skipped += 1

        return entries, skipped
