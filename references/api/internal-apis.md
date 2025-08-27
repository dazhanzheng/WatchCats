# Internal API Documentation

## Core APIs

### LLMHandler API

The central interface for all LLM interactions in the application.

```python
class LLMHandler:
    """Manages LLM interactions with streaming support"""
    
    def __init__(self, base_url: str, api_key: str, model: str, persona_level: PersonaLevel)
        """
        Initialize the LLM handler.
        
        Args:
            base_url: API endpoint URL
            api_key: Authentication key
            model: Model identifier (e.g., "doubao-seed-1-6-flash-250715")
            persona_level: Initial personality setting
        """
    
    async def chat_stream(self, user_input: str) -> AsyncGenerator[str, None]
        """
        Stream chat responses token by token.
        
        Args:
            user_input: User's message
            
        Yields:
            str: Individual tokens from the response
            
        Raises:
            Exception: API errors or network issues
        """
    
    def set_persona(self, persona_level: PersonaLevel) -> None
        """
        Switch to a different personality.
        
        Args:
            persona_level: New personality level
        """
    
    def clear_memory(self) -> None
        """Clear conversation history"""
    
    def save_conversation(self) -> None
        """Persist conversation to disk"""
    
    def load_conversation(self) -> None
        """Restore conversation from disk"""
```

### ConfigManager API

Cross-platform configuration management system.

```python
class ConfigManager:
    """Manages application configuration with platform-specific paths"""
    
    def __init__(self)
        """Initialize config manager and load existing config"""
    
    def get_config(self) -> Dict[str, Any]
        """
        Get current configuration.
        
        Returns:
            Dict containing all configuration values
        """
    
    def update_config(self, updates: Dict[str, Any]) -> bool
        """
        Update configuration values.
        
        Args:
            updates: Dictionary of config updates
            
        Returns:
            bool: Success status
        """
    
    def save_config(self) -> bool
        """
        Save configuration to disk.
        
        Returns:
            bool: Success status
        """
    
    def is_configured(self) -> bool
        """
        Check if API keys are configured.
        
        Returns:
            bool: True if properly configured
        """
    
    def get_config_path(self) -> Path
        """
        Get platform-specific config directory.
        
        Returns:
            Path: Configuration directory path
        """
```

### PersonaManager API

Manages different AI personality modes.

```python
class PersonaManager:
    """Manages persona switching and prompt generation"""
    
    def __init__(self, initial_level: PersonaLevel = PersonaLevel.STRICT_MASTER)
        """Initialize with a persona level"""
    
    def get_system_prompt(self) -> str
        """
        Get current persona's system prompt.
        
        Returns:
            str: Complete system prompt with persona
        """
    
    def set_persona(self, level: PersonaLevel) -> None
        """
        Switch to different persona.
        
        Args:
            level: New persona level
        """
    
    def get_current_persona(self) -> PersonaLevel
        """
        Get current persona level.
        
        Returns:
            PersonaLevel: Current active persona
        """
    
    def get_persona_info(self) -> Dict[str, str]
        """
        Get current persona details.
        
        Returns:
            Dict with name and description
        """
```

### EmotionManager API

Controls the pet's emotional expressions.

```python
class EmotionManager:
    """Manages emotion states and expression assets"""
    
    EMOTIONS = ['normal', 'happy', 'angry', 'confused', 'sad', 'excited', 'tired']
    
    def __init__(self)
        """Initialize emotion manager"""
    
    def get_emotion_from_text(self, text: str) -> Optional[str]
        """
        Detect emotion from text content.
        
        Args:
            text: Text to analyze
            
        Returns:
            Optional[str]: Detected emotion or None
        """
    
    def detect_emotion_tag(self, text: str) -> Optional[int]
        """
        Extract emotion tag from response.
        
        Args:
            text: Text with potential emotion tag <#n>
            
        Returns:
            Optional[int]: Emotion ID (1-7) or None
        """
    
    def get_emotion_image_path(self, emotion: str) -> Path
        """
        Get image asset path for emotion.
        
        Args:
            emotion: Emotion name
            
        Returns:
            Path: Path to emotion image file
        """
    
    def map_tag_to_emotion(self, tag_id: int) -> str
        """
        Map numeric tag to emotion name.
        
        Args:
            tag_id: Emotion tag ID (1-7)
            
        Returns:
            str: Emotion name
        """
```

### SupervisionMode API

Productivity monitoring and reminder system.

```python
class SupervisionMode(QObject):
    """Manages supervision mode for productivity monitoring"""
    
    # Qt Signals
    reminder_needed = pyqtSignal(dict)
    mode_changed = pyqtSignal(bool)
    
    def __init__(self, persona_manager: Optional[PersonaManager] = None)
        """Initialize supervision mode"""
    
    def start_supervision(self, 
                         long_term_goal: Optional[str] = None,
                         short_term_goals: Optional[List[str]] = None) -> bool
        """
        Start supervision monitoring.
        
        Args:
            long_term_goal: Main objective
            short_term_goals: List of immediate tasks
            
        Returns:
            bool: Success status
        """
    
    def stop_supervision(self) -> None
        """Stop supervision monitoring"""
    
    def is_active(self) -> bool
        """Check if supervision is active"""
    
    def check_productivity(self) -> Dict[str, Any]
        """
        Analyze current productivity.
        
        Returns:
            Dict with productivity metrics and analysis
        """
    
    def get_supervision_status(self) -> Dict[str, Any]
        """
        Get current supervision status.
        
        Returns:
            Dict with goals, status, and last check time
        """
```

### StatsProcessor API

ActivityWatch data processing interface.

```python
class StatsProcessor:
    """Processes ActivityWatch statistics"""
    
    def __init__(self)
        """Initialize stats processor with AW client"""
    
    def get_stats(self, 
                  query_type: str,
                  time_range: str = "today",
                  **kwargs) -> Dict[str, Any]
        """
        Get activity statistics.
        
        Args:
            query_type: Type of query (apps, categories, timeline, etc.)
            time_range: Time period (today, week, month, custom)
            **kwargs: Additional query parameters
            
        Returns:
            Dict: Processed statistics data
        """
    
    def get_recent_activity(self, minutes: int = 30) -> List[Dict]
        """
        Get recent activity events.
        
        Args:
            minutes: How many minutes back to query
            
        Returns:
            List of activity events
        """
    
    def calculate_productivity_score(self, 
                                    activities: List[Dict],
                                    productive_apps: List[str]) -> float
        """
        Calculate productivity score.
        
        Args:
            activities: List of activity events
            productive_apps: Apps considered productive
            
        Returns:
            float: Score between 0.0 and 1.0
        """
```

## UI Component APIs

### PetWindow API

Main application window interface.

```python
class PetWindow(QWidget):
    """Main pet window widget"""
    
    # Qt Signals
    summary_status_signal = pyqtSignal(str)
    
    def __init__(self)
        """Initialize pet window"""
    
    def show_chat_bubble(self) -> None
        """Display chat interface"""
    
    def hide_chat_bubble(self) -> None
        """Hide chat interface"""
    
    def send_message(self, message: str) -> None
        """
        Send user message to LLM.
        
        Args:
            message: User input text
        """
    
    def update_pet_image(self, emotion: str) -> None
        """
        Update pet's displayed emotion.
        
        Args:
            emotion: Emotion name to display
        """
    
    def show_preset_message(self, message: str, duration: int = 5000) -> None
        """
        Show temporary preset message.
        
        Args:
            message: Message to display
            duration: Display time in milliseconds
        """
    
    def toggle_supervision(self) -> None
        """Toggle supervision mode on/off"""
```

### ChatBubble API

Chat interface component.

```python
class ChatBubble(QWidget):
    """Resizable chat bubble widget"""
    
    def __init__(self, parent: Optional[QWidget] = None)
        """Initialize chat bubble"""
    
    def append_text(self, text: str) -> None
        """
        Append text to chat display.
        
        Args:
            text: Text to append
        """
    
    def set_typing_indicator(self, visible: bool) -> None
        """
        Show/hide typing indicator.
        
        Args:
            visible: Indicator visibility
        """
    
    def clear_chat(self) -> None
        """Clear all chat content"""
    
    def save_chat_history(self) -> None
        """Save chat to file"""
    
    def load_chat_history(self) -> None
        """Load chat from file"""
```

## Parser APIs

### StatsCommandParser API

Natural language to structured command parsing.

```python
class StatsCommandParser:
    """Parses natural language to stats commands"""
    
    def __init__(self)
        """Initialize parser with LangChain components"""
    
    def parse(self, query: str) -> ParsedStatsCommand
        """
        Parse natural language query.
        
        Args:
            query: Natural language input
            
        Returns:
            ParsedStatsCommand: Structured command object
        """
```

### BinaryIntentClassifier API

Intent detection for queries.

```python
class BinaryIntentClassifier:
    """Classifies if query needs data access"""
    
    def __init__(self, llm: ChatOpenAI)
        """Initialize classifier with LLM"""
    
    def requires_data(self, query: str) -> bool
        """
        Check if query needs data access.
        
        Args:
            query: User query text
            
        Returns:
            bool: True if data access needed
        """
```

## Thread Worker APIs

### AsyncWorker API

Background thread for LLM streaming.

```python
class AsyncWorker(QThread):
    """Async worker thread for streaming responses"""
    
    # Qt Signals
    token_received = pyqtSignal(str)
    stream_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    emotion_detected = pyqtSignal(str)
    
    def __init__(self, llm_handler: LLMHandler)
        """Initialize worker with LLM handler"""
    
    def set_input(self, user_input: str) -> None
        """Set user input for processing"""
    
    def run(self) -> None
        """Thread execution entry point"""
    
    def stop(self) -> None
        """Stop thread execution"""
```

## External API Integrations

### OpenAI-Compatible LLM API

```python
# Configuration
base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
api_key: str = "your-api-key"
model: str = "doubao-seed-1-6-flash-250715"

# Request Format
{
    "model": "model-name",
    "messages": [
        {"role": "system", "content": "system prompt"},
        {"role": "user", "content": "user message"},
        {"role": "assistant", "content": "response"}
    ],
    "temperature": 0.7,
    "stream": true
}

# Streaming Response Format
data: {"choices": [{"delta": {"content": "token"}}]}
```

### ActivityWatch API

```python
# Base URL
base_url: str = "http://localhost:5600/api"

# Key Endpoints
GET /0/buckets/                    # List all buckets
GET /0/buckets/{bucket_id}/events  # Get events from bucket
POST /0/query/                     # Execute custom query

# Query Format
{
    "timeperiods": ["2025-01-01T00:00:00+00:00/2025-01-02T00:00:00+00:00"],
    "query": ["QUERY_STRING"]
}
```

## Signal/Slot Connections

### Key Signal Flows

```python
# Chat Flow
user_input → send_button.clicked → pet_window.send_message()
           → async_worker.start() → token_received → chat_bubble.append_text()

# Emotion Flow  
llm_response → emotion_detected → emotion_manager.update()
            → emotion_changed → pet_window.update_image()

# Supervision Flow
timer.timeout → supervision_mode.check() → reminder_needed 
             → pet_window.show_alert()

# Settings Flow
settings_action → settings_dialog.show() → config_updated
               → components.reload_config()
```

## Error Codes and Handling

### Application Error Codes

```python
# Configuration Errors
CONFIG_NOT_FOUND = 1001
CONFIG_CORRUPT = 1002
CONFIG_PERMISSION_DENIED = 1003

# API Errors
API_KEY_INVALID = 2001
API_RATE_LIMIT = 2002
API_NETWORK_ERROR = 2003
API_TIMEOUT = 2004

# ActivityWatch Errors
AW_NOT_RUNNING = 3001
AW_BUCKET_NOT_FOUND = 3002
AW_QUERY_FAILED = 3003

# UI Errors
UI_RESOURCE_NOT_FOUND = 4001
UI_RENDER_FAILED = 4002

# System Errors
INSTANCE_ALREADY_RUNNING = 5001
INSUFFICIENT_MEMORY = 5002
```

### Error Handler Pattern

```python
try:
    # Operation
    result = perform_operation()
except SpecificError as e:
    logger.error(f"Specific error: {e}")
    # Specific recovery
    fallback_action()
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    # Generic recovery
    show_error_dialog(e)
finally:
    # Cleanup
    release_resources()
```