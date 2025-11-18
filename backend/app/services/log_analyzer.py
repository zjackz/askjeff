from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from app.models.system_log import SystemLog


@dataclass
class LogAnalysisResult:
    summary: str
    probable_causes: list[str]
    suggestions: list[str]
    used_ai: bool = False


class LogAnalyzer:
    """日志分析器，若无外部 AI 配置则返回启发式结果。"""

    @staticmethod
    def analyze(logs: Iterable[SystemLog]) -> LogAnalysisResult:
        logs_list = list(logs)
        if not logs_list:
            return LogAnalysisResult(summary="未找到可分析的日志", probable_causes=[], suggestions=[], used_ai=False)

        levels = Counter(log.level for log in logs_list)
        categories = Counter(log.category for log in logs_list)
        errors = [log for log in logs_list if log.level == "error"]

        summary_parts = [
            f"共 {len(logs_list)} 条日志，错误 {levels.get('error', 0)} 条，警告 {levels.get('warning', 0)} 条。",
            "高频分类：" + ", ".join(f"{k}({v})" for k, v in categories.most_common(3)),
        ]
        probable = []
        suggestions: list[str] = []

        if errors:
            top_error_msgs = Counter(err.message for err in errors).most_common(3)
            probable.append("错误集中在：" + "；".join(f"{msg}({cnt})" for msg, cnt in top_error_msgs))
            suggestions.append("优先排查最近错误堆栈，复现并对照失败上下文。")

        if levels.get("warning", 0) > 0:
            suggestions.append("存在告警，请确认是否影响主流程，必要时提升为 error 以便监控。")

        suggestions.append("如需深入分析，可配置 CODEx API 后再调用 /logs/analyze 获取 AI 诊断。")

        return LogAnalysisResult(
            summary=" ".join(summary_parts),
            probable_causes=probable,
            suggestions=suggestions,
            used_ai=False,
        )
