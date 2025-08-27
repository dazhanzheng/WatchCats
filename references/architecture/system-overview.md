# System Architecture Overview

## Project: Baal Desktop Pet Assistant

**Version:** 1.0  
**Architecture Type:** Event-Driven Desktop Application with AI Integration  
**Primary Language:** Python 3.9+  
**UI Framework:** PyQt6  

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    User Interface Layer                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │   Pet    │ │   Chat   │ │ Settings │ │ Calendar │   │
│  │  Window  │ │  Bubble  │ │  Dialog  │ │  Dialog  │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└──────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────┐
│                     Core Services Layer                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │   LLM    │ │ Emotion  │ │ Persona  │ │  Config  │   │
│  │ Handler  │ │ Manager  │ │ Manager  │ │ Manager  │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└──────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────┐
│                    Integration Layer                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ Activity │ │ LangChain│ │ Schedule │ │Supervision│  │
│  │  Watch   │ │Assistant │ │ Manager  │ │   Mode    │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└──────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────┐
│                      Data Layer                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │  Config  │ │ Activity │ │ Schedule │ │  Memory  │   │
│  │   Files  │ │   Data   │ │   Data   │ │  Storage │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└──────────────────────────────────────────────────────────┘
```

## Core Design Patterns

### 1. Model-View-Controller (MVC) Pattern
- **Model**: Core business logic (LLMHandler, ConfigManager, StatsProcessor)
- **View**: PyQt6 UI components (PetWindow, ChatBubble, dialogs)
- **Controller**: Event handlers and signal/slot connections

### 2. Observer Pattern
- PyQt6 signals and slots for event propagation
- Asynchronous event handling for UI updates
- Decoupled component communication

### 3. Singleton Pattern
- ConfigManager: Single configuration instance
- SingleInstance: Prevents multiple app instances
- Resource managers for shared assets

### 4. Strategy Pattern
- PersonaManager: Switchable personality strategies
- EmotionManager: Dynamic emotion state handling
- Different LLM temperature settings for various tasks

### 5. Factory Pattern
- Dialog creation (settings, supervision, calendar)
- LLM instance creation with different configurations

## Key Architectural Components

### Entry Points
1. **run_desktop_pet.py**: Main entry point with environment setup
2. **baal/desktop_pet/main.py**: Application initialization
3. **baal/desktop_pet/__main__.py**: Package entry point

### Core Modules

#### UI Layer (`baal/desktop_pet/ui/`)
- **pet_window.py**: Main floating window with drag support
- **chat_bubble.py**: Resizable chat interface with streaming text
- **settings_dialog.py**: Configuration management UI
- **supervision_dialog.py**: Productivity monitoring settings
- **calendar_dialog_modern.py**: Modern calendar with 3 view modes
- **developer_console.py**: Debug and development tools
- **memory_clear_dialog.py**: Memory management interface

#### Core Services (`baal/desktop_pet/core/`)
- **llm_handler.py**: LLM interaction and streaming responses
- **config_manager.py**: Cross-platform configuration persistence
- **emotion_manager.py**: 7-state emotion system
- **persona_manager.py**: 3 personality modes with hot-swapping
- **single_instance.py**: Application instance management
- **autostart_manager.py**: System startup integration
- **preset_responses.py**: Cached response management
- **resource_manager.py**: Asset and resource handling
- **logger_config.py**: Centralized logging system

#### Integration Layer (`baal/llm_assistant/`)
- **assistant.py**: LangChain-based LLM orchestration
- **binary_intent_classifier.py**: Intent detection for queries
- **parsers.py**: Natural language to structured command parsing

#### Data Processing (`baal/aw_stats/`)
- **stats_processor.py**: ActivityWatch data analysis and aggregation

#### Supervision System (`baal/desktop_pet/supervision_mode.py`)
- Productivity monitoring and alerting
- Goal tracking and reminder system
- Threaded background monitoring

## Threading Model

### Main Thread (UI Thread)
- PyQt6 event loop
- UI updates and rendering
- User input handling
- Signal emission

### Worker Threads
1. **AsyncWorker (QThread)**: LLM streaming responses
2. **SupervisionMode Thread**: Background activity monitoring
3. **Summary Generation Thread**: Conversation summarization

### Thread Safety Mechanisms
- Qt Signal/Slot for cross-thread communication
- Threading locks for shared resource access
- Thread-safe configuration management
- Proper cleanup on application exit

## Event Flow

### User Input Processing
```
User Input → PetWindow → LLMHandler → AsyncWorker Thread
                ↓                           ↓
          Input Validation            Stream Processing
                ↓                           ↓
          Intent Classification        Token Generation
                ↓                           ↓
          Tool Selection              UI Update Signals
                ↓                           ↓
          Data Fetching               ChatBubble Update
```

### Emotion System Flow
```
LLM Response → Emotion Detection → EmotionManager
                     ↓                    ↓
              Extract Emotion Tag    Update State
                     ↓                    ↓
              Validate Emotion      Load Image Asset
                     ↓                    ↓
              Signal Emission       Update Pet Display
```

## Memory Management

### Conversation Memory
- In-memory message history with size limits
- Automatic summarization for long conversations
- Persistent storage between sessions
- Graceful degradation on memory pressure

### Resource Management
- Lazy loading of image assets
- Proper cleanup of Qt objects
- Thread termination on exit
- File handle management

## Security Considerations

### API Key Management
- Encrypted storage in user config directory
- No hardcoded credentials
- Environment variable support
- Secure key transmission

### Data Privacy
- Local data storage only
- No telemetry or tracking
- User-controlled data retention
- Explicit consent for features

## Platform-Specific Implementations

### Windows
- AppData directory for configuration
- Windows registry for autostart
- System tray integration
- PowerShell build scripts

### macOS  
- ~/Library/Application Support for config
- LaunchAgent for autostart
- Menu bar integration
- Notch-safe area handling (90px top margin)
- DMG packaging

### Linux (Planned)
- XDG config directories
- Systemd for autostart
- System tray support
- AppImage packaging

## Performance Optimizations

### Streaming Response System
- Character-by-character display
- Punctuation delays for natural reading
- Async/await for non-blocking operations
- Token buffering and batching

### Parallel Processing
- Concurrent ActivityWatch queries
- Parallel tool execution in LangChain
- Background thread for monitoring
- Asynchronous file operations

### Caching Strategies
- Preset response caching
- Configuration caching
- Resource asset caching
- LLM response memoization

## Build System

### PyInstaller Configuration
- Single-file executable generation
- Resource bundling
- Hidden import management
- Platform-specific specs

### Dependency Management
- Virtual environment isolation
- Requirements.txt for pip
- Platform-specific dependencies
- Version pinning for stability

## Error Handling Strategy

### Graceful Degradation
- Feature fallback on API failure
- Default configurations
- Offline mode support
- Recovery mechanisms

### Error Reporting
- Comprehensive logging system
- User-friendly error messages
- Debug console for developers
- Diagnostic information collection

## Scalability Considerations

### Modular Design
- Pluggable components
- Interface-based contracts
- Dependency injection
- Service locator pattern

### Future Extensions
- Plugin system architecture
- Additional LLM providers
- Custom tool integration
- Theme system support