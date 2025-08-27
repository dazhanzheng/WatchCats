# Dependency Graph and Module Relationships

## Module Dependency Hierarchy

```
run_desktop_pet.py
    ├── baal.desktop_pet.core.logger_config
    ├── baal.desktop_pet.core.preflight_check
    ├── baal.desktop_pet.core.single_instance
    └── baal.desktop_pet.main
        └── PyQt6 (QApplication)
        └── baal.desktop_pet.ui.PetWindow
            ├── baal.desktop_pet.core
            │   ├── ConfigManager
            │   ├── LLMHandler
            │   │   ├── langchain_openai.ChatOpenAI
            │   │   ├── baal.llm_assistant.LLMAssistant
            │   │   │   ├── langchain
            │   │   │   ├── baal.aw_stats.StatsProcessor
            │   │   │   └── baal.llm_assistant.parsers
            │   │   └── baal.llm_assistant.BinaryIntentClassifier
            │   ├── EmotionManager
            │   ├── PersonaManager
            │   ├── PresetResponseManager
            │   └── ResourceManager
            ├── baal.desktop_pet.ui
            │   ├── ChatBubble
            │   ├── SettingsDialog
            │   ├── SupervisionDialog
            │   ├── DeveloperConsole
            │   └── MemoryClearDialog
            └── baal.desktop_pet.supervision_mode
                ├── baal.aw_stats.StatsProcessor
                └── baal.llm_assistant.LLMAssistant
```

## External Dependencies

### Core Framework Dependencies

```yaml
PyQt6:
  version: "6.5.3"
  components:
    - PyQt6-Qt6: "6.5.3"
    - PyQt6-sip: "13.8.0"
  usage:
    - UI framework
    - Event system
    - Signal/slot mechanism
    - System tray integration
  critical: true

langchain:
  version: "0.3.26"
  usage:
    - LLM orchestration
    - Prompt management
    - Tool integration
    - Memory management
  critical: true

langchain-openai:
  version: "0.3.17"
  usage:
    - OpenAI API compatibility
    - Chat model interface
    - Streaming support
  critical: true
```

### API and Integration Dependencies

```yaml
aw-client:
  version: ">=0.5.13"
  usage:
    - ActivityWatch API client
    - Event data fetching
    - Bucket management
  critical: false
  fallback: "Works without ActivityWatch"

aw-core:
  version: ">=0.5.16"
  usage:
    - ActivityWatch data models
    - Event processing
    - Time period handling
  critical: false

volcengine-python-sdk:
  version: "1.0.110"
  usage:
    - Volcano Engine API support
    - Alternative LLM provider
  critical: false
  note: "Optional for Doubao model"
```

### Utility Dependencies

```yaml
python-dateutil:
  version: "2.9.0"
  usage:
    - Date parsing
    - Time zone handling
    - Relative date calculation
  critical: true

pytz:
  version: "2024.2"
  usage:
    - Time zone database
    - DST handling
  critical: false

pydantic:
  version: "2.10.6"
  usage:
    - Data validation
    - Structured output parsing
    - Settings management
  critical: true

httpx:
  version: "0.28.1"
  usage:
    - Async HTTP client
    - API requests
    - Better performance than requests
  critical: true

requests:
  version: "2.32.3"
  usage:
    - Legacy HTTP client
    - Backward compatibility
  critical: false
```

### Development Dependencies

```yaml
PyInstaller:
  version: "6.11.1"
  usage:
    - Application bundling
    - Executable creation
    - Resource packaging
  critical: false
  note: "Only needed for building"

dmgbuild:
  version: "latest"
  usage:
    - macOS DMG creation
    - Distribution packaging
  critical: false
  note: "macOS only"
```

## Internal Module Dependencies

### Core Module Relationships

```python
# ConfigManager dependencies
ConfigManager:
  imports:
    - pathlib.Path
    - json
    - threading (for locks)
    - .logger_config
    - .default_config
    - .data_migration
  provides:
    - Configuration storage
    - API key management
    - Platform-specific paths
  used_by:
    - LLMHandler
    - PetWindow
    - SupervisionMode
    - All dialogs

# LLMHandler dependencies
LLMHandler:
  imports:
    - langchain_openai
    - langchain_core.messages
    - .persona_manager
    - .config_manager
    - .preset_dialogues
    - ..llm_assistant.assistant
    - ..llm_assistant.binary_intent_classifier
  provides:
    - LLM interaction
    - Streaming responses
    - Conversation management
  used_by:
    - PetWindow
    - AsyncWorker
    - SupervisionMode

# PersonaManager dependencies
PersonaManager:
  imports:
    - enum.Enum
    - typing
  provides:
    - Persona switching
    - System prompts
    - Response styles
  used_by:
    - LLMHandler
    - SupervisionMode

# EmotionManager dependencies
EmotionManager:
  imports:
    - pathlib.Path
    - re (regex)
    - .resource_manager
  provides:
    - Emotion detection
    - Asset mapping
    - State management
  used_by:
    - PetWindow
    - AsyncWorker
```

### UI Component Dependencies

```python
# PetWindow dependencies
PetWindow(QWidget):
  imports:
    - PyQt6.QtWidgets.*
    - PyQt6.QtCore.*
    - PyQt6.QtGui.*
    - .chat_bubble.ChatBubble
    - .settings_dialog.SettingsDialog
    - .supervision_dialog.SupervisionDialog
    - ..core.config_manager
    - ..core.llm_handler
    - ..core.emotion_manager
    - ..supervision_mode
  provides:
    - Main window
    - System tray
    - Event coordination
  
# ChatBubble dependencies
ChatBubble(QWidget):
  imports:
    - PyQt6.QtWidgets.*
    - PyQt6.QtCore.QTimer
  provides:
    - Chat display
    - Text streaming
    - Auto-dismiss
  used_by:
    - PetWindow

# Dialog dependencies
SettingsDialog(QDialog):
  imports:
    - PyQt6.QtWidgets.*
    - ..core.config_manager
    - ..core.autostart_manager
  provides:
    - Settings UI
    - Configuration updates
```

### Integration Module Dependencies

```python
# LLMAssistant dependencies
LLMAssistant:
  imports:
    - langchain_openai
    - langchain.schema
    - .parsers
    - ..aw_stats.stats_processor
    - ..desktop_pet.core.logger_config
  provides:
    - Full LLM functionality
    - Tool orchestration
    - Intent routing
  used_by:
    - LLMHandler
    - SupervisionMode

# StatsProcessor dependencies  
StatsProcessor:
  imports:
    - aw_client
    - datetime
    - typing
  provides:
    - ActivityWatch queries
    - Data aggregation
    - Productivity metrics
  used_by:
    - LLMAssistant
    - SupervisionMode

# SupervisionMode dependencies
SupervisionMode(QObject):
  imports:
    - threading
    - PyQt6.QtCore.pyqtSignal
    - ..aw_stats.stats_processor
    - ..llm_assistant.assistant
    - .core.config_manager
  provides:
    - Background monitoring
    - Productivity alerts
    - Goal tracking
  used_by:
    - PetWindow
```

## Circular Dependencies

### Identified Circular Dependencies

```yaml
None identified:
  - Proper use of dependency injection
  - Interface-based design
  - Signal/slot decoupling
```

### Dependency Injection Patterns

```python
# Example: LLMHandler receives dependencies
class LLMHandler:
    def __init__(self, 
                 base_url: str,
                 api_key: str, 
                 model: str,
                 persona_level: PersonaLevel):
        # Dependencies injected, not created
        self.persona_manager = PersonaManager(persona_level)
        self.config_manager = ConfigManager()

# Example: SupervisionMode receives optional dependency
class SupervisionMode:
    def __init__(self, persona_manager=None):
        # Optional dependency injection
        self.persona_manager = persona_manager
```

## Build-Time Dependencies

### PyInstaller Hidden Imports

```python
hiddenimports = [
    # Core Python
    'asyncio', 'threading', 'json', 'pathlib',
    
    # PyQt6
    'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets',
    'PyQt6.sip',
    
    # LangChain
    'langchain', 'langchain_openai', 'langchain_community',
    'langchain_core',
    
    # Data processing
    'pydantic', 'dateutil', 'pytz',
    
    # HTTP clients
    'httpx', 'httpcore', 'requests', 'urllib3',
    
    # ActivityWatch
    'aw_client', 'aw_core',
    
    # Internal modules
    'baal.desktop_pet', 'baal.llm_assistant', 
    'baal.aw_stats'
]
```

### Platform-Specific Dependencies

```yaml
Windows:
  runtime:
    - Visual C++ Redistributables
    - Windows API (user32.dll, kernel32.dll)
  build:
    - PowerShell 5.0+
    - Inno Setup (optional)

macOS:
  runtime:
    - Cocoa framework
    - CoreFoundation
  build:
    - Xcode Command Line Tools
    - dmgbuild (optional)

Linux:
  runtime:
    - X11 or Wayland
    - GTK/Qt libraries
  build:
    - gcc/clang
    - make
```

## Dependency Version Constraints

### Strict Version Requirements

```yaml
Critical versions:
  PyQt6: "==6.5.3"  # Exact version for stability
  langchain: ">=0.3.26,<0.4.0"  # Minor version locked
  pydantic: ">=2.10.0,<3.0.0"  # Major version locked
```

### Flexible Version Requirements

```yaml
Flexible versions:
  aw-client: ">=0.5.13"  # Minimum version
  python-dateutil: ">=2.8.0"  # Compatible range
  requests: "*"  # Any version
```

## Dependency Resolution Order

### Initialization Sequence

```
1. Logging System (logger_config)
2. Configuration (ConfigManager)
3. Data Migration (if needed)
4. Single Instance Check
5. Qt Application
6. Resource Manager
7. Persona/Emotion Managers
8. LLM Components
9. UI Components
10. Background Services (Supervision)
```

### Shutdown Sequence

```
1. Stop background threads (Supervision, AsyncWorker)
2. Save conversation history
3. Save configuration
4. Release single instance lock
5. Cleanup Qt objects
6. Close logging handlers
```

## Performance Impact

### Heavy Dependencies

```yaml
PyQt6:
  size: "~60MB"
  load_time: "~500ms"
  memory: "~50MB baseline"

LangChain:
  size: "~20MB"
  load_time: "~200ms"
  memory: "~30MB with models"

Bundle Size Impact:
  total: "~150MB compressed"
  extracted: "~400MB"
```

### Optimization Strategies

```yaml
Lazy Loading:
  - ActivityWatch client (only when needed)
  - Calendar dialog (on first use)
  - Developer console (on demand)

Caching:
  - Resource assets
  - Configuration values
  - LLM responses

Exclusions:
  - numpy (not needed)
  - matplotlib (not needed)
  - PyQt5 (explicitly excluded)
```