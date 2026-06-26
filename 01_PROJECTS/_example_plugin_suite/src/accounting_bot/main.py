"""AccountingBot 记账插件。

本插件演示如何实现一个持久化存储的个人记账插件：
- 继承 PluginBase 抽象基类
- 通过事件总线与其他插件通信
- 使用 JSON 文件持久化账目数据

支持的命令：
    /account add [金额] [描述]      新增一笔支出记录
    /account list                    列出所有账目记录
    /account summary                 汇总账目统计信息
    /account clear                   清空所有账目记录
    /account help                    显示帮助信息
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from shared.plugin_base import EventBus, PluginBase


class AccountingBot(PluginBase):
    """个人记账插件。

    通过 /account 命令管理个人账目。
    账目数据持久化到 JSON 文件中，重启后不丢失。
    """

    def __init__(self, event_bus: Optional[EventBus] = None, config: Optional[Dict[str, Any]] = None) -> None:
        """初始化记账插件。

        参数：
            event_bus: 共享事件总线实例
            config: 插件配置，支持以下字段：
                - data_file: 数据存储文件名（默认 accounting_data.json）
                - currency: 货币单位（默认 CNY）
                - max_records: 最大记录数（默认 10000）
        """
        super().__init__(event_bus, config)
        self.name = "accounting_bot"
        # 数据文件路径：与插件主模块同目录
        self._data_file: str = self.config.get("data_file", "accounting_data.json")
        self._currency: str = self.config.get("currency", "CNY")
        self._max_records: int = int(self.config.get("max_records", 10000))
        # 账目记录列表，每条记录为字典
        self._records: List[Dict[str, Any]] = []

    def on_load(self) -> None:
        """插件加载时触发。

        从 JSON 文件加载历史账目数据。
        """
        self._load_records()
        print(f"[{self.name}] 记账插件已加载（已加载 {len(self._records)} 条记录）")
        # 注册事件：允许其他插件请求账目统计
        self.register_event("account.summary", self._handle_summary_request)

    def on_unload(self) -> None:
        """插件卸载时触发。

        保存数据到文件，注销事件处理器。
        """
        self._save_records()
        print(f"[{self.name}] 记账插件已卸载（已保存 {len(self._records)} 条记录）")
        if self.event_bus is not None:
            self.event_bus.unregister("account.summary", self._handle_summary_request)

    def on_message(self, message: Dict[str, Any]) -> Optional[str]:
        """处理接收到的消息。

        解析消息文本，若为 /account 命令则交由 on_command 处理。
        """
        text: str = message.get("text", "").strip()
        if not text.startswith("/account"):
            return None

        parts: List[str] = text.split()
        # parts[0] = "/account"
        # parts[1] = 子命令（add/list/summary/clear/help）
        # parts[2:] = 子命令参数（如金额、描述）
        sub_command = parts[1] if len(parts) > 1 else "help"
        args = parts[2:]
        return self.on_command("account", [sub_command] + args)

    def on_command(self, command: str, args: List[str]) -> Optional[str]:
        """处理 /account 命令。

        支持的子命令：
            add [金额] [描述]    新增支出记录
            list                 列出所有记录
            summary              汇总统计
            clear                清空记录
            help                 帮助信息
        """
        if command != "account":
            return None

        # 取出子命令
        sub_command = args[0].lower() if args else "help"
        sub_args = args[1:] if len(args) > 1 else []

        if sub_command == "add":
            return self._add_record(sub_args)
        elif sub_command == "list":
            return self._list_records()
        elif sub_command == "summary":
            return self._summary()
        elif sub_command == "clear":
            return self._clear_records()
        elif sub_command == "help":
            return self._help()
        else:
            return f"未知子命令：{sub_command}\n输入 /account help 查看帮助"

    def _add_record(self, args: List[str]) -> str:
        """新增一条账目记录。

        参数：
            args: [金额, 描述...]

        返回：
            操作结果字符串
        """
        if len(args) < 2:
            return "参数不足，用法：/account add [金额] [描述]"

        # 解析金额
        try:
            amount = float(args[0])
        except ValueError:
            return f"金额格式错误：{args[0]}，请输入数字"

        if amount <= 0:
            return f"金额必须为正数，收到：{amount}"

        # 描述为剩余参数拼接
        description = " ".join(args[1:]).strip()
        if not description:
            return "请提供账目描述"

        # 检查记录数上限
        if len(self._records) >= self._max_records:
            return f"已达记录上限 {self._max_records}，请先清理历史记录"

        # 构造记录
        record: Dict[str, Any] = {
            "id": self._next_id(),
            "amount": amount,
            "description": description,
            "currency": self._currency,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self._records.append(record)

        # 持久化保存
        self._save_records()

        # 通过事件总线通知其他插件
        self.emit_event("account.recorded", amount=amount, desc=description, record_id=record["id"])

        return f"记账成功 [#{record['id']}]：{self._currency} {amount:.2f} - {description}"

    def _list_records(self) -> str:
        """列出所有账目记录。

        返回：
            格式化的记录列表字符串
        """
        if not self._records:
            return "暂无账目记录，使用 /account add [金额] [描述] 添加记录"

        lines = [f"共 {len(self._records)} 条账目记录："]
        lines.append(f"{'ID':>4}  {'金额':>10}  {'时间':<20}  描述")
        lines.append("-" * 60)
        for record in self._records:
            amount_str = f"{self._currency} {record['amount']:.2f}"
            lines.append(
                f"#{record['id']:>3}  {amount_str:>10}  {record['timestamp']:<20}  {record['description']}"
            )
        return "\n".join(lines)

    def _summary(self) -> str:
        """汇总账目统计信息。

        返回：
            格式化的统计信息字符串
        """
        if not self._records:
            return "暂无账目记录，无法生成汇总"

        total_amount = sum(r["amount"] for r in self._records)
        count = len(self._records)
        avg_amount = total_amount / count if count > 0 else 0
        max_record = max(self._records, key=lambda r: r["amount"])
        min_record = min(self._records, key=lambda r: r["amount"])

        # 按日期分组统计
        daily_stats: Dict[str, float] = {}
        for record in self._records:
            date = record["timestamp"][:10]  # 取 YYYY-MM-DD 部分
            daily_stats[date] = daily_stats.get(date, 0) + record["amount"]

        lines = [
            "═══ 账目汇总 ═══",
            f"记录总数：{count} 条",
            f"总支出：{self._currency} {total_amount:.2f}",
            f"平均每笔：{self._currency} {avg_amount:.2f}",
            f"最大单笔：{self._currency} {max_record['amount']:.2f} - {max_record['description']}",
            f"最小单笔：{self._currency} {min_record['amount']:.2f} - {min_record['description']}",
            "",
            "─── 按日期统计 ───",
        ]
        for date in sorted(daily_stats.keys()):
            lines.append(f"  {date}：{self._currency} {daily_stats[date]:.2f}")

        return "\n".join(lines)

    def _clear_records(self) -> str:
        """清空所有账目记录。

        返回：
            操作结果字符串
        """
        count = len(self._records)
        if count == 0:
            return "暂无记录可清空"

        self._records.clear()
        self._save_records()
        return f"已清空 {count} 条账目记录"

    def _help(self) -> str:
        """返回帮助信息。"""
        return (
            "═══ 记账插件帮助 ═══\n"
            "命令列表：\n"
            "  /account add [金额] [描述]      新增一笔支出记录\n"
            "  /account list                    列出所有账目记录\n"
            "  /account summary                 汇总账目统计信息\n"
            "  /account clear                   清空所有账目记录\n"
            "  /account help                    显示本帮助信息\n"
            "示例：\n"
            "  /account add 50 午餐\n"
            "  /account add 12.5 咖啡\n"
            "数据存储：accounting_data.json"
        )

    def _next_id(self) -> int:
        """生成下一条记录的 ID。

        返回：
            新记录的 ID（自增，从 1 开始）
        """
        if not self._records:
            return 1
        return max(r["id"] for r in self._records) + 1

    def _load_records(self) -> None:
        """从 JSON 文件加载账目数据。

        文件不存在时初始化为空列表。
        """
        data_path = self._get_data_path()
        if not os.path.exists(data_path):
            self._records = []
            return

        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 兼容字段名 records 或直接为列表
            if isinstance(data, dict):
                self._records = data.get("records", [])
            elif isinstance(data, list):
                self._records = data
            else:
                self._records = []
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[{self.name}] 加载账目数据失败：{exc}，将使用空记录")
            self._records = []

    def _save_records(self) -> None:
        """保存账目数据到 JSON 文件。"""
        data_path = self._get_data_path()
        data = {
            "currency": self._currency,
            "count": len(self._records),
            "records": self._records,
        }
        try:
            with open(data_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as exc:
            print(f"[{self.name}] 保存账目数据失败：{exc}")

    def _get_data_path(self) -> str:
        """获取数据文件的绝对路径。

        数据文件位于插件主模块所在目录下。

        返回：
            数据文件的绝对路径
        """
        # 当前模块所在目录
        module_dir = os.path.dirname(os.path.abspath(__file__))
        # 若 data_file 为绝对路径则直接使用，否则拼接模块目录
        if os.path.isabs(self._data_file):
            return self._data_file
        return os.path.join(module_dir, self._data_file)

    def _handle_summary_request(self) -> Dict[str, Any]:
        """事件处理器：响应 account.summary 事件。

        供其他插件通过事件总线获取账目统计。

        返回：
            包含统计信息的字典
        """
        if not self._records:
            return {"count": 0, "total": 0.0}

        return {
            "count": len(self._records),
            "total": sum(r["amount"] for r in self._records),
            "currency": self._currency,
        }
