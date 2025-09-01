"""
LLM 处理器

负责与LLM的交互，支持流式输出
集成 ActivityWatch 数据访问功能
"""

import asyncio
import time
import threading
from typing import Optional, AsyncGenerator, List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from ...llm_assistant import LLMAssistant
from ...llm_assistant.binary_intent_classifier import BinaryIntentClassifier
from ...aw_stats import StatsProcessor
from .logger_config import get_logger, log_performance
from .constants import CHAR_DELAYS, get_char_delay
from .persona_manager import PersonaManager, PersonaLevel
from .preset_dialogues import PresetDialogues
from .config_manager import ConfigManager
from .state_update_manager import get_update_manager, StateComponent


class LLMHandler:
    """LLM处理器类"""
    
    def __init__(self, base_url: str, api_key: str, model: str = "doubao-seed-1-6-flash-250715", persona_level: PersonaLevel = PersonaLevel.STRICT_MASTER, supervision_mode=None):
        """
        初始化LLM处理器
        
        Args:
            base_url: API基础URL
            api_key: API密钥
            model: 模型名称
            persona_level: 人设档位
            supervision_mode: 监督模式管理器实例（可选）
        """
        self.logger = get_logger('baal.desktop_pet.core.llm_handler')
        self.logger.info(f"Initializing LLMHandler with model: {model}")
        
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.supervision_mode = supervision_mode  # 保存监督模式管理器引用
        
        # 双模型配置：对话使用seed模型，工具调用使用flash模型
        # 从配置中读取模型设置，如果没有则使用默认值
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        self.chat_model = config.get('chat_model', "doubao-seed-1-6-250615")  # 对话模型（角色扮演优化）
        self.tool_model = config.get('tool_model', "doubao-seed-1-6-flash-250715")  # 工具模型（保持原有）
        
        self.logger.info(f"Dual model configuration: chat={self.chat_model}, tool={self.tool_model}")
        
        # 初始化人设管理器
        self.persona_manager = PersonaManager(persona_level)
        self.logger.info(f"Persona manager initialized with level: {persona_level.name}")
        
        # 不记录敏感信息的DEBUG日志
        
        # 字符显示间隔配置（从常量模块加载）
        self.char_delays = {
            'normal': CHAR_DELAYS['normal'],
            'punctuation': CHAR_DELAYS['punctuation'],
            'newline': CHAR_DELAYS['newline']
        }
        
        # 初始化 LLMAssistant（具有完整功能，使用工具模型）
        try:
            self.logger.info("Initializing LLMAssistant with complete functionality")
            self.assistant = LLMAssistant(
                base_url=base_url,
                api_key=api_key,
                model=self.tool_model,  # 工具调用使用flash模型
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
        
        # 初始化二进制意图分类器（使用工具模型进行意图分类）
        try:
            self.logger.info("Initializing binary intent classifier")
            self.intent_classifier = BinaryIntentClassifier(
                llm=self._create_llm(streaming=False, temperature=0.1, use_chat_model=False)  # 意图分类使用工具模型
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
        
        # 初始化状态更新管理器
        self.update_manager = get_update_manager()
        
        # 使用人设管理器获取系统提示词（添加动态状态）
        self.system_prompt = self._get_dynamic_system_prompt()
        
        # 添加系统消息
        self.messages.append(SystemMessage(content=self.system_prompt))
        
        # 记录初始状态哈希
        self.current_state_hash = None
        
        # 初始化配置管理器用于历史记录存储
        self.config_manager = ConfigManager()
        
        # 自动保存相关
        self.auto_save_enabled = True
        self.auto_save_interval = 60  # 60秒后自动保存
        self.auto_save_timer = None
        self.auto_save_lock = threading.Lock()
        self.last_save_time = time.time()
        self.min_save_interval = 10  # 最小保存间隔10秒，防止频繁保存
        
        # 尝试加载历史对话记录
        self._load_conversation_history()
        
        self.logger.debug(f"System message added, total messages: {len(self.messages)}")
        self.logger.info("LLMHandler initialization completed successfully")
    
    def _get_dynamic_system_prompt(self, use_cache: bool = True) -> str:
        """生成包含动态状态的系统提示词
        
        Args:
            use_cache: 是否使用缓存的状态
        """
        from .state_awareness import get_state_awareness
        
        # 获取基础人设提示词
        base_prompt = self.persona_manager.get_system_prompt()
        
        # 如果使用缓存且缓存有效，直接返回
        if use_cache and hasattr(self, '_cached_prompt'):
            cache_time = getattr(self, '_cached_prompt_time', 0)
            if time.time() - cache_time < 60:  # 缓存1分钟
                return self._cached_prompt
        
        # 获取状态感知系统
        state_system = get_state_awareness()
        
        # 智能获取状态：只更新需要的组件
        if hasattr(self, 'update_manager'):
            needs_update, components = self.update_manager.should_update()
            if needs_update:
                current_state = self.update_manager.get_updated_state(components)
            else:
                # 使用缓存的状态
                current_state = getattr(self, '_last_state', state_system.get_current_state(include_weather=False))
        else:
            current_state = state_system.get_current_state(include_weather=False)
        
        # 保存状态
        self._last_state = current_state
        
        # 监督模式状态
        if self.supervision_mode and self.supervision_mode.is_active:
            work_state = "你正在监督模式中，需要关注用户的工作效率，但也要注意劳逸结合"
        else:
            work_state = "你处于休闲模式，可以轻松闲聊，分享有趣的事情"
        
        # 格式化状态提示词
        state_prompt = state_system.format_state_prompt(current_state)
        
        # 添加工作模式
        state_prompt = state_prompt.replace(
            "记住这些状态会影响你的反应和语气。",
            f"- 模式：{work_state}\n\n记住这些状态会影响你的反应和语气。"
        )
        
        # 添加一些动态的个性化元素
        personality_hints = [
            "你今天话比较多。",
            "你今天比较安静。",
            "你最近在学习新东西。",
            "你刚刚做了个有趣的梦。",
            "你发现了一个有趣的秘密。",
            "你今天特别想聊天。",
            "你正在观察一只虫子。",
            "你刚刚打了个盹。",
            "你在回味刚才的美食。",
            "你感觉今天会有好事发生。",
        ]
        
        # 基于互动计数选择个性化提示
        stats = state_system.get_statistics()
        interaction_count = stats.get("total_interactions", 0)
        
        # 使用互动次数作为随机种子，确保短时间内保持一致
        import hashlib
        from datetime import datetime
        
        # 每小时更换一次个性提示
        seed = f"{interaction_count}_{datetime.now().strftime('%Y%m%d%H')}"
        hash_value = int(hashlib.md5(seed.encode()).hexdigest(), 16)
        personality = personality_hints[hash_value % len(personality_hints)]
        
        state_prompt += f"\n- {personality}"
        
        # 如果认识很久了，添加关系深度
        days_known = stats.get("days_known", 0)
        if days_known > 30:
            state_prompt += f"\n- 你们已经认识{days_known}天了，关系很亲密。"
        elif days_known > 7:
            state_prompt += f"\n- 你们认识有一段时间了，正在建立信任。"
        elif days_known > 0:
            state_prompt += f"\n- 你们刚认识不久，还在互相了解。"
        
        # 缓存生成的提示词
        full_prompt = base_prompt + "\n\n" + state_prompt
        self._cached_prompt = full_prompt
        self._cached_prompt_time = time.time()
        
        return full_prompt
    
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
    
    def _create_llm(self, streaming: bool = True, temperature: float = 0.7, use_chat_model: bool = True) -> ChatOpenAI:
        """创建LLM实例
        
        Args:
            streaming: 是否流式输出
            temperature: 温度参数
            use_chat_model: 是否使用对话模型（True=seed模型，False=flash模型）
        """
        # 选择模型
        model = self.chat_model if use_chat_model else self.tool_model
        
        # 创建LLM实例
        try:
            # 为seed模型添加深度思考控制
            if model == "doubao-seed-1-6-250615":
                # seed模型需要显式禁用深度思考
                llm = ChatOpenAI(
                    base_url=self.base_url,
                    api_key=self.api_key,
                    model=model,
                    temperature=temperature,
                    streaming=streaming,
                    extra_body={
                        "thinking": {
                            "type": "disabled"  # 不使用深度思考功能
                        }
                    }
                )
            else:
                # flash模型不需要额外参数
                llm = ChatOpenAI(
                    base_url=self.base_url,
                    api_key=self.api_key,
                    model=model,
                    temperature=temperature,
                    streaming=streaming
                )
            # LLM实例创建成功
            return llm
        except Exception as e:
            self.logger.error(f"Failed to create LLM instance: {e}", exc_info=True)
            raise
    
    def _generate_baal_response(self, prompt: str) -> str:
        """生成巴利风格的回复（低温度，准确性优先）"""
        self.logger.debug(f"Generating Baal response for prompt length: {len(prompt)}")
        
        # 使用对话模型生成回复
        llm = self._create_llm(streaming=False, temperature=0.4, use_chat_model=True)  # 使用seed模型
        
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
            # 使用对话模型生成聊天回复
            llm = self._create_llm(streaming=False, temperature=0.7, use_chat_model=True)
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
    
    def _update_system_state_if_needed(self) -> bool:
        """
        根据需要更新系统状态
        
        Returns:
            是否进行了更新
        """
        # 检查是否需要更新
        needs_update, components = self.update_manager.should_update()
        
        if not needs_update:
            return False
        
        # 获取更新的状态
        updated_state = self.update_manager.get_updated_state(components)
        
        # 如果有显著变化，重新生成系统提示词
        if self.update_manager.has_significant_change(updated_state):
            self.logger.debug(f"Significant state change detected, updating system prompt")
            
            # 重新生成系统提示词
            new_prompt = self._get_dynamic_system_prompt()
            
            # 更新系统消息
            if self.messages and isinstance(self.messages[0], SystemMessage):
                self.messages[0] = SystemMessage(content=new_prompt)
                self.system_prompt = new_prompt
            
            self.logger.info(f"System state updated with components: {[c.value for c in components]}")
            return True
        
        return False
    
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
        
        # 智能更新状态
        self._update_system_state_if_needed()
        
        # 触发互动事件
        self.update_manager.trigger_event("intense_interaction")
        
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
        
        # 安排自动保存
        self._schedule_auto_save()
        
        total_time = time.time() - overall_start
        self.logger.info(f"Streaming chat completed in {total_time:.3f}s")
    
    @log_performance
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
        
        # 创建LLM并获取回复（同步对话使用对话模型）
        llm = self._create_llm(streaming=False, use_chat_model=True)
        try:
            response = llm.invoke(self.messages)
            self.messages.append(response)
            
            # 安排自动保存
            self._schedule_auto_save()
            
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
        
        # 触发人设变化事件
        self.update_manager.trigger_event("mood_shift")
        
        # 更新系统提示词
        self.system_prompt = self._get_dynamic_system_prompt()
        
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
                    self.last_save_time = time.time()  # 更新最后保存时间
                else:
                    self.logger.warning("Failed to save conversation history")
                return success
            else:
                self.logger.debug("No messages to save")
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving conversation history: {e}", exc_info=True)
            return False
    
    def _schedule_auto_save(self):
        """安排自动保存"""
        if not self.auto_save_enabled:
            return
        
        with self.auto_save_lock:
            # 如果已有定时器，先取消
            if self.auto_save_timer:
                self.auto_save_timer.cancel()
            
            # 创建新的定时器
            self.auto_save_timer = threading.Timer(self.auto_save_interval, self._auto_save)
            self.auto_save_timer.daemon = True  # 设置为守护线程
            self.auto_save_timer.start()
            self.logger.debug(f"Auto-save scheduled in {self.auto_save_interval} seconds")
    
    def _auto_save(self):
        """执行自动保存"""
        try:
            current_time = time.time()
            # 检查最小保存间隔，防止频繁保存
            if current_time - self.last_save_time >= self.min_save_interval:
                self.logger.debug("Performing auto-save...")
                success = self.save_conversation_history()
                if success:
                    self.logger.debug("Auto-save completed successfully")
                else:
                    self.logger.warning("Auto-save failed")
            else:
                self.logger.debug(f"Skipping auto-save, last save was {current_time - self.last_save_time:.1f}s ago")
        except Exception as e:
            self.logger.error(f"Auto-save error: {e}", exc_info=True)
        finally:
            # 清理定时器引用
            with self.auto_save_lock:
                self.auto_save_timer = None
    
    def trigger_immediate_save(self):
        """立即触发保存（用于重要时刻）"""
        try:
            current_time = time.time()
            # 检查最小保存间隔
            if current_time - self.last_save_time >= self.min_save_interval:
                self.logger.debug("Triggering immediate save...")
                return self.save_conversation_history()
            else:
                self.logger.debug(f"Immediate save skipped, last save was {current_time - self.last_save_time:.1f}s ago")
                return True
        except Exception as e:
            self.logger.error(f"Immediate save error: {e}", exc_info=True)
            return False
    
    def clear_conversation_history(self):
        """清除对话历史"""
        try:
            # 取消自动保存定时器
            with self.auto_save_lock:
                if self.auto_save_timer:
                    self.auto_save_timer.cancel()
                    self.auto_save_timer = None
            
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
    
    def cleanup(self):
        """清理资源（在程序退出时调用）"""
        try:
            # 取消自动保存定时器
            with self.auto_save_lock:
                if self.auto_save_timer:
                    self.auto_save_timer.cancel()
                    self.auto_save_timer = None
            
            # 执行最后一次保存
            self.save_conversation_history()
            self.logger.info("LLMHandler cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}", exc_info=True)
    
    def add_supervision_reminder(self, message: str):
        """添加监督提醒到对话历史并触发保存
        
        Args:
            message: 监督提醒消息
        """
        try:
            # 添加到对话历史
            ai_msg = AIMessage(content=message)
            self.messages.append(ai_msg)
            
            # 同步到assistant的历史
            if hasattr(self, 'assistant'):
                self.assistant.conversation_history.append(ai_msg)
            
            self.logger.info(f"Supervision reminder added to history: {message[:50]}...")
            
            # 立即触发保存（监督提醒属于重要消息）
            self.trigger_immediate_save()
            
        except Exception as e:
            self.logger.error(f"Failed to add supervision reminder: {e}", exc_info=True)
    
    def has_conversation_history(self) -> bool:
        """检查是否有对话历史"""
        return hasattr(self, 'has_history') and self.has_history
    
    def generate_dynamic_response(self, context: str, mood: int = 5, parameters: Dict[str, Any] = None) -> str:
        """动态生成响应消息
        
        Args:
            context: 上下文场景（如 "memory_cleared", "supervision_stopped" 等）
            mood: 心情表情 (1-7)
            parameters: 额外参数字典
            
        Returns:
            str: 生成的响应消息，带表情标记
        """
        try:
            # 根据人设和上下文生成提示词
            persona_level = self.persona_manager.current_level
            persona_traits = self.persona_manager.get_traits()
            
            # 构建场景描述
            context_descriptions = {
                "memory_cleared": "用户刚刚清除了对话记忆，需要给出确认反馈",
                "memory_clear_failed": "清除对话记忆失败了，需要给出错误提示",
                "no_memory_to_clear": "用户想清除记忆但没有历史记录需要清除",
                "supervision_stopped": "监督模式已关闭，需要给出确认",
                "supervision_started": "监督模式已启动，需要给出确认",
                "goals_updated": "监督目标已更新，需要给出确认",
                "api_required_for_supervision": "监督模式需要API密钥才能工作",
                "api_config_error": "API配置有误，无法正常工作",
                "supervision_cancelled": "用户取消了监督模式设置"
            }
            
            scenario = context_descriptions.get(context, f"场景：{context}")
            
            # 构建动态生成的系统提示词
            dynamic_prompt = f"""你是{persona_traits['name']}，一个{persona_traits['description']}。
你的性格特点：{', '.join(persona_traits['characteristics'])}
你的语言风格：{persona_traits['language_style']}

当前场景：{scenario}
当前心情值：{mood}（1=开心，2=微笑，3=正常，4=困惑，5=平静，6=生气，7=愤怒）

请根据你的人设和当前心情，生成一个简短的反应。
要求：
1. 必须符合你的人设特点和语言风格
2. 长度控制在20字以内
3. 必须在开头加上表情标记 <#{mood}>
4. 不要重复场景描述，直接给出反应

生成的格式：<#{mood}>你的反应文本"""

            # 如果有额外参数，添加到提示词中
            if parameters:
                param_str = '\n'.join([f"{k}: {v}" for k, v in parameters.items()])
                dynamic_prompt += f"\n\n额外信息：\n{param_str}"
            
            # 使用对话模型生成响应
            llm = self._create_llm(streaming=False, temperature=0.8, use_chat_model=True)
            response = llm.invoke([SystemMessage(content=dynamic_prompt)])
            
            # 确保响应包含表情标记
            result = response.content.strip()
            if not result.startswith(f"<#{mood}>"):
                result = f"<#{mood}>{result}"
            
            self.logger.debug(f"Generated dynamic response for {context}: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate dynamic response: {e}", exc_info=True)
            # 返回预设的后备响应
            return PresetDialogues.get_dialogue(persona_level, "default", "default") 