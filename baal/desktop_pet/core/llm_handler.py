"""
LLM 处理器

负责与LLM的交互，支持流式输出
集成 ActivityWatch 数据访问功能
"""

import asyncio
import time
from typing import Optional, AsyncGenerator, List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from ...llm_assistant import LLMAssistant
from ...llm_assistant.binary_intent_classifier import BinaryIntentClassifier
from ...aw_stats import StatsProcessor
from .logger_config import get_logger, log_performance, log_api_call
from .persona_manager import PersonaManager, PersonaLevel
from .preset_dialogues import PresetDialogues
from .config_manager import ConfigManager


class LLMHandler:
    """LLM处理器类"""
    
    def __init__(self, base_url: str, api_key: str, model: str = "doubao-seed-1-6-flash-250715", persona_level: PersonaLevel = PersonaLevel.STRICT_MASTER):
        """
        初始化LLM处理器
        
        Args:
            base_url: API基础URL
            api_key: API密钥
            model: 模型名称
            persona_level: 人设档位
        """
        self.logger = get_logger('baal.desktop_pet.core.llm_handler')
        self.logger.info(f"Initializing LLMHandler with model: {model}")
        
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        
        # 初始化人设管理器
        self.persona_manager = PersonaManager(persona_level)
        self.logger.info(f"Persona manager initialized with level: {persona_level.name}")
        
        # 不记录敏感信息的DEBUG日志
        
        # 字符显示间隔配置（单位：秒）
        self.char_delays = {
            'normal': 0.02,      # 普通字符：20ms
            'punctuation': 0.08,  # 标点符号：80ms
            'newline': 0.05      # 换行符：50ms
        }
        
        # 初始化 LLMAssistant（具有完整功能）
        try:
            self.logger.info("Initializing LLMAssistant with complete functionality")
            self.assistant = LLMAssistant(
                base_url=base_url,
                api_key=api_key,
                model=model,
                parse_temperature=0.1,
                chat_temperature=0.7,
                stats_processor=StatsProcessor(),
                streaming=False  # LLMAssistant 内部流式输出不兼容我们的实现
            )
            self.logger.info("LLMAssistant initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize LLMAssistant: {e}", exc_info=True)
            raise
        
        # 确保 assistant 的对话历史与 llm_handler 同步初始化
        if len(self.assistant.conversation_history) == 0:
            self.assistant._init_system_message()
        
        # 初始化二进制意图分类器
        try:
            self.logger.info("Initializing binary intent classifier")
            self.intent_classifier = BinaryIntentClassifier(
                llm=self._create_llm(streaming=False, temperature=0.1)
            )
            self.logger.info("Binary intent classifier initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize intent classifier: {e}", exc_info=True)
            raise
        
        # 对话历史
        self.messages: List[Any] = []
        
        # 状态回调函数
        self.status_callback = None
        
        # 总结状态回调函数
        self.summary_status_callback = None
        
        # 设置助手的总结回调
        self.assistant.set_summary_callback(self._on_summary_status)
        
        # 使用人设管理器获取系统提示词
        self.system_prompt = self.persona_manager.get_system_prompt()
        
        # 添加系统消息
        self.messages.append(SystemMessage(content=self.system_prompt))
        
        # 初始化配置管理器用于历史记录存储
        self.config_manager = ConfigManager()
        
        # 尝试加载历史对话记录
        self._load_conversation_history()
        
        self.logger.debug(f"System message added, total messages: {len(self.messages)}")
        self.logger.info("LLMHandler initialization completed successfully")
    
    def set_status_callback(self, callback):
        """设置状态回调函数"""
        self.logger.debug("Setting status callback function")
        self.status_callback = callback
    
    def _notify_status(self, status: str):
        """通知状态变化"""
        self.logger.debug(f"Status notification: {status}")
        if self.status_callback:
            try:
                self.status_callback(status)
                self.logger.debug(f"Status callback executed successfully: {status}")
            except Exception as e:
                self.logger.error(f"Status callback failed: {e}", exc_info=True)
    
    def set_summary_status_callback(self, callback):
        """设置总结状态回调函数"""
        self.logger.debug("Setting summary status callback function")
        self.summary_status_callback = callback
    
    def _on_summary_status(self, status: str):
        """处理来自助手的总结状态"""
        self.logger.debug(f"Summary status notification: {status}")
        if self.summary_status_callback:
            try:
                self.summary_status_callback(status)
                self.logger.debug(f"Summary status callback executed: {status}")
            except Exception as e:
                self.logger.error(f"Summary status callback failed: {e}", exc_info=True)
    
    def _create_llm(self, streaming: bool = True, temperature: float = 0.7) -> ChatOpenAI:
        """创建LLM实例"""
        # 创建LLM实例
        try:
            llm = ChatOpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                model=self.model,
                temperature=temperature,
                streaming=streaming
            )
            # LLM实例创建成功
            return llm
        except Exception as e:
            self.logger.error(f"Failed to create LLM instance: {e}", exc_info=True)
            raise
    
    @log_api_call('openai', '/v1/chat/completions', 'POST')
    def _generate_baal_response(self, prompt: str) -> str:
        """生成巴利风格的回复（低温度，准确性优先）"""
        self.logger.debug(f"Generating Baal response for prompt length: {len(prompt)}")
        
        llm = self._create_llm(streaming=False, temperature=0.4)  # 略高温度允许更多个性表达
        
        messages = [
            SystemMessage(content=self.persona_manager.get_brief_response_prompt()),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = llm.invoke(messages)
            self.logger.info(f"Baal response generated successfully, length: {len(response.content)}")
            self.logger.debug(f"Response content preview: {response.content[:100]}...")
            return response.content
        except Exception as e:
            self.logger.error(f"Failed to generate Baal response: {e}", exc_info=True)
            return PresetDialogues.get_error_message(self.persona_manager.current_level, "system_error")
    
    def set_char_delays(self, normal: float = None, punctuation: float = None, newline: float = None):
        """
        设置字符显示延迟
        
        Args:
            normal: 普通字符延迟（秒）
            punctuation: 标点符号延迟（秒）
            newline: 换行符延迟（秒）
        """
        old_delays = self.char_delays.copy()
        
        if normal is not None:
            self.char_delays['normal'] = normal
        if punctuation is not None:
            self.char_delays['punctuation'] = punctuation
        if newline is not None:
            self.char_delays['newline'] = newline
            
        self.logger.info(f"Character delays updated: {old_delays} -> {self.char_delays}")
    
    @log_performance
    @log_api_call('openai', '/v1/chat/completions', 'POST')
    async def _generate_chat_response(self, user_input: str) -> str:
        """生成普通聊天回复"""
        self.logger.debug(f"Generating chat response for input: {user_input[:100]}...")
        
        # 构建带有强化提示的消息列表
        enhanced_messages = []
        for msg in self.messages:
            if isinstance(msg, SystemMessage):
                # 强化系统提示，确保包含表情标记
                enhanced_content = msg.content + "\n\n【重要提醒】不要包含任何动作描写、场景描述。只输出巴利会说的话。必须在每句话开头添加一个表情标记，格式：<#n>你要说的话。绝不使用<符号，除非是表情标记。"
                enhanced_messages.append(SystemMessage(content=enhanced_content))
            else:
                enhanced_messages.append(msg)
        
        # 添加用户消息
        enhanced_messages.append(HumanMessage(content=user_input))
        self.logger.debug(f"Built enhanced message list with {len(enhanced_messages)} messages")
        
        # 生成回复
        try:
            llm = self._create_llm(streaming=False, temperature=0.7)
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                llm.invoke,
                enhanced_messages
            )
            
            self.logger.info(f"Chat response generated successfully, length: {len(response.content)}")
            self.logger.debug(f"Response preview: {response.content[:100]}...")
            return response.content
        except Exception as e:
            self.logger.error(f"Failed to generate chat response: {e}", exc_info=True)
            return PresetDialogues.get_error_message(self.persona_manager.current_level, "chat_error")
    
    async def _parallel_all_operations(self, user_input: str) -> Dict[str, Any]:
        """
        并行执行所有操作：意图分类、普通聊天、工具调用
        
        Args:
            user_input: 用户输入
            
        Returns:
            包含所有结果的字典
        """
        # 记录每个任务的开始和结束时间
        timings = {}
        
        async def get_chat_safe():
            start = time.time()
            try:
                result = await self._generate_chat_response(user_input)
                end = time.time()
                timings['chat'] = {'start': start, 'end': end, 'duration': end - start}
                return result
            except Exception as e:
                end = time.time()
                timings['chat'] = {'start': start, 'end': end, 'duration': end - start, 'error': str(e)}
                return f"对话生成失败: {str(e)}"
        
        async def get_stats_safe():
            start = time.time()
            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    self.assistant.process_stats_query, 
                    user_input
                )
                end = time.time()
                timings['stats'] = {'start': start, 'end': end, 'duration': end - start}
                return result
            except Exception as e:
                end = time.time()
                timings['stats'] = {'start': start, 'end': end, 'duration': end - start, 'error': str(e)}
                return f"统计查询失败: {str(e)}"
        
        async def get_schedule_safe():
            start = time.time()
            result = ""
            end = time.time()
            timings['schedule'] = {'start': start, 'end': end, 'duration': end - start}
            return result
        
        async def get_intent_safe():
            start = time.time()
            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.intent_classifier.classify,
                    user_input
                )
                end = time.time()
                timings['intent'] = {'start': start, 'end': end, 'duration': end - start}
                return result
            except Exception as e:
                end = time.time()
                timings['intent'] = {'start': start, 'end': end, 'duration': end - start, 'error': str(e)}
                # 默认返回普通聊天的二进制码
                return "100"
        
        # 记录并行执行开始时间
        parallel_start = time.time()
        
        # 并行执行所有操作
        results = await asyncio.gather(
            get_intent_safe(),
            get_chat_safe(),
            get_stats_safe(),
            get_schedule_safe()
        )
        
        # 记录并行执行结束时间
        parallel_end = time.time()
        
        return {
            "intent": results[0],
            "chat": results[1],
            "stats": results[2],
            "schedule": results[3],
            "timings": timings,
            "parallel_duration": parallel_end - parallel_start
        }
    
    @log_performance
    async def chat_stream(self, user_input: str) -> AsyncGenerator[str, None]:
        """
        流式对话 - 使用真正的流式并行策略
        
        Args:
            user_input: 用户输入
            
        Yields:
            str: 流式输出的token
        """
        # 记录整体开始时间
        overall_start = time.time()
        self.logger.info(f"Starting streaming chat for input: {user_input[:50]}...")
        
        # 通知开始思考
        self._notify_status("thinking")
        
        
        # 创建并行任务
        # 意图分类任务
        async def get_intent():
            try:
                binary_str = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.intent_classifier.classify,
                    user_input,
                    self.messages  # 传递对话历史
                )
                
                # 解析二进制结果
                is_chat, needs_stats, needs_schedule = BinaryIntentClassifier.parse_binary(binary_str)
                
                self.logger.info(f"Intent classification: {binary_str} -> chat={is_chat}, stats={needs_stats}")
                
                return {
                    'binary': binary_str,
                    'is_chat': is_chat,
                    'needs_stats': needs_stats,
                    'needs_schedule': needs_schedule
                }
            except Exception as e:
                self.logger.warning(f"Intent classification failed, defaulting to chat: {e}")
                # 默认为普通聊天
                return {
                    'binary': '100',
                    'is_chat': True,
                    'needs_stats': False,
                    'needs_schedule': False
                }
        
        # 聊天生成任务
        async def get_chat():
            try:
                result = await self._generate_chat_response(user_input)
                return result
            except Exception as e:
                return f"对话生成失败: {str(e)}"
        
        # 统计查询任务
        async def get_stats():
            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    self.assistant.process_stats_query, 
                    user_input
                )
                return result
            except Exception as e:
                return f"统计查询失败: {str(e)}"
        
        
        # 首先启动意图分类和聊天任务（这两个总是需要的）
        intent_task = asyncio.create_task(get_intent())
        chat_task = asyncio.create_task(get_chat())
        
        # 首先等待意图分类完成
        intent_decision = await intent_task
        
        # 根据意图决定是否启动工具任务
        stats_task = None
        stats_data = None  # 初始化 stats_data 变量
        
        if intent_decision['needs_stats']:
            stats_task = asyncio.create_task(get_stats())
        
        # 根据意图决定策略
        final_response = ""
        
        if intent_decision['is_chat']:
            # 普通聊天：等待chat任务完成并立即输出
            chat_response = await chat_task
            final_response = chat_response
            
            self.logger.debug("Intent classification completed, using pre-generated chat response")
            
        else:
            # 需要工具：通知正在使用工具
            self.logger.debug("Tools required, switching to tool mode")
            self._notify_status("tools")
            
            # 只等待需要的工具
            tasks_to_wait = []
            tool_context = ""
            
            if intent_decision['needs_stats'] and stats_task:
                tasks_to_wait.append(('stats', stats_task))
            
            # 等待需要的工具完成
            for task_name, task in tasks_to_wait:
                result = await task
                if task_name == 'stats':
                    stats_data = result  # 保存统计数据结果
                    tool_context += f"\n\n【活动监控数据】\n{result}"
                elif task_name == 'schedule':
                    tool_context += f"\n\n【日程数据】\n{result}"
            
            # 生成工具回复
            prompt = self.persona_manager.get_tool_response_prompt(user_input, tool_context)
            
            final_response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._generate_baal_response(prompt)
            )
            
            self.logger.debug("Tool data prepared, generating response")
        
        # 通知开始输出
        self._notify_status("streaming")
        
        # 开始流式输出
        char_count = 0
        for i, char in enumerate(final_response):
            yield char
            char_count += 1
            
            # 根据字符类型调整延迟
            if char in '，。！？；：':
                await asyncio.sleep(self.char_delays['punctuation'])
            elif char == '\n':
                await asyncio.sleep(self.char_delays['newline'])
            else:
                await asyncio.sleep(self.char_delays['normal'])
                
        self.logger.debug(f"Streamed {char_count} characters")
        
        # 等待所有启动的任务完成（不影响输出）
        tasks_to_wait_final = [chat_task]
        if stats_task:
            tasks_to_wait_final.append(stats_task)
        
        await asyncio.gather(*tasks_to_wait_final, return_exceptions=True)
        
        # 构建包含工具调用信息的完整响应
        full_response = final_response
        if stats_data and stats_data not in ['统计查询失败', '工具错误', '未匹配']:
            # 将工具调用的结果作为系统信息添加到响应中
            full_response = f"{final_response}\n[数据查询结果：{stats_data}]"
        
        # 添加到对话历史
        self.messages.append(HumanMessage(content=user_input))
        self.messages.append(AIMessage(content=full_response))
        
        # 同步更新 assistant 的对话历史以触发总结功能
        self.assistant.conversation_history.append(HumanMessage(content=user_input))
        self.assistant.conversation_history.append(AIMessage(content=full_response))
        
        # 检查是否需要生成总结
        if self.assistant._should_generate_summary():
            self.assistant._start_background_summary()
        
        # 通知完成
        self._notify_status("done")
        
        total_time = time.time() - overall_start
        self.logger.info(f"Streaming chat completed in {total_time:.3f}s")
    
    @log_performance
    @log_api_call('openai', '/v1/chat/completions', 'POST')
    def chat_sync(self, user_input: str) -> str:
        """
        同步对话（非流式）
        
        Args:
            user_input: 用户输入
            
        Returns:
            str: AI回复
        """
        self.logger.info(f"Starting synchronous chat for input: {user_input[:50]}...")
        
        # 添加用户消息
        self.messages.append(HumanMessage(content=user_input))
        self.logger.debug(f"Added user message, total messages: {len(self.messages)}")
        
        # 创建LLM并获取回复
        llm = self._create_llm(streaming=False)
        try:
            response = llm.invoke(self.messages)
            self.messages.append(response)
            
            self.logger.info(f"Sync chat completed, response length: {len(response.content)}")
            self.logger.debug(f"Response preview: {response.content[:100]}...")
            return response.content
        except Exception as e:
            error_msg = PresetDialogues.get_error_message(self.persona_manager.current_level, "general_error")
            self.logger.error(f"Synchronous chat failed: {e}", exc_info=True)
            return error_msg
    
    def clear_history(self):
        """清除对话历史"""
        old_count = len(self.messages)
        self.messages = [SystemMessage(content=self.system_prompt)]
        self.logger.info(f"Chat history cleared: {old_count} -> {len(self.messages)} messages")
    
    def set_persona_level(self, level: PersonaLevel):
        """
        设置人设档位
        
        Args:
            level: 人设档位
        """
        self.logger.info(f"Changing persona level from {self.persona_manager.current_level.name} to {level.name}")
        self.persona_manager.set_persona_level(level)
        
        # 更新系统提示词
        self.system_prompt = self.persona_manager.get_system_prompt()
        
        # 更新对话历史中的系统消息
        if self.messages and isinstance(self.messages[0], SystemMessage):
            self.messages[0] = SystemMessage(content=self.system_prompt)
        
        self.logger.info(f"Persona level changed successfully to {level.name}")
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        获取对话历史
        
        Returns:
            List[Dict[str, str]]: 对话历史列表
        """
        self.logger.debug(f"Retrieving chat history, total messages: {len(self.messages)}")
        
        history = []
        for msg in self.messages[1:]:  # 跳过系统消息
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                history.append({"role": "assistant", "content": msg.content})
                
        self.logger.debug(f"Retrieved {len(history)} history entries")
        return history
    
    def _load_conversation_history(self):
        """加载对话历史"""
        try:
            history_data = self.config_manager.load_conversation_history()
            
            if history_data:
                self.logger.info(f"Found conversation history with {len(history_data)} messages")
                
                # 恢复消息对象
                for msg_dict in history_data:
                    msg_type = msg_dict.get('type', '')
                    content = msg_dict.get('content', '')
                    
                    if msg_type == 'HumanMessage':
                        self.messages.append(HumanMessage(content=content))
                        # 同步到assistant的历史
                        if hasattr(self, 'assistant'):
                            self.assistant.conversation_history.append(HumanMessage(content=content))
                    elif msg_type == 'AIMessage':
                        self.messages.append(AIMessage(content=content))
                        # 同步到assistant的历史
                        if hasattr(self, 'assistant'):
                            self.assistant.conversation_history.append(AIMessage(content=content))
                
                self.logger.info(f"Loaded {len(history_data)} messages from history")
                # 标记为已有历史记录
                self.has_history = True
            else:
                self.logger.info("No conversation history found, starting fresh")
                self.has_history = False
                
        except Exception as e:
            self.logger.error(f"Failed to load conversation history: {e}", exc_info=True)
            self.has_history = False
    
    def save_conversation_history(self):
        """保存对话历史"""
        try:
            # 只保存用户和AI的消息，不保存系统消息
            messages_to_save = [msg for msg in self.messages if not isinstance(msg, SystemMessage)]
            
            if messages_to_save:
                success = self.config_manager.save_conversation_history(messages_to_save)
                if success:
                    self.logger.info(f"Saved {len(messages_to_save)} messages to history")
                else:
                    self.logger.warning("Failed to save conversation history")
                return success
            else:
                self.logger.debug("No messages to save")
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving conversation history: {e}", exc_info=True)
            return False
    
    def clear_conversation_history(self):
        """清除对话历史"""
        try:
            # 清除内存中的历史
            self.messages = [self.messages[0]]  # 只保留系统消息
            
            # 清除assistant的历史
            if hasattr(self, 'assistant'):
                self.assistant.clear_history()
            
            # 清除持久化的历史
            success = self.config_manager.clear_conversation_history()
            
            if success:
                self.logger.info("Conversation history cleared successfully")
                self.has_history = False
            else:
                self.logger.warning("Failed to clear persistent conversation history")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Error clearing conversation history: {e}", exc_info=True)
            return False
    
    def has_conversation_history(self) -> bool:
        """检查是否有对话历史"""
        return hasattr(self, 'has_history') and self.has_history 