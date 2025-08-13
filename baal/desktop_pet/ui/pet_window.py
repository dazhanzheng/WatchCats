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
                             QApplication, QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal, QThread
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
from ..core import ConfigManager, LLMHandler
from ..core.persona_manager import PersonaLevel
from ..core.emotion_manager import EmotionManager
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
        
        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._process_stream())
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            loop.close()
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
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        self.logger = get_logger('baal.desktop_pet.ui.pet_window')
        self.logger.info("Initializing PetWindow")
        
        # 配置管理器
        self.config_manager = ConfigManager()
        self.logger.debug("ConfigManager initialized")
        
        # 表情管理器
        try:
            self.emotion_manager = EmotionManager()
            self.logger.debug("EmotionManager initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize EmotionManager: {e}", exc_info=True)
            raise
        
        # LLM处理器
        self.llm_handler = None
        self.async_worker = None
        self.logger.debug("LLM handler and async worker placeholder initialized")
        
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
            self.supervision_mode = SupervisionMode()
            self.logger.debug("Advanced features initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize advanced features: {e}", exc_info=True)
            # Continue without advanced features
        
        # 连接信号
        self.supervision_mode.reminder_needed.connect(self._on_supervision_reminder)
        self.supervision_mode.mode_changed.connect(self._on_supervision_mode_changed)
        
        # 初始化UI
        self._init_ui()
        
        # 初始化系统托盘
        self._init_tray()
        
        
        # 连接总结状态信号
        self.summary_status_signal.connect(self._handle_summary_status)
        
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
            
            # 应用当前的置顶设置到气泡窗口
            config = self.config_manager.get_config()
            always_on_top = config.get('always_on_top', True)
            self._update_chat_bubble_flags(always_on_top)
            
            self.logger.debug("Chat bubble initialized and connected")
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
            
            # 重置表情恢复计时器（10秒后恢复到默认表情）
            self.emotion_reset_timer.stop()
            self.emotion_reset_timer.start(10000)  # 10秒
            
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
        
        # 设置图标
        icon_path = Path(__file__).parent.parent.parent / "resources" / "cat.png"
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        else:
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
        
        # 聊天
        chat_action = tray_menu.addAction("聊天")
        chat_action.triggered.connect(self._show_chat_from_tray)
        
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
                self.logger.debug("Configuration found, initializing LLM handler")
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
        
        if self.config_manager.is_configured():
            welcome_msg = "哼，又一个需要监管的人类。右键召唤本座，让我看看你今天都在偷懒些什么。"
            # 设置默认表情为正常
            self._update_emotion("<#5>")
            self.logger.debug("Configured welcome message displayed")
        else:
            welcome_msg = "契约未成立。设置你的密钥，否则本座可没兴趣理会你。"
            self.logger.debug("Unconfigured welcome message displayed")
        
        # 使用独立气泡显示消息
        self.chat_bubble.show_message(welcome_msg)
        # 设置气泡位置（使用默认位置）
        self.chat_bubble.set_position_relative_to(self, use_offset=False)
    
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
        QTimer.singleShot(500, self._check_hide_buttons)
    
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
            self.double_click_count += 1
            self.logger.info(f"Double click event #{self.double_click_count}")
            
            if self.double_click_count == 1:
                # 第一次：基本不耐烦
                self.chat_bubble.show_message("别碰本座。右键召唤才是正确的方式，愚蠢的人类。")
                self.logger.debug("First double-click: basic annoyance message")
            elif self.double_click_count == 2:
                # 第二次：更加不耐烦
                self.chat_bubble.show_message("哼...又来这一套？我已经说过了，右键。还是你的大脑无法理解这么简单的指令？")
                self.logger.debug("Second double-click: increased annoyance")
            elif self.double_click_count == 3:
                # 第三次：非常不耐烦
                self.chat_bubble.show_message("最后一次警告，人类。再这样挑衅我的耐心，后果自负。")
                self.logger.debug("Third double-click: final warning")
            elif self.double_click_count >= 4:
                # 第四次及以后：如果气泡打开，则关闭它；否则不回应
                if self.chat_bubble.isVisible():
                    self.chat_bubble.hide()
                    self.logger.debug("Fourth+ double-click: hiding chat bubble")
                else:
                    self.logger.debug("Fourth+ double-click: ignoring (silent treatment)")
                # 如果气泡未打开，则什么都不做（保持沉默）
    
    @log_ui_event("show_chat_bubble")
    def _show_chat_bubble(self):
        """显示对话气泡"""
        # 正确使用右键，重置双击计数器
        self.double_click_count = 0
        self.logger.debug("Double click counter reset")
        
        if not self.chat_bubble.isVisible():
            self.chat_bubble.show()
            self.chat_bubble.raise_()
            # 设置气泡位置（使用保存的相对偏移）
            self.chat_bubble.set_position_relative_to(self, use_offset=True)
            # 聚焦到输入框
            self.chat_bubble.input_field.setFocus()
            self.logger.info("Chat bubble shown and focused")
        else:
            self.logger.debug("Chat bubble already visible")
    
    @log_ui_event("message_sent")
    def _on_bubble_message_sent(self, user_input: str):
        """处理从气泡发送的消息"""
        self.logger.info(f"Message sent from bubble: {user_input[:50]}...")
        
        # 检查是否已配置
        if not self.config_manager.is_configured():
            self.logger.warning("Message sent but LLM not configured")
            self.chat_bubble.show_message("契约未成立，本座拒绝回应。去设置你的密钥。")
            return
        
        # 延迟显示AI回复（让用户消息先显示）
        QTimer.singleShot(500, lambda: self._start_ai_response())
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
        if len(token.strip()) > 0:  # Only log non-whitespace tokens
            self.logger.debug(f"Token received: '{token[:20]}...'")
        self.chat_bubble.append_text(token)
    
    def _on_stream_finished(self):
        """处理流式输出结束"""
        self.logger.info("Stream output finished")
        self.chat_bubble.end_stream()
        
        # 启动表情恢复计时器（10秒后恢复默认表情）
        self.emotion_reset_timer.stop()
        self.emotion_reset_timer.start(10000)
    
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
            if new_persona_level != old_persona_level and self.llm_handler:
                # 切换人设
                persona_level = PersonaLevel(new_persona_level)
                self.llm_handler.set_persona_level(persona_level)
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
            
            if self.config_manager.is_configured():
                self.chat_bubble.show_message("契约成立。现在，让本座看看你都在做些什么见不得人的事。")
    
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
        
        # 显示提示
        if hasattr(self, 'chat_bubble'):
            self.chat_bubble.show_message("位置已重置。本座现在应该在你的右下角了。")
    
    
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
            if checked:
                self.chat_bubble.show_message("哼，本座当然要居高临下地监视你。")
            else:
                self.chat_bubble.show_message("切，本座偶尔也会给你一点喘息的空间。")
    
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
    
    def _show_chat_from_tray(self):
        """从托盘显示聊天窗口"""
        # 先确保主窗口可见
        if not self.isVisible():
            self.show()
            self.toggle_action.setText("隐藏桌宠")
        
        # 显示聊天气泡
        self._show_chat_bubble()
    
    def _quit_application(self):
        """完全退出应用程序"""
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
    
    def _hide_to_tray(self):
        """隐藏到系统托盘"""
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
                self.tray_icon.showMessage(
                    "巴利监管者",
                    "本座在暗处盯着你。",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
            else:
                # macOS可能需要通知权限
                try:
                    self.tray_icon.showMessage(
                        "巴利监管者",
                        "本座在暗处盯着你。",
                        QSystemTrayIcon.MessageIcon.Information,
                        2000
                    )
                except Exception as e:
                    print(f"[WARNING] 托盘消息显示失败: {e}")
    
    def _show_context_menu(self, pos):
        """显示右键菜单"""
        menu = QMenu(self)
        
        # 聊天
        chat_action = menu.addAction("聊天")
        chat_action.triggered.connect(self._show_chat_bubble)
        
        menu.addSeparator()
        
        # 监督模式
        supervision_text = "停止监督" if self.supervision_mode.is_active else "监督模式"
        supervision_action = menu.addAction(supervision_text)
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
            self.chat_bubble.show_message("监督模式已关闭。")
            self._update_supervision_button_style()
        else:
            # 检查是否已有保存的目标
            if self.supervision_mode.long_term_goal or self.supervision_mode.short_term_goals:
                # 使用已保存的目标直接启动
                success = self.supervision_mode.start_supervision()
                if success:
                    self.chat_bubble.show_message("监督模式已启动。")
                    self._update_supervision_button_style()
                else:
                    # API未配置，提示用户
                    self._prompt_api_config()
            else:
                # 没有保存的目标，打开设置对话框
                self._show_supervision_dialog()
    
    def _show_supervision_dialog(self):
        """显示监督模式设置对话框"""
        dialog = SupervisionDialog(
            self,
            current_goal=self.supervision_mode.long_term_goal,
            current_tasks=self.supervision_mode.short_term_goals
        )
        dialog.supervision_started.connect(self._start_supervision)
        dialog.exec()
    
    def _toggle_supervision_mode(self):
        """切换监督模式"""
        if self.supervision_mode.is_active:
            # 停止监督
            self.supervision_mode.stop_supervision()
            self.chat_bubble.show_message("监督模式已关闭。哼，本座也需要休息。")
        else:
            # 显示监督设置对话框
            dialog = SupervisionDialog(
                self,
                current_goal=self.supervision_mode.long_term_goal,
                current_tasks=self.supervision_mode.short_term_goals
            )
            dialog.supervision_started.connect(self._start_supervision)
            dialog.exec()
    
    def _start_supervision(self, long_term_goal: str, short_term_goals: list):
        """启动监督模式"""
        # 保存目标和任务，以便配置完成后使用
        self._pending_supervision_goal = long_term_goal
        self._pending_supervision_tasks = short_term_goals
        
        success = self.supervision_mode.start_supervision(long_term_goal, short_term_goals)
        if success:
            self.chat_bubble.show_message(f"监督模式已启动。本座会盯着你的，别想偷懒。")
            self._update_supervision_button_style()
        else:
            # 监督模式启动失败，提示用户配置API
            self.chat_bubble.show_message("监督模式需要配置API密钥。即将打开设置...")
            # 延迟一下让用户看到消息
            QTimer.singleShot(1500, self._open_settings_for_supervision)
    
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
                    self.chat_bubble.show_message("API配置成功！监督模式已启动。")
                else:
                    self.chat_bubble.show_message("API配置可能有误，请检查设置。")
        else:
            # 用户取消了设置
            self.chat_bubble.show_message("已取消监督模式。")
            # 清除待处理的任务
            if hasattr(self, '_pending_supervision_goal'):
                delattr(self, '_pending_supervision_goal')
                delattr(self, '_pending_supervision_tasks')
    
    def _on_supervision_mode_changed(self, is_active: bool):
        """监督模式状态变更处理"""
        self._update_supervision_button_style()
    
    def _on_supervision_reminder(self, context: dict):
        """处理监督模式提醒"""
        # 确保窗口显示
        if not self.isVisible():
            self.show()
            self.raise_()
            self.activateWindow()
        
        # 确保气泡显示并更新位置
        if not self.chat_bubble.isVisible():
            self.chat_bubble.show()
        self.chat_bubble.raise_()
        self.chat_bubble.activateWindow()
        self._update_bubble_position()
        
        # 获取提醒消息（由LLM生成的个性化消息）
        reminder_message = context.get('reminder_message')
        if reminder_message:
            # 使用LLM生成的消息
            message = reminder_message
        else:
            # 后备消息（如果LLM评估失败）
            long_term_goal = context.get('long_term_goal', '')
            short_term_goals = context.get('short_term_goals', [])
            
            message = f"喂，人类！你说好要「{long_term_goal}」的，现在在做什么？\n"
            if short_term_goals:
                message += f"你不是要{short_term_goals[0]}吗？赶紧回到正轨！"
            else:
                message += "别以为本座没看见，赶紧专心工作！"
        
        # 根据偏离程度设置显示时长
        deviation_level = context.get('deviation_level', '中度')
        duration = 15000 if deviation_level == '严重' else 10000
        
        self.chat_bubble.show_message(message, duration=duration)
    
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
            QTimer.singleShot(500, self._show_welcome_message)
    
    def closeEvent(self, event):
        """关闭事件"""
        # 隐藏到托盘而不是退出
        event.ignore()
        self._hide_to_tray()
