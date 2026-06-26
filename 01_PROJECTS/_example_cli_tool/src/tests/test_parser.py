"""LogParser 单元测试模块。

使用 unittest 框架测试 LogParser.parse_line 方法的解析能力，
覆盖标准格式、级别大小写、无效格式三类场景。
"""

import unittest
from datetime import datetime

from loganalyzer.parser import LogParser, LogEntry


class TestLogParserParseLine(unittest.TestCase):
    """LogParser.parse_line 方法测试用例集。"""

    def setUp(self):
        """每个测试用例执行前创建解析器实例。"""
        self.parser = LogParser()

    def test_parse_standard_error_line(self):
        """测试用例 1：解析标准 ERROR 级别日志行。

        验证时间戳、级别、消息三个字段均正确解析。
        """
        line = "[2026-06-25 10:30:45] [ERROR] Database connection timeout"
        entry = self.parser.parse_line(line)

        # 验证返回类型
        self.assertIsInstance(entry, LogEntry)

        # 验证时间戳
        expected_time = datetime(2026, 6, 25, 10, 30, 45)
        self.assertEqual(entry.timestamp, expected_time)

        # 验证级别（统一为大写）
        self.assertEqual(entry.level, "ERROR")

        # 验证消息内容
        self.assertEqual(entry.message, "Database connection timeout")

    def test_parse_lowercase_level(self):
        """测试用例 2：解析小写级别的日志行。

        验证级别不区分大小写，统一转为大写存储。
        """
        line = "[2026-06-25 10:31:02] [warn] Cache miss ratio exceeds 50%"
        entry = self.parser.parse_line(line)

        # 级别应转为大写
        self.assertEqual(entry.level, "WARN")

        # 验证消息内容
        self.assertEqual(entry.message, "Cache miss ratio exceeds 50%")

        # 验证时间戳
        expected_time = datetime(2026, 6, 25, 10, 31, 2)
        self.assertEqual(entry.timestamp, expected_time)

    def test_parse_invalid_format_raises_error(self):
        """测试用例 3：解析非标准格式日志行应抛出 ValueError。

        验证不符合格式的行会被正确识别并抛出异常。
        """
        # 缺少时间戳与级别前缀
        invalid_line = "This is not a valid log line"
        with self.assertRaises(ValueError):
            self.parser.parse_line(invalid_line)

        # 仅时间戳缺少级别
        invalid_line_2 = "[2026-06-25 10:30:45] something happened"
        with self.assertRaises(ValueError):
            self.parser.parse_line(invalid_line_2)

    def test_parse_info_level_with_extra_spaces(self):
        """测试用例 4：解析带额外空格的 INFO 级别日志行。

        验证消息首尾空白被正确去除。
        """
        line = "[2026-06-25 10:31:30] [INFO]    Request processed in 120ms   "
        entry = self.parser.parse_line(line)

        self.assertEqual(entry.level, "INFO")
        # 消息应去除首尾多余空白
        self.assertEqual(entry.message, "Request processed in 120ms")


if __name__ == "__main__":
    unittest.main()
