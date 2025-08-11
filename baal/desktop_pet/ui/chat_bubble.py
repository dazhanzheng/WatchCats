"""
对话气泡组件 - 紧凑型微信风格

气泡跟随宠物位置，支持动态大小调整
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QApplication, QPushButton, QHBoxLayout, QLineEdit, QScrollArea
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QRect, QRectF, QPoint
from PyQt6.QtGui import QAction,  QPainter, QPainterPath, QBrush, QColor, QFont, QFontMetrics
from ..core.logger_config import get_logger, log_ui_event


class ChatBubble(QWidget):
    """紧凑型对话气泡组件"""
    
    # 信号
    next_sentence_requested = pyqtSignal()
    message_sent = pyqtSignal(str)  # 用户发送消息的信号
    
    def __init__(self):
        """初始化对话气泡"""
        super().__init__()
        
        self.logger = get_logger('baal.desktop_pet.ui.chat_bubble')
        self.logger.info("Initializing ChatBubble")
        
        # 设置为独立窗口（移除点击穿透）
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.WindowStaysOnTopHint | 
                           Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.logger.debug("Window flags and attributes set")
        
        # 文本相关
        self.conversation_history = []  # 存储完整对话历史
        self.current_text = ""
        self.current_type = "baal"  # 当前消息类型
        self.is_streaming = False
        self.show_history = False  # 是否显示历史记录
        
        # 状态相关
        self.current_status = "idle"  # idle, thinking, tools, streaming, done
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status_animation)
        self.status_animation_frame = 0
        
        # 宠物窗口引用
        self.pet_window = None
        
        # 相对位置偏移（用于独立拖动时）
        self.relative_offset = QPoint(-260, -30)  # 默认在宠物左上方
        
        # 气泡大小
        self.min_width = 250  # 增加到250px，给文本更多空间
        self.max_width = 400
        self.min_height = 80  # 增加最小高度到80px，确保内容完整显示
        self.current_width = self.min_width
        self.current_height = self.min_height
        
        # 初始化UI
        try:
            self._init_ui()
            self.logger.info("ChatBubble initialization completed")
        except Exception as e:
            self.logger.error(f"Failed to initialize ChatBubble: {e}", exc_info=True)
            raise
        
        # 设置初始大小
        self.setFixedSize(self.current_width, self.current_height)
        
        # 动画
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        
        # 大小调整计时器
        self.resize_timer = QTimer()
        self.resize_timer.timeout.connect(self._adjust_size)
        self.resize_timer.setInterval(50)  # 每50ms检查一次
    
    @log_ui_event("chat_bubble_init")
    def _init_ui(self):
        """初始化UI"""
        self.logger.debug("Initializing ChatBubble UI components")
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 25, 8)  # 右边留出关闭按钮空间，减少底部边距
        layout.setSpacing(3)  # 减少组件间距
        
        # 关闭按钮（绝对定位）
        self.close_btn = QPushButton("×", self)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666;
                font-size: 16px;
                font-weight: bold;
                padding: 0;
                width: 16px;
                height: 16px;
            }
            QPushButton:hover {
                color: #333;
            }
        """)
        self.close_btn.clicked.connect(self.hide)
        
        # 文本显示（可滚动）
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # 初始不显示垂直滚动条
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(0, 0, 0, 30);
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 0, 0, 60);
                border-radius: 3px;
            }
        """)
        
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                font-size: 13px;
                line-height: 1.4;
                padding: 0;
                margin: 0;
            }
        """)
        # 设置文档边距为0
        self.text_display.document().setDocumentMargin(0)
        
        # 设置字体
        font = QFont()
        font.setFamily("Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif")
        font.setPointSize(11)
        self.text_display.setFont(font)
        
        self.scroll_area.setWidget(self.text_display)
        layout.addWidget(self.scroll_area)
        
        # 输入框（紧凑型）
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("输入消息...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 180);
                border: 1px solid #ddd;
                border-radius: 12px;
                padding: 5px 10px;
                font-size: 12px;
                color: #333;
            }
            QLineEdit:focus {
                border: 1px solid #4CAF50;
                background-color: rgba(255, 255, 255, 220);
            }
        """)
        self.input_field.returnPressed.connect(self._on_send_message)
        
        layout.addWidget(self.input_field)
    
    def set_position_relative_to(self, pet_window, use_offset=True):
        """设置气泡相对于宠物窗口的位置
        
        Args:
            pet_window: 宠物窗口
            use_offset: 是否使用当前的相对偏移
        """
        if pet_window:
            # 保存宠物窗口引用
            self.pet_window = pet_window
            
            pet_pos = pet_window.pos()
            
            if use_offset:
                # 使用当前的相对偏移
                bubble_pos = pet_pos + self.relative_offset
            else:
                # 使用默认位置（宠物左上方）
                bubble_pos = QPoint(pet_pos.x() - self.width() - 10, pet_pos.y() - 30)
                # 更新相对偏移
                self.relative_offset = bubble_pos - pet_pos
            
            # 确保不超出屏幕边界
            screen = QApplication.primaryScreen()
            screen_rect = screen.availableGeometry()
            
            if bubble_pos.x() < 0:
                bubble_pos.setX(pet_pos.x() + pet_window.size().width() + 10)
                # 更新相对偏移
                self.relative_offset = bubble_pos - pet_pos
            if bubble_pos.y() < 0:
                bubble_pos.setY(10)
                # 更新相对偏移
                self.relative_offset = bubble_pos - pet_pos
                
            self.move(bubble_pos)
            
            # 更新关闭按钮位置
            self.close_btn.move(self.width() - 20, 5)
    
    def paintEvent(self, event):
        """绘制气泡背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 创建圆角矩形路径
        path = QPainterPath()
        rect = self.rect().adjusted(5, 5, -5, -5)
        rect_f = QRectF(rect)
        path.addRoundedRect(rect_f, 12, 12)
        
        # 绘制阴影
        painter.fillPath(path.translated(1, 1), QColor(0, 0, 0, 20))
        
        # 绘制背景（浅灰色，更像微信）
        painter.fillPath(path, QColor(240, 240, 240, 250))
        
        # 绘制边框
        painter.setPen(QColor(200, 200, 200, 150))
        painter.drawPath(path)
        
        painter.end()
    
    def show_message(self, message: str, duration: int = 0, is_stream: bool = False, msg_type: str = "baal"):
        """显示消息"""
        if not is_stream:
            # 添加到对话历史
            self.conversation_history.append({"text": message, "type": msg_type})
        
        self.current_text = message
        self.current_type = msg_type
        self.is_streaming = is_stream
        
        # 更新显示
        self._update_display()
        
        # 计算初始高度（避免后续调整）
        if not self.show_history:
            plain_text = self.text_display.toPlainText()
            if plain_text:
                font_metrics = QFontMetrics(self.text_display.font())
                fixed_text_width = self.min_width - 40
                text_rect = font_metrics.boundingRect(
                    0, 0, fixed_text_width,
                    2000, Qt.TextFlag.TextWordWrap,
                    plain_text
                )
                
                text_height = text_rect.height()
                padding_height = 65  # 输入框 + 上下边距（稍微增加）
                initial_height = min(300, max(self.min_height, text_height + padding_height))
                
                if initial_height != self.current_height:
                    self.current_height = initial_height
                    self.setFixedSize(self.current_width, self.current_height)
                    self.close_btn.move(self.width() - 20, 5)
        
        # 如果正在流式输出，启动大小调整计时器
        if is_stream:
            self.resize_timer.start()
        
        # 显示窗口
        if not self.isVisible():
            self.setWindowOpacity(0)
            self.show()
            self.raise_()
            
            # 淡入动画
            self.fade_animation.stop()
            self.fade_animation.setStartValue(0)
            self.fade_animation.setEndValue(1)
            self.fade_animation.start()
    
    def append_text(self, text: str):
        """追加文本（用于流式输出）"""
        if self.is_streaming:
            self.current_text += text
            self._update_display()
            
            # 滚动到底部
            cursor = self.text_display.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.text_display.setTextCursor(cursor)
            
            # 立即检查是否需要调整大小（不等待定时器）
            self._adjust_size()
    
    def _update_display(self):
        """更新显示（根据是否显示历史）"""
        self.text_display.clear()
        
        # 生成状态图标的HTML
        status_icon_html = ""
        if self.current_status == "thinking":
            # 思考动画 - 两个实心球一个空心球
            dots = []
            for i in range(3):
                if i == self.status_animation_frame:
                    # 空心球
                    dots.append('<span style="color: #666; font-size: 14px;">○</span>')
                else:
                    # 实心球
                    dots.append('<span style="color: #666; font-size: 14px;">●</span>')
            status_icon_html = f'<span style="margin-left: 5px;">{" ".join(dots)}</span>'
        elif self.current_status == "tools":
            # 扳手图标（使用文字表示）
            status_icon_html = '<span style="margin-left: 5px; color: #666; font-size: 12px;">[工具查询中]</span>'
        
        if self.show_history:
            # 显示所有历史对话
            for msg_data in self.conversation_history:
                text = msg_data["text"]
                msg_type = msg_data["type"]
                
                if msg_type == "user":
                    colored_text = f'<div style="margin: 5px 0;"><span style="color: #006400; font-weight: bold;">你: </span><span style="color: #333;">{text[3:]}</span></div>'
                else:
                    colored_text = f'<div style="margin: 5px 0;"><span style="color: #8B008B; font-weight: bold;">Baal: </span><span style="color: #333;">{text}</span></div>'
                
                self.text_display.append(colored_text)
        else:
            # 只显示最后一条消息或当前流式消息
            if self.is_streaming and self.current_text:
                # 显示当前流式消息
                if self.current_type == "user":
                    colored_text = f'<span style="color: #006400; font-weight: bold;">你: </span><span style="color: #333;">{self.current_text[3:]}</span>'
                else:
                    # 如果是Baal的消息且正在思考/使用工具，添加状态图标
                    if self.current_status in ["thinking", "tools"] and not self.current_text[6:].strip():
                        colored_text = f'<span style="color: #8B008B; font-weight: bold;">Baal: </span>{status_icon_html}'
                    else:
                        colored_text = f'<span style="color: #8B008B; font-weight: bold;">Baal: </span><span style="color: #333;">{self.current_text[6:]}</span>'
                self.text_display.append(colored_text)
            elif self.conversation_history:
                # 显示最后一条历史消息
                last_msg = self.conversation_history[-1]
                text = last_msg["text"]
                msg_type = last_msg["type"]
                
                if msg_type == "user":
                    colored_text = f'<span style="color: #006400; font-weight: bold;">你: </span><span style="color: #333;">{text[3:]}</span>'
                else:
                    colored_text = f'<span style="color: #8B008B; font-weight: bold;">Baal: </span><span style="color: #333;">{text}</span>'
                self.text_display.append(colored_text)
            elif self.current_status in ["thinking", "tools"]:
                # 如果没有消息但正在处理，显示状态
                colored_text = f'<span style="color: #8B008B; font-weight: bold;">Baal: </span>{status_icon_html}'
                self.text_display.append(colored_text)
    
    def _adjust_size(self):
        """动态调整气泡大小（固定宽度，预测性调整高度）"""
        if not self.is_streaming:
            self.resize_timer.stop()
            return
            
        # 获取文本内容
        plain_text = self.text_display.toPlainText()
        if not plain_text:
            return
            
        # 使用固定宽度计算文本高度
        font_metrics = QFontMetrics(self.text_display.font())
        fixed_text_width = self.min_width - 40  # 250 - 40 = 210px 可用文本宽度
        
        # 计算当前文本的高度
        current_text_rect = font_metrics.boundingRect(
            0, 0, fixed_text_width,
            2000,  # 最大高度
            Qt.TextFlag.TextWordWrap,
            plain_text
        )
        
        # 预测性计算：添加一个测试字符来检测是否即将换行
        # 使用"测"作为测试字符（中文字符通常较宽）
        test_text = plain_text + "测"
        predicted_text_rect = font_metrics.boundingRect(
            0, 0, fixed_text_width,
            2000,
            Qt.TextFlag.TextWordWrap,
            test_text
        )
        
        # 如果添加一个字符后高度会增加，说明即将换行
        current_height = current_text_rect.height()
        predicted_height = predicted_text_rect.height()
        
        # 如果预测到即将换行，使用预测的高度
        if predicted_height > current_height:
            text_height = predicted_height
        else:
            text_height = current_height
        
        # 宽度始终保持最小宽度
        new_width = self.min_width
        
        # 计算实际需要的高度（文本高度 + 输入框高度 + 边距）
        padding_height = 65  # 输入框 + 上下边距
        new_height = min(300, max(self.min_height, text_height + padding_height))
        
        # 只有高度变化时才更新（移除了5像素阈值，因为现在是预测性调整）
        if new_height != self.current_height:
            self.current_width = new_width  # 保持固定宽度
            self.current_height = new_height
            self.setFixedSize(self.current_width, self.current_height)
            
            # 更新关闭按钮位置
            self.close_btn.move(self.width() - 20, 5)
            
            # 不需要更新位置，因为气泡大小改变时不应该改变位置
    
    def start_stream(self):
        """开始流式输出"""
        self.logger.info("Starting stream output")
        self.is_streaming = True
        self.current_text = ""
        self.resize_timer.start()
    
    def end_stream(self):
        """结束流式输出"""
        self.logger.info("Ending stream output")
        self.is_streaming = False
        self.resize_timer.stop()
        
        # 将当前流式文本添加到对话历史
        if self.current_text:
            self.conversation_history.append({"text": self.current_text, "type": self.current_type})
            self.logger.debug(f"Stream text added to history: {len(self.current_text)} characters")
        
        # 最终调整一次大小（保持固定宽度）
        if not self.show_history:
            # 确保最终大小合适
            plain_text = self.text_display.toPlainText()
            if plain_text:
                font_metrics = QFontMetrics(self.text_display.font())
                fixed_text_width = self.min_width - 40
                text_rect = font_metrics.boundingRect(
                    0, 0, fixed_text_width,
                    2000, Qt.TextFlag.TextWordWrap,
                    plain_text
                )
                
                text_height = text_rect.height()
                padding_height = 60
                final_height = min(300, max(self.min_height, text_height + padding_height))
                
                if final_height != self.current_height:
                    self.current_height = final_height
                    self.setFixedSize(self.min_width, self.current_height)
                    self.close_btn.move(self.width() - 20, 5)
    
    def wheelEvent(self, event):
        """处理滚轮事件"""
        # 向上滚动显示历史，向下滚动隐藏历史
        if event.angleDelta().y() > 0:
            # 向上滚动 - 显示历史
            if not self.show_history and len(self.conversation_history) > 1:
                self.show_history = True
                self._update_display()
                # 增大窗口高度以显示更多内容
                self.setFixedSize(self.current_width, 300)
                # 显示历史时启用滚动条
                self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        else:
            # 向下滚动 - 隐藏历史
            if self.show_history:
                self.show_history = False
                self._update_display()
                # 恢复原始大小
                self.setFixedSize(self.current_width, self.current_height)
                # 隐藏历史时禁用滚动条
                self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 传递事件给滚动区域（只在显示历史时）
        if self.show_history:
            self.scroll_area.wheelEvent(event)
    
    def mousePressEvent(self, event):
        """处理鼠标点击事件"""
        # 允许拖动窗口
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_position'):
            # 移动气泡
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.move(new_pos)
            
            # 更新相对于宠物的偏移
            if self.pet_window:
                self.relative_offset = self.pos() - self.pet_window.pos()
            
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = None
    
    def _on_send_message(self):
        """处理发送消息"""
        message = self.input_field.text().strip()
        if message:
            # 清空输入框
            self.input_field.clear()
            
            # 显示用户消息
            self.show_message(f"你: {message}", msg_type="user")
            
            # 发送信号
            self.message_sent.emit(message)
    
    def set_status(self, status: str):
        """设置当前状态
        
        Args:
            status: 状态字符串 - idle, thinking, tools, streaming, done
        """
        print(f"[DEBUG ChatBubble] 设置状态: {self.current_status} -> {status}")
        self.current_status = status
        
        if status in ["thinking", "tools"]:
            # 开始动画
            self.status_animation_frame = 0
            self.status_timer.start(500)  # 每500ms更新一次
            # 立即更新显示
            self._update_display()
        else:
            # 停止动画
            self.status_timer.stop()
        
        # 触发重绘
        self.update()
    
    def _update_status_animation(self):
        """更新状态动画帧"""
        self.status_animation_frame = (self.status_animation_frame + 1) % 3
        # 只更新显示，不重绘
        self._update_display()
    
    def show_summary_hint(self, hint_text: str):
        """显示总结提示
        
        Args:
            hint_text: 提示文本
        """
        # 在当前内容下方添加提示（使用特殊样式）
        if not hasattr(self, '_summary_hint_shown') or not self._summary_hint_shown:
            self._summary_hint_shown = True
            # 添加分隔线和提示
            hint_html = f'<hr style="border: none; border-top: 1px dotted #ccc; margin: 5px 0;"><div style="color: #999; font-size: 11px; font-style: italic; text-align: center; margin: 5px 0;">{hint_text}</div>'
            current_html = self.text_display.toHtml()
            self.text_display.setHtml(current_html + hint_html)
            # 滚动到底部
            self.text_display.verticalScrollBar().setValue(
                self.text_display.verticalScrollBar().maximum()
            )
    
    def hide_summary_hint(self):
        """隐藏总结提示"""
        if hasattr(self, '_summary_hint_shown') and self._summary_hint_shown:
            self._summary_hint_shown = False
            # 移除提示内容
            current_html = self.text_display.toHtml()
            # 查找并移除提示部分（从最后一个<hr>开始）
            hr_index = current_html.rfind('<hr style="border: none; border-top: 1px dotted #ccc;')
            if hr_index != -1:
                self.text_display.setHtml(current_html[:hr_index]) 