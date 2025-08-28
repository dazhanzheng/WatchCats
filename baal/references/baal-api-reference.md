# Baal Desktop Pet API Reference

## 概述

本文档为 Baal 桌面宠物助手的 API 和架构参考指南，详细说明了系统的核心接口和使用方法。

## 核心模块

### 1. LLM 处理器 (llm_handler.py)

负责与大语言模型的交互，支持流式响应和多种 API 提供商。

```python
class LLMHandler:
    def __init__(self, config_manager: ConfigManager)
    async def get_streaming_response(self, message: str, history: List[Dict]) -> AsyncGenerator
    def get_system_prompt(self, persona_type: str = "strict_master") -> str
```

**支持的 API 提供商:**
- OpenAI 及兼容 API
- 火山引擎（Volcengine）
- 本地部署模型

### 2. 配置管理器 (config_manager.py)

跨平台的配置文件管理，处理 API 密钥和用户偏好。

```python
class ConfigManager:
    def __init__(self)
    def get_api_key(self) -> str
    def set_api_key(self, key: str)
    def get_config_value(self, key: str, default=None)
    def save_config()
```

**配置文件位置:**
- macOS/Linux: `~/.baal_pet/config.json`
- Windows: `%APPDATA%/BaalPet/config.json`

### 3. 表情管理器 (emotion_manager.py)

管理宠物的表情状态，支持 7 种不同表情。

```python
class EmotionManager:
    EMOTIONS = ['normal', 'happy', 'angry', 'confused', 'sad', 'excited', 'tired']
    
    def set_emotion(self, emotion: str)
    def get_emotion() -> str
    def analyze_text_emotion(self, text: str) -> str
```

### 4. 人格管理器 (persona_manager.py)

处理不同的 AI 人格模式。

```python
class PersonaManager:
    PERSONAS = {
        'strict_master': '严格主人',
        'sarcastic_butler': '嘲讽管家', 
        'gentle_companion': '温柔伴侣'
    }
    
    def set_persona(self, persona_type: str)
    def get_current_persona() -> str
    def get_system_prompt(self, persona_type: str) -> str
```

### 5. 监督模式 (supervision_mode.py)

生产力监控和评估系统。

```python
class SupervisionMode:
    def __init__(self, pet_window, config_manager)
    def start_supervision()
    def stop_supervision()
    def evaluate_productivity() -> Dict
    def generate_report() -> str
```

## UI 组件

### PetWindow (pet_window.py)

主窗口组件，显示宠物形象。

**主要方法:**
- `show_bubble(text: str)` - 显示对话气泡
- `set_emotion(emotion: str)` - 改变表情
- `toggle_chat()` - 切换聊天界面

### ChatBubble (chat_bubble.py)

对话气泡组件，支持流式文本显示。

**特性:**
- 自动调整大小
- 滚动支持
- 30秒自动消失（预设消息）
- 流式文本动画

### CalendarDialogModern (calendar_dialog_modern.py)

现代化的日历界面，支持多种视图。

**视图模式:**
- 月视图 - 概览整月日程
- 周视图 - 详细周计划
- 日视图 - 单日时间轴

## LangChain 工具

### 1. ActivityWatch 数据工具

```python
class ActivityStatsTools:
    @tool
    def get_app_usage(start_time: str, end_time: str) -> Dict
    
    @tool  
    def get_activity_summary(date: str) -> Dict
    
    @tool
    def get_productivity_score() -> float
```

### 2. 日程管理工具

```python
class ScheduleTools:
    @tool
    def add_schedule(title: str, start: datetime, end: datetime)
    
    @tool
    def list_schedules(date: str) -> List[Dict]
    
    @tool
    def delete_schedule(schedule_id: str)
```

### 3. 系统控制工具

```python
class SystemTools:
    @tool
    def set_reminder(message: str, time: datetime)
    
    @tool
    def change_persona(persona_type: str)
    
    @tool
    def toggle_supervision_mode(enabled: bool)
```

## 数据格式

### 配置文件格式

```json
{
    "api_key": "sk-xxx",
    "api_base": "https://api.openai.com/v1",
    "model": "gpt-4",
    "persona": "strict_master",
    "window_position": [100, 100],
    "supervision_targets": {
        "productive_hours": 6,
        "break_interval": 60
    },
    "memories": []
}
```

### 日程数据格式

```json
{
    "id": "uuid",
    "title": "任务标题",
    "start": "2025-08-28T10:00:00",
    "end": "2025-08-28T11:00:00",
    "description": "任务描述",
    "reminder": true,
    "category": "work"
}
```

### ActivityWatch 数据格式

```json
{
    "timestamp": "2025-08-28T10:00:00Z",
    "duration": 3600,
    "data": {
        "app": "VSCode",
        "title": "project.py",
        "category": "productive"
    }
}
```

## 事件系统

### 信号和槽

```python
# 表情变化信号
emotion_changed = pyqtSignal(str)

# 消息接收信号  
message_received = pyqtSignal(str)

# 监督模式状态变化
supervision_state_changed = pyqtSignal(bool)

# 日程提醒信号
schedule_reminder = pyqtSignal(dict)
```

### 事件处理流程

1. **用户输入** → ChatBubble
2. **消息处理** → LLMHandler
3. **工具调用** → LangChain Tools
4. **响应生成** → Streaming Response
5. **UI 更新** → PetWindow/ChatBubble

## 性能优化

### 并行处理

- 多个 ActivityWatch 查询并发执行
- 工具调用的异步处理
- 流式响应的非阻塞渲染

### 内存管理

- Qt 对象的正确清理
- 异步任务的生命周期管理
- 配置文件的懒加载

### 缓存策略

- LLM 响应的短期缓存
- 表情图片的预加载
- ActivityWatch 数据的本地缓存

## 错误处理

### 常见错误码

- `ERR_API_KEY`: API 密钥无效
- `ERR_NETWORK`: 网络连接失败
- `ERR_AW_CONNECTION`: ActivityWatch 连接失败
- `ERR_CONFIG`: 配置文件损坏

### 错误恢复策略

1. **API 失败**: 自动重试 3 次，指数退避
2. **配置损坏**: 使用默认配置，提示用户重新配置
3. **AW 断开**: 降级模式，禁用相关功能

## 扩展开发

### 添加新工具

```python
from langchain.tools import tool

@tool
def my_custom_tool(param: str) -> str:
    """工具描述"""
    # 实现逻辑
    return result

# 注册到助手
assistant.add_tool(my_custom_tool)
```

### 添加新表情

1. 添加图片到 `动作表情拆分/` 目录
2. 更新 `EmotionManager.EMOTIONS` 列表
3. 在 `analyze_text_emotion` 中添加触发逻辑

### 添加新人格

```python
# persona_manager.py
PERSONAS['new_persona'] = {
    'name': '新人格',
    'prompt': '系统提示词...'
}
```

## 测试指南

### 单元测试

```bash
# 测试 LLM 处理
./venv/bin/python -m pytest tests/test_llm_handler.py

# 测试配置管理
./venv/bin/python -m pytest tests/test_config_manager.py
```

### 集成测试

```bash
# 完整流程测试
./venv/bin/python tests/test_integration.py
```

### 性能测试

```bash
# 并行工具调用性能
./venv/bin/python tests/test_parallel_performance.py
```

## 部署注意事项

### macOS

- 需要代码签名和公证
- LSUIElement 设置为 1（无 Dock 图标）
- 刘海屏适配（顶部 90px 安全区）

### Windows

- 需要管理员权限（自启动功能）
- 使用 %APPDATA% 存储配置
- 注意路径分隔符差异

### Linux

- 需要 X11 或 Wayland 支持
- 系统托盘兼容性考虑
- 依赖包管理

## 版本兼容性

- Python: 3.9+
- PyQt6: 6.5.3+
- LangChain: 0.3.26+
- ActivityWatch: 0.12+

---

*最后更新: 2025-08-28*
*Baal Desktop Pet v1.0.0*