# Core Functions Documentation

## Entry Point Functions

### run_desktop_pet.py

```python
def main() -> None:
    """
    Application entry point with environment setup.
    
    Flow:
        1. Configure SSL settings based on environment
        2. Initialize logging system
        3. Run preflight checks (Windows/frozen only)
        4. Check single instance lock
        5. Import and execute main application
        6. Handle cleanup on exit
    
    Environment Variables:
        BAAL_DEV_MODE: Enable development mode
        DISABLE_SSL_VERIFY: Disable SSL verification
        BAAL_LOG_DIR: Custom log directory
        BAAL_DEBUG: Enable debug mode
    
    Exit Codes:
        0: Normal exit
        1: Startup failure
    """
```

## LLM Handler Functions

### baal/desktop_pet/core/llm_handler.py

```python
def _create_llm(self, streaming: bool = True, temperature: float = 0.7) -> ChatOpenAI:
    """
    Create LLM instance with specified configuration.
    
    Args:
        streaming: Enable streaming responses
        temperature: Model temperature (0.0-1.0)
    
    Returns:
        ChatOpenAI: Configured LLM instance
    
    Raises:
        Exception: If LLM creation fails
    """

async def _process_with_intent(self, user_input: str) -> AsyncGenerator[str, None]:
    """
    Process user input with intent classification.
    
    Args:
        user_input: Raw user message
    
    Yields:
        str: Response tokens
    
    Flow:
        1. Classify intent (data query vs chat)
        2. Route to appropriate handler
        3. Stream response tokens
    """

def _load_conversation_history(self) -> None:
    """
    Load persisted conversation from disk.
    
    Side Effects:
        - Updates self.messages
        - Updates self.assistant.conversation_history
        - Logs loading status
    
    File Format:
        JSON with messages array and optional summary
    """

def _save_conversation_history(self) -> None:
    """
    Persist conversation to disk.
    
    Side Effects:
        - Writes to conversation_memory.json
        - Creates config directory if needed
        - Logs save status
    
    Error Handling:
        Silently fails with warning log
    """

async def _generate_summary(self, messages: List[Any]) -> str:
    """
    Generate conversation summary using LLM.
    
    Args:
        messages: Conversation messages to summarize
    
    Returns:
        str: Generated summary text
    
    Note:
        Uses lower temperature (0.3) for consistency
    """
```

## Configuration Manager Functions

### baal/desktop_pet/core/config_manager.py

```python
def _get_config_dir(self) -> Path:
    """
    Determine platform-specific config directory.
    
    Returns:
        Path: Configuration directory path
    
    Platform Logic:
        Windows:
            1. Try LOCALAPPDATA env var
            2. Try APPDATA env var
            3. Construct AppData path
            4. Fall back to Documents
            5. Last resort: user home
        
        macOS/Linux:
            Use ~/.baal_pet/
    """

def _ensure_config_dir(self) -> None:
    """
    Create config directory with retry logic.
    
    Retry Strategy:
        - 3 attempts with exponential backoff
        - Test write permissions
        - Fall back to alternative locations
    
    Raises:
        RuntimeError: If all attempts fail
    """

def _migrate_old_config(self) -> None:
    """
    Migrate configuration from old location.
    
    Migration Paths:
        ~/.baal_pet/config.json → new location
        ~/BaalPet/config.json → new location
    
    Behavior:
        - Copies old config if found
        - Preserves original file
        - Logs migration status
    """

def get_api_config(self) -> Dict[str, str]:
    """
    Get API configuration subset.
    
    Returns:
        Dict with base_url, api_key, and model
    
    Security:
        Returns empty strings for missing values
        Never returns None for API fields
    """
```

## Emotion Manager Functions

### baal/desktop_pet/core/emotion_manager.py

```python
def detect_emotion_tag(self, text: str) -> Optional[Tuple[str, str]]:
    """
    Extract emotion tag from LLM response.
    
    Args:
        text: Response text with potential <#n> tag
    
    Returns:
        Optional[Tuple[str, str]]: (emotion, cleaned_text)
    
    Pattern:
        <#1> to <#7> at start of text
    
    Mapping:
        1,2 → happy
        3,4 → confused  
        5 → normal
        6,7 → angry
    """

def get_emotion_path(self, emotion: str) -> str:
    """
    Get file path for emotion asset.
    
    Args:
        emotion: Emotion name
    
    Returns:
        str: Absolute path to image file
    
    Asset Location:
        动作表情拆分/{emotion}.png
    """

def analyze_text_emotion(self, text: str) -> str:
    """
    Analyze text content for emotion.
    
    Args:
        text: Text to analyze
    
    Returns:
        str: Detected emotion (defaults to 'normal')
    
    Keywords:
        happy: 开心, 愉快, 满意, 不错
        angry: 愚蠢, 废物, 无能, 失望
        confused: 什么, 嗯?, 不懂
    """
```

## Persona Manager Functions

### baal/desktop_pet/core/persona_manager.py

```python
def get_system_prompt(self) -> str:
    """
    Generate complete system prompt.
    
    Returns:
        str: Combined base + persona prompts
    
    Components:
        1. Base functional prompt (expressions, rules)
        2. Persona-specific prompt
        3. Custom additions if applicable
    """

def set_persona(self, level: PersonaLevel) -> None:
    """
    Switch active persona.
    
    Args:
        level: New persona level
    
    Side Effects:
        Updates current_level
        Regenerates prompts
        Logs persona change
    """

def get_response_style(self) -> Dict[str, Any]:
    """
    Get persona-specific response parameters.
    
    Returns:
        Dict with:
            - max_length: Response length limit
            - temperature: Suggested LLM temperature
            - tone: Response tone descriptor
    """
```

## Supervision Mode Functions

### baal/desktop_pet/supervision_mode.py

```python
def _check_productivity(self) -> None:
    """
    Background thread productivity check.
    
    Flow:
        1. Get recent activity from ActivityWatch
        2. Analyze against goals
        3. Generate productivity score
        4. Emit reminder if needed
    
    Runs Every:
        self.check_interval seconds (default 300)
    """

def _analyze_activity(self, activities: List[Dict]) -> Dict[str, Any]:
    """
    Analyze activity data for productivity.
    
    Args:
        activities: Recent activity events
    
    Returns:
        Dict with:
            - score: 0.0 to 1.0
            - productive_time: minutes
            - unproductive_time: minutes
            - top_apps: list of (app, duration)
            - recommendation: string
    """

def _generate_reminder(self, analysis: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate reminder message based on analysis.
    
    Args:
        analysis: Productivity analysis results
    
    Returns:
        Dict with:
            - message: Reminder text
            - severity: low/medium/high
            - emotion: Suggested emotion
    
    Uses:
        Current persona for tone
        LLM for dynamic messages
    """
```

## UI Component Functions

### baal/desktop_pet/ui/pet_window.py

```python
def setup_ui(self) -> None:
    """
    Initialize UI components and layout.
    
    Components Created:
        - Pet image display
        - Control buttons (draggable)
        - System tray icon
        - Context menus
    
    Layout:
        Frameless window
        Transparent background
        Always on top
    """

def handle_streaming_response(self) -> None:
    """
    Process streaming LLM response.
    
    Flow:
        1. Start async worker thread
        2. Connect signal handlers
        3. Update UI progressively
        4. Handle completion/errors
    
    Signals Connected:
        token_received → append to chat
        emotion_detected → update pet image
        stream_finished → cleanup
        error_occurred → show error
    """

def update_position(self) -> None:
    """
    Save and restore window position.
    
    Behavior:
        - Saves on move
        - Restores on startup
        - Respects screen boundaries
        - Handles multi-monitor
    
    macOS Special:
        Enforces 90px top margin for notch
    """
```

### baal/desktop_pet/ui/chat_bubble.py

```python
def setup_resize_handle(self) -> None:
    """
    Create draggable resize handle.
    
    Features:
        - Corner grip for resizing
        - Minimum size constraints
        - Aspect ratio preservation
        - Smooth resize animation
    """

def append_text_animated(self, text: str) -> None:
    """
    Append text with typing animation.
    
    Args:
        text: Text to append
    
    Animation:
        - Character by character
        - Punctuation delays
        - Maintains scroll position
        - Preserves formatting
    """

def auto_dismiss(self, duration: int = 30000) -> None:
    """
    Auto-hide bubble after timeout.
    
    Args:
        duration: Milliseconds before hiding
    
    Behavior:
        - Starts timer on message complete
        - Resets on user interaction
        - Cancels on new message
    """
```

## Stats Processor Functions

### baal/aw_stats/stats_processor.py

```python
def get_window_data(self, start: datetime, end: datetime) -> List[Dict]:
    """
    Get window activity data from ActivityWatch.
    
    Args:
        start: Period start time
        end: Period end time
    
    Returns:
        List of window events with app and title
    
    Processing:
        - Fetches from aw-watcher-window bucket
        - Filters by time range
        - Aggregates by application
    """

def calculate_category_time(self, events: List[Dict]) -> Dict[str, float]:
    """
    Categorize and sum activity time.
    
    Args:
        events: Window activity events
    
    Returns:
        Dict mapping category to hours
    
    Categories:
        - Productivity (IDEs, Office)
        - Communication (Slack, Email)
        - Entertainment (Games, Video)
        - Browsing (Browsers)
        - Other
    """

def get_productivity_score(self, 
                          productive_apps: List[str],
                          time_range: str = "today") -> float:
    """
    Calculate productivity percentage.
    
    Args:
        productive_apps: Apps considered productive
        time_range: Period to analyze
    
    Returns:
        float: Score from 0.0 to 1.0
    
    Formula:
        productive_time / total_active_time
    """
```

## Utility Functions

### baal/desktop_pet/core/single_instance.py

```python
def check_single_instance(app_id: str) -> Optional[FileLock]:
    """
    Ensure only one instance runs.
    
    Args:
        app_id: Unique application identifier
    
    Returns:
        Optional[FileLock]: Lock object or None
    
    Implementation:
        Windows: Named mutex
        Unix: PID file with lock
    
    Behavior:
        Returns lock if acquired
        Returns None if instance exists
    """
```

### baal/desktop_pet/core/resource_manager.py

```python
def get_resource_path(relative_path: str) -> Path:
    """
    Get absolute path to resource file.
    
    Args:
        relative_path: Path relative to resources
    
    Returns:
        Path: Absolute path to resource
    
    Handles:
        - Development (source tree)
        - Frozen (PyInstaller bundle)
        - Package (installed module)
    """

def load_image_asset(asset_name: str) -> QPixmap:
    """
    Load and cache image asset.
    
    Args:
        asset_name: Image filename
    
    Returns:
        QPixmap: Loaded image
    
    Features:
        - LRU cache for performance
        - Fallback to default image
        - Format auto-detection
    """
```

### baal/desktop_pet/core/logger_config.py

```python
def init_logging(console_level: str = 'INFO',
                file_level: str = 'DEBUG') -> None:
    """
    Initialize logging system.
    
    Args:
        console_level: Console log level
        file_level: File log level
    
    Configuration:
        - Rotating file handler (10MB, 5 backups)
        - Structured formatting
        - Thread-safe operations
        - Performance timing decorators
    """

@log_performance
def timed_function():
    """
    Decorator for timing function execution.
    
    Logs:
        - Function name
        - Execution time
        - Parameters (if debug)
        - Return value type
    """

def log_ui_event(event_type: str, details: Dict = None) -> None:
    """
    Log UI interaction events.
    
    Args:
        event_type: Event identifier
        details: Additional event data
    
    Used For:
        - User action tracking
        - Performance analysis
        - Error reproduction
    """
```

## Parser Functions

### baal/llm_assistant/parsers.py

```python
def parse_stats_command(self, query: str) -> ParsedStatsCommand:
    """
    Parse natural language to structured command.
    
    Args:
        query: User's natural language query
    
    Returns:
        ParsedStatsCommand with:
            - query_type: apps/categories/timeline
            - time_range: today/week/month/custom
            - filters: Optional filters
            - format: table/chart/summary
    
    Examples:
        "今天用了哪些软件" → (apps, today, None, table)
        "本周生产力如何" → (productivity, week, None, summary)
    """

def extract_time_range(self, text: str) -> Tuple[datetime, datetime]:
    """
    Extract time range from text.
    
    Args:
        text: Text containing time references
    
    Returns:
        Tuple[datetime, datetime]: (start, end)
    
    Patterns:
        - "今天" → today 00:00 to now
        - "本周" → Monday 00:00 to now
        - "3小时" → 3 hours ago to now
        - "1月15日" → specific date
    """
```

## Build System Functions

### Scripts and Build Functions

```python
# convert_icon.py
def create_multisize_ico(input_path: str, output_path: str) -> None:
    """
    Create Windows ICO with multiple resolutions.
    
    Args:
        input_path: Source image path
        output_path: Output ICO path
    
    Resolutions:
        16x16, 32x32, 48x48, 64x64, 128x128, 256x256
    """

# ci_windows_fix.py  
def fix_windows_paths() -> None:
    """
    Fix path issues in Windows CI environment.
    
    Fixes:
        - Qt plugin paths
        - DLL search paths
        - Virtual environment activation
    """

# fix_paths_windows.py
def ensure_qt_plugins() -> None:
    """
    Ensure Qt plugins are properly located.
    
    Actions:
        - Copy plugins to correct location
        - Set QT_PLUGIN_PATH
        - Verify plugin loading
    """
```

## Data Migration Functions

### baal/desktop_pet/core/data_migration.py

```python
def auto_migrate() -> Dict[str, Any]:
    """
    Automatically migrate data from old versions.
    
    Returns:
        Dict with:
            - success: bool
            - files_migrated: List[str]
            - errors: List[str]
    
    Migrations:
        - Config format updates
        - Path relocations
        - Schema changes
        - Default value additions
    """

def migrate_config_v1_to_v2(old_config: Dict) -> Dict:
    """
    Migrate v1 config format to v2.
    
    Changes:
        - Rename 'goal' to 'long_term_goal'
        - Add 'short_term_goals' array
        - Update model to latest version
        - Add new default settings
    """
```