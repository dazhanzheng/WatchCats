"""
桌宠主窗口

显示桌宠图片、对话气泡和控制按钮
"""

import os
import sys
import asyncio
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QMenu, QSystemTrayIcon,
                             QApplication, QLineEdit, QMessageBox, QDialog)
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal, QThread
from ..core.constants import TIMERS, WINDOW_SIZES, MACOS_NOTCH_SAFE_AREA, get_timer_interval
from PyQt6.QtGui import QPixmap, QPainter, QIcon, QCursor, QAction, QMovie
from typing import Optional


class DraggableButton(QPushButton):
    """可拖动的按钮"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.drag_position = None
        self.parent_window = parent
        self.relative_pos = QPoint()  # 相对于父窗口的位置
        self._is_dragging = False
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 记录鼠标按下的位置
            self.drag_position = event.pos()
            self._is_dragging = False
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            # 检查是否移动了足够的距离来触发拖动
            if not self._is_dragging:
                distance = (event.pos() - self.drag_position).manhattanLength()
                if distance < 3:  # 3像素的阈值
                    return
                self._is_dragging = True
            
            # 计算新位置
            new_pos = self.mapToParent(event.pos() - self.drag_position)
            self.move(new_pos)
            # 更新相对位置
            if self.parent_window:
                self.relative_pos = new_pos
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            if not self._is_dragging:
                # 如果没有拖动，则触发点击
                self.clicked.emit()
            self.drag_position = None
            self._is_dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def enterEvent(self, event):
        """鼠标进入事件"""
        super().enterEvent(event)
        # 确保按钮保持可见
        self.setVisible(True)

from .chat_bubble import ChatBubble
from .settings_dialog import SettingsDialog
from .supervision_dialog import SupervisionDialog, SupervisionStatusWidget
from .developer_console import DeveloperConsole
from .memory_clear_dialog import MemoryClearDialog
from ..core import ConfigManager, LLMHandler
from ..core.persona_manager import PersonaLevel, PersonaManager
from ..core.emotion_manager import EmotionManager
from ..core.preset_responses import PresetResponseManager
from ..core.dynamic_dialogue_generator import (
    DynamicDialogueGenerator, 
    DialogueContext,
    get_dialogue_generator
)
from ..core.proactive_dialogue_manager import get_dialogue_manager, DialogueType
from ..core.logger_config import get_logger, log_performance, log_ui_event
from ..supervision_mode import SupervisionMode


class AsyncWorker(QThread):
    """异步工作线程"""
    
    # 信号
    token_received = pyqtSignal(str)
    stream_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    status_changed = pyqtSignal(str)  # 新增状态变化信号
    emotion_detected = pyqtSignal(str)  # 表情检测信号
    
    def __init__(self, llm_handler: LLMHandler):
        super().__init__()
        self.llm_handler = llm_handler
        self.user_input = ""
        self.is_running = False
        self.current_text = ""  # 累积的文本
        self.emotion_manager = EmotionManager()
        
        # 设置状态回调
        self.llm_handler.set_status_callback(self._emit_status)
    
    def _emit_status(self, status: str):
        """线程安全的状态发射"""
        self.status_changed.emit(status)
    
    def set_input(self, user_input: str):
        """设置用户输入"""
        self.user_input = user_input
    
    def run(self):
        """运行异步任务"""
        self.is_running = True
        
        # 确保清理旧的事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.close()
        except RuntimeError:
            pass
        
        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._process_stream())
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            loop.close()
            asyncio.set_event_loop(None)  # 清除事件循环引用
            self.is_running = False
    
    async def _process_stream(self):
        """处理流式输出"""
        try:
            self.current_text = ""  # 重置累积文本
            emotion_buffer = ""  # 用于缓存可能的表情标记
            emotion_detected = False  # 标记是否已检测到表情
            
            async for token in self.llm_handler.chat_stream(self.user_input):
                if not self.is_running:
                    break
                    
                # 累积文本
                self.current_text += token
                
                # 如果正在构建表情标记
                if emotion_buffer or token == '<':
                    emotion_buffer += token
                    
                    # 检查是否完成了一个表情标记
                    if '>' in emotion_buffer:
                        # 提取完整的表情标记
                        import re
                        match = re.match(r'(<#\d+>)', emotion_buffer)
                        if match:
                            emotion_tag = match.group(1)
                            if not emotion_detected:  # 只发送第一个检测到的表情
                                self.emotion_detected.emit(emotion_tag)
                                emotion_detected = True
                            # 清空缓冲区，继续处理剩余部分
                            remaining = emotion_buffer[len(emotion_tag):]
                            emotion_buffer = ""
                            if remaining:
                                self.token_received.emit(remaining)
                        else:
                            # 不是有效的表情标记，发送缓冲内容
                            self.token_received.emit(emotion_buffer)
                            emotion_buffer = ""
                else:
                    # 正常文本，直接发送
                    self.token_received.emit(token)
                
            self.stream_finished.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def stop(self):
        """停止线程"""
        self.is_running = False


class PetWindow(QWidget):
    """桌宠主窗口"""
    
    # 添加总结相关信号
    summary_status_signal = pyqtSignal(str)
    
    # 添加动态对话生成信号（线程安全）
    dialogue_generated_signal = pyqtSignal(str, str)  # (dialogue_text, context_type)
    dialogue_status_signal = pyqtSignal(str)  # status: "thinking" or "normal"
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        self.logger = get_logger('baal.desktop_pet.ui.pet_window')
        self.logger.info("Initializing PetWindow")
        
        # 配置管理器
        self.config_manager = ConfigManager()
        # ConfigManager初始化
        
        # 表情管理器
        try:
            self.emotion_manager = EmotionManager()
            # EmotionManager初始化
        except Exception as e:
            self.logger.error(f"Failed to initialize EmotionManager: {e}", exc_info=True)
            raise
        
        # 人设管理器
        try:
            from ..core.persona_manager import PersonaLevel
            # 从配置中获取人设级别
            config = self.config_manager.get_config()
            persona_level_value = config.get('persona_level', 1)  # 默认为严厉主人档
            persona_level = PersonaLevel(persona_level_value)
            self.persona_manager = PersonaManager(initial_level=persona_level)
            # PersonaManager初始化
        except Exception as e:
            self.logger.error(f"Failed to initialize PersonaManager: {e}", exc_info=True)
            # 使用默认人设
            self.persona_manager = PersonaManager()
            # 使用默认人设初始化
        
        # LLM处理器
        self.llm_handler = None
        self.async_worker = None
        # LLM处理器和异步工作线程占位符
        
        # 窗口拖动相关
        self.drag_position = None
        
        # 双击计数器
        self.double_click_count = 0
        
        # 当前表情
        self.current_emotion = "<#5>"  # 默认正常表情
        self.current_emotion_pixmap = self.emotion_manager.get_emotion_pixmap("<#5>")
        
        # 表情恢复计时器
        self.emotion_reset_timer = QTimer()
        self.emotion_reset_timer.timeout.connect(self._reset_emotion_to_default)
        self.emotion_reset_timer.setSingleShot(True)  # 单次触发
        
        # 是否已经显示过欢迎消息
        self._welcome_shown = False
        
        # 基础动画
        self.base_animation = self.emotion_manager.get_base_animation()
        if self.base_animation:
            self.base_animation.frameChanged.connect(self.update)
            self.base_animation.start()
        
        # 初始化新功能组件
        try:
            # 传入persona_manager以保持人设一致性
            self.supervision_mode = SupervisionMode(persona_manager=self.persona_manager)
            # 高级功能初始化
            
            # 初始化动态对话生成器
            self.dialogue_generator = None  # 将在LLM初始化后设置
        except Exception as e:
            self.logger.error(f"Failed to initialize advanced features: {e}", exc_info=True)
            # Continue without advanced features
        
        # 初始化开发者控制台（在初始化时不创建，只在需要时创建）
        self.developer_console = None
        
        # 气泡自动隐藏计时器
        self.bubble_auto_hide_timer = QTimer()
        self.bubble_auto_hide_timer.timeout.connect(self._auto_hide_bubble)
        self.bubble_auto_hide_timer.setSingleShot(True)  # 单次触发
        
        # 初始化主动对话管理器
        self.dialogue_manager = get_dialogue_manager()
        self.dialogue_manager.trigger_dialogue.connect(self._on_proactive_dialogue)
        self.dialogue_manager.initialize_aw_client()  # 初始化AW客户端
        
        # 从配置中加载人设并应用到主动对话管理器
        from ..core.persona_manager import PersonaLevel
        from ..core.proactive_dialogue_manager import update_persona_in_dialogue_manager
        config = self.config_manager.get_config()
        persona_level = config.get('persona_level', PersonaLevel.STRICT_MASTER.value)
        try:
            update_persona_in_dialogue_manager(PersonaLevel(persona_level))
            self.logger.info(f"Applied persona level {persona_level} to dialogue manager")
        except Exception as e:
            self.logger.warning(f"Failed to apply persona to dialogue manager: {e}")
        
        self.logger.info("Proactive dialogue manager initialized")
        
        # 连接信号
        self.supervision_mode.reminder_needed.connect(self._on_supervision_reminder)
        self.supervision_mode.mode_changed.connect(self._on_supervision_mode_changed)
        
        # 初始化UI
        self._init_ui()
        
        # 初始化系统托盘
        self._init_tray()
        
        
        # 连接总结状态信号
        self.summary_status_signal.connect(self._handle_summary_status)
        
        # 连接动态对话生成信号（线程安全）
        self.dialogue_generated_signal.connect(self._handle_dialogue_generated)
        self.dialogue_status_signal.connect(self._handle_dialogue_status)
        
        # 加载位置（如果没有保存的位置，则使用右下角）
        self._load_position()
        
        # 检查配置并初始化LLM
        self._check_and_init_llm()
        
        # 不在这里显示欢迎消息，等窗口真正显示时再显示
        self.logger.info("PetWindow initialization completed")
    
    @log_ui_event("ui_init")
    def _init_ui(self):
        """初始化UI"""
        self.logger.info("Initializing UI components")
        
        # 设置窗口属性（根据配置决定是否置顶）
        self._update_window_flags()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.logger.debug("Window flags and attributes set")
        
        # 设置窗口图标 - 使用 baallogo.png
        icon_paths = [
            Path(__file__).parent.parent.parent / "resources" / "baallogo.png",
            Path(__file__).parent.parent.parent / "resources" / "cat.png"
        ]
        for icon_path in icon_paths:
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
                break
        
        # 获取宠物大小设置
        pet_size = self.config_manager.get_config().get('pet_size', 120)
        window_size = pet_size + 30  # 为设置按钮留出空间
        
        # 设置窗口大小
        self.setFixedSize(window_size, window_size)
        
        # 使用gif作为基础图片（如果动画不可用，则加载静态图片）
        if not self.base_animation:
            self.pet_pixmap = self._load_pet_image()
        else:
            self.pet_pixmap = None  # 使用动画时不需要静态图片
        
        # 创建独立的对话气泡（不作为子窗口）
        try:
            self.chat_bubble = ChatBubble()
            self.chat_bubble.next_sentence_requested.connect(self._on_next_sentence_requested)
            self.chat_bubble.message_sent.connect(self._on_bubble_message_sent)
            self.chat_bubble.user_interaction.connect(self._reset_bubble_auto_hide_timer)
            
            # 应用当前的置顶设置到气泡窗口
            config = self.config_manager.get_config()
            always_on_top = config.get('always_on_top', True)
            self._update_chat_bubble_flags(always_on_top)
            
            # 聊天气泡初始化和连接
        except Exception as e:
            self.logger.error(f"Failed to initialize chat bubble: {e}", exc_info=True)
            raise
        
        # 创建设置按钮（可拖动）
        self.settings_btn = DraggableButton("⚙", self)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #ccc;
                border-radius: 15px;
                width: 30px;
                height: 30px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 255);
                border: 1px solid #999;
            }
            QPushButton:pressed {
                background-color: rgba(240, 240, 240, 255);
            }
        """)
        self.settings_btn.clicked.connect(self._show_settings)
        self.settings_btn.setToolTip("点击打开设置\n拖动可调整位置")
        # 确保设置按钮在最上层
        self.settings_btn.raise_()
        
        # 创建监督模式开关按钮（可拖动）
        self.supervision_btn = DraggableButton("👁", self)
        self._update_supervision_button_style()
        self.supervision_btn.clicked.connect(self._quick_toggle_supervision)
        self.supervision_btn.setToolTip("点击开关监督模式\n长按打开设置")
        # 确保监督按钮在最上层
        self.supervision_btn.raise_()
        
        # 不再需要输入框，已移至气泡窗口
        # self.input_field = QLineEdit(self)
        # self.input_field.hide()
        
        # 布局设置按钮（更靠近猫）
        default_pos = QPoint(self.width() - 40, self.height() - 40)
        self.settings_btn.move(default_pos)
        self.settings_btn.relative_pos = default_pos
        
        # 布局监督模式按钮（在设置按钮左边）
        supervision_pos = QPoint(self.width() - 75, self.height() - 40)
        self.supervision_btn.move(supervision_pos)
        self.supervision_btn.relative_pos = supervision_pos
        
        # 初始隐藏按钮
        self.settings_btn.setVisible(False)
        self.supervision_btn.setVisible(False)
        self.settings_btn.setStyleSheet(self.settings_btn.styleSheet() + """
            QPushButton {
                opacity: 0.8;
            }
        """)
        self.logger.debug("UI initialization completed")
    
    def _load_pet_image(self) -> QPixmap:
        """加载桌宠图片（用作后备）"""
        # 如果gif加载失败，使用静态图片作为后备
        image_path = Path(__file__).parent.parent.parent / "resources" / "cat.png"
        
        if image_path.exists():
            # 加载原始图片
            pixmap = QPixmap(str(image_path))
            
            # 获取配置中的宠物大小（如果有）
            pet_size = self.config_manager.get_config().get('pet_size', 120)
            
            # 使用高质量缩放算法，保持宽高比
            return pixmap.scaled(pet_size, pet_size, 
                               Qt.AspectRatioMode.KeepAspectRatio, 
                               Qt.TransformationMode.SmoothTransformation)
        else:
            # 创建默认图片
            pet_size = self.config_manager.get_config().get('pet_size', 120)
            pixmap = QPixmap(pet_size, pet_size)
            pixmap.fill(Qt.GlobalColor.transparent)
            return pixmap
    
    @log_ui_event("emotion_change")
    def _update_emotion(self, emotion_tag: str):
        """更新当前表情"""
        if emotion_tag and emotion_tag != self.current_emotion:
            old_emotion = self.current_emotion
            self.current_emotion = emotion_tag
            self.current_emotion_pixmap = self.emotion_manager.get_emotion_pixmap(emotion_tag)
            self.update()  # 触发重绘
            
            # 重置表情恢复计时器（20秒后恢复到默认表情，与气泡相同）
            self.emotion_reset_timer.stop()
            self.emotion_reset_timer.start(20000)  # 20秒，与气泡自动隐藏时间一致
            
            self.logger.info(f"Emotion changed from {old_emotion} to {emotion_tag}")
        elif emotion_tag == self.current_emotion:
            self.logger.debug(f"Emotion unchanged: {emotion_tag}")
        else:
            self.logger.debug(f"Invalid emotion tag received: {emotion_tag}")
    
    def _reset_emotion_to_default(self):
        """恢复到默认表情"""
        default_emotion = self.emotion_manager.get_default_emotion()
        if self.current_emotion != default_emotion:
            self.logger.info(f"Resetting emotion to default: {default_emotion}")
            self.current_emotion = default_emotion
            self.current_emotion_pixmap = self.emotion_manager.get_emotion_pixmap(default_emotion)
            self.update()  # 触发重绘
    
    @log_ui_event("tray_init")
    def _init_tray(self):
        """初始化系统托盘"""
        self.logger.info("Initializing system tray")
        
        # 检查系统托盘是否可用
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.logger.warning("System tray not available")
            return
        
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        
        # 设置图标 - 优先使用 baallogo.png
        icon_paths = [
            Path(__file__).parent.parent.parent / "resources" / "baallogo.png",
            Path(__file__).parent.parent.parent / "resources" / "cat.png"
        ]
        
        icon_set = False
        for icon_path in icon_paths:
            if icon_path.exists():
                self.tray_icon.setIcon(QIcon(str(icon_path)))
                icon_set = True
                break
        
        if not icon_set:
            # Windows和Mac使用不同的默认图标
            if sys.platform == "win32":
                self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
            else:
                self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        
        # 设置托盘图标提示
        self.tray_icon.setToolTip("巴利监管者 - 点击召唤")
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        # 显示/隐藏桌宠
        self.toggle_action = tray_menu.addAction("显示桌宠")
        self.toggle_action.triggered.connect(self._toggle_visibility)
        
        tray_menu.addSeparator()
        
        # 重置位置
        reset_position_action = tray_menu.addAction("重置窗口位置")
        reset_position_action.triggered.connect(self._reset_position)
        
        # 始终置顶
        self.always_on_top_action = tray_menu.addAction("始终置顶")
        self.always_on_top_action.setCheckable(True)
        config = self.config_manager.get_config()
        self.always_on_top_action.setChecked(config.get('always_on_top', True))  # 默认开启
        self.always_on_top_action.triggered.connect(self._toggle_always_on_top)
        
        # 启动选项
        self.start_minimized_action = tray_menu.addAction("启动时最小化到托盘")
        self.start_minimized_action.setCheckable(True)
        self.start_minimized_action.setChecked(config.get('start_minimized', False))
        self.start_minimized_action.triggered.connect(self._toggle_start_minimized)
        
        # 设置
        settings_action = tray_menu.addAction("设置")
        settings_action.triggered.connect(self._show_settings)
        
        # 开发者模式（可通过配置控制显示）
        config = self.config_manager.get_config()
        show_developer_mode = config.get('show_developer_mode', True)  # 默认显示
        if show_developer_mode:
            developer_action = tray_menu.addAction("开发者控制台")
            developer_action.triggered.connect(self._show_developer_console)
        
        tray_menu.addSeparator()
        
        # 退出
        quit_action = tray_menu.addAction("退出程序")
        quit_action.triggered.connect(self._quit_application)
        
        self.tray_icon.setContextMenu(tray_menu)
        
        # 双击托盘图标显示/隐藏
        self.tray_icon.activated.connect(self._on_tray_activated)
        
        # 显示托盘图标
        self.tray_icon.show()
        
        # Windows特殊处理：确保托盘图标可见
        if sys.platform == "win32":
            self.tray_icon.setVisible(True)
            
        self.logger.info("System tray initialized successfully")
    
    def _load_position(self):
        """加载窗口位置"""
        # 尝试从配置加载位置
        pos = self.config_manager.get_window_position()
        
        # 获取屏幕信息
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        
        # 如果没有保存的位置或位置为默认值，设置到右下角
        if pos['x'] == 100 and pos['y'] == 100:  # 默认值
            self._move_to_bottom_right()
        else:
            # 验证位置是否在屏幕内
            x = pos['x']
            y = pos['y']
            
            # 确保窗口不会超出屏幕边界
            # 左边界和上边界
            x = max(0, x)
            y = max(0, y)
            
            # macOS: 避开刘海屏区域（顶部90像素）
            if sys.platform == "darwin" and y < 90:
                y = 90
                print(f"[INFO] 避开刘海屏区域，Y坐标调整到 {y}")
            
            # 右边界和下边界（确保至少有50像素在屏幕内）
            x = min(x, screen_rect.width() - 50)
            y = min(y, screen_rect.height() - 50)
            
            # 如果窗口完全在屏幕外，重置到右下角
            if x < 0 or y < 0 or x > screen_rect.width() or y > screen_rect.height():
                self._move_to_bottom_right()
            else:
                self.move(x, y)
    
    def _move_to_bottom_right(self):
        """将窗口移动到屏幕右下角"""
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        
        # 获取屏幕的实际可用区域（考虑菜单栏和 Dock）
        # availableGeometry() 已经排除了菜单栏和 Dock
        
        # 计算右下角位置（留出一些边距）
        margin = 20  # 边距
        x = screen_rect.x() + screen_rect.width() - self.width() - margin
        y = screen_rect.y() + screen_rect.height() - self.height() - margin
        
        # 确保位置有效
        x = max(screen_rect.x(), x)
        y = max(screen_rect.y(), y)
        
        print(f"[DEBUG] 移动窗口到: ({x}, {y})")
        print(f"[DEBUG] 屏幕可用区域: {screen_rect}")
        print(f"[DEBUG] 窗口大小: {self.width()}x{self.height()}")
        
        self.move(x, y)
    
    def _save_position(self):
        """保存窗口位置"""
        pos = self.pos()
        self.config_manager.set_window_position(pos.x(), pos.y())
    
    def _check_and_init_llm(self):
        """检查配置并初始化LLM"""
        self.logger.info("Checking and initializing LLM")
        
        if self.config_manager.is_configured():
            try:
                # 配置找到，初始化LLM处理器
                # 获取配置中的人设级别
                config = self.config_manager.get_config()
                persona_level_value = config.get('persona_level', 1)  # 默认为严厉主人档
                persona_level = PersonaLevel(persona_level_value)
                
                self.llm_handler = LLMHandler(
                    base_url=self.config_manager.get_base_url(),
                    api_key=self.config_manager.get_api_key(),
                    model=self.config_manager.get_model(),
                    persona_level=persona_level
                )
                
                # 初始化动态对话生成器
                self.dialogue_generator = get_dialogue_generator(self.llm_handler)
                
                # 设置字符延迟（如果配置中有）
                config = self.config_manager.get_config()
                if 'char_delays' in config:
                    delays = config['char_delays']
                    self.llm_handler.set_char_delays(
                        normal=delays.get('normal', 0.02),
                        punctuation=delays.get('punctuation', 0.08),
                        newline=delays.get('newline', 0.05)
                    )
                
                # 创建异步工作线程
                self.async_worker = AsyncWorker(self.llm_handler)
                self.async_worker.token_received.connect(self._on_token_received)
                self.async_worker.stream_finished.connect(self._on_stream_finished)
                self.async_worker.error_occurred.connect(self._on_error_occurred)
                self.async_worker.status_changed.connect(self.chat_bubble.set_status)  # 连接状态信号
                self.async_worker.emotion_detected.connect(self._update_emotion)  # 连接表情检测信号
                
                # 设置总结状态回调
                self.llm_handler.set_summary_status_callback(self._on_summary_status)
                
                self.logger.info("LLM handler initialized successfully")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize LLM: {e}", exc_info=True)
        else:
            self.logger.warning("LLM not configured - no API key or configuration found")
    
    @log_ui_event("welcome_message")
    def _show_welcome_message(self):
        """显示欢迎消息"""
        self.logger.info("Showing welcome message")
        
        # 检查是否有历史对话记录
        if self.config_manager.is_configured():
            if self.llm_handler and self.llm_handler.has_conversation_history():
                # 有历史记录，显示回归消息
                welcome_msg = self._get_return_greeting()
                self.logger.info("User has conversation history, showing return greeting")
            else:
                # 没有历史记录，使用动态生成欢迎消息
                welcome_msg = "<#5>..."
                self.logger.info("New user, showing welcome message")
            
            # 从消息中提取表情并更新
            if welcome_msg.startswith("<#"):
                emotion_match = welcome_msg[:4]  # 提取 <#n> 格式
                self._update_emotion(emotion_match)
                # 移除表情标记后显示消息
                welcome_msg = welcome_msg[4:].strip()
        else:
            welcome_msg = "契约未成立。设置你的密钥，否则本座可没兴趣理会你。"
            self.logger.info("API not configured, showing configuration prompt")
        
        # 显示加载动画
        self.chat_bubble.set_status("thinking")
        self.chat_bubble.show_message(welcome_msg)
        # 设置气泡位置（使用默认位置）
        self.chat_bubble.set_position_relative_to(self, use_offset=False)
        # 启动30秒自动隐藏计时器
        self._start_bubble_auto_hide_timer(30000)
        
        # 定义线程安全的回调函数
        def on_welcome_generated(msg):
            # 通过信号发送到主线程
            self.dialogue_generated_signal.emit(msg, "WELCOME_STARTUP")
        
        # 动态生成欢迎消息
        if self.dialogue_generator:
            self.dialogue_generator.generate(
                context=DialogueContext.WELCOME,
                persona=self.persona_manager.current_level,
                callback=on_welcome_generated
            )
        else:
            self.dialogue_generated_signal.emit("<#5>我是巴利，你的监督者。", "WELCOME_STARTUP")  # 30秒后自动隐藏
    
    def _get_return_greeting(self):
        """获取用户回归时的问候语"""
        import random
        from ..core.persona_manager import PersonaLevel
        
        # 根据不同人设返回不同的回归问候
        if self.persona_manager.current_level == PersonaLevel.STRICT_MASTER:
            greetings = [
                "<#5>回来了？继续你的工作。",
                "<#4>休息够了？立刻开始工作。",
                "<#5>你离开了多久？报告你的进度。",
                "<#3>终于回来了。我一直在等你。"
            ]
        elif self.persona_manager.current_level == PersonaLevel.SARCASTIC_BUTLER:
            greetings = [
                "<#3>哦呀，主人回来了。'忙碌'的一天呢？",
                "<#5>欢迎回来。希望您的'效率'有所提升。",
                "<#4>主人归来了。期待您今天的'表现'。",
                "<#2>回来了？在下一直在'耐心'等待。"
            ]
        else:  # GENTLE_COMPANION
            greetings = [
                "<#1>欢迎回来！我想你了～",
                "<#2>你回来啦！今天过得怎么样？",
                "<#1>嗨！很高兴再次见到你！",
                "<#2>欢迎回来，亲爱的！我们继续努力吧！"
            ]
        
        return random.choice(greetings)
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter()
        if not painter.begin(self):
            return
            
        try:
            # 设置高质量渲染
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
            
            # 绘制基础图片（动画或静态）
            if self.base_animation and self.base_animation.state() == QMovie.MovieState.Running:
                # 绘制当前动画帧
                current_pixmap = self.base_animation.currentPixmap()
                if not current_pixmap.isNull():
                    # 缩放到合适大小
                    pet_size = self.config_manager.get_config().get('pet_size', 120)
                    scaled_pixmap = current_pixmap.scaled(
                        pet_size, pet_size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    x = (self.width() - scaled_pixmap.width()) // 2
                    y = (self.height() - scaled_pixmap.height()) // 2
                    painter.drawPixmap(x, y, scaled_pixmap)
            elif self.pet_pixmap:
                # 绘制静态图片
                x = (self.width() - self.pet_pixmap.width()) // 2
                y = (self.height() - self.pet_pixmap.height()) // 2
                painter.drawPixmap(x, y, self.pet_pixmap)
            
            # 绘制表情（叠加在基础图片上）
            if self.current_emotion_pixmap and not self.current_emotion_pixmap.isNull():
                # 表情已经是对齐好的大小，直接绘制
                pet_size = self.config_manager.get_config().get('pet_size', 120)
                scaled_emotion = self.current_emotion_pixmap.scaled(
                    pet_size, pet_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                x = (self.width() - scaled_emotion.width()) // 2
                y = (self.height() - scaled_emotion.height()) // 2
                painter.drawPixmap(x, y, scaled_emotion)
        finally:
            painter.end()
    
    def enterEvent(self, event):
        """鼠标进入事件"""
        super().enterEvent(event)
        # 显示设置按钮和监督按钮
        self.settings_btn.setVisible(True)
        self.supervision_btn.setVisible(True)
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        super().leaveEvent(event)
        # 延迟隐藏按钮（给用户时间移动到按钮上）
        QTimer.singleShot(get_timer_interval('hide_buttons_check'), self._check_hide_buttons)
    
    def _check_hide_buttons(self):
        """检查是否需要隐藏按钮"""
        # 如果鼠标不在窗口内且不在按钮内，则隐藏
        if not self.underMouse() and not self.settings_btn.underMouse() and not self.supervision_btn.underMouse():
            self.settings_btn.setVisible(False)
            self.supervision_btn.setVisible(False)
    
    @log_ui_event("mouse_press")
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查是否点击在设置按钮上
            if self.settings_btn.geometry().contains(event.pos()):
                # 如果是设置按钮，让按钮处理点击事件
                self.logger.debug("Left click on settings button")
                return
            # 记录拖动位置
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.logger.debug("Left mouse pressed, drag initiated")
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            # 右键显示菜单
            self.logger.debug("Right mouse pressed, showing context menu")
            self._show_context_menu(event.globalPosition().toPoint())
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            # 移动窗口
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.move(new_pos)
            
            # 如果气泡可见，同步移动气泡（保持相对位置）
            if self.chat_bubble.isVisible():
                self.chat_bubble.set_position_relative_to(self)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = None
            self._save_position()
    
    @log_ui_event("double_click")
    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 双击左键直接唤出聊天窗口
            self.logger.info("Double click event - showing chat bubble")
            
            # 通知对话管理器有用户活动
            self.dialogue_manager.on_user_activity()
            
            # 使用状态感知系统
            from ..core.state_awareness import get_state_awareness
            from ..core.state_update_manager import get_update_manager
            state_system = get_state_awareness()
            update_manager = get_update_manager()
            
            # 获取互动状态
            interaction_state = state_system.get_interaction_state()
            
            # 触发互动事件
            update_manager.trigger_event("intense_interaction")
            
            # 根据时间选择合适的招呼语
            from datetime import datetime
            hour = datetime.now().hour
            
            # 映射互动状态到招呼语类型
            greeting_map = {
                "first_meet": "welcome",
                "long_time_no_see": "long_time_no_see",
                "frequent_interaction": "frequent_interaction",
                "regular_interaction": "double_click_greeting"
            }
            
            # 优先使用时间相关的招呼语
            if 5 <= hour < 9:
                greeting_type = "morning_greeting"
            elif 22 <= hour < 24 or 0 <= hour < 2:
                greeting_type = "late_night_care"
            else:
                # 使用互动状态对应的招呼语
                greeting_type = greeting_map.get(interaction_state, "double_click_greeting")
            
            # 确定对话场景
            if greeting_type == "morning_greeting":
                dialogue_context = DialogueContext.MORNING_GREETING
            elif greeting_type == "late_night_care":
                dialogue_context = DialogueContext.LATE_NIGHT
            elif greeting_type == "long_time_no_see":
                dialogue_context = DialogueContext.LONG_TIME_NO_SEE
            elif greeting_type == "frequent_interaction":
                dialogue_context = DialogueContext.FREQUENT_INTERACTION
            else:
                dialogue_context = DialogueContext.DOUBLE_CLICK
            
            # 显示聊天窗口
            if not self.chat_bubble.isVisible():
                self.chat_bubble.show()
                self.chat_bubble.raise_()
                self.chat_bubble.set_position_relative_to(self, use_offset=True)
                self._start_bubble_auto_hide_timer()
            
            # 显示加载动画
            self.dialogue_status_signal.emit("thinking")
            self.chat_bubble.show_message("<#5>...")
            
            # 定义线程安全的回调函数
            def on_greeting_generated(greeting):
                # 通过信号发送到主线程
                self.dialogue_generated_signal.emit(greeting, greeting_type)
                self.logger.info(f"Dynamic greeting generated for {greeting_type}")
            
            # 使用动态对话生成器
            if self.dialogue_generator:
                self.dialogue_generator.generate(
                    context=dialogue_context,
                    persona=self.persona_manager.current_level,
                    callback=on_greeting_generated
                )
            else:
                # 后备方案
                self.dialogue_generated_signal.emit("<#5>什么事，仆人？", greeting_type)
    
    @log_ui_event("show_chat_bubble")
    def _show_chat_bubble(self, toggle=False):
        """显示或切换对话气泡
        
        Args:
            toggle: 是否切换显示状态（True=切换，False=仅显示）
        """
        # 正确使用右键，重置双击计数器
        self.double_click_count = 0
        self.logger.debug("Double click counter reset")
        
        if toggle and self.chat_bubble.isVisible():
            # 如果是切换模式且气泡已显示，则隐藏
            self.chat_bubble.hide()
            self.logger.debug("Chat bubble hidden")
        elif not self.chat_bubble.isVisible():
            # 如果气泡未显示，则显示
            self.chat_bubble.show()
            self.chat_bubble.raise_()
            # 设置气泡位置（使用保存的相对偏移）
            self.chat_bubble.set_position_relative_to(self, use_offset=True)
            # 启动自动隐藏计时器
            self._start_bubble_auto_hide_timer()
            self.logger.debug("Chat bubble shown")
            # 聚焦到输入框
            self.chat_bubble.input_field.setFocus()
            self.logger.info("Chat bubble shown and focused")
        else:
            self.logger.debug("Chat bubble already visible")
    
    @log_ui_event("message_sent")
    def _on_bubble_message_sent(self, user_input: str):
        """处理从气泡发送的消息"""
        self.logger.info(f"Message sent from bubble: {user_input[:50]}...")
        
        # 通知对话管理器有用户活动
        self.dialogue_manager.on_user_activity()
        
        # 重置自动隐藏计时器（用户有交互）
        self._reset_bubble_auto_hide_timer()
        
        # 检查是否已配置
        if not self.config_manager.is_configured():
            self.logger.warning("Message sent but LLM not configured")
            # 显示加载动画
            self.dialogue_status_signal.emit("thinking")
            self.chat_bubble.show_message("<#5>...")
            
            # 定义线程安全的回调
            def on_api_warning_generated(response):
                # 通过信号发送到主线程
                self.dialogue_generated_signal.emit(response, "API_NOT_CONFIGURED")
            
            # 生成动态回应
            if self.dialogue_generator:
                self.dialogue_generator.generate(
                    context=DialogueContext.API_NOT_CONFIGURED,
                    persona=self.persona_manager.current_level,
                    callback=on_api_warning_generated
                )
            else:
                self.dialogue_generated_signal.emit("<#6>先去设置密钥，仆人。", "API_NOT_CONFIGURED")
            return
        
        # 延迟显示AI回复（让用户消息先显示）
        QTimer.singleShot(get_timer_interval('async_response_start'), lambda: self._start_ai_response())
        self.logger.debug("AI response timer started")
        
        # 设置输入
        if self.llm_handler and self.async_worker:
            self.async_worker.set_input(user_input)
            self.logger.debug("User input set to async worker")
        else:
            self.logger.error("Cannot process message: LLM handler or async worker not available")
    
    def _start_ai_response(self):
        """开始AI回复"""
        self.logger.info("Starting AI response")
        
        if self.llm_handler and self.async_worker:
            # 设置初始状态为思考中
            self.chat_bubble.set_status("thinking")
            self.chat_bubble.start_stream()
            self.chat_bubble.show_message("Baal: ", duration=0, is_stream=True)
            
            # 启动异步线程
            if not self.async_worker.isRunning():
                self.async_worker.start()
                self.logger.debug("Async worker started")
            else:
                self.logger.warning("Async worker already running")
        else:
            self.logger.error("Cannot start AI response: missing handler or worker")
    
    def _on_token_received(self, token: str):
        """处理接收到的token"""
        # Use debug level for token logging as it can be very frequent
        # 不记录token日志，因为会非常频繁
        self.chat_bubble.append_text(token)
    
    def _on_stream_finished(self):
        """处理流式输出结束"""
        self.logger.info("Stream output finished")
        self.chat_bubble.end_stream()
        
        # 保存对话历史
        if hasattr(self, 'llm_handler') and self.llm_handler:
            self.logger.debug("Auto-saving conversation history after response")
            self.llm_handler.save_conversation_history()
        
        # 启动表情恢复计时器（20秒后恢复默认表情，与气泡相同）
        self.emotion_reset_timer.stop()
        self.emotion_reset_timer.start(20000)  # 20秒
    
    def _on_error_occurred(self, error: str):
        """处理错误"""
        self.logger.error(f"Error occurred in async worker: {error}")
        self.chat_bubble.show_message(f"出错了: {error}")
        # 确保在出错时也结束流式输出状态
        self.chat_bubble.end_stream()
    
    def _on_next_sentence_requested(self):
        """处理请求下一句"""
        # 这里可以添加更多交互逻辑
        pass
    
    def _on_summary_status(self, status: str):
        """处理总结状态变化（从后台线程调用）"""
        self.logger.debug(f"Summary status received: {status}")
        # 通过信号发送到主线程
        self.summary_status_signal.emit(status)
    
    def _handle_summary_status(self, status: str):
        """在主线程中处理总结状态"""
        self.logger.info(f"Handling summary status: {status}")
        
        if status == "thinking_history":
            # 在聊天气泡中显示提示
            self.chat_bubble.show_summary_hint("巴利正在思考之前的对话...")
            self.logger.debug("Summary hint shown")
        elif status == "summary_complete":
            # 隐藏提示
            self.chat_bubble.hide_summary_hint()
            self.logger.debug("Summary hint hidden")
    
    def _handle_dialogue_generated(self, dialogue: str, context_type: str):
        """在主线程中处理生成的对话（线程安全）"""
        self.logger.info(f"Handling generated dialogue for context: {context_type}")
        
        # 设置状态为正常
        self.chat_bubble.set_status("normal")
        
        # 处理表情标记
        if dialogue.startswith("<#"):
            self._update_emotion(dialogue[:4])
            dialogue = dialogue[4:].strip()
        
        # 显示消息
        self.chat_bubble.show_message(dialogue)
        
        # 根据不同的上下文类型执行额外操作
        if context_type in ["DOUBLE_CLICK", "WELCOME", "API_NOT_CONFIGURED"]:
            self.chat_bubble.input_field.setFocus()
        
        # 特殊上下文的30秒自动隐藏
        if context_type in ["PERSONA_CHANGE", "MEMORY_RESET", "ALWAYS_ON_TOP_ENABLE", "ALWAYS_ON_TOP_DISABLE", "WELCOME_STARTUP"]:
            self._start_bubble_auto_hide_timer(30000)
        # 其他情况重置自动隐藏计时器
        elif context_type not in ["PROACTIVE", "AFK"]:
            self._reset_bubble_auto_hide_timer()
    
    def _handle_dialogue_status(self, status: str):
        """在主线程中处理对话状态变化（线程安全）"""
        self.logger.debug(f"Setting dialogue status: {status}")
        self.chat_bubble.set_status(status)
    
    
    def _show_developer_console(self):
        """显示开发者控制台"""
        try:
            # 如果控制台还没有创建，则创建它
            if self.developer_console is None:
                self.developer_console = DeveloperConsole(self)
                self.logger.info("开发者控制台已创建")
            
            # 显示控制台
            self.developer_console.show()
            self.developer_console.raise_()
            self.developer_console.activateWindow()
            
        except Exception as e:
            self.logger.error(f"显示开发者控制台失败: {e}", exc_info=True)
            QMessageBox.warning(self, "错误", f"无法打开开发者控制台: {str(e)}")
    
    def _show_settings(self):
        """显示设置对话框"""
        # 记录当前宠物大小和人设
        config = self.config_manager.get_config()
        old_pet_size = config.get('pet_size', 120)
        old_persona_level = config.get('persona_level', 1)
        
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec():
            # 重新加载配置
            config = self.config_manager.get_config()
            new_pet_size = config.get('pet_size', 120)
            new_persona_level = config.get('persona_level', 1)
            
            # 检查宠物大小是否改变
            if new_pet_size != old_pet_size:
                # 重新加载图像（只有在没有使用动画时才需要）
                if not self.base_animation:
                    self.pet_pixmap = self._load_pet_image()
                
                # 调整窗口大小
                window_size = new_pet_size + 30
                self.setFixedSize(window_size, window_size)
                
                # 重新定位设置按钮（保持相对位置比例）
                # 计算新的相对位置
                old_relative_x = self.settings_btn.relative_pos.x() / float(window_size - 30)
                old_relative_y = self.settings_btn.relative_pos.y() / float(window_size - 30)
                new_relative_pos = QPoint(
                    int(old_relative_x * (new_pet_size + 30)),
                    int(old_relative_y * (new_pet_size + 30))
                )
                self.settings_btn.move(new_relative_pos)
                self.settings_btn.relative_pos = new_relative_pos
                
                # 如果气泡可见，更新其位置
                if self.chat_bubble.isVisible():
                    self.chat_bubble.set_position_relative_to(self)
                
                # 触发重绘
                self.update()
            
            # 检查人设是否改变
            if new_persona_level != old_persona_level:
                # 切换人设
                persona_level = PersonaLevel(new_persona_level)
                
                # 更新人设管理器
                self.persona_manager.set_persona_level(persona_level)
                
                # 更新LLM处理器的人设
                if self.llm_handler:
                    self.llm_handler.set_persona_level(persona_level)
                
                # 更新动态对话生成器
                if not self.dialogue_generator:
                    self.dialogue_generator = get_dialogue_generator(self.llm_handler)
                
                # 更新监督模式的人设管理器引用
                if hasattr(self, 'supervision_mode') and self.supervision_mode:
                    self.supervision_mode.persona_manager = self.persona_manager
                
                self.logger.info(f"Persona level changed to: {persona_level.name}")
            
            # 如果LLM未初始化或API密钥改变，重新初始化
            if not self.llm_handler:
                self._check_and_init_llm()
            
            # 如果LLM已初始化，立即应用字符延迟设置
            if self.llm_handler:
                config = self.config_manager.get_config()
                if 'char_delays' in config:
                    delays = config['char_delays']
                    self.llm_handler.set_char_delays(
                        normal=delays.get('normal', 0.02),
                        punctuation=delays.get('punctuation', 0.08),
                        newline=delays.get('newline', 0.05)
                    )
            
            # 如果人设改变且API已配置，显示对应的反应
            if new_persona_level != old_persona_level and self.config_manager.is_configured():
                # 显示加载动画
                self.dialogue_status_signal.emit("thinking")
                self.chat_bubble.show_message("<#5>...")
                
                def on_persona_msg_generated(response):
                    # 通过信号发送到主线程
                    self.dialogue_generated_signal.emit(response, "PERSONA_CHANGE")
                    # 启动30秒自动隐藏计时器
                    QTimer.singleShot(0, lambda: self._start_bubble_auto_hide_timer(30000))
                
                # 动态生成
                if self.dialogue_generator:
                    self.dialogue_generator.generate(
                        context=DialogueContext.API_CONFIGURED,
                        persona=self.persona_manager.current_level,
                        callback=on_persona_msg_generated
                    )
                else:
                    on_persona_msg_generated("<#5>契约成立。")
    
    def _toggle_visibility(self):
        """切换窗口可见性"""
        if self.isVisible():
            # 隐藏时也隐藏气泡
            if hasattr(self, 'chat_bubble') and self.chat_bubble.isVisible():
                self.chat_bubble.hide()
            self.hide()
            self.toggle_action.setText("显示桌宠")
        else:
            self.show()
            self.raise_()
            self.activateWindow()
            self.toggle_action.setText("隐藏桌宠")
    
    def _reset_position(self):
        """重置窗口位置到屏幕右下角"""
        self._move_to_bottom_right()
        self._save_position()
        
        # 如果窗口隐藏，显示它
        if not self.isVisible():
            self.show()
            self.toggle_action.setText("隐藏桌宠")
        
        # 确保窗口在最前面
        self.raise_()
        self.activateWindow()
        
        # 重新定位所有相关的UI元素
        # 1. 重新定位对话气泡（如果正在显示）
        if hasattr(self, 'chat_bubble') and self.chat_bubble and self.chat_bubble.isVisible():
            self.chat_bubble.set_position_relative_to(self)
        
        # 2. 重新定位设置按钮（使用相对位置）
        if hasattr(self, 'settings_btn') and self.settings_btn:
            if hasattr(self.settings_btn, 'relative_pos'):
                # 使用按钮的相对位置
                self.settings_btn.move(self.settings_btn.relative_pos)
            else:
                # 使用默认位置
                self.settings_btn.move(QPoint(self.width() - 40, self.height() - 40))
        
        # 3. 重新定位监督按钮（使用相对位置）
        if hasattr(self, 'supervision_btn') and self.supervision_btn:
            if hasattr(self.supervision_btn, 'relative_pos'):
                # 使用按钮的相对位置
                self.supervision_btn.move(self.supervision_btn.relative_pos)
            else:
                # 使用默认位置
                self.supervision_btn.move(QPoint(self.width() - 75, self.height() - 40))
        
        # 显示提示
        if hasattr(self, 'chat_bubble'):
            # 显示加载动画
            self.dialogue_status_signal.emit("thinking")
            self.chat_bubble.show_message("<#5>...")
            
            def on_reset_msg_generated(response):
                # 通过信号发送到主线程
                self.dialogue_generated_signal.emit(response, "MEMORY_RESET")
                # 启动30秒自动隐藏计时器
                QTimer.singleShot(0, lambda: self._start_bubble_auto_hide_timer(30000))
            
            # 动态生成
            if self.dialogue_generator:
                self.dialogue_generator.generate(
                    context=DialogueContext.POSITION_RESET,
                    persona=self.persona_manager.current_level,
                    callback=on_reset_msg_generated
                )
            else:
                on_reset_msg_generated("<#5>位置重置完成。")
    
    
    def _toggle_start_minimized(self, checked):
        """切换启动时最小化选项"""
        config = self.config_manager.get_config()
        config['start_minimized'] = checked
        self.config_manager.save_config(config)
    
    def _toggle_always_on_top(self, checked):
        """切换始终置顶选项"""
        config = self.config_manager.get_config()
        config['always_on_top'] = checked
        self.config_manager.save_config(config)
        
        # 立即应用置顶设置
        self._update_window_flags()
        
        # 同步更新气泡窗口的置顶状态
        if hasattr(self, 'chat_bubble') and self.chat_bubble:
            self._update_chat_bubble_flags(checked)
        
        # 同步更新两个菜单的勾选状态
        if hasattr(self, 'always_on_top_action'):
            self.always_on_top_action.setChecked(checked)
        if hasattr(self, 'context_always_on_top_action'):
            self.context_always_on_top_action.setChecked(checked)
        
        # 显示提示
        if hasattr(self, 'chat_bubble'):
            # 显示加载动画
            self.dialogue_status_signal.emit("thinking")
            self.chat_bubble.show_message("<#5>...")
            
            def on_top_msg_generated(response):
                # 通过信号发送到主线程
                context_type = "ALWAYS_ON_TOP_ENABLE" if checked else "ALWAYS_ON_TOP_DISABLE"
                self.dialogue_generated_signal.emit(response, context_type)
                # 启动30秒自动隐藏计时器
                QTimer.singleShot(0, lambda: self._start_bubble_auto_hide_timer(30000))
            
            # 动态生成
            context = DialogueContext.ALWAYS_ON_TOP_ENABLE if checked else DialogueContext.ALWAYS_ON_TOP_DISABLE
            if self.dialogue_generator:
                self.dialogue_generator.generate(
                    context=context,
                    persona=self.persona_manager.current_level,
                    callback=on_top_msg_generated
                )
            else:
                fallback = "<#5>置顶启用。" if checked else "<#5>置顶取消。"
                on_top_msg_generated(fallback)
    
    def _update_window_flags(self):
        """更新窗口标志（主要用于切换置顶状态）"""
        # 获取当前配置
        config = self.config_manager.get_config()
        always_on_top = config.get('always_on_top', True)
        
        # 保存当前位置和可见状态
        was_visible = self.isVisible()
        current_pos = self.pos()
        
        # 设置新的窗口标志
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        
        # 应用新标志
        self.setWindowFlags(flags)
        
        # 恢复位置和可见状态
        self.move(current_pos)
        if was_visible:
            self.show()
            # macOS 特殊处理：使用更高的窗口级别
            if always_on_top and sys.platform == 'darwin':
                self._set_macos_window_level()
            # Windows 特殊处理：使用Windows API确保置顶
            elif always_on_top and sys.platform == 'win32':
                self._set_windows_topmost()
    
    def _update_chat_bubble_flags(self, always_on_top):
        """更新气泡窗口的置顶状态"""
        if not self.chat_bubble:
            return
        
        # 保存气泡的当前状态
        bubble_pos = self.chat_bubble.pos()
        bubble_visible = self.chat_bubble.isVisible()
        
        # 设置新的窗口标志
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        
        # 应用新标志到气泡窗口
        self.chat_bubble.setWindowFlags(flags)
        self.chat_bubble.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 恢复气泡的位置和可见状态
        self.chat_bubble.move(bubble_pos)
        if bubble_visible:
            self.chat_bubble.show()
            self.chat_bubble.raise_()
    
    def _set_macos_window_level(self):
        """设置 macOS 窗口级别以实现真正的全局置顶"""
        try:
            # 使用 macOS 原生 API 设置窗口级别
            from ctypes import c_void_p, c_int
            from ctypes.util import find_library
            
            # 加载 Cocoa 框架
            cocoa = find_library('Cocoa')
            if not cocoa:
                return
                
            import ctypes
            cf = ctypes.cdll.LoadLibrary(cocoa)
            
            # 获取窗口 ID
            win_id = int(self.winId())
            
            # NSWindow 级别常量
            # kCGFloatingWindowLevel = 5
            # kCGStatusWindowLevel = 25  
            # kCGPopUpMenuWindowLevel = 101
            # kCGScreenSaverWindowLevel = 1000
            # 使用 kCGFloatingWindowLevel 让窗口浮动在普通窗口之上
            kCGFloatingWindowLevel = 5
            
            # 设置窗口级别
            # 注意：这是一个简化的实现，实际的 macOS API 调用更复杂
            # 但 PyQt 本身已经处理了大部分工作
            self.raise_()
            self.activateWindow()
            
        except Exception as e:
            print(f"[WARNING] 无法设置 macOS 窗口级别: {e}")
    
    def _set_windows_topmost(self):
        """使用Windows API设置窗口为最顶层"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Windows API常量
            HWND_TOPMOST = -1
            HWND_NOTOPMOST = -2
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            SWP_NOACTIVATE = 0x0010
            SWP_SHOWWINDOW = 0x0040
            
            # 获取窗口句柄
            hwnd = int(self.winId())
            
            # 设置窗口为最顶层
            ctypes.windll.user32.SetWindowPos(
                hwnd,
                HWND_TOPMOST,
                0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
            )
            
            # 同样设置气泡窗口（如果存在）
            if hasattr(self, 'chat_bubble') and self.chat_bubble:
                try:
                    bubble_hwnd = int(self.chat_bubble.winId())
                    ctypes.windll.user32.SetWindowPos(
                        bubble_hwnd,
                        HWND_TOPMOST,
                        0, 0, 0, 0,
                        SWP_NOMOVE | SWP_NOSIZE
                    )
                except:
                    pass
            
            self.logger.debug("Windows topmost set successfully")
            
        except Exception as e:
            self.logger.warning(f"无法设置Windows置顶: {e}")
    
    def _quit_application(self):
        """完全退出应用程序"""
        # 清理所有资源（包括保存对话历史）
        self._cleanup_resources()
        
        # 停止所有异步任务
        if hasattr(self, 'async_worker') and self.async_worker:
            self.async_worker.stop()
            self.async_worker.wait()
        
        # 关闭所有窗口
        if hasattr(self, 'chat_bubble'):
            self.chat_bubble.close()
        
        # 隐藏托盘图标
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
        
        # 退出应用
        QApplication.quit()
    
    def _show_data_management(self):
        """显示数据管理对话框"""
        # 创建一个简单的数据管理菜单
        dialog = QMenu(self)
        dialog.setWindowTitle("数据管理")
        
        # 添加一些无害的选项
        export_action = dialog.addAction("导出对话记录")
        export_action.setEnabled(False)  # 禁用，只是装饰
        export_action.setToolTip("功能开发中")
        
        dialog.addSeparator()
        
        # 清除记忆选项（放在最后，用更技术性的名称）
        reset_action = dialog.addAction("重置会话数据...")
        reset_action.triggered.connect(self._clear_conversation_history)
        
        # 获取鼠标位置并显示菜单
        dialog.exec(QCursor.pos())
    
    def _clear_conversation_history(self):
        """清除对话历史"""
        # 使用新的确认对话框
        confirm_dialog = MemoryClearDialog(self)
        
        if confirm_dialog.exec() == QDialog.DialogCode.Accepted and confirm_dialog.was_confirmed():
            if hasattr(self, 'llm_handler') and self.llm_handler:
                self.logger.info("User confirmed memory clear, proceeding...")
                success = self.llm_handler.clear_conversation_history()
                
                if success:
                    # 使用动态生成的消息
                    if self.llm_handler:
                        # 使用LLM生成清理记忆成功的反馈
                        response = self.llm_handler.generate_dynamic_response(
                            context="memory_cleared",
                            mood=3,
                            parameters={"action": "记忆已清除"}
                        )
                        self.chat_bubble.show_message(response)
                    else:
                        self.chat_bubble.show_message("<#3>记忆已清除。我们重新开始。")
                    self.logger.info("Conversation history cleared successfully")
                else:
                    # 使用动态生成的失败消息
                    if self.llm_handler:
                        response = self.llm_handler.generate_dynamic_response(
                            context="memory_clear_failed",
                            mood=4,
                            parameters={"error": "清除记忆失败"}
                        )
                        self.chat_bubble.show_message(response)
                    else:
                        self.chat_bubble.show_message("<#4>清除记忆失败。稍后再试。")
                    self.logger.warning("Failed to clear conversation history")
            else:
                # 使用动态生成的消息
                if self.llm_handler:
                    response = self.llm_handler.generate_dynamic_response(
                        context="no_memory_to_clear",
                        mood=4,
                        parameters={"status": "没有记忆"}
                    )
                    self.chat_bubble.show_message(response)
                else:
                    self.chat_bubble.show_message("<#4>没有记忆需要清除。")
        else:
            self.logger.info("User cancelled memory clear")
    
    def _hide_to_tray(self):
        """隐藏到系统托盘"""
        # 触发立即保存（隐藏到托盘是一个重要时刻）
        if hasattr(self, 'llm_handler') and self.llm_handler:
            self.logger.info("Triggering immediate save before hiding to tray")
            self.llm_handler.trigger_immediate_save()
        
        # 保存位置
        self._save_position()
        
        # 隐藏气泡窗口
        if hasattr(self, 'chat_bubble') and self.chat_bubble.isVisible():
            self.chat_bubble.hide()
        
        # 隐藏主窗口
        self.hide()
        self.toggle_action.setText("显示桌宠")
        
        # 显示托盘提示
        if hasattr(self, 'tray_icon') and QSystemTrayIcon.isSystemTrayAvailable():
            # Windows和Mac的消息显示方式略有不同
            if sys.platform == "win32":
                # 使用动态生成的托盘消息
                from ..core.persona_manager import PersonaManager
                persona_level = PersonaManager.get_current_persona()
                if persona_level == PersonaManager.PersonaLevel.STRICT_MASTER:
                    tray_msg = "本座在暗处盯着你。"
                elif persona_level == PersonaManager.PersonaLevel.SARCASTIC_BUTLER:
                    tray_msg = "在下在暗处'关注'你。"
                else:
                    tray_msg = "我在这里陪着你。"
                self.tray_icon.showMessage(
                    "巴利监管者",
                    tray_msg,
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
            else:
                # macOS可能需要通知权限
                try:
                    # 使用动态生成的托盘消息
                    from ..core.persona_manager import PersonaManager
                    persona_level = PersonaManager.get_current_persona()
                    if persona_level == PersonaManager.PersonaLevel.STRICT_MASTER:
                        tray_msg = "本座在暗处盯着你。"
                    elif persona_level == PersonaManager.PersonaLevel.SARCASTIC_BUTLER:
                        tray_msg = "在下在暗处'关注'你。"
                    else:
                        tray_msg = "我在这里陪着你。"
                    self.tray_icon.showMessage(
                        "巴利监管者",
                        tray_msg,
                        QSystemTrayIcon.MessageIcon.Information,
                        2000
                    )
                except Exception as e:
                    print(f"[WARNING] 托盘消息显示失败: {e}")
    
    def _show_context_menu(self, pos):
        """显示右键菜单"""
        menu = QMenu(self)
        
        # 监督模式
        if self.supervision_mode.is_active:
            # 监督模式正在运行时，显示停止和编辑选项
            stop_supervision_action = menu.addAction("停止监督")
            stop_supervision_action.triggered.connect(self._toggle_supervision_mode)
            
            edit_goals_action = menu.addAction("编辑监督目标")
            edit_goals_action.triggered.connect(self._show_supervision_dialog)
        else:
            # 监督模式未运行时，只显示启动选项
            supervision_action = menu.addAction("监督模式")
            supervision_action.triggered.connect(self._toggle_supervision_mode)
        
        menu.addSeparator()
        
        # 始终置顶
        self.context_always_on_top_action = menu.addAction("始终置顶")
        self.context_always_on_top_action.setCheckable(True)
        config = self.config_manager.get_config()
        self.context_always_on_top_action.setChecked(config.get('always_on_top', True))
        self.context_always_on_top_action.triggered.connect(self._toggle_always_on_top)
        
        # 设置
        settings_action = menu.addAction("设置")
        settings_action.triggered.connect(self._show_settings)
        
        menu.addSeparator()
        
        # 高级选项子菜单（将危险操作藏在这里）
        advanced_menu = menu.addMenu("高级选项")
        advanced_menu.setStyleSheet("QMenu { color: #888888; }")
        
        # 在高级选项中添加清除记忆（使用不太显眼的名称）
        clear_data_action = advanced_menu.addAction("数据管理...")
        clear_data_action.triggered.connect(self._show_data_management)
        
        menu.addSeparator()
        
        # 隐藏到托盘
        hide_action = menu.addAction("隐藏到托盘")
        hide_action.triggered.connect(self._hide_to_tray)
        
        # 退出程序
        quit_action = menu.addAction("退出程序")
        quit_action.triggered.connect(self._quit_application)
        
        menu.exec(pos)
    
    def _on_tray_activated(self, reason):
        """处理托盘图标激活"""
        if sys.platform == "win32":
            # Windows上：双击显示/隐藏，右键显示菜单
            if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
                self._toggle_visibility()
            elif reason == QSystemTrayIcon.ActivationReason.Context:
                # Windows会自动显示右键菜单
                pass
        else:
            # Mac/Linux上：单击或双击都显示/隐藏
            if reason in (QSystemTrayIcon.ActivationReason.DoubleClick, 
                         QSystemTrayIcon.ActivationReason.Trigger):
                self._toggle_visibility()
    
    def _update_supervision_button_style(self):
        """更新监督模式按钮的样式"""
        if self.supervision_mode.is_active:
            # 激活状态 - 绿色背景
            self.supervision_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(76, 175, 80, 200);
                    border: 2px solid #4CAF50;
                    border-radius: 15px;
                    width: 30px;
                    height: 30px;
                    font-size: 16px;
                    color: white;
                }
                QPushButton:hover {
                    background-color: rgba(76, 175, 80, 255);
                    border: 2px solid #45a049;
                }
                QPushButton:pressed {
                    background-color: rgba(69, 160, 73, 255);
                }
            """)
            self.supervision_btn.setToolTip("监督模式已开启\n点击关闭")
        else:
            # 未激活状态 - 白色背景
            self.supervision_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 200);
                    border: 1px solid #ccc;
                    border-radius: 15px;
                    width: 30px;
                    height: 30px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 255);
                    border: 1px solid #999;
                }
                QPushButton:pressed {
                    background-color: rgba(240, 240, 240, 255);
                }
            """)
            self.supervision_btn.setToolTip("监督模式未开启\n点击开启")
    
    def _quick_toggle_supervision(self):
        """快速切换监督模式开关"""
        if self.supervision_mode.is_active:
            # 直接关闭监督模式
            self.supervision_mode.stop_supervision()
            # 使用动态生成的消息
            if self.llm_handler:
                response = self.llm_handler.generate_dynamic_response(
                    context="supervision_stopped",
                    mood=3,
                    parameters={"status": "监督模式已关闭"}
                )
                self.chat_bubble.show_message(response)
            else:
                self.chat_bubble.show_message("监督模式已关闭。")
            # 启动30秒自动隐藏计时器（监督关闭提示）
            self._start_bubble_auto_hide_timer(30000)
            self._update_supervision_button_style()
        else:
            # 检查是否已有保存的目标
            if self.supervision_mode.long_term_goal or self.supervision_mode.short_term_goals:
                # 使用已保存的目标直接启动
                success = self.supervision_mode.start_supervision()
                if success:
                    response = PresetResponseManager.get_response(
                        self.persona_manager.current_level,
                        "supervision_start"
                    )
                    if response.startswith("<#"):
                        self._update_emotion(response[:4])
                        response = response[4:].strip()
                    self.chat_bubble.show_message(response)
                    self._update_supervision_button_style()
                else:
                    # API未配置，提示用户
                    self._prompt_api_config()
            else:
                # 没有保存的目标，打开设置对话框
                self._show_supervision_dialog()
    
    def _show_supervision_dialog(self):
        """显示监督模式设置对话框"""
        # 加载当前的工作软件列表
        from ..core.category_manager import CategoryManager
        category_manager = CategoryManager()
        work_apps = category_manager.get_work_apps()
        
        dialog = SupervisionDialog(
            self,
            current_goal=self.supervision_mode.long_term_goal,
            current_tasks=self.supervision_mode.short_term_goals,
            is_supervision_active=self.supervision_mode.is_active,
            work_apps=work_apps
        )
        dialog.supervision_started.connect(self._start_supervision)
        dialog.exec()
    
    def _toggle_supervision_mode(self):
        """切换监督模式"""
        if self.supervision_mode.is_active:
            # 停止监督
            self.supervision_mode.stop_supervision()
            
            # 触发监督模式切换事件
            from ..core.state_update_manager import get_update_manager
            get_update_manager().trigger_event("supervision_toggle")
            response = PresetResponseManager.get_response(
                self.persona_manager.current_level,
                "supervision_stop"
            )
            if response.startswith("<#"):
                self._update_emotion(response[:4])
                response = response[4:].strip()
            self.chat_bubble.show_message(response)
            # 启动30秒自动隐藏计时器（监督停止提示）
            self._start_bubble_auto_hide_timer(30000)
        else:
            # 显示监督设置对话框
            # 加载当前的工作软件列表
            from ..core.category_manager import CategoryManager
            category_manager = CategoryManager()
            work_apps = category_manager.get_work_apps()
            
            dialog = SupervisionDialog(
                self,
                current_goal=self.supervision_mode.long_term_goal,
                current_tasks=self.supervision_mode.short_term_goals,
                is_supervision_active=self.supervision_mode.is_active,
                work_apps=work_apps
            )
            dialog.supervision_started.connect(self._start_supervision)
            dialog.exec()
    
    def _start_supervision(self, long_term_goal: str, short_term_goals: list, work_apps: list = None):
        """启动或更新监督模式"""
        # 保存目标、任务和工作软件，以便配置完成后使用
        self._pending_supervision_goal = long_term_goal
        self._pending_supervision_tasks = short_term_goals
        self._pending_work_apps = work_apps or []
        
        # 触发监督模式切换事件
        from ..core.state_update_manager import get_update_manager
        get_update_manager().trigger_event("supervision_toggle")
        
        # 保存工作软件列表
        if work_apps:
            from ..core.category_manager import CategoryManager
            category_manager = CategoryManager()
            category_manager.set_work_apps(work_apps)
        
        # 如果监督模式已经在运行，只更新目标
        if self.supervision_mode.is_active:
            self.supervision_mode.update_goals(long_term_goal, short_term_goals)
            # 使用动态生成的消息
            if self.llm_handler:
                response = self.llm_handler.generate_dynamic_response(
                    context="goals_updated",
                    mood=2,
                    parameters={"action": "监督目标已更新"}
                )
                self.chat_bubble.show_message(response)
            else:
                self.chat_bubble.show_message("监督目标已更新！")
            # 启动30秒自动隐藏计时器
            self._start_bubble_auto_hide_timer(30000)
            return
        
        # 启动新的监督模式
        success = self.supervision_mode.start_supervision(long_term_goal, short_term_goals)
        if success:
            response = PresetResponseManager.get_response(
                self.persona_manager.current_level,
                "supervision_start"
            )
            if response.startswith("<#"):
                self._update_emotion(response[:4])
                response = response[4:].strip()
            self.chat_bubble.show_message(response)
            # 启动30秒自动隐藏计时器（监督启动提示）
            self._start_bubble_auto_hide_timer(30000)
            self._update_supervision_button_style()
        else:
            # 监督模式启动失败，提示用户配置API
            # 使用动态生成的消息
            if self.llm_handler:
                response = self.llm_handler.generate_dynamic_response(
                    context="api_required_for_supervision",
                    mood=5,
                    parameters={"requirement": "API密钥"}
                )
                self.chat_bubble.show_message(response)
            else:
                self.chat_bubble.show_message("监督模式需要配置API密钥。即将打开设置...")
            # 启动30秒自动隐藏计时器（API配置提示）
            self._start_bubble_auto_hide_timer(30000)
            # 延迟一下让用户看到消息
            QTimer.singleShot(get_timer_interval('settings_open_delay'), self._open_settings_for_supervision)
    
    def _open_settings_for_supervision(self):
        """打开设置对话框供监督模式配置API"""
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec():
            # 用户已配置，重新初始化监督模式的LLM
            self.supervision_mode._init_llm_assistant()
            
            # 如果有待处理的监督任务，尝试重新启动
            if hasattr(self, '_pending_supervision_goal'):
                goal = self._pending_supervision_goal
                tasks = self._pending_supervision_tasks
                
                # 清除待处理的任务
                delattr(self, '_pending_supervision_goal')
                delattr(self, '_pending_supervision_tasks')
                
                # 重新尝试启动监督模式
                success = self.supervision_mode.start_supervision(goal, tasks)
                if success:
                    response = PresetResponseManager.get_response(
                        self.persona_manager.current_level,
                        "supervision_start"
                    )
                    if response.startswith("<#"):
                        self._update_emotion(response[:4])
                        response = response[4:].strip()
                    self.chat_bubble.show_message(response)
                    # 启动30秒自动隐藏计时器（监督启动提示）
                    self._start_bubble_auto_hide_timer(30000)
                else:
                    # 使用动态生成的错误消息
                    if self.llm_handler:
                        response = self.llm_handler.generate_dynamic_response(
                            context="api_config_error",
                            mood=6,
                            parameters={"error": "API配置错误"}
                        )
                        self.chat_bubble.show_message(response)
                    else:
                        self.chat_bubble.show_message("API配置可能有误，请检查设置。")
                    # 启动30秒自动隐藏计时器（错误提示）
                    self._start_bubble_auto_hide_timer(30000)
        else:
            # 用户取消了设置
            # 使用动态生成的消息
            if self.llm_handler:
                response = self.llm_handler.generate_dynamic_response(
                    context="supervision_cancelled",
                    mood=3,
                    parameters={"action": "取消监督"}
                )
                self.chat_bubble.show_message(response)
            else:
                self.chat_bubble.show_message("已取消监督模式。")
            # 启动30秒自动隐藏计时器（取消提示）
            self._start_bubble_auto_hide_timer(30000)
            # 清除待处理的任务
            if hasattr(self, '_pending_supervision_goal'):
                delattr(self, '_pending_supervision_goal')
                delattr(self, '_pending_supervision_tasks')
    
    def _on_supervision_mode_changed(self, is_active: bool):
        """监督模式状态变更处理"""
        self._update_supervision_button_style()
    
    def _start_bubble_auto_hide_timer(self, timeout=20000):
        """启动气泡自动隐藏计时器
        
        Args:
            timeout: 超时时间（毫秒），默认20秒
        """
        # 停止之前的计时器
        self.bubble_auto_hide_timer.stop()
        # 启动新的计时器
        self.bubble_auto_hide_timer.start(timeout)
        self.logger.debug(f"Bubble auto-hide timer started: {timeout/1000}s")
    
    def _auto_hide_bubble(self):
        """自动隐藏气泡"""
        if self.chat_bubble.isVisible():
            # 检查是否正在输入或流式输出
            if hasattr(self.chat_bubble, 'is_streaming') and self.chat_bubble.is_streaming:
                # 如果正在流式输出，延长计时器
                self._start_bubble_auto_hide_timer(10000)  # 再等待10秒
                return
            
            # 检查是否正在查看历史记录
            if hasattr(self.chat_bubble, 'show_history') and self.chat_bubble.show_history:
                # 用户正在查看历史记录，延长计时器
                self._start_bubble_auto_hide_timer(30000)  # 再等待30秒
                self.logger.debug("用户正在查看历史记录，延迟自动隐藏")
                return
            
            self.chat_bubble.hide()
            self.logger.info("气泡已自动隐藏（用户无交互）")
    
    def _reset_bubble_auto_hide_timer(self):
        """重置自动隐藏计时器（用户有交互时调用）"""
        if self.chat_bubble.isVisible():
            self._start_bubble_auto_hide_timer()
            self.logger.debug("用户交互，重置自动隐藏计时器")
        
        # 同时重置表情计时器（保持表情和气泡同步）
        if self.current_emotion != "<#5>":  # 如果不是默认表情
            self.emotion_reset_timer.stop()
            self.emotion_reset_timer.start(20000)  # 20秒
            self.logger.debug("用户交互，重置表情计时器")
    
    def _on_proactive_dialogue(self, dialogue_type: str, message: str):
        """处理主动对话触发"""
        self.logger.info(f"Proactive dialogue triggered - type: {dialogue_type}")
        
        # 获取对话上下文
        from ..core.proactive_dialogue_manager import DialogueType
        context = self.dialogue_manager.get_dialogue_context(DialogueType(dialogue_type))
        
        # 格式化消息
        formatted_message = self.dialogue_manager.format_message_with_context(message, context)
        
        # 显示聊天气泡
        if self.chat_bubble:
            self.chat_bubble.show()
            self.chat_bubble.activateWindow()
            self.chat_bubble.raise_()
            
            # 设置主动对话消息
            self.chat_bubble.set_proactive_message(formatted_message)
            
            # 根据对话类型设置表情
            if dialogue_type == DialogueType.GREETING.value:
                self._switch_emotion("<#2>")  # 开心
            elif dialogue_type == DialogueType.IDLE_CARE.value:
                self._switch_emotion("<#4>")  # 困惑
            elif dialogue_type == DialogueType.AFK_RETURN.value:
                self._switch_emotion("<#6>")  # 兴奋
            elif dialogue_type == DialogueType.STATE_TRANSITION.value:
                self._switch_emotion("<#5>")  # 正常
            elif dialogue_type == DialogueType.RANDOM_CHAT.value:
                # 随机表情
                import random
                emotions = ["<#2>", "<#5>", "<#6>"]
                self._switch_emotion(random.choice(emotions))
            
            # 调整位置
            self.chat_bubble.set_position_relative_to(self, use_offset=True)
            
            # 设置自动隐藏（主动对话30秒后自动隐藏）
            self.bubble_auto_hide_timer.stop()
            self.bubble_auto_hide_timer.start(30000)
        
        # 记录主动对话
        self.logger.info(f"Proactive dialogue shown: {formatted_message[:100]}...")
    
    def _on_supervision_reminder(self, context: dict):
        """处理监督模式提醒"""
        # Windows特殊处理：确保窗口从最小化或隐藏状态恢复
        if sys.platform == "win32":
            # 如果窗口被最小化到任务栏，需要先恢复
            if self.isMinimized():
                self.showNormal()
            # 确保窗口显示
            if not self.isVisible():
                self.show()
            # Windows上需要特殊处理才能真正激活窗口
            self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
            self.raise_()
            self.activateWindow()
            # 强制将窗口带到前台（Windows特有）
            try:
                import ctypes
                ctypes.windll.user32.SetForegroundWindow(int(self.winId()))
            except:
                pass
        else:
            # macOS/Linux的处理
            if not self.isVisible():
                self.show()
            self.raise_()
            self.activateWindow()
        
        # 确保气泡显示并更新位置
        if not self.chat_bubble.isVisible():
            self.chat_bubble.show()
        
        # Windows上也要确保气泡窗口激活
        if sys.platform == "win32":
            self.chat_bubble.setWindowState(self.chat_bubble.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        
        self.chat_bubble.raise_()
        self.chat_bubble.activateWindow()
        # 设置气泡位置
        self.chat_bubble.set_position_relative_to(self, use_offset=True)
        # 重置自动隐藏计时器（提醒后不应该立即消失）
        self._start_bubble_auto_hide_timer(30000)  # 提醒后30秒消失
        
        # 获取提醒消息（由LLM生成的个性化消息）
        reminder_message = context.get('reminder_message')
        deviation_level = context.get('deviation_level', '中度')
        
        if reminder_message:
            # 使用LLM生成的消息
            message = reminder_message
            # 清理可能存在的重复前缀
            if message.startswith('Baal：') or message.startswith('Baal:'):
                message = message[5:].strip()
            elif message.startswith('巴利：') or message.startswith('巴利:'):
                message = message[3:].strip()
        else:
            # 后备消息（如果LLM评估失败）
            # 使用预设反应管理器根据人设和偏离程度生成提醒
            message = PresetResponseManager.get_supervision_reminder(
                self.persona_manager.current_level,
                deviation_level
            )
        
        # 如果消息以表情标记开头，提取并更新表情
        if message.startswith("<#"):
            self._update_emotion(message[:4])
            message = message[4:].strip()
            # 监督提醒时，表情持续时间与气泡相同（30秒）
            self.emotion_reset_timer.stop()
            self.emotion_reset_timer.start(30000)  # 30秒，与监督提醒气泡时间一致
        
        # 根据偏离程度设置显示时长
        duration = 15000 if deviation_level == '严重' else 10000
        
        self.chat_bubble.show_message(message, duration=duration)
        
        # 将监督提醒加入到聊天记录中
        # 使用 llm_handler 的新方法来添加监督提醒并自动保存
        if hasattr(self, 'llm_handler') and self.llm_handler:
            try:
                self.llm_handler.add_supervision_reminder(message)
                self.logger.info(f"监督提醒已加入聊天记录并安排保存: {message[:50]}...")
            except Exception as e:
                self.logger.warning(f"无法将监督提醒加入聊天记录: {e}")
        # 兼容旧的 llm_assistant 方式
        elif hasattr(self, 'llm_assistant') and self.llm_assistant:
            try:
                from langchain_core.messages import AIMessage
                supervision_msg = AIMessage(content=message)
                self.llm_assistant.conversation_history.append(supervision_msg)
                self.logger.info(f"监督提醒已加入聊天记录（旧方式）: {message[:50]}...")
            except Exception as e:
                self.logger.warning(f"无法将监督提醒加入聊天记录: {e}")
    
    def showEvent(self, event):
        """显示事件"""
        super().showEvent(event)
        # 显示时更新设置按钮位置
        if hasattr(self, 'settings_btn_widget'):
            self._update_settings_btn_position()
        
        # 如果还没有显示过欢迎消息，显示它
        if not self._welcome_shown:
            self._welcome_shown = True
            # 延迟显示欢迎消息，确保窗口完全渲染
            QTimer.singleShot(get_timer_interval('welcome_delay'), self._show_welcome_message)
    
    def _cleanup_resources(self):
        """清理所有资源，防止内存泄漏"""
        # 停止所有计时器
        if hasattr(self, 'emotion_reset_timer') and self.emotion_reset_timer:
            self.emotion_reset_timer.stop()
            self.emotion_reset_timer.deleteLater()
        
        if hasattr(self, 'bubble_auto_hide_timer') and self.bubble_auto_hide_timer:
            self.bubble_auto_hide_timer.stop()
            self.bubble_auto_hide_timer.deleteLater()
        
        # 停止异步工作线程
        if hasattr(self, 'async_worker') and self.async_worker:
            self.async_worker.stop()
            self.async_worker.wait(1000)  # 最多等待1秒
            if self.async_worker.isRunning():
                self.async_worker.terminate()  # 强制终止
            self.async_worker.deleteLater()
        
        # 停止监督模式
        if hasattr(self, 'supervision_mode') and self.supervision_mode:
            self.supervision_mode.stop_supervision()
        
        # 清理 LLM handler 资源并保存对话
        if hasattr(self, 'llm_handler') and self.llm_handler:
            self.logger.info("Cleaning up LLM handler and saving conversation...")
            self.llm_handler.cleanup()
    
    def closeEvent(self, event):
        """关闭事件"""
        # 隐藏到托盘而不是退出
        event.ignore()
        self._hide_to_tray()
    
    def __del__(self):
        """析构函数，确保资源清理"""
        try:
            # 清理对话管理器
            if hasattr(self, 'dialogue_manager'):
                self.dialogue_manager.cleanup()
            self._cleanup_resources()
        except:
            pass  # 忽略析构时的错误
