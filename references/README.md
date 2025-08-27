# Baal Desktop Pet Assistant - Technical Reference Documentation

## Overview

This directory contains comprehensive technical documentation for the Baal Desktop Pet Assistant codebase. These references serve as the authoritative source for understanding the system's architecture, implementation details, and design decisions.

## Documentation Structure

### 📐 [Architecture](./architecture/)
- **[System Overview](./architecture/system-overview.md)** - High-level architecture, design patterns, and core components
  - Application layers and their responsibilities
  - Key architectural patterns (MVC, Observer, Singleton, Strategy, Factory)
  - Threading model and event flow
  - Platform-specific implementations
  - Build and deployment architecture

### 🔄 [Data Flow](./data-flow/)
- **[Data Flow Diagrams](./data-flow/data-flow-diagrams.md)** - How data moves through the system
  - User interaction flows
  - Configuration management flow
  - Emotion and persona state flows
  - ActivityWatch integration
  - API request/response pipelines
  - Error recovery flows

### 🔌 [APIs](./api/)
- **[Internal APIs](./api/internal-apis.md)** - Internal interfaces and contracts
  - Core service APIs (LLMHandler, ConfigManager, PersonaManager)
  - UI component APIs (PetWindow, ChatBubble, Dialogs)
  - Parser and worker thread APIs
  - External API integrations
  - Signal/slot connections
  - Error codes and handling patterns

### ⚙️ [Functions](./functions/)
- **[Core Functions](./functions/core-functions.md)** - Detailed function documentation
  - Entry point functions
  - LLM handler functions
  - Configuration management functions
  - UI component functions
  - Data processing functions
  - Utility and helper functions

### 🔗 [Dependencies](./dependencies/)
- **[Dependency Graph](./dependencies/dependency-graph.md)** - Module relationships and dependencies
  - External dependency specifications
  - Internal module dependencies
  - Build-time dependencies
  - Platform-specific requirements
  - Version constraints and compatibility

### 🎛️ [Configuration](./configuration/)
- **[Configuration System](./configuration/configuration-system.md)** - Configuration management details
  - Configuration file formats and locations
  - Environment variables
  - Default values and constants
  - Platform-specific paths
  - Security considerations

### 🔄 [Workflows](./workflows/)
- **[Business Workflows](./workflows/business-workflows.md)** - Core application workflows
  - Application startup sequence
  - User interaction workflows
  - Supervision mode operation
  - Memory management flows
  - Error handling and recovery

### 🖼️ [UI Components](./ui-components/)
- **[UI Architecture](./ui-components/ui-architecture.md)** - User interface system
  - PyQt6 component hierarchy
  - Window and dialog management
  - Event handling system
  - Animation and styling
  - Platform-specific UI adaptations

### 🤖 [LLM Integration](./llm-integration/)
- **[LLM System](./llm-integration/llm-system.md)** - AI integration documentation
  - LangChain integration
  - Streaming response system
  - Intent classification
  - Tool orchestration
  - Memory management
  - API provider configurations

## Quick Reference

### Key Classes and Their Locations

| Class | File | Purpose |
|-------|------|---------|
| `PetWindow` | `baal/desktop_pet/ui/pet_window.py` | Main application window |
| `LLMHandler` | `baal/desktop_pet/core/llm_handler.py` | LLM interaction management |
| `ConfigManager` | `baal/desktop_pet/core/config_manager.py` | Configuration management |
| `PersonaManager` | `baal/desktop_pet/core/persona_manager.py` | AI personality system |
| `EmotionManager` | `baal/desktop_pet/core/emotion_manager.py` | Emotion state management |
| `SupervisionMode` | `baal/desktop_pet/supervision_mode.py` | Productivity monitoring |
| `LLMAssistant` | `baal/llm_assistant/assistant.py` | Advanced LLM orchestration |
| `StatsProcessor` | `baal/aw_stats/stats_processor.py` | ActivityWatch data processing |

### Important Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| `config.json` | Platform-specific user directory | User settings |
| `supervision.json` | Same as config.json | Supervision settings |
| `conversation_memory.json` | Same as config.json | Chat history |
| `developer_config.json` | Project root | Developer overrides |

### Key Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `BAAL_DEV_MODE` | Enable development features | `false` |
| `BAAL_DEBUG` | Enable debug output | `false` |
| `DISABLE_SSL_VERIFY` | Disable SSL (dev only) | `false` |
| `SUPERVISION_CHECK_INTERVAL` | Supervision check interval (seconds) | `300` |
| `BAAL_LOG_DIR` | Custom log directory | Platform default |

## Navigation Guide

### For New Developers
1. Start with [System Overview](./architecture/system-overview.md) to understand the architecture
2. Review [Data Flow Diagrams](./data-flow/data-flow-diagrams.md) to see how components interact
3. Study [Business Workflows](./workflows/business-workflows.md) for application behavior

### For Debugging
1. Check [Internal APIs](./api/internal-apis.md) for interface contracts
2. Review [Core Functions](./functions/core-functions.md) for implementation details
3. Consult [Configuration System](./configuration/configuration-system.md) for settings

### For UI Development
1. Read [UI Architecture](./ui-components/ui-architecture.md) for component structure
2. Check signal/slot connections in [Internal APIs](./api/internal-apis.md)
3. Review styling and themes in the UI documentation

### For LLM/AI Work
1. Study [LLM System](./llm-integration/llm-system.md) for AI integration
2. Review persona system in [Core Functions](./functions/core-functions.md)
3. Check streaming implementation details

## Documentation Standards

### Code Examples
All code examples in this documentation:
- Are extracted from the actual codebase
- Include relevant context and comments
- Show both usage and implementation
- Include error handling patterns

### Diagrams
- Use ASCII art or Mermaid format for compatibility
- Show data flow direction clearly
- Include component boundaries
- Label all connections

### Updates
This documentation should be updated when:
- New features are added
- APIs change
- Architectural decisions are made
- Bugs reveal documentation gaps

## Version Information

**Documentation Version:** 1.0.0  
**Last Updated:** 2025-01-27  
**Codebase Version:** 1.0.0  
**Primary Maintainer:** Claude Code

## Contributing

When updating this documentation:
1. Maintain consistent formatting
2. Update the index when adding new files
3. Cross-reference related sections
4. Include code examples where helpful
5. Document both the "what" and "why"

## Additional Resources

### Internal References
- [ActivityWatch API Documentation](../baal/references/aw-api.md)
- [ActivityWatch API (Chinese)](../baal/references/aw-api-zh.md)
- [Categorization Rules](../baal/references/categorization.md)

### External Resources
- [PyQt6 Documentation](https://doc.qt.io/qtforpython-6/)
- [LangChain Documentation](https://python.langchain.com/)
- [ActivityWatch Documentation](https://docs.activitywatch.net/)

---

*This documentation is generated and maintained to provide a complete technical reference for the Baal Desktop Pet Assistant. It serves as the single source of truth for understanding the system's implementation.*