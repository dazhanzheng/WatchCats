# 聊天功能修复说明

## 修复日期
2025-08-13

## 修复的问题

### 1. ❌ 监督提醒错误
**问题**: `AttributeError: 'PetWindow' object has no attribute '_update_bubble_position'`
**修复**: 替换为 `self.chat_bubble.set_position_relative_to(self, use_offset=True)`

### 2. ❌ 聊天按钮无切换功能
**问题**: 点击聊天按钮只能显示，不能隐藏
**修复**: 添加 `toggle` 参数实现显示/隐藏切换

### 3. ❌ 气泡不会自动隐藏
**问题**: 气泡一直显示，用户需要手动关闭
**修复**: 添加20秒自动隐藏计时器

### 4. ❌ Windows提醒无置顶
**问题**: Windows端监督提醒时窗口不会置顶
**修复**: 添加Windows特殊处理代码

## 实现细节

### 聊天切换功能

#### 1. 方法签名修改
```python
def _show_chat_bubble(self, toggle=False):
    """显示或切换对话气泡
    
    Args:
        toggle: 是否切换显示状态（True=切换，False=仅显示）
    """
```

#### 2. 右键巴利菜单
```python
def _show_context_menu(self, pos):
    # 根据气泡状态显示不同文本
    chat_text = "隐藏聊天" if self.chat_bubble.isVisible() else "聊天"
    chat_action = menu.addAction(chat_text)
    chat_action.triggered.connect(lambda: self._show_chat_bubble(toggle=True))
```

#### 3. 系统托盘菜单
```python
def _show_chat_from_tray(self):
    # 切换聊天气泡显示状态
    self._show_chat_bubble(toggle=True)
```

### 自动隐藏功能

#### 新增属性
```python
# 气泡自动隐藏计时器
self.bubble_auto_hide_timer = QTimer()
self.bubble_auto_hide_timer.timeout.connect(self._auto_hide_bubble)
self.bubble_auto_hide_timer.setSingleShot(True)  # 单次触发
```

#### 新增方法
- `_start_bubble_auto_hide_timer(timeout=20000)` - 启动计时器
- `_auto_hide_bubble()` - 执行隐藏
- `_reset_bubble_auto_hide_timer()` - 重置计时器

#### 触发时机
- 显示气泡时启动20秒计时器
- 用户交互时重置计时器
- 监督提醒时延长到30秒

### 监督提醒修复

#### Windows置顶处理
```python
if sys.platform == "win32":
    # 恢复最小化窗口
    if self.isMinimized():
        self.showNormal()
    # 激活并置顶
    self.setWindowState(...)
    self.raise_()
    self.activateWindow()
    # 使用Windows API
    ctypes.windll.user32.SetForegroundWindow(int(self.winId()))
```

## 使用说明

### 聊天切换
1. **右键巴利立绘** -> 聊天/隐藏聊天（点击切换）
2. **右键系统托盘** -> 聊天（点击切换）
3. 菜单文本根据气泡状态动态变化

### 自动隐藏
- 气泡显示后20秒无交互自动消失
- 用户点击或输入时重置计时器
- 正在流式输出时延长计时器

### 监督提醒
- 自动显示气泡和提醒消息
- Windows端窗口会置顶
- 提醒后30秒自动隐藏

## 测试脚本

```bash
# 验证修复
./venv/bin/python verify_toggle_fix.py

# 功能测试
./venv/bin/python test_chat_toggle.py
./venv/bin/python test_fixes.py
```

## 文件修改

### 修改的文件
- `/baal/desktop_pet/ui/pet_window.py`
  - 修改 `_show_chat_bubble` 方法
  - 修改 `_show_context_menu` 方法
  - 修改 `_show_chat_from_tray` 方法
  - 修改 `_on_supervision_reminder` 方法
  - 新增自动隐藏相关方法

- `/baal/desktop_pet/ui/chat_bubble.py`
  - 新增 `user_interaction` 信号
  - 在鼠标事件中触发交互信号

## 验证清单

- [x] 右键巴利 -> 聊天可以切换显示/隐藏
- [x] 右键托盘 -> 聊天可以切换显示/隐藏
- [x] 菜单文本根据状态显示"聊天"或"隐藏聊天"
- [x] 气泡20秒后自动隐藏
- [x] 用户交互时重置计时器
- [x] 监督提醒不再报错
- [x] Windows端提醒时窗口置顶

## 注意事项

1. **监督模式间隔**: 当前设置为5秒用于调试，发布前需恢复为300秒
2. **自动隐藏时间**: 默认20秒，监督提醒30秒，可根据需要调整
3. **Windows兼容**: 置顶功能仅在Windows平台生效

---
*修复完成于 2025-08-13*