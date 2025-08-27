# UI Architecture Documentation

## Overview

The Baal Desktop Pet Assistant uses PyQt6 as its UI framework, implementing a floating pet window with chat capabilities, system tray integration, and multiple dialog components.

## UI Component Hierarchy

```
QApplication
    └── PetWindow (QWidget)
        ├── Pet Display (QLabel with QPixmap/QMovie)
        ├── Control Buttons (DraggableButton)
        ├── System Tray Icon (QSystemTrayIcon)
        ├── ChatBubble (QWidget - separate window)
        └── Dialogs
            ├── SettingsDialog (QDialog)
            ├── SupervisionDialog (QDialog)
            ├── DeveloperConsole (QDialog)
            └── MemoryClearDialog (QDialog)
```

## Core UI Components

### PetWindow

**File:** `baal/desktop_pet/ui/pet_window.py`

**Description:** Main application window displaying the pet avatar.

```python
class PetWindow(QWidget):
    """
    Main pet window - frameless, transparent, always on top.
    
    Properties:
        - Size: 150x150 pixels
        - Position: Saved/restored from config
        - Flags: Frameless, StaysOnTop, Transparent
        - Draggable: Entire window is draggable
    """
    
    # Key Attributes
    pet_label: QLabel              # Displays pet image/animation
    chat_bubble: ChatBubble        # Chat interface (separate window)
    tray_icon: QSystemTrayIcon    # System tray integration
    buttons: List[DraggableButton] # Control buttons
    
    # Signals
    summary_status_signal = pyqtSignal(str)  # Memory summary status
```

**Key Features:**
- Frameless window with transparency
- Always stays on top of other windows
- Draggable by clicking anywhere
- macOS notch-safe positioning (90px top margin)
- Emotion-based image switching
- System tray integration

**Layout Management:**
```python
def setup_ui(self):
    # Main layout
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    
    # Pet display
    self.pet_label = QLabel()
    self.pet_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(self.pet_label)
    
    # Transparent background
    self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    
    # Window flags
    self.setWindowFlags(
        Qt.WindowType.FramelessWindowHint |
        Qt.WindowType.WindowStaysOnTopHint |
        Qt.WindowType.Tool
    )
```

### ChatBubble

**File:** `baal/desktop_pet/ui/chat_bubble.py`

**Description:** Resizable chat interface with streaming text support.

```python
class ChatBubble(QWidget):
    """
    Chat bubble window with resize capabilities.
    
    Properties:
        - Default size: 400x500 pixels
        - Min size: 300x400 pixels
        - Max size: 800x800 pixels
        - Resizable: Corner grip handle
        - Auto-dismiss: 30 seconds after message
    """
    
    # Components
    chat_display: QTextEdit      # Message display area
    input_field: QLineEdit       # User input
    send_button: QPushButton     # Send message button
    resize_grip: QSizeGrip      # Resize handle
    auto_dismiss_timer: QTimer   # Auto-hide timer
```

**Features:**
- Streaming text display with character delays
- Markdown rendering support
- Auto-scrolling during message display
- Corner resize grip
- Auto-dismiss after inactivity
- Separate window from main pet

**Text Streaming Implementation:**
```python
def append_text_animated(self, text: str):
    """Append text with typing animation"""
    self.current_stream_text = ""
    for char in text:
        self.current_stream_text += char
        self.chat_display.append(char)
        
        # Apply delays
        if char in '，。！？':
            QThread.msleep(300)  # Punctuation delay
        elif char == '\n':
            QThread.msleep(200)  # Newline delay
        else:
            QThread.msleep(50)   # Normal delay
        
        # Process events to update UI
        QApplication.processEvents()
```

### DraggableButton

**File:** `baal/desktop_pet/ui/pet_window.py` (inline class)

**Description:** Movable button that can be repositioned by dragging.

```python
class DraggableButton(QPushButton):
    """
    Button that can be dragged around its parent.
    
    Features:
        - Drag threshold: 3 pixels
        - Maintains relative position
        - Click vs drag detection
    """
    
    def mouseMoveEvent(self, event):
        if self._is_dragging:
            new_pos = self.mapToParent(event.pos() - self.drag_position)
            self.move(new_pos)
```

### SettingsDialog

**File:** `baal/desktop_pet/ui/settings_dialog.py`

**Description:** Configuration interface with tabbed layout.

```python
class SettingsDialog(QDialog):
    """
    Settings dialog with multiple tabs.
    
    Tabs:
        1. API Settings - API key, model selection
        2. Behavior - Persona, auto-start
        3. Appearance - Theme, language
        4. Advanced - Developer options
    """
    
    # Tab structure
    tabs = {
        "API设置": APISettingsTab,
        "行为设置": BehaviorSettingsTab,
        "界面设置": AppearanceSettingsTab,
        "高级选项": AdvancedSettingsTab
    }
```

**Key Widgets:**
```python
# API Settings Tab
api_key_input = QLineEdit()
api_key_input.setEchoMode(QLineEdit.EchoMode.Password)

model_combo = QComboBox()
model_combo.addItems([
    "doubao-seed-1-6-flash-250715",
    "gpt-3.5-turbo",
    "gpt-4"
])

# Behavior Settings Tab
persona_radio_group = QButtonGroup()
personas = [
    QRadioButton("严厉主人"),
    QRadioButton("毒舌管家"),
    QRadioButton("温柔伴侣")
]

auto_start_checkbox = QCheckBox("开机自启动")
start_minimized_checkbox = QCheckBox("启动时最小化")
```

### SupervisionDialog

**File:** `baal/desktop_pet/ui/supervision_dialog.py`

**Description:** Productivity monitoring configuration.

```python
class SupervisionDialog(QDialog):
    """
    Supervision mode configuration dialog.
    
    Sections:
        - Long-term goal input
        - Short-term goals list
        - Productive apps selection
        - Check interval setting
        - Alert threshold slider
    """
    
    # Main components
    long_term_goal_input = QTextEdit()
    short_term_goals_list = QListWidget()
    check_interval_spin = QSpinBox()
    threshold_slider = QSlider(Qt.Orientation.Horizontal)
```

**Goal Management:**
```python
def add_short_term_goal(self):
    text, ok = QInputDialog.getText(
        self, "添加短期目标", "输入短期目标:"
    )
    if ok and text:
        self.short_term_goals_list.addItem(text)
        
def remove_selected_goal(self):
    current = self.short_term_goals_list.currentItem()
    if current:
        row = self.short_term_goals_list.row(current)
        self.short_term_goals_list.takeItem(row)
```

### DeveloperConsole

**File:** `baal/desktop_pet/ui/developer_console.py`

**Description:** Debug and development tools interface.

```python
class DeveloperConsole(QDialog):
    """
    Developer tools for debugging and testing.
    
    Features:
        - Log viewer with filtering
        - Configuration editor
        - Memory statistics
        - API test interface
        - Emotion tester
    """
    
    # Components
    log_display = QTextEdit()
    log_filter = QComboBox()  # Filter by level
    config_editor = QTextEdit()  # JSON editor
    memory_label = QLabel()  # Memory usage
    test_input = QLineEdit()  # Test commands
```

### MemoryClearDialog

**File:** `baal/desktop_pet/ui/memory_clear_dialog.py`

**Description:** Memory management interface.

```python
class MemoryClearDialog(QDialog):
    """
    Dialog for clearing conversation memory.
    
    Options:
        - Clear current session
        - Clear all history
        - Export before clearing
        - View memory usage
    """
    
    def setup_ui(self):
        # Memory info
        info_label = QLabel(f"当前对话: {self.message_count} 条消息")
        
        # Clear options
        clear_session_btn = QPushButton("清除本次会话")
        clear_all_btn = QPushButton("清除所有记录")
        export_btn = QPushButton("导出后清除")
```

## UI State Management

### Window States

```python
class WindowState(Enum):
    HIDDEN = "hidden"
    VISIBLE = "visible"
    MINIMIZED = "minimized"
    DRAGGING = "dragging"
    RESIZING = "resizing"

class UIStateManager:
    def __init__(self):
        self.pet_state = WindowState.VISIBLE
        self.chat_state = WindowState.HIDDEN
        self.current_emotion = "normal"
        self.is_typing = False
```

### Signal/Slot Connections

```python
# Main signal connections in PetWindow
def connect_signals(self):
    # Chat signals
    self.chat_bubble.message_sent.connect(self.handle_user_message)
    self.chat_bubble.closed.connect(self.on_chat_closed)
    
    # Worker signals
    self.worker.token_received.connect(self.chat_bubble.append_text)
    self.worker.emotion_detected.connect(self.update_emotion)
    self.worker.stream_finished.connect(self.on_stream_complete)
    
    # Tray signals
    self.tray_icon.activated.connect(self.on_tray_activated)
    
    # Supervision signals
    self.supervision_mode.reminder_needed.connect(self.show_reminder)
```

## Styling and Themes

### Style Sheets

```python
# Dark theme style
DARK_THEME = """
QWidget {
    background-color: #2b2b2b;
    color: #ffffff;
}

QPushButton {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    border-radius: 5px;
    padding: 5px 10px;
}

QPushButton:hover {
    background-color: #4a4a4a;
}

QTextEdit {
    background-color: #1e1e1e;
    border: 1px solid #555555;
    border-radius: 5px;
}

QLineEdit {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    border-radius: 3px;
    padding: 5px;
}
"""

# Apply theme
def apply_theme(self, theme_name: str):
    if theme_name == "dark":
        self.setStyleSheet(DARK_THEME)
    elif theme_name == "light":
        self.setStyleSheet(LIGHT_THEME)
```

## Platform-Specific UI Adjustments

### macOS Adaptations

```python
def adjust_for_macos(self):
    """macOS-specific UI adjustments"""
    # Notch avoidance
    screen_geometry = QApplication.primaryScreen().geometry()
    if self.y() < MACOS_NOTCH_SAFE_AREA:
        self.move(self.x(), MACOS_NOTCH_SAFE_AREA)
    
    # Menu bar style tray icon
    self.tray_icon.setIcon(self.get_menubar_icon())
```

### Windows Adaptations

```python
def adjust_for_windows(self):
    """Windows-specific UI adjustments"""
    # Taskbar integration
    self.setWindowFlag(Qt.WindowType.Tool, False)
    
    # DPI scaling
    QApplication.setAttribute(
        Qt.ApplicationAttribute.AA_EnableHighDpiScaling
    )
```

## Animation System

### Pet Animations

```python
class PetAnimator:
    def __init__(self, pet_label: QLabel):
        self.pet_label = pet_label
        self.base_animation = QMovie("动作表情拆分/巴力2.gif")
        self.emotion_images = {}
        
    def play_base_animation(self):
        """Play looping base animation"""
        self.pet_label.setMovie(self.base_animation)
        self.base_animation.start()
    
    def show_emotion(self, emotion: str):
        """Display static emotion image"""
        pixmap = QPixmap(f"动作表情拆分/{emotion}.png")
        self.pet_label.setPixmap(
            pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio)
        )
    
    def transition_emotion(self, from_emotion: str, to_emotion: str):
        """Smooth transition between emotions"""
        # Fade out
        self.fade_effect = QGraphicsOpacityEffect()
        self.pet_label.setGraphicsEffect(self.fade_effect)
        
        self.fade_animation = QPropertyAnimation(
            self.fade_effect, b"opacity"
        )
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        
        self.fade_animation.finished.connect(
            lambda: self.show_emotion(to_emotion)
        )
        self.fade_animation.start()
```

## Event Handling

### Mouse Events

```python
class PetWindow(QWidget):
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle window dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def contextMenuEvent(self, event):
        """Right-click context menu"""
        menu = QMenu(self)
        menu.addAction("显示对话", self.show_chat_bubble)
        menu.addAction("设置", self.show_settings)
        menu.addSeparator()
        menu.addAction("退出", self.quit_application)
        menu.exec(event.globalPos())
```

### Keyboard Events

```python
class ChatBubble(QWidget):
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_Return:
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                # Shift+Enter: New line
                self.input_field.insert('\n')
            else:
                # Enter: Send message
                self.send_message()
        elif event.key() == Qt.Key.Key_Escape:
            # Escape: Hide chat
            self.hide()
```

## Accessibility

### Screen Reader Support

```python
def setup_accessibility(self):
    """Configure accessibility features"""
    # Widget descriptions
    self.pet_label.setAccessibleName("巴利宠物")
    self.pet_label.setAccessibleDescription("显示巴利的当前表情")
    
    self.chat_bubble.input_field.setAccessibleName("消息输入框")
    self.chat_bubble.send_button.setAccessibleName("发送消息")
    
    # Keyboard navigation
    self.setTabOrder(self.input_field, self.send_button)
```

## Performance Optimizations

### UI Rendering Optimizations

```python
class OptimizedUI:
    def __init__(self):
        # Enable OpenGL rendering
        QApplication.setAttribute(
            Qt.ApplicationAttribute.AA_UseOpenGLES
        )
        
        # Buffer updates
        self.update_buffer = []
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.flush_updates)
        self.update_timer.start(16)  # 60 FPS
    
    def buffer_update(self, update_func):
        """Buffer UI updates for batch processing"""
        self.update_buffer.append(update_func)
    
    def flush_updates(self):
        """Process buffered updates"""
        for update in self.update_buffer:
            update()
        self.update_buffer.clear()
```

### Resource Management

```python
class UIResourceManager:
    def __init__(self):
        self._image_cache = {}
        self._icon_cache = {}
    
    def get_image(self, path: str) -> QPixmap:
        """Get cached image"""
        if path not in self._image_cache:
            self._image_cache[path] = QPixmap(path)
        return self._image_cache[path]
    
    def clear_cache(self):
        """Clear resource caches"""
        self._image_cache.clear()
        self._icon_cache.clear()
```

## Testing UI Components

### Unit Testing Strategy

```python
def test_pet_window_creation():
    """Test PetWindow initialization"""
    app = QApplication([])
    window = PetWindow()
    
    assert window.windowFlags() & Qt.WindowType.FramelessWindowHint
    assert window.windowFlags() & Qt.WindowType.WindowStaysOnTopHint
    assert window.size() == QSize(150, 150)

def test_chat_bubble_text_streaming():
    """Test streaming text display"""
    bubble = ChatBubble()
    test_text = "Hello, World!"
    
    bubble.append_text_animated(test_text)
    assert bubble.chat_display.toPlainText().endswith(test_text)
```