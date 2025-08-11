"""
LLM 助手模块

提供基于 LangChain 的智能助手功能，包括：
- 自然语言解析
- ActivityWatch 统计查询
- 日程管理
- 灵活的对话交互
"""

from .assistant import LLMAssistant
from .parsers import (
    StatsCommandParser,
    ScheduleCommandParser,
    ParsedStatsCommand,
    ParsedScheduleCommand
)
from .binary_intent_classifier import BinaryIntentClassifier

__version__ = "0.1.0"
__all__ = [
    'LLMAssistant',
    'StatsCommandParser',
    'ScheduleCommandParser',
    'ParsedStatsCommand',
    'ParsedScheduleCommand',
    'BinaryIntentClassifier'
] 