# Baal Desktop Pet Assistant - 技术参考文档

## 目录

1. [项目架构概述](#1-项目架构概述)
2. [核心模块详解](#2-核心模块详解)
3. [关键功能实现](#3-关键功能实现)
4. [API和接口](#4-api和接口)
5. [配置和数据结构](#5-配置和数据结构)
6. [构建和部署](#6-构建和部署)
7. [性能优化要点](#7-性能优化要点)
8. [错误处理机制](#8-错误处理机制)

---

## 1. 项目架构概述

### 1.1 整体技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                      用户界面层 (PyQt6)                       │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │PetWindow │ChatBubble│Settings  │Supervision│Calendar  │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
├─────────────────────────────────────────────────────────────┤
│                      核心功能层                              │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │LLMHandler│Emotion   │Persona   │Config    │Single    │  │
│  │          │Manager   │Manager   │Manager   │Instance  │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
├─────────────────────────────────────────────────────────────┤
│                      业务逻辑层                              │
│  ┌──────────┬──────────┬──────────┬──────────┐            │
│  │LLM       │Stats     │Supervision│Schedule │            │
│  │Assistant │Processor │Mode      │Manager  │            │
│  └──────────┴──────────┴──────────┴──────────┘            │
├─────────────────────────────────────────────────────────────┤
│                      外部服务层                              │
│  ┌──────────┬──────────┬──────────┐                       │
│  │LangChain │Activity  │Volcengine│                       │
│  │OpenAI    │Watch API │SDK       │                       │
│  └──────────┴──────────┴──────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 主要模块和组件

#### 应用入口
- **run_desktop_pet.py**: 主入口脚本，处理单实例检查和应用启动
- **baal/desktop_pet/main.py**: 应用主函数，初始化Qt应用和主窗口

#### UI组件（baal/desktop_pet/ui/）
- **PetWindow**: 主宠物窗口，显示动画和表情
- **ChatBubble**: 对话气泡，支持流式文本显示
- **SettingsDialog**: 设置对话框，配置API密钥等
- **SupervisionDialog**: 监督模式设置界面
- **DeveloperConsole**: 开发者控制台
- **MemoryClearDialog**: 记忆清理对话框

#### 核心功能（baal/desktop_pet/core/）
- **LLMHandler**: LLM交互处理器，管理流式响应
- **EmotionManager**: 表情管理，7种表情状态切换
- **PersonaManager**: 人格系统，3种性格模式
- **ConfigManager**: 配置管理，跨平台配置存储
- **SingleInstance**: 单实例保护机制
- **ProactiveDialogueManager**: 主动对话管理
- **StateAwareness**: 状态感知系统
- **ResourceManager**: 资源文件管理

#### LLM集成（baal/llm_assistant/）
- **LLMAssistant**: 完整功能的LLM助手
- **BinaryIntentClassifier**: 意图分类器
- **Parsers**: 命令解析器（日程、统计等）

#### 数据处理（baal/aw_stats/）
- **StatsProcessor**: ActivityWatch数据处理和分析

### 1.3 数据流和通信机制

#### 消息流向
```
用户输入 → PetWindow → AsyncWorker(QThread) → LLMHandler → LLMAssistant
    ↓                                              ↓
ChatBubble ← 流式响应 ← token_received信号 ← 异步生成器
```

#### 信号机制（PyQt6）
- **token_received**: 流式文本token传递
- **stream_finished**: 流式响应完成
- **emotion_detected**: 表情状态改变
- **status_changed**: LLM处理状态变化
- **reminder_needed**: 监督模式提醒
- **user_interaction**: 用户交互事件

---

## 2. 核心模块详解

### 2.1 baal/desktop_pet/core/llm_handler.py

#### 类：LLMHandler
主要负责与LLM的交互和流式响应处理。

**初始化参数：**
```python
def __init__(self, 
    base_url: str,           # API基础URL
    api_key: str,            # API密钥
    model: str = "doubao-seed-1-6-flash-250715",  # 模型名称
    persona_level: PersonaLevel = PersonaLevel.STRICT_MASTER,  # 人格档位
    supervision_mode=None    # 监督模式管理器实例
)
```

**核心方法：**

```python
async def stream_chat(self, user_input: str) -> AsyncGenerator[str, None]:
    """
    流式聊天生成
    
    Args:
        user_input: 用户输入文本
        
    Yields:
        str: 生成的文本token
        
    处理流程：
    1. 意图分类（是否需要工具调用）
    2. 如果需要工具：调用LLMAssistant获取数据
    3. 生成响应（带人格特征）
    4. 逐字符流式输出，带标点延迟
    """
```

```python
def _get_dynamic_system_prompt(self, use_cache: bool = True) -> str:
    """
    生成包含动态状态的系统提示词
    
    Returns:
        包含人格、状态、监督模式等信息的完整提示词
        
    动态元素：
    - 当前时间和日期
    - 天气状况（可选）
    - 监督模式状态
    - 用户活动状态
    - 个性化元素（随机）
    """
```

**双模型配置：**
- **chat_model**: "doubao-seed-1-6-250615" - 对话生成（角色扮演优化）
- **tool_model**: "doubao-seed-1-6-flash-250715" - 工具调用（功能执行）

### 2.2 baal/desktop_pet/ui/pet_window.py

#### 类：PetWindow
主宠物窗口，管理整个桌面宠物的显示和交互。

**关键属性：**
```python
class PetWindow(QWidget):
    # UI组件
    pet_button: DraggableButton      # 可拖动的宠物按钮
    chat_bubble: ChatBubble          # 对话气泡
    supervision_widget: SupervisionStatusWidget  # 监督状态显示
    
    # 管理器
    config_manager: ConfigManager    # 配置管理
    llm_handler: LLMHandler          # LLM处理
    emotion_manager: EmotionManager  # 表情管理
    preset_manager: PresetResponseManager  # 预设响应
    supervision_mode: SupervisionMode  # 监督模式
    
    # 异步处理
    async_worker: AsyncWorker        # 异步工作线程
```

**核心方法：**

```python
def _update_pet_emotion(self, emotion_tag: str):
    """
    更新宠物表情
    
    Args:
        emotion_tag: 表情标记 (<#1>到<#7>)
        
    处理：
    1. 从EmotionManager获取对应图片
    2. 缩放到合适大小
    3. 更新按钮显示
    """
```

```python
def handle_user_input(self, user_input: str):
    """
    处理用户输入
    
    流程：
    1. 检查预设响应
    2. 检查命令（/开头）
    3. 启动异步工作线程处理LLM响应
    4. 更新UI状态
    """
```

### 2.3 baal/desktop_pet/core/emotion_manager.py

#### 类：EmotionManager
管理表情资源和状态切换。

**表情映射：**
```python
EMOTION_MAP = {
    "<#1>": "开心1.png",
    "<#2>": "开心2.png", 
    "<#3>": "无语1.png",
    "<#4>": "无语2.png",
    "<#5>": "正常.png",
    "<#6>": "生气1.png",
    "<#7>": "生气2.png"
}
```

**核心方法：**

```python
def extract_emotion_from_text(self, text: str) -> tuple[str, Optional[str]]:
    """
    从文本中提取表情标记
    
    Returns:
        (清理后的文本, 最后一个表情标记)
        
    处理：
    1. 查找所有表情标记
    2. 移除标记，清理文本
    3. 返回最后一个有效标记
    """
```

### 2.4 baal/desktop_pet/core/persona_manager.py

#### 类：PersonaManager
管理AI的不同人格模式。

**人格档位：**
```python
class PersonaLevel(Enum):
    STRICT_MASTER = 1      # 严厉主人档
    SARCASTIC_BUTLER = 2   # 毒舌管家档
    GENTLE_COMPANION = 3   # 温柔伴侣档
    CUSTOM = 4            # 自定义档
```

**核心方法：**

```python
def get_system_prompt(self) -> str:
    """
    获取完整的系统提示词
    
    Returns:
        人设提示词 + 功能提示词的组合
        
    包含：
    - 身份设定
    - 性格特点
    - 语言风格
    - 互动原则
    - 表情使用规则
    """
```

### 2.5 baal/desktop_pet/supervision_mode.py

#### 类：SupervisionMode
监督模式管理器，监控用户活动并提供提醒。

**核心属性：**
```python
class SupervisionMode(QObject):
    # 信号
    reminder_needed = pyqtSignal(dict)  # 提醒信号
    mode_changed = pyqtSignal(bool)     # 模式改变信号
    
    # 状态
    is_active: bool                     # 是否激活
    long_term_goal: str                 # 长期目标
    short_term_goals: List[str]         # 短期目标列表
    check_interval: int = 300           # 检查间隔（秒）
```

**监督流程：**

```python
def _supervision_loop(self):
    """
    监督循环
    
    流程：
    1. 定期获取ActivityWatch数据
    2. 分析用户活动
    3. 与设定目标对比
    4. 生成智能提醒
    5. 发送reminder_needed信号
    """
```

### 2.6 baal/llm_assistant/assistant.py

#### 类：LLMAssistant
完整功能的LLM助手，集成工具调用能力。

**核心功能：**

```python
async def process_query(self, query: str) -> str:
    """
    处理用户查询
    
    流程：
    1. 意图分类
    2. 如果需要数据：
       - 解析命令
       - 并行执行工具调用
       - 聚合结果
    3. 生成响应
    4. 更新对话历史
    """
```

**并行工具调用优化：**
```python
async def _execute_parallel_tools(self, commands: List[ParsedCommand]):
    """
    并行执行多个工具调用
    
    优化：
    - 使用asyncio.gather并发执行
    - 减少复杂查询的响应时间
    - 异常隔离，单个失败不影响其他
    """
```

---

## 3. 关键功能实现

### 3.1 表情系统实现

#### 工作原理
1. **表情标记注入**：LLM在生成文本时，在句首添加表情标记（<#1>到<#7>）
2. **实时提取**：AsyncWorker在流式处理中实时提取表情标记
3. **异步更新**：通过emotion_detected信号更新UI
4. **资源管理**：EmotionManager预加载所有表情资源，避免运行时加载

#### 表情切换流程
```python
文本生成 → 检测标记 → 发送信号 → UI更新 → 图片切换
   ↓          ↓          ↓         ↓         ↓
LLMHandler  AsyncWorker  Signal  PetWindow  EmotionManager
```

### 3.2 流式响应机制

#### 实现细节

```python
async def stream_chat(self, user_input: str):
    """流式聊天实现"""
    # 1. 创建流式LLM实例
    streaming_llm = self._create_llm(streaming=True)
    
    # 2. 异步生成
    async for chunk in streaming_llm.astream(messages):
        content = chunk.content
        
        # 3. 逐字符输出，带延迟
        for char in content:
            yield char
            
            # 4. 标点符号延迟
            if char in '，。！？；：':
                await asyncio.sleep(0.3)
            elif char == '\n':
                await asyncio.sleep(0.2)
            else:
                await asyncio.sleep(0.05)
```

#### 字符延迟配置（constants.py）
```python
CHAR_DELAYS = {
    'normal': 0.05,      # 普通字符
    'punctuation': 0.3,  # 标点符号
    'newline': 0.2       # 换行符
}
```

### 3.3 并行工具调用

#### 实现架构

```python
class LLMAssistant:
    async def _process_with_data(self, user_input: str):
        """带数据的处理流程"""
        # 1. 解析用户意图
        parsed_command = self.stats_parser.parse(user_input)
        
        # 2. 构建查询列表
        queries = self._build_queries(parsed_command)
        
        # 3. 并行执行
        results = await asyncio.gather(
            *[self._execute_query(q) for q in queries],
            return_exceptions=True
        )
        
        # 4. 聚合结果
        return self._aggregate_results(results)
```

#### 优化效果
- 串行执行：3个查询 × 2秒 = 6秒
- 并行执行：max(3个查询) = 2秒
- 性能提升：66%

### 3.4 监督模式工作原理

#### 监督循环
```python
def _supervision_loop(self):
    """监督主循环"""
    while not self._stop_event.is_set():
        # 1. 等待检查间隔
        self._stop_event.wait(self.check_interval)
        
        # 2. 获取最近活动数据
        recent_stats = self._get_recent_stats()
        
        # 3. 分析生产力
        productivity_score = self._analyze_productivity(recent_stats)
        
        # 4. 生成提醒
        if self._should_remind(productivity_score):
            reminder = self._generate_reminder(recent_stats)
            self.reminder_needed.emit(reminder)
```

#### 生产力评分算法
```python
def _calculate_productivity_score(self, stats: Dict) -> float:
    """计算生产力分数"""
    work_apps = self.category_manager.get_work_apps()
    total_time = sum(stats.values())
    work_time = sum(time for app, time in stats.items() 
                   if app in work_apps)
    
    return (work_time / total_time) * 100 if total_time > 0 else 0
```

### 3.5 人格系统切换机制

#### 运行时切换
```python
def switch_persona(self, new_level: PersonaLevel):
    """切换人格"""
    # 1. 更新人格管理器
    self.persona_manager.set_persona_level(new_level)
    
    # 2. 重新生成系统提示词
    new_prompt = self.persona_manager.get_system_prompt()
    
    # 3. 更新LLM对话历史
    self.llm_handler.messages[0] = SystemMessage(content=new_prompt)
    
    # 4. 保存配置
    self.config_manager.set_config('persona_level', new_level.value)
```

#### 人格影响因素
- 语言风格（称呼、语气）
- 响应长度（1-4句动态调整）
- 表情使用频率
- 关怀程度
- 监督严格度

---

## 4. API和接口

### 4.1 模块间接口

#### LLMHandler ↔ LLMAssistant
```python
interface LLMHandlerToAssistant:
    process_query(query: str) -> str
    get_quick_response(query: str) -> str
    should_use_tools(query: str) -> bool
```

#### PetWindow ↔ ChatBubble
```python
interface PetWindowToBubble:
    show_message(text: str, type: str)
    set_streaming_mode(enabled: bool)
    append_token(token: str)
    update_position(pet_pos: QPoint)
```

#### SupervisionMode ↔ StatsProcessor
```python
interface SupervisionToStats:
    get_stats(time_range: str) -> Dict
    get_productivity_score() -> float
    get_active_window() -> str
```

### 4.2 信号接口（PyQt6）

#### AsyncWorker信号
```python
class AsyncWorker(QThread):
    # 输出信号
    token_received = pyqtSignal(str)      # 文本token
    stream_finished = pyqtSignal()        # 流完成
    error_occurred = pyqtSignal(str)      # 错误信息
    status_changed = pyqtSignal(str)      # 状态变化
    emotion_detected = pyqtSignal(str)    # 表情检测
```

#### SupervisionMode信号
```python
class SupervisionMode(QObject):
    reminder_needed = pyqtSignal(dict)    # 提醒数据
    mode_changed = pyqtSignal(bool)       # 模式改变
```

### 4.3 外部API集成

#### LangChain OpenAI接口
```python
# 配置示例
llm_config = {
    "base_url": "https://ark.cn-beijing.volces.com/api/v3",
    "api_key": "your-api-key",
    "model": "doubao-seed-1-6-flash-250715",
    "temperature": 0.7,
    "streaming": True
}
```

#### ActivityWatch API
```python
# 客户端配置
aw_client = ActivityWatchClient(
    client_name="baal-pet",
    host="localhost",
    port=5600
)

# 查询示例
query = """
    RETURN = query_bucket(find_bucket("aw-watcher-window_"));
    RETURN = merge_events_by_keys(RETURN, ["app"]);
    RETURN = sort_by_duration(RETURN);
"""
```

---

## 5. 配置和数据结构

### 5.1 配置文件格式

#### config.json
```json
{
    "api_key": "encrypted_api_key",
    "base_url": "https://ark.cn-beijing.volces.com/api/v3",
    "model": "doubao-seed-1-6-flash-250715",
    "chat_model": "doubao-seed-1-6-250615",
    "tool_model": "doubao-seed-1-6-flash-250715",
    "persona_level": 1,
    "window_position": {"x": 100, "y": 100},
    "start_minimized": false,
    "conversation_history": [],
    "updated_at": "2025-08-31T10:00:00"
}
```

#### supervision.json
```json
{
    "long_term_goal": "完成项目开发",
    "short_term_goals": [
        "编写技术文档",
        "修复bug",
        "代码审查"
    ],
    "check_interval": 300,
    "work_apps": ["VSCode", "PyCharm", "Terminal"],
    "updated_at": "2025-08-31T10:00:00"
}
```

### 5.2 重要数据结构

#### 对话消息结构
```python
@dataclass
class Message:
    role: str          # "system", "user", "assistant"
    content: str       # 消息内容
    timestamp: float   # 时间戳
    emotion: Optional[str]  # 表情标记
    metadata: Dict     # 额外元数据
```

#### 监督提醒结构
```python
@dataclass
class SupervisionReminder:
    type: str          # "productivity", "break", "goal"
    message: str       # 提醒内容
    severity: int      # 严重程度 1-5
    data: Dict        # 相关数据
    timestamp: float   # 时间戳
```

#### 活动统计结构
```python
@dataclass
class ActivityStats:
    app_name: str      # 应用名称
    duration: float    # 使用时长（秒）
    category: str      # 分类
    productivity: float  # 生产力分数
    time_range: str    # 时间范围
```

### 5.3 状态管理

#### 全局状态
```python
class GlobalState:
    # UI状态
    is_visible: bool
    is_minimized: bool
    window_position: QPoint
    
    # 功能状态
    supervision_active: bool
    streaming_active: bool
    current_emotion: str
    
    # 用户状态
    last_interaction: float
    idle_time: float
    productivity_score: float
```

---

## 6. 构建和部署

### 6.1 PyInstaller配置

#### baal.spec核心配置
```python
a = Analysis(
    ['run_desktop_pet.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('动作表情拆分', '动作表情拆分'),
        ('baal/references', 'baal/references'),
        ('baal/resources', 'baal/resources'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'langchain_openai',
        'aw_client',
        # ... 60+ 隐藏导入
    ],
    excludes=['PyQt5', 'numpy', 'matplotlib'],
)
```

#### 平台特定配置

**macOS (baal_macos.spec)**
```python
app = BUNDLE(
    exe,
    name='Watch Cats.app',
    icon='baal/resources/icons/app_icon.icns',
    bundle_identifier='com.baal.watchcats',
    info_plist={
        'NSHighResolutionCapable': True,
        'LSUIElement': '1',  # 菜单栏应用
    }
)
```

**Windows (baal_windows.spec)**
```python
exe = EXE(
    pyz,
    name='Watch Cats',
    icon='baal/resources/icons/app_icon.ico',
    console=False,
    uac_admin=False,
    runtime_tmpdir=None,
)
```

### 6.2 构建流程

#### 自动化构建脚本

**macOS (build.sh)**
```bash
#!/bin/bash
# 1. 创建/激活虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 清理旧构建
rm -rf build dist

# 4. PyInstaller打包
pyinstaller --clean --noconfirm baal_macos.spec

# 5. 创建DMG（可选）
dmgbuild -s scripts/dmgbuild-settings.py \
    -D app=dist/Watch\ Cats.app \
    "Watch Cats" dist/Watch\ Cats.dmg
```

**Windows (build_windows.ps1)**
```powershell
# 1. 创建/激活虚拟环境
python -m venv venv
.\venv\Scripts\Activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 清理旧构建
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

# 4. PyInstaller打包
pyinstaller --clean --noconfirm baal_windows.spec

# 5. 创建安装程序（可选）
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\baal_installer.iss
```

### 6.3 资源打包机制

#### 资源路径处理
```python
def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后
        base_path = Path(sys._MEIPASS)
    else:
        # 开发环境
        base_path = Path(__file__).parent.parent
    
    return base_path / relative_path
```

#### 资源类型
- **表情素材**: 动作表情拆分/*.png, *.gif
- **图标文件**: baal/resources/icons/*
- **API文档**: baal/references/*
- **配置模板**: baal/desktop_pet/core/default_config.py

---

## 7. 性能优化要点

### 7.1 内存管理

#### Qt对象生命周期
```python
class PetWindow(QWidget):
    def closeEvent(self, event):
        """正确清理资源"""
        # 1. 停止所有定时器
        self.timers.stop_all()
        
        # 2. 断开信号连接
        self.disconnect_all_signals()
        
        # 3. 停止异步线程
        if self.async_worker.isRunning():
            self.async_worker.terminate()
            self.async_worker.wait()
        
        # 4. 清理LLM资源
        self.llm_handler.cleanup()
        
        # 5. 保存配置
        self.config_manager.save()
```

#### 缓存管理
```python
class EmotionManager:
    def __init__(self):
        # 预加载所有表情，避免运行时IO
        self.emotion_pixmaps = self._preload_all_emotions()
        
        # 设置缓存大小限制
        self.cache_size_limit = 50 * 1024 * 1024  # 50MB
```

### 7.2 异步优化

#### 事件循环管理
```python
class AsyncWorker(QThread):
    def run(self):
        # 创建独立的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._process_stream())
        finally:
            # 清理事件循环
            loop.close()
            asyncio.set_event_loop(None)
```

#### 并发控制
```python
# 限制并发工具调用数量
MAX_CONCURRENT_TOOLS = 5
semaphore = asyncio.Semaphore(MAX_CONCURRENT_TOOLS)

async def execute_tool(tool_call):
    async with semaphore:
        return await tool_call()
```

### 7.3 响应时间优化

#### 预设响应系统
```python
class PresetResponseManager:
    """快速响应常见查询"""
    INSTANT_RESPONSES = {
        "你好": "主人好",
        "在吗": "本座一直在监视着",
        # ...
    }
    
    def get_instant_response(self, input_text):
        """0延迟响应"""
        return self.INSTANT_RESPONSES.get(input_text)
```

#### 状态缓存
```python
class StateAwareness:
    def get_current_state(self, use_cache=True):
        """智能状态获取"""
        if use_cache and self._is_cache_valid():
            return self._cached_state
        
        # 只更新变化的组件
        updated_components = self._get_changed_components()
        self._update_state(updated_components)
        return self._cached_state
```

---

## 8. 错误处理机制

### 8.1 分层错误处理

#### UI层错误处理
```python
class PetWindow:
    def handle_error(self, error: Exception):
        """UI层错误处理"""
        if isinstance(error, NetworkError):
            self.show_message("网络连接失败，请检查设置")
        elif isinstance(error, ConfigError):
            self.show_settings_dialog()
        else:
            self.logger.error(f"Unexpected error: {error}")
            self.show_message("发生了错误，请重试")
```

#### 业务层错误处理
```python
class LLMHandler:
    async def stream_chat(self, user_input: str):
        """带重试的流式聊天"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                async for token in self._stream_impl(user_input):
                    yield token
                break
            except RateLimitError:
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                if attempt == max_retries - 1:
                    yield f"抱歉，发生了错误：{str(e)}"
```

### 8.2 降级策略

#### 功能降级
```python
class StatsProcessor:
    def get_stats(self, time_range: str):
        """带降级的统计获取"""
        try:
            # 尝试从ActivityWatch获取
            return self._get_from_activitywatch(time_range)
        except ConnectionError:
            # 降级：返回缓存数据
            return self._get_cached_stats(time_range)
        except Exception:
            # 最终降级：返回空数据
            return self._get_empty_stats()
```

#### 优雅降级链
```python
降级优先级：
1. 完整功能（ActivityWatch + LLM）
2. 部分功能（仅LLM，无数据）
3. 基础功能（预设响应）
4. 最小功能（仅显示表情）
```

### 8.3 日志系统

#### 分级日志
```python
# 日志级别配置
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'baal.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
        }
    },
    'loggers': {
        'baal': {
            'level': 'DEBUG',
            'handlers': ['file', 'console'],
        }
    }
}
```

#### 性能日志装饰器
```python
@log_performance("function_name")
def some_function():
    """自动记录执行时间"""
    pass

# 日志输出：
# [PERFORMANCE] function_name took 0.123s
```

---

## 附录A：关键常量定义

```python
# 时间间隔（毫秒）
TIMERS = {
    'auto_hide': 30000,        # 自动隐藏
    'status_update': 100,      # 状态更新
    'emotion_check': 500,      # 表情检查
    'save_interval': 60000,    # 自动保存
}

# 窗口尺寸
WINDOW_SIZES = {
    'pet': (120, 120),
    'bubble_min': (250, 80),
    'bubble_max': (400, 300),
}

# 监督模式
SUPERVISION = {
    'default_check_interval': 300,  # 5分钟
    'parse_temperature': 0.1,
    'chat_temperature': 0.85,
}
```

## 附录B：第三方依赖版本

```
PyQt6==6.5.3
langchain==0.3.26
langchain-openai==0.3.17
aw-client>=0.5.13
aw-core>=0.5.16
volcengine-python-sdk==1.0.110
python-dateutil>=2.8.2
pytz>=2023.3
pydantic>=2.0.0
httpx>=0.24.0
```

---

*文档版本：1.0.0*  
*最后更新：2025-08-31*  
*由 Claude Code 生成*