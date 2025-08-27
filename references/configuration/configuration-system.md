# Configuration System Documentation

## Overview

The Baal Desktop Pet Assistant uses a multi-layered configuration system with platform-specific paths, default values, migration support, and developer overrides.

## Configuration Architecture

```
┌─────────────────────────────────────────┐
│         Configuration Layers            │
├─────────────────────────────────────────┤
│ 1. Hard-coded Defaults (constants.py)   │
│ 2. Default Config (default_config.py)   │
│ 3. User Config (config.json)            │
│ 4. Developer Config (developer_config)  │
│ 5. Environment Variables                │
└─────────────────────────────────────────┘
         Priority: 5 > 4 > 3 > 2 > 1
```

## Configuration Files

### Main Configuration (config.json)

**Location:**
- Windows: `%LOCALAPPDATA%\WatchCats\config.json` or `%APPDATA%\WatchCats\config.json`
- macOS: `~/.baal_pet/config.json`
- Linux: `~/.baal_pet/config.json`

**Structure:**
```json
{
  "api_key": "your-api-key",
  "base_url": "https://ark.cn-beijing.volces.com/api/v3",
  "model": "doubao-seed-1-6-flash-250715",
  "persona_level": 1,
  "window_position": {
    "x": 1200,
    "y": 100
  },
  "chat_position": {
    "x": 900,
    "y": 200
  },
  "chat_size": {
    "width": 400,
    "height": 500
  },
  "start_minimized": false,
  "auto_start": false,
  "theme": "dark",
  "language": "zh_CN",
  "supervision_check_interval": 300,
  "show_developer_menu": false,
  "enable_logging": true,
  "log_level": "INFO"
}
```

### Supervision Configuration (supervision.json)

**Location:** Same directory as config.json

**Structure:**
```json
{
  "long_term_goal": "成为全栈开发专家",
  "short_term_goals": [
    "完成React教程",
    "学习TypeScript",
    "构建个人项目"
  ],
  "productive_apps": [
    "Visual Studio Code",
    "Terminal",
    "Chrome DevTools"
  ],
  "check_interval": 300,
  "alert_threshold": 0.6,
  "updated_at": "2025-01-27T10:30:00"
}
```

### Conversation Memory (conversation_memory.json)

**Location:** Same directory as config.json

**Structure:**
```json
{
  "messages": [
    {
      "role": "system",
      "content": "System prompt..."
    },
    {
      "role": "user",
      "content": "User message"
    },
    {
      "role": "assistant",
      "content": "Assistant response"
    }
  ],
  "summary": "Previous conversation summary if messages were condensed",
  "message_count": 150,
  "updated_at": "2025-01-27T10:30:00"
}
```

### Developer Configuration (developer_config.json)

**Location:** Project root directory

**Purpose:** Override settings for development without affecting user config

**Structure:**
```json
{
  "api_key": "dev-api-key",
  "base_url": "http://localhost:8080/api",
  "model": "test-model",
  "debug_mode": true,
  "mock_responses": false,
  "log_level": "DEBUG"
}
```

## Configuration Constants

### baal/desktop_pet/core/constants.py

```python
# Window Configuration
WINDOW_SIZES = {
    'pet_window': {'width': 150, 'height': 150},
    'chat_bubble': {
        'default_width': 400,
        'default_height': 500,
        'min_width': 300,
        'min_height': 400,
        'max_width': 800,
        'max_height': 800
    }
}

# macOS Specific
MACOS_NOTCH_SAFE_AREA = 90  # pixels from top

# Timer Intervals (milliseconds)
TIMERS = {
    'response_check': 100,
    'auto_save': 60000,
    'supervision_check': 300000,
    'memory_cleanup': 1800000,
    'bubble_auto_dismiss': 30000
}

# Character Display Delays (milliseconds)
CHAR_DELAYS = {
    'normal': 50,
    'punctuation': 300,
    'newline': 200
}

# Supervision Settings
SUPERVISION = {
    'default_check_interval': 300,  # seconds
    'min_check_interval': 60,
    'max_check_interval': 3600,
    'parse_temperature': 0.1,
    'chat_temperature': 0.85,
    'alert_cooldown': 600  # seconds between alerts
}

# Memory Management
MEMORY = {
    'max_messages': 50,
    'summary_threshold': 30,
    'max_summary_length': 500
}

# API Settings
API = {
    'timeout': 30,
    'max_retries': 3,
    'retry_delay': 1,
    'stream_buffer_size': 10
}
```

### baal/desktop_pet/core/default_config.py

```python
def get_default_config() -> Dict[str, Any]:
    """
    Returns default configuration values.
    
    Returns:
        Dict with all default settings
    """
    return {
        # API Configuration
        'base_url': 'https://ark.cn-beijing.volces.com/api/v3',
        'api_key': '',
        'model': 'doubao-seed-1-6-flash-250715',
        
        # Persona Settings
        'persona_level': 1,  # STRICT_MASTER
        
        # Window Settings
        'window_position': {'x': 1200, 'y': 100},
        'chat_position': None,  # Auto-calculated
        'chat_size': {
            'width': WINDOW_SIZES['chat_bubble']['default_width'],
            'height': WINDOW_SIZES['chat_bubble']['default_height']
        },
        
        # Behavior Settings
        'start_minimized': False,
        'auto_start': False,
        'supervision_enabled': False,
        'supervision_check_interval': SUPERVISION['default_check_interval'],
        
        # UI Settings
        'theme': 'dark',
        'language': 'zh_CN',
        'show_timestamps': True,
        'show_developer_menu': False,
        
        # System Settings
        'enable_logging': True,
        'log_level': 'INFO',
        'check_updates': True,
        'anonymous_analytics': False
    }
```

## Environment Variables

### Runtime Configuration

```bash
# Development Mode
BAAL_DEV_MODE=true              # Enable development features
BAAL_DEBUG=true                 # Enable debug output

# SSL Configuration  
DISABLE_SSL_VERIFY=true         # Disable SSL verification (dev only)

# Logging
BAAL_LOG_DIR=/custom/log/path   # Custom log directory
BAAL_LOG_LEVEL=DEBUG            # Override log level

# Supervision
SUPERVISION_CHECK_INTERVAL=60   # Override check interval (seconds)

# Testing
BAAL_TEST_MODE=true            # Enable test mode
BAAL_MOCK_LLM=true             # Use mock LLM responses
```

### Build-Time Configuration

```bash
# PyInstaller
PYTHONOPTIMIZE=1               # Optimize Python bytecode
PYTHONHASHSEED=1               # Reproducible builds

# Platform-specific
MACOSX_DEPLOYMENT_TARGET=10.15 # macOS minimum version
WINDOWS_ICON_PATH=./icon.ico   # Custom icon path
```

## Configuration Management

### Loading Priority

```python
class ConfigManager:
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration with priority:
        1. Get defaults
        2. Load user config if exists
        3. Apply developer config if exists
        4. Apply environment overrides
        """
        # Start with defaults
        config = get_default_config()
        
        # Load user config
        if self.config_file.exists():
            with open(self.config_file) as f:
                user_config = json.load(f)
                config.update(user_config)
        
        # Apply developer overrides
        if self.developer_config_file.exists():
            with open(self.developer_config_file) as f:
                dev_config = json.load(f)
                config.update(dev_config)
        
        # Apply environment overrides
        config = self._apply_env_overrides(config)
        
        return config
```

### Configuration Migration

```python
def auto_migrate() -> Dict[str, Any]:
    """
    Automatic configuration migration.
    
    Migrations:
        v1 → v2: Rename 'goal' to 'long_term_goal'
        v2 → v3: Add persona_level field
        v3 → v4: Update model to latest version
    """
    
    # Check version
    if 'version' not in config:
        # v1 config
        config = migrate_v1_to_v2(config)
    
    if config['version'] == 2:
        config = migrate_v2_to_v3(config)
    
    if config['version'] == 3:
        config = migrate_v3_to_v4(config)
    
    return config
```

## Platform-Specific Behavior

### Windows Configuration

```python
def _get_windows_config_dir() -> Path:
    """
    Windows config directory selection.
    
    Priority:
        1. %LOCALAPPDATA%\WatchCats
        2. %APPDATA%\WatchCats  
        3. %USERPROFILE%\AppData\Local\WatchCats
        4. %USERPROFILE%\Documents\WatchCats
        5. %USERPROFILE%\WatchCats
    """
```

### macOS Configuration

```python
def _get_macos_config_dir() -> Path:
    """
    macOS config directory.
    
    Standard location:
        ~/.baal_pet/
    
    Alternative (if Library preferred):
        ~/Library/Application Support/WatchCats/
    """
```

## Configuration Validation

### Schema Validation

```python
from pydantic import BaseModel, Field

class APIConfig(BaseModel):
    base_url: str = Field(..., pattern=r'^https?://')
    api_key: str = Field(..., min_length=1)
    model: str = Field(...)
    
class WindowConfig(BaseModel):
    x: int = Field(..., ge=0)
    y: int = Field(..., ge=0)
    
class AppConfig(BaseModel):
    api: APIConfig
    window_position: WindowConfig
    persona_level: int = Field(..., ge=1, le=4)
```

### Runtime Validation

```python
def validate_config(config: Dict) -> Tuple[bool, List[str]]:
    """
    Validate configuration.
    
    Checks:
        - Required fields present
        - Value types correct
        - Ranges valid
        - API endpoint reachable
    
    Returns:
        (valid, errors)
    """
    errors = []
    
    # Check required fields
    if not config.get('api_key'):
        errors.append("API key is required")
    
    # Check ranges
    if not 1 <= config.get('persona_level', 1) <= 4:
        errors.append("Invalid persona level")
    
    # Check types
    if not isinstance(config.get('window_position'), dict):
        errors.append("Invalid window position")
    
    return len(errors) == 0, errors
```

## Configuration UI

### Settings Dialog Fields

```python
class SettingsDialog:
    """
    Configuration UI mapping.
    
    Tabs:
        1. API Settings
           - API Key (password field)
           - Base URL (combo box)
           - Model (combo box)
        
        2. Behavior
           - Persona (radio buttons)
           - Start minimized (checkbox)
           - Auto-start (checkbox)
        
        3. Appearance
           - Theme (combo box)
           - Language (combo box)
           - Show timestamps (checkbox)
        
        4. Advanced
           - Check interval (spin box)
           - Log level (combo box)
           - Developer mode (checkbox)
    """
```

## Security Considerations

### API Key Storage

```python
class ConfigManager:
    def _save_api_key(self, key: str) -> None:
        """
        Securely save API key.
        
        Security measures:
            - Never log the key
            - Store in user-only readable file
            - Consider encryption (future)
        """
        # Set file permissions (Unix)
        self.config_file.chmod(0o600)
        
        # Save encrypted (future enhancement)
        # encrypted = self._encrypt(key)
```

### Sensitive Data Handling

```python
SENSITIVE_FIELDS = [
    'api_key',
    'api_secret',
    'password',
    'token'
]

def sanitize_config_for_logging(config: Dict) -> Dict:
    """
    Remove sensitive data before logging.
    """
    sanitized = config.copy()
    for field in SENSITIVE_FIELDS:
        if field in sanitized:
            sanitized[field] = '***REDACTED***'
    return sanitized
```

## Configuration Best Practices

### Do's
1. Always use ConfigManager for config access
2. Validate configuration on load
3. Provide sensible defaults
4. Support environment overrides
5. Handle missing/corrupt config gracefully
6. Backup before migration

### Don'ts
1. Never hardcode configuration values
2. Don't log sensitive configuration
3. Don't modify config from multiple threads
4. Don't assume config file exists
5. Don't ignore validation errors

## Troubleshooting

### Common Issues

```yaml
Config not loading:
  - Check file permissions
  - Verify JSON syntax
  - Look for migration errors
  - Check log files

Settings not saving:
  - Verify write permissions
  - Check disk space
  - Look for file locks
  - Review error logs

API key issues:
  - Verify key format
  - Check base URL
  - Test network connectivity
  - Validate model name
```

### Reset Configuration

```bash
# Windows
del %LOCALAPPDATA%\WatchCats\config.json

# macOS/Linux
rm ~/.baal_pet/config.json

# Full reset (including memory)
rm -rf ~/.baal_pet/
```