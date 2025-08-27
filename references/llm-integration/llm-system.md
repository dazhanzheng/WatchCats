# LLM Integration System Documentation

## Overview

The Baal Desktop Pet Assistant integrates Large Language Models (LLMs) through LangChain, supporting OpenAI-compatible APIs including Volcano Engine's Doubao model. The system features streaming responses, intent classification, tool orchestration, and conversation memory management.

## Architecture

```
┌──────────────────────────────────────────┐
│            LLM Integration Layer          │
├──────────────────────────────────────────┤
│   LLMHandler (Main Interface)            │
│      ├── Chat Streaming                  │
│      ├── Intent Classification           │
│      └── Memory Management               │
├──────────────────────────────────────────┤
│   LLMAssistant (Tool Orchestration)      │
│      ├── ActivityWatch Integration       │
│      ├── Command Parsing                 │
│      └── Structured Output               │
├──────────────────────────────────────────┤
│   LangChain Components                   │
│      ├── ChatOpenAI Client              │
│      ├── Message History                │
│      └── Streaming Callbacks            │
└──────────────────────────────────────────┘
```

## Core Components

### LLMHandler

**File:** `baal/desktop_pet/core/llm_handler.py`

**Purpose:** Primary interface for LLM interactions with streaming support and persona management.

```python
class LLMHandler:
    """
    Central LLM management class.
    
    Responsibilities:
        - API client initialization
        - Streaming response generation
        - Conversation history management
        - Persona and emotion integration
        - Intent-based routing
    """
    
    def __init__(self, 
                 base_url: str,
                 api_key: str,
                 model: str = "doubao-seed-1-6-flash-250715",
                 persona_level: PersonaLevel = PersonaLevel.STRICT_MASTER):
        # Initialize components
        self.persona_manager = PersonaManager(persona_level)
        self.assistant = LLMAssistant(...)  # Full functionality
        self.intent_classifier = BinaryIntentClassifier(...)
        self.messages = []  # Conversation history
```

**Key Methods:**

```python
async def chat_stream(self, user_input: str) -> AsyncGenerator[str, None]:
    """
    Stream chat response with intent routing.
    
    Flow:
        1. Classify intent (needs data vs pure chat)
        2. Route to appropriate handler
        3. Stream response tokens
        4. Detect and emit emotions
    """
    
    # Intent classification
    needs_data = await self.intent_classifier.requires_data(user_input)
    
    if needs_data:
        # Use LLMAssistant with tools
        response = await self.assistant.process_with_tools(user_input)
    else:
        # Direct LLM streaming
        response = await self._stream_direct_chat(user_input)
    
    # Stream tokens with emotion detection
    async for token in response:
        emotion = self.detect_emotion(token)
        if emotion:
            self.emit_emotion(emotion)
        yield token
```

### LLMAssistant

**File:** `baal/llm_assistant/assistant.py`

**Purpose:** Advanced LLM orchestration with tool integration and structured outputs.

```python
class LLMAssistant:
    """
    LangChain-based assistant with tool capabilities.
    
    Features:
        - ActivityWatch data access
        - Structured command parsing
        - Parallel tool execution
        - Response formatting
    """
    
    def __init__(self,
                 base_url: str,
                 api_key: str,
                 model: str,
                 parse_temperature: float = 0.1,  # For parsing
                 chat_temperature: float = 0.7,   # For chat
                 stats_processor: Optional[StatsProcessor] = None):
        
        # Dual LLM setup for different tasks
        self.parse_llm = ChatOpenAI(
            temperature=parse_temperature,  # Low for consistency
            streaming=False
        )
        
        self.chat_llm = ChatOpenAI(
            temperature=chat_temperature,  # Higher for variety
            streaming=True
        )
```

**Tool Integration:**

```python
def process_with_tools(self, query: str) -> str:
    """
    Process query with tool access.
    
    Available Tools:
        - get_app_usage: Application usage statistics
        - get_category_time: Time by category
        - get_productivity_score: Productivity metrics
        - get_timeline: Activity timeline
    """
    
    # Parse command
    parsed = self.stats_parser.parse(query)
    
    # Execute tools in parallel
    results = await asyncio.gather(
        self.get_app_usage(parsed.time_range),
        self.get_category_time(parsed.time_range),
        self.get_productivity_score()
    )
    
    # Format response
    return self.format_response(results, parsed.format)
```

### Intent Classification

**File:** `baal/llm_assistant/binary_intent_classifier.py`

**Purpose:** Determine whether queries require data access or can be answered directly.

```python
class BinaryIntentClassifier:
    """
    Binary classification for query routing.
    
    Categories:
        - Needs Data: Queries about activity, statistics, productivity
        - Direct Chat: General conversation, opinions, jokes
    """
    
    def requires_data(self, query: str) -> bool:
        """
        Classify if query needs ActivityWatch data.
        
        Keywords that trigger data access:
            - 时间 (time)
            - 统计 (statistics)
            - 应用/软件 (apps/software)
            - 效率/生产力 (efficiency/productivity)
            - 今天/本周/本月 (today/this week/this month)
        """
        
        prompt = f"""
        判断以下查询是否需要访问用户活动数据：
        
        查询: {query}
        
        需要数据的情况:
        - 询问使用时间或统计
        - 查看应用使用情况
        - 分析生产力或效率
        - 获取具体的活动记录
        
        不需要数据的情况:
        - 一般对话或闲聊
        - 询问建议或意见
        - 情感交流
        - 与活动无关的问题
        
        回答: true 或 false
        """
        
        response = self.llm.invoke(prompt)
        return response.content.strip().lower() == "true"
```

### Command Parsing

**File:** `baal/llm_assistant/parsers.py`

**Purpose:** Convert natural language to structured commands.

```python
class StatsCommandParser:
    """
    Parse natural language to structured stats commands.
    
    Uses LangChain's output parsers for structured extraction.
    """
    
    def __init__(self):
        self.parser = PydanticOutputParser(
            pydantic_object=ParsedStatsCommand
        )
    
    def parse(self, query: str) -> ParsedStatsCommand:
        """
        Parse query to structured command.
        
        Example:
            Input: "今天我用了哪些软件？"
            Output: ParsedStatsCommand(
                query_type="apps",
                time_range="today",
                filters=None,
                format="table"
            )
        """
        
        # Dynamic prompt with current date
        prompt = self.get_system_prompt().format(
            query=query,
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            format_instructions=self.parser.get_format_instructions()
        )
        
        response = self.llm.invoke(prompt)
        return self.parser.parse(response.content)
```

**Structured Output Models:**

```python
class ParsedStatsCommand(BaseModel):
    """Structured command for statistics queries"""
    query_type: Literal["apps", "categories", "timeline", "productivity"]
    time_range: str  # "today", "week", "month", or custom
    filters: Optional[Dict[str, Any]] = None
    format: Literal["table", "chart", "summary"] = "table"
    
class TimeRange(BaseModel):
    """Time range specification"""
    start: datetime
    end: datetime
    description: str  # Human-readable description
```

## Streaming System

### Token Streaming Implementation

```python
class StreamingHandler:
    """
    Manages streaming responses with character delays.
    
    Features:
        - Character-by-character display
        - Punctuation delays for natural reading
        - Emotion tag detection during streaming
        - Buffer management for smooth display
    """
    
    async def stream_response(self, text: str) -> AsyncGenerator[str, None]:
        """
        Stream text with natural delays.
        
        Delays:
            - Normal character: 50ms
            - Punctuation (，。！？): 300ms
            - Newline: 200ms
        """
        
        emotion_buffer = ""
        
        for char in text:
            # Check for emotion tags
            if char == '<' or emotion_buffer:
                emotion_buffer += char
                if '>' in emotion_buffer and emotion_buffer.startswith('<#'):
                    # Complete emotion tag found
                    emotion = self.extract_emotion(emotion_buffer)
                    if emotion:
                        yield f"[EMOTION:{emotion}]"
                    emotion_buffer = ""
                continue
            
            # Yield character
            yield char
            
            # Apply delay
            if char in '，。！？':
                await asyncio.sleep(0.3)
            elif char == '\n':
                await asyncio.sleep(0.2)
            else:
                await asyncio.sleep(0.05)
```

### Async Worker Thread

```python
class AsyncWorker(QThread):
    """
    Background thread for LLM streaming.
    
    Signals:
        - token_received: Single token ready
        - stream_finished: Response complete
        - emotion_detected: Emotion tag found
        - error_occurred: Error during streaming
    """
    
    def run(self):
        """
        Thread execution with event loop management.
        """
        # Create new event loop for thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._process_stream())
        finally:
            loop.close()
            asyncio.set_event_loop(None)
    
    async def _process_stream(self):
        """Process streaming response"""
        async for token in self.llm_handler.chat_stream(self.user_input):
            if not self.is_running:
                break
            
            # Emit token to UI thread
            self.token_received.emit(token)
```

## Memory Management

### Conversation History

```python
class ConversationMemory:
    """
    Manages conversation history with summarization.
    
    Features:
        - Maximum message limit (50)
        - Automatic summarization at threshold (30)
        - Persistent storage
        - Context window management
    """
    
    def __init__(self, max_messages: int = 50):
        self.messages = []
        self.summary = None
        self.max_messages = max_messages
    
    def add_message(self, role: str, content: str):
        """Add message to history"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Check if summarization needed
        if len(self.messages) > 30:
            asyncio.create_task(self.summarize())
    
    async def summarize(self):
        """
        Summarize old messages to reduce token usage.
        """
        # Extract messages to summarize
        to_summarize = self.messages[:20]
        
        # Generate summary
        summary_prompt = """
        总结以下对话的要点，保留重要信息：
        {messages}
        """
        
        summary = await self.llm.agenerate(
            summary_prompt.format(messages=to_summarize)
        )
        
        # Replace with summary
        self.messages = [
            {"role": "system", "content": f"[历史总结: {summary}]"},
            *self.messages[20:]
        ]
```

### Context Window Optimization

```python
def optimize_context(messages: List[Dict], max_tokens: int = 4000) -> List[Dict]:
    """
    Optimize message history for context window.
    
    Strategy:
        1. Keep system message
        2. Keep last N messages
        3. Summarize middle messages if needed
        4. Ensure under token limit
    """
    
    # Always keep system message
    system_msg = messages[0]
    
    # Estimate tokens (rough: 1 Chinese char ≈ 2 tokens)
    def estimate_tokens(msg):
        return len(msg['content']) * 2
    
    # Keep recent messages
    recent_messages = []
    total_tokens = estimate_tokens(system_msg)
    
    for msg in reversed(messages[1:]):
        msg_tokens = estimate_tokens(msg)
        if total_tokens + msg_tokens < max_tokens:
            recent_messages.insert(0, msg)
            total_tokens += msg_tokens
        else:
            break
    
    return [system_msg] + recent_messages
```

## Persona Integration

### System Prompt Management

```python
class PersonaPromptBuilder:
    """
    Builds system prompts based on persona.
    
    Components:
        1. Base functional instructions
        2. Persona-specific behavior
        3. Emotion expression rules
        4. Response constraints
    """
    
    def build_prompt(self, persona: PersonaLevel) -> str:
        """
        Generate complete system prompt.
        
        Structure:
            - Identity and role
            - Behavioral guidelines
            - Expression format (emotions)
            - Response constraints
            - Tool usage instructions
        """
        
        base_prompt = """
        【基础设定】
        你是Watch Cats桌面宠物应用的AI角色巴利。
        
        【表情系统】
        在每句话开头使用表情标记：
        <#1> - 开心
        <#2> - 得意  
        <#3> - 无语
        <#4> - 鄙视
        <#5> - 平静
        <#6> - 生气
        <#7> - 暴怒
        
        【回复规则】
        - 简洁有力，不超过3句话
        - 只输出对话文字和表情标记
        - 不使用括号描述动作
        """
        
        persona_prompt = self.PERSONA_PROMPTS[persona]
        
        return base_prompt + "\n\n" + persona_prompt
```

## API Configuration

### Supported Providers

```python
API_PROVIDERS = {
    "volcano": {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "models": [
            "doubao-seed-1-6-flash-250715",
            "doubao-pro-128k"
        ],
        "headers": {
            "Authorization": "Bearer {api_key}"
        }
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "models": [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo"
        ],
        "headers": {
            "Authorization": "Bearer {api_key}"
        }
    },
    "custom": {
        "base_url": "{user_provided}",
        "models": [],
        "headers": {
            "Authorization": "Bearer {api_key}"
        }
    }
}
```

### API Client Configuration

```python
def create_llm_client(provider: str, api_key: str, model: str) -> ChatOpenAI:
    """
    Create configured LLM client.
    
    Parameters tuned for different use cases:
        - Parsing: temperature=0.1, max_tokens=500
        - Chat: temperature=0.7, max_tokens=2000
        - Summary: temperature=0.3, max_tokens=1000
    """
    
    config = API_PROVIDERS[provider]
    
    return ChatOpenAI(
        base_url=config["base_url"],
        api_key=api_key,
        model=model,
        temperature=0.7,
        max_tokens=2000,
        streaming=True,
        timeout=30,
        max_retries=3,
        request_timeout=30
    )
```

## Error Handling

### LLM Error Recovery

```python
class LLMErrorHandler:
    """
    Handles LLM-related errors gracefully.
    
    Error Types:
        - Network errors → Retry with backoff
        - API errors → Check credentials
        - Rate limits → Queue and delay
        - Timeout → Increase timeout or fallback
    """
    
    async def handle_llm_error(self, error: Exception, context: Dict) -> str:
        """
        Handle LLM errors with appropriate recovery.
        """
        
        if isinstance(error, RateLimitError):
            # Rate limit - wait and retry
            await asyncio.sleep(60)
            return await self.retry_operation(context)
        
        elif isinstance(error, AuthenticationError):
            # Invalid API key
            return "API密钥无效，请检查设置。"
        
        elif isinstance(error, TimeoutError):
            # Timeout - try simpler query
            simplified = self.simplify_query(context['query'])
            return await self.retry_with_simplified(simplified)
        
        elif isinstance(error, NetworkError):
            # Network issue - exponential backoff
            for attempt in range(3):
                await asyncio.sleep(2 ** attempt)
                try:
                    return await self.retry_operation(context)
                except:
                    continue
            
            return "网络连接失败，请检查网络设置。"
        
        else:
            # Unknown error - log and fallback
            logger.error(f"Unexpected LLM error: {error}")
            return "抱歉，遇到了未知错误。"
```

## Performance Optimization

### Token Usage Optimization

```python
class TokenOptimizer:
    """
    Optimizes token usage for cost and performance.
    
    Strategies:
        - Message compression
        - Selective history inclusion
        - Response caching
        - Batch processing
    """
    
    def compress_messages(self, messages: List[Dict]) -> List[Dict]:
        """
        Compress messages to reduce tokens.
        
        Techniques:
            - Remove redundant whitespace
            - Abbreviate common phrases
            - Remove filler words
            - Combine similar messages
        """
        
        compressed = []
        for msg in messages:
            content = msg['content']
            
            # Remove extra whitespace
            content = ' '.join(content.split())
            
            # Abbreviate common phrases
            replacements = {
                "应用程序": "应用",
                "生产力": "效率",
                "统计数据": "统计"
            }
            
            for old, new in replacements.items():
                content = content.replace(old, new)
            
            compressed.append({
                "role": msg['role'],
                "content": content
            })
        
        return compressed
```

### Response Caching

```python
class ResponseCache:
    """
    Caches common responses for instant delivery.
    
    Cache Strategy:
        - Hash query for cache key
        - TTL: 5 minutes for dynamic data
        - TTL: 1 hour for static responses
        - LRU eviction when full
    """
    
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
    
    def get(self, query: str) -> Optional[str]:
        """Get cached response if available"""
        key = self.hash_query(query)
        
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < entry['ttl']:
                self.access_times[key] = time.time()
                return entry['response']
        
        return None
    
    def set(self, query: str, response: str, ttl: int = 300):
        """Cache response with TTL"""
        if len(self.cache) >= self.max_size:
            self.evict_lru()
        
        key = self.hash_query(query)
        self.cache[key] = {
            'response': response,
            'timestamp': time.time(),
            'ttl': ttl
        }
```

## Testing and Debugging

### LLM Testing Utilities

```python
class LLMMockClient:
    """
    Mock LLM client for testing.
    
    Features:
        - Predictable responses
        - Simulated delays
        - Error injection
        - Token counting
    """
    
    async def chat_stream(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """Mock streaming response"""
        response = "这是一个测试响应。"
        
        for char in response:
            await asyncio.sleep(0.01)  # Simulate delay
            yield char
    
    def inject_error(self, error_type: str):
        """Inject specific error for testing"""
        if error_type == "rate_limit":
            raise RateLimitError("Rate limit exceeded")
        elif error_type == "timeout":
            raise TimeoutError("Request timeout")
```

### Debug Logging

```python
def log_llm_interaction(messages: List[Dict], response: str, metadata: Dict):
    """
    Log LLM interactions for debugging.
    
    Logs:
        - Request messages
        - Response content
        - Token usage
        - Latency
        - Errors
    """
    
    logger.debug("=" * 50)
    logger.debug("LLM Interaction")
    logger.debug(f"Model: {metadata.get('model')}")
    logger.debug(f"Messages: {len(messages)}")
    logger.debug(f"Response length: {len(response)}")
    logger.debug(f"Latency: {metadata.get('latency_ms')}ms")
    logger.debug(f"Tokens: {metadata.get('total_tokens')}")
    logger.debug("=" * 50)
```