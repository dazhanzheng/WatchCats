# Data Flow Documentation

## Overview
This document describes how data flows through the Baal Desktop Pet Assistant system, including user inputs, API calls, state management, and UI updates.

## Primary Data Flows

### 1. User Chat Interaction Flow

```
[User Input] → [PetWindow.send_message()]
    ↓
[Input Validation & Preprocessing]
    ↓
[LLMHandler.chat_stream()] ←→ [Conversation History]
    ↓
[Intent Classification] → [BinaryIntentClassifier]
    ↓
┌─────────────────────────────────┐
│ Intent Router                   │
├─────────────────────────────────┤
│ • Data Query → LLMAssistant     │
│ • Normal Chat → Direct Stream   │
│ • Command → Parser              │
└─────────────────────────────────┘
    ↓
[AsyncWorker Thread Processing]
    ↓
[Token Stream Generation]
    ↓
[Signal: token_received] → [ChatBubble.append_text()]
    ↓
[UI Update & Display]
```

### 2. Configuration Management Flow

```
[Application Start]
    ↓
[ConfigManager.__init__()]
    ↓
[Platform Detection]
    ↓
┌──────────────────────────────┐
│ Config Directory Selection    │
├──────────────────────────────┤
│ Windows: %APPDATA%/WatchCats │
│ macOS: ~/.baal_pet/          │
│ Linux: ~/.baal_pet/           │
└──────────────────────────────┘
    ↓
[Load config.json] ←→ [File System]
    ↓
[Merge with defaults] ← [default_config.py]
    ↓
[Data Migration Check] → [data_migration.py]
    ↓
[Configuration Ready]
    ↓
[Components Initialize with Config]
```

### 3. Emotion State Management Flow

```
[LLM Response Text]
    ↓
[Emotion Tag Detection: <#n>]
    ↓
[EmotionManager.detect_emotion()]
    ↓
[Validate Emotion ID (1-7)]
    ↓
[Map to Emotion State]
    ↓
┌────────────────────┐
│ Emotion States:    │
├────────────────────┤
│ 1,2 → happy       │
│ 3,4 → confused    │
│ 5 → normal        │
│ 6,7 → angry       │
└────────────────────┘
    ↓
[Load Emotion Asset] ← [动作表情拆分/*.png]
    ↓
[Signal: emotion_changed]
    ↓
[PetWindow.update_pet_image()]
    ↓
[UI Display Update]
```

### 4. ActivityWatch Data Flow

```
[User Query about Activity]
    ↓
[Intent Classifier: Needs Data]
    ↓
[LLMAssistant.process_query()]
    ↓
[StatsCommandParser] → [Parse to Structured Command]
    ↓
[StatsProcessor.get_stats()]
    ↓
[ActivityWatch API Call]
    ↓
┌─────────────────────────────┐
│ AW Server (localhost:5600)  │
├─────────────────────────────┤
│ • Get buckets               │
│ • Query events              │
│ • Aggregate data            │
└─────────────────────────────┘
    ↓
[Data Processing & Aggregation]
    ↓
[Format Response]
    ↓
[Stream to User]
```

### 5. Supervision Mode Data Flow

```
[Supervision Settings] → [Start Supervision]
    ↓
[SupervisionMode Thread Start]
    ↓
┌──────────────────────────────────┐
│ Monitoring Loop (every N seconds) │
└──────────────────────────────────┘
    ↓
[Fetch Recent Activity] ← [ActivityWatch]
    ↓
[Analyze Against Goals]
    ↓
[Calculate Productivity Score]
    ↓
┌────────────────────────┐
│ Decision Engine        │
├────────────────────────┤
│ • On Track → Continue  │
│ • Off Track → Alert    │
│ • Critical → Urgent    │
└────────────────────────┘
    ↓
[Generate Reminder Message]
    ↓
[Signal: reminder_needed]
    ↓
[PetWindow Display Alert]
```

### 6. Persona Switching Flow

```
[User Selects New Persona]
    ↓
[PersonaManager.set_persona()]
    ↓
[Load Persona Template]
    ↓
┌──────────────────────────┐
│ Persona Templates:       │
├──────────────────────────┤
│ • STRICT_MASTER         │
│ • SARCASTIC_BUTLER      │
│ • GENTLE_COMPANION      │
│ • CUSTOM                │
└──────────────────────────┘
    ↓
[Generate System Prompt]
    ↓
[Update LLMHandler]
    ↓
[Clear Conversation History]
    ↓
[Reinitialize with New Persona]
```

### 7. Memory Management Flow

```
[Conversation History Growth]
    ↓
[Check Message Count]
    ↓
[Threshold Exceeded?]
    ↓ Yes
[Trigger Summarization]
    ↓
[Background Thread Start]
    ↓
[Generate Summary via LLM]
    ↓
[Replace Old Messages with Summary]
    ↓
[Update conversation_memory.json]
    ↓
[Memory Optimized]
```

## State Management

### Application State

```
ApplicationState {
    config: ConfigManager
    llm_handler: LLMHandler
    persona: PersonaLevel
    emotion: EmotionState
    supervision_active: bool
    window_position: QPoint
    chat_visible: bool
    conversation_history: List[Message]
}
```

### State Transitions

#### Window State
```
Hidden → Visible: Tray icon click / Show action
Visible → Hidden: Close button / Hide action
Normal → Dragging: Mouse press on pet
Dragging → Normal: Mouse release
```

#### Chat State
```
Idle → Processing: User sends message
Processing → Streaming: LLM responds
Streaming → Idle: Response complete
Any → Error: Exception occurred
Error → Idle: Error handled
```

#### Supervision State
```
Inactive → Active: Start supervision
Active → Checking: Timer triggered
Checking → Alert: Off-track detected
Alert → Active: Alert shown
Active → Inactive: Stop supervision
```

## Data Persistence

### Configuration Files

```
~/.baal_pet/ (or platform equivalent)
├── config.json               # Main configuration
├── supervision.json          # Supervision settings
├── conversation_memory.json  # Conversation history
├── developer_config.json     # Developer settings
└── logs/                    # Application logs
```

### Data Structures

#### config.json
```json
{
  "api_key": "encrypted_key",
  "base_url": "https://api.endpoint",
  "model": "model_name",
  "persona_level": 1,
  "window_position": {"x": 100, "y": 100},
  "start_minimized": false,
  "supervision_check_interval": 300
}
```

#### supervision.json
```json
{
  "long_term_goal": "Goal description",
  "short_term_goals": ["goal1", "goal2"],
  "is_active": false,
  "updated_at": "2025-01-01T00:00:00"
}
```

#### conversation_memory.json
```json
{
  "messages": [
    {"role": "user", "content": "message"},
    {"role": "assistant", "content": "response"}
  ],
  "summary": "Previous conversation summary",
  "updated_at": "2025-01-01T00:00:00"
}
```

## API Data Flow

### LLM API Request/Response

```
Request Pipeline:
[User Input] → [Message Construction] → [Add System Prompt]
    → [Add History] → [HTTP POST to API] → [Stream Response]

Response Pipeline:
[API Stream] → [Token Reception] → [Buffer Management]
    → [Emotion Detection] → [Text Processing] → [UI Update]
```

### ActivityWatch API

```
Query Pipeline:
[Stats Request] → [Build AW Query] → [HTTP GET to AW Server]
    → [JSON Response] → [Data Processing] → [Aggregation]
    → [Format for Display]
```

## Error Recovery Flows

### API Failure Recovery

```
[API Call Failed]
    ↓
[Check Error Type]
    ↓
┌────────────────────────┐
│ Error Handler          │
├────────────────────────┤
│ • Network → Retry 3x   │
│ • Auth → Request Key   │
│ • Rate → Backoff       │
│ • Other → Fallback    │
└────────────────────────┘
    ↓
[Recovery Action]
    ↓
[Update UI with Status]
```

### Configuration Corruption Recovery

```
[Config Load Failed]
    ↓
[Backup Check]
    ↓ Exists?
[Load Backup]
    ↓ Failed?
[Load Defaults]
    ↓
[Prompt User for Critical Settings]
    ↓
[Save New Config]
```

## Performance Optimization Points

### Caching Layers

1. **Response Cache**: Frequently used responses
2. **Asset Cache**: Emotion images and animations
3. **Config Cache**: In-memory configuration
4. **Query Cache**: Recent ActivityWatch queries

### Async Operations

1. **LLM Streaming**: Non-blocking token generation
2. **File I/O**: Async configuration saves
3. **Network Calls**: Concurrent API requests
4. **UI Updates**: Batched rendering updates

## Security Data Flow

### API Key Handling

```
[User Enters API Key]
    ↓
[Validation]
    ↓
[Encryption (if enabled)]
    ↓
[Store in Config]
    ↓
[Memory Only for Runtime]
    ↓
[Never in Logs]
```

### Sensitive Data Filtering

```
[Data to Log]
    ↓
[Filter Sensitive Fields]
    ↓
[Mask API Keys]
    ↓
[Remove Personal Info]
    ↓
[Safe Logging]
```