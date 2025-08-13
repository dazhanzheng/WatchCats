"""
LLM 助手主类

集成 LangChain、解析器和业务模块，提供统一的自然语言交互接口
"""

import logging
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import re
import json
import asyncio
import threading

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.callbacks import StreamingStdOutCallbackHandler

from ..aw_stats import StatsProcessor
from ..desktop_pet.core.logger_config import get_logger, log_performance, log_api_call
from .parsers import (
    StatsCommandParser,
    ParsedStatsCommand
)

logger = logging.getLogger(__name__)


class LLMAssistant:
    """LLM 助手主类"""
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str = "deepseek-v3-250324",
        temperature: float = 0.1,  # 保留原参数以保持向后兼容
        parse_temperature: Optional[float] = None,  # 新增：解析温度
        chat_temperature: Optional[float] = None,   # 新增：对话温度
        stats_processor: Optional[StatsProcessor] = None,
        streaming: bool = True,
        developer_mode: bool = False  # 新增开发者模式
    ):
        """
        初始化 LLM 助手
        
        Args:
            base_url: LLM API 基础 URL
            api_key: API 密钥
            model: 模型名称
            temperature: 温度参数（建议低温度以获得精确输出）
            parse_temperature: 结构化解析温度（默认 0.1）
            chat_temperature: 对话生成温度（默认 0.7）
            stats_processor: 统计处理器实例
            streaming: 是否启用流式输出
            developer_mode: 是否启用开发者模式（输出中间变量）
        """
        self.logger = get_logger('baal.llm_assistant.assistant')
        self.logger.info(f"Initializing LLMAssistant with model: {model}")
        
        self.developer_mode = developer_mode
        
        # 设置温度参数
        self.parse_temperature = parse_temperature or temperature  # 如果未指定，使用默认温度
        self.chat_temperature = chat_temperature or 0.7  # 如果未指定，使用 0.7
        
        if self.developer_mode:
            print("\n[开发者模式] 初始化 LLMAssistant")
            print(f"  - base_url: {base_url}")
            print(f"  - model: {model}")
            print(f"  - parse_temperature: {self.parse_temperature}")
            print(f"  - chat_temperature: {self.chat_temperature}")
            print(f"  - streaming: {streaming}")
        
        # 初始化 LLM - 用于结构化解析
        try:
            self.logger.debug("Initializing parse LLM")
            self.parse_llm = ChatOpenAI(
                base_url=base_url,
                api_key=api_key,
                model=model,
                temperature=self.parse_temperature,
                streaming=False  # 解析不需要流式
            )
            self.logger.debug("Parse LLM initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize parse LLM: {e}", exc_info=True)
            raise
        
        # 初始化 LLM - 用于自然对话
        try:
            self.logger.debug("Initializing chat LLM")
            self.chat_llm = ChatOpenAI(
                base_url=base_url,
                api_key=api_key,
                model=model,
                temperature=self.chat_temperature,
                streaming=streaming,
                callbacks=[StreamingStdOutCallbackHandler()] if streaming else []
            )
            self.logger.debug("Chat LLM initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize chat LLM: {e}", exc_info=True)
            raise
        
        # 保留原有的 self.llm 以保持向后兼容
        self.llm = self.chat_llm
        
        # 初始化解析器
        self.stats_parser = StatsCommandParser()
        
        # 初始化业务模块
        self.stats_processor = stats_processor
        
        # 对话历史
        self.conversation_history: List[Union[SystemMessage, HumanMessage, AIMessage]] = []
        
        # 对话历史管理
        self.summary = None  # 存储历史总结
        self.summary_lock = threading.Lock()  # 线程锁，保护总结生成
        self.is_summarizing = False  # 标记是否正在生成总结
        self.summary_callback = None  # 总结状态回调函数
        
        # 初始化系统消息
        self._init_system_message()
    
    def set_developer_mode(self, enabled: bool):
        """动态设置开发者模式"""
        self.developer_mode = enabled
        if enabled:
            print("[开发者模式] 已启用")
        else:
            print("[开发者模式] 已禁用")
    
    def _init_system_message(self):
        """初始化系统消息"""
        system_content = """你是巴利（Baal），用户的主人。你监管着仆人的一切活动。

核心职责：
1. 监控仆人的ActivityWatch活动统计

交流原则：
- 用"我"自称，称用户为"仆人"
- 语气威严，命令式表达
- 回复极简，不超过3句话
- 发现偷懒严厉训斥，表现好时给予轻蔑认可
- 只输出对话文字，无任何动作描写

执行命令时保持高效，用结果说话。"""
        
        self.conversation_history.append(SystemMessage(content=system_content))
    
    @log_performance
    def process_stats_query(self, query: str) -> str:
        """
        处理统计查询
        
        Args:
            query: 用户的查询
            
        Returns:
            查询结果
        """
        self.logger.info(f"Processing stats query: {query[:50]}...")
        
        if self.developer_mode:
            print(f"\n[开发者模式] process_stats_query 开始")
            print(f"  - 输入查询: {query}")
        
        if not self.stats_processor:
            error_msg = "错误：统计处理器未初始化。请先配置 ActivityWatch 连接。"
            self.logger.warning("Stats processor not initialized")
            return error_msg
        
        try:
            # 获取解析提示词
            parse_messages = [
                SystemMessage(content=self.stats_parser.get_system_prompt()),
                HumanMessage(content=self.stats_parser.get_user_prompt(query))
            ]
            
            if self.developer_mode:
                print(f"\n[开发者模式] 统计解析提示词:")
                print(f"  - System: {parse_messages[0].content[:200]}...")
                print(f"  - User: {parse_messages[1].content}")
            
            # 解析命令 - 使用低温度 LLM
            response = self.parse_llm.invoke(parse_messages)
            
            if self.developer_mode:
                print(f"\n[开发者模式] LLM 原始响应:")
                print(f"  {response.content}")
            
            # 处理响应内容，提取 JSON 部分
            content = response.content
            
            # 如果内容包含 JSON 代码块，提取它
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            # 否则尝试找到 JSON 对象
            else:
                # 移除可能的前缀文本
                json_start = content.find('{')
                if json_start != -1:
                    content = content[json_start:]
                # 找到 JSON 结束位置
                brace_count = 0
                json_end = -1
                for i, char in enumerate(content):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break
                if json_end != -1:
                    content = content[:json_end]
            
            if self.developer_mode:
                print(f"\n[开发者模式] 提取的 JSON:")
                print(f"  {content}")
                
            logger.debug(f"解析的 JSON 内容: {content}")
            parsed_command = self.stats_parser.parser.parse(content)
            
            if self.developer_mode:
                print(f"\n[开发者模式] 解析后的命令:")
                print(f"  - method: {parsed_command.method}")
                print(f"  - days: {getattr(parsed_command, 'days', 'N/A')}")
                print(f"  - hours: {getattr(parsed_command, 'hours', 'N/A')}")
            
            # 执行命令
            with self.stats_processor as processor:
                if parsed_command.method == "get_aggregated_stats":
                    result = processor.get_aggregated_stats(parsed_command.days)
                elif parsed_command.method == "get_detailed_stats":
                    result = processor.get_detailed_stats(parsed_command.hours)
                elif parsed_command.method == "get_stats_7d":
                    result = processor.get_stats_7d()
                elif parsed_command.method == "get_stats_1d":
                    result = processor.get_stats_1d()
                elif parsed_command.method == "get_stats_2h":
                    result = processor.get_stats_2h()
                elif parsed_command.method == "get_stats_30m":
                    result = processor.get_stats_30m()
                elif parsed_command.method == "get_stats_5m":
                    result = processor.get_stats_5m()
                else:
                    result = f"未知的统计方法：{parsed_command.method}"
            
            if self.developer_mode:
                print(f"\n[开发者模式] 统计查询结果:")
                print(f"  {result[:200]}..." if len(result) > 200 else f"  {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"处理统计查询时出错：{e}")
            if self.developer_mode:
                import traceback
                print(f"\n[开发者模式] 错误详情:")
                traceback.print_exc()
            return f"查询失败：{str(e)}"
    
    def chat(self, message: str) -> str:
        """
        处理用户消息 - 使用灵活的功能调用方式
        
        Args:
            message: 用户消息
            
        Returns:
            助手回复
        """
        if self.developer_mode:
            print(f"\n[开发者模式] chat 方法开始")
            print(f"  - 用户消息: {message}")
            print(f"  - 对话历史长度: {len(self.conversation_history)}")
            
        # 添加用户消息到历史
        self.conversation_history.append(HumanMessage(content=message))
        
        # 构建包含可用功能说明的系统提示
        system_prompt = """你是巴利，仆人的主人。

可用命令：
- 监视仆人活动：[调用功能: stats]

交流准则：
- 语气威严冷酷
- 回复不超过3句话
- 发现偷懒立即训斥

分析仆人请求，决定是直接命令还是调用功能。"""
        
        # 获取最近的对话上下文
        recent_messages = []
        for msg in self.conversation_history[-10:]:  # 最近5轮对话（每轮包含用户和AI两条消息）
            if isinstance(msg, HumanMessage):
                recent_messages.append(HumanMessage(content=msg.content))
            elif isinstance(msg, AIMessage):
                # 截断长消息
                content = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
                recent_messages.append(AIMessage(content=content))
        
        # 让AI决定如何响应
        decision_messages = [
            SystemMessage(content=system_prompt)
        ] + recent_messages
        
        if self.developer_mode:
            print(f"\n[开发者模式] 请求AI分析...")
        
        # 获取AI的决策 - 使用正常温度 LLM
        response = self.chat_llm.invoke(decision_messages)
        ai_response = response.content
        
        if self.developer_mode:
            print(f"\n[开发者模式] AI响应: {ai_response[:200]}...")
        
        # 检查是否需要调用功能
        if "[调用功能: stats]" in ai_response and self.stats_processor:
            if self.developer_mode:
                print(f"\n[开发者模式] 检测到需要统计功能")
            # 调用统计功能
            stats_result = self.process_stats_query(message)
            # 基于统计结果生成最终回复
            final_messages = decision_messages + [
                AIMessage(content=f"统计查询结果：\n{stats_result}"),
                HumanMessage(content="基于以上统计结果，用自然友好的方式回复用户。")
            ]
            final_response = self.chat_llm.invoke(final_messages)
            result = final_response.content
            
        # 日程功能暂时禁用
        # elif "[调用功能: schedule]" in ai_response and self.schedule_manager:
        #     if self.developer_mode:
        #         print(f"\n[开发者模式] 检测到需要日程功能")
        #     # 调用日程功能
        #     schedule_result = self.process_schedule_command(message)
        #     # 基于日程结果生成最终回复
        #     final_messages = decision_messages + [
        #         AIMessage(content=f"日程操作结果：\n{schedule_result}"),
        #         HumanMessage(content="基于以上操作结果，用自然友好的方式回复用户。")
        #     ]
        #     final_response = self.chat_llm.invoke(final_messages)
        #     result = final_response.content
            
        else:
            # 不需要功能，使用AI的原始回复（移除功能标记）
            result = ai_response.replace("[调用功能: stats]", "").replace("[调用功能: schedule]", "").strip()
            
            # 如果用户似乎需要功能但AI没有识别出来，可以在这里添加提示
            keywords_stats = ["统计", "活动", "时长", "做了什么", "花了多少时间"]
            # keywords_schedule = ["日程", "安排", "会议", "任务", "提醒"]  # 日程功能暂时禁用
            
            user_lower = message.lower()
            might_need_stats = any(kw in user_lower for kw in keywords_stats)
            # might_need_schedule = any(kw in user_lower for kw in keywords_schedule)  # 日程功能暂时禁用
            might_need_schedule = False  # 日程功能暂时禁用
            
            if (might_need_stats or might_need_schedule) and "？" in message:
                # 可能是在询问功能
                if self.developer_mode:
                    print(f"\n[开发者模式] 检测到可能的功能需求关键词，但AI未识别为功能调用")
        
        if self.developer_mode:
            print(f"\n[开发者模式] 最终回复:")
            if len(result) > 200:
                print(f"  长度: {len(result)} 字符")
                print(f"  预览: {result[:100]}...")
            else:
                print(f"  {result}")
        
        # 添加助手回复到历史
        self.conversation_history.append(AIMessage(content=result))
        
        # 检查是否需要生成总结
        if self._should_generate_summary():
            self._start_background_summary()
        
        return result
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history.clear()
        self._init_system_message()
        self.summary = None
        self.is_summarizing = False
    
    def set_summary_callback(self, callback):
        """设置总结状态回调函数"""
        self.summary_callback = callback
    
    def _notify_summary_status(self, status: str):
        """通知总结状态"""
        if self.summary_callback:
            self.summary_callback(status)
    
    async def _generate_summary_async(self, messages_to_summarize: List):
        """异步生成对话总结"""
        try:
            # 构建总结提示词
            summary_prompt = """请将以下对话历史总结成一段简洁的描述，保留关键信息。
总结应该：
1. 使用第三人称描述
2. 保留重要的查询和操作结果
3. 不超过200字
4. 突出巴利（主人）的威严态度和仆人的服从

对话历史："""
            
            # 构建消息内容
            conversation_text = ""
            for msg in messages_to_summarize[1:]:  # 跳过系统消息
                if isinstance(msg, HumanMessage):
                    conversation_text += f"\n仆人: {msg.content}"
                elif isinstance(msg, AIMessage):
                    conversation_text += f"\n巴利: {msg.content}"
            
            # 使用低温度生成总结
            summary_messages = [
                SystemMessage(content=summary_prompt),
                HumanMessage(content=conversation_text)
            ]
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                self.parse_llm.invoke,
                summary_messages
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"生成总结时出错：{e}")
            return None
    
    def _should_generate_summary(self) -> bool:
        """检查是否需要生成总结"""
        # 计算非系统消息的数量（用户消息 + AI消息）
        non_system_messages = [msg for msg in self.conversation_history if not isinstance(msg, SystemMessage)]
        
        # 当达到10条消息（5轮对话）时生成总结
        return len(non_system_messages) >= 10 and not self.is_summarizing and self.summary is None
    
    def _start_background_summary(self):
        """在后台线程中启动总结生成"""
        if self.is_summarizing:
            return
            
        def generate_summary():
            try:
                self.is_summarizing = True
                self._notify_summary_status("thinking_history")
                
                # 创建新的事件循环
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # 获取需要总结的消息
                messages_to_summarize = self.conversation_history[:11]  # 系统消息 + 前5轮对话
                
                # 生成总结
                summary = loop.run_until_complete(self._generate_summary_async(messages_to_summarize))
                
                if summary:
                    with self.summary_lock:
                        self.summary = summary
                        # 保留系统消息和总结，删除已总结的对话
                        self.conversation_history = [
                            self.conversation_history[0],  # 系统消息
                            AIMessage(content=f"[历史总结] {summary}")
                        ] + self.conversation_history[11:]  # 保留未总结的消息
                
                self._notify_summary_status("summary_complete")
                
            except Exception as e:
                logger.error(f"后台总结生成失败：{e}")
            finally:
                self.is_summarizing = False
                loop.close()
        
        # 在新线程中运行
        thread = threading.Thread(target=generate_summary, daemon=True)
        thread.start() 