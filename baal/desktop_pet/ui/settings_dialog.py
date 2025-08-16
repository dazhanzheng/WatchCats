"""
设置对话框

用于配置API密钥等设置
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, 
                             QMessageBox, QGroupBox, QSlider, QSpinBox,
                             QComboBox, QTextEdit, QScrollArea, QWidget,
                             QApplication)
from PyQt6.QtCore import Qt
from typing import Optional
from ..core.persona_manager import PersonaLevel


class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, config_manager, parent=None):
        """
        初始化设置对话框
        
        Args:
            config_manager: 配置管理器实例
            parent: 父窗口
        """
        super().__init__(parent)
        self.config_manager = config_manager
        
        # 设置窗口属性
        self.setWindowTitle("设置")
        self.setModal(True)
        
        # 获取屏幕可用高度，并设置合适的窗口大小
        screen = QApplication.primaryScreen()
        available_rect = screen.availableGeometry()
        
        # 设置最大高度为屏幕可用高度的90%，留出任务栏空间
        max_height = int(available_rect.height() * 0.85)
        # 如果800像素超过最大高度，使用最大高度，否则使用800
        window_height = min(800, max_height)
        # 最小高度为600，确保内容可以显示
        window_height = max(600, window_height)
        
        self.setFixedSize(500, window_height)
        
        # 设置窗口标志
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        
        # 初始化UI
        self._init_ui()
        
        # 加载当前配置
        self._load_config()
    
    def _init_ui(self):
        """初始化UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 创建内容容器
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # API配置组
        api_group = QGroupBox("API 配置")
        api_layout = QVBoxLayout()
        
        # API密钥输入
        key_layout = QHBoxLayout()
        key_label = QLabel("API密钥:")
        key_label.setFixedWidth(70)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("请输入您的API密钥")
        
        # 显示/隐藏密钥按钮
        self.toggle_key_btn = QPushButton("显示")
        self.toggle_key_btn.setFixedWidth(50)
        self.toggle_key_btn.clicked.connect(self._toggle_key_visibility)
        
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.api_key_input)
        key_layout.addWidget(self.toggle_key_btn)
        
        api_layout.addLayout(key_layout)
        
        # 基础URL显示（只读）
        url_layout = QHBoxLayout()
        url_label = QLabel("API地址:")
        url_label.setFixedWidth(70)
        
        self.base_url_display = QLineEdit()
        self.base_url_display.setReadOnly(True)
        self.base_url_display.setStyleSheet("""
            QLineEdit {
                background-color: #f0f0f0;
                color: #666666;
            }
        """)
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.base_url_display)
        
        api_layout.addLayout(url_layout)
        
        # 模型显示（只读）
        model_layout = QHBoxLayout()
        model_label = QLabel("模型:")
        model_label.setFixedWidth(70)
        
        self.model_display = QLineEdit()
        self.model_display.setReadOnly(True)
        self.model_display.setStyleSheet("""
            QLineEdit {
                background-color: #f0f0f0;
                color: #666666;
            }
        """)
        
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_display)
        
        api_layout.addLayout(model_layout)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # 人设设置组
        persona_group = QGroupBox("人设设置")
        persona_layout = QVBoxLayout()
        
        # 人设选择下拉框
        persona_select_layout = QHBoxLayout()
        persona_label = QLabel("人设档位:")
        persona_label.setFixedWidth(100)
        
        self.persona_combo = QComboBox()
        self.persona_combo.addItem("严厉主人 - 巴利是你的主人，拥有绝对支配权", 1)
        self.persona_combo.addItem("毒舌管家 - 巴利是你的管家，表面恭敬实则毒舌", 2)
        self.persona_combo.addItem("温顺伴侣 - 巴利是你的伴侣，温柔体贴关怀备至", 3)
        self.persona_combo.currentIndexChanged.connect(self._on_persona_changed)
        
        persona_select_layout.addWidget(persona_label)
        persona_select_layout.addWidget(self.persona_combo)
        persona_layout.addLayout(persona_select_layout)
        
        # 人设描述显示
        self.persona_description = QTextEdit()
        self.persona_description.setReadOnly(True)
        self.persona_description.setMaximumHeight(100)
        self.persona_description.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                padding: 5px;
                font-size: 12px;
            }
        """)
        persona_layout.addWidget(self.persona_description)
        
        # 提示文本
        persona_info = QLabel("提示：切换人设后，巴利的性格和说话方式会发生变化")
        persona_info.setStyleSheet("color: #666666; font-size: 11px; margin-top: 5px;")
        persona_layout.addWidget(persona_info)
        
        persona_group.setLayout(persona_layout)
        layout.addWidget(persona_group)
        
        # 字符延迟设置组
        delay_group = QGroupBox("字符显示速度")
        delay_layout = QVBoxLayout()
        
        # 创建字符延迟控件
        self.delay_widgets = {}
        
        # 普通字符延迟
        normal_layout = QHBoxLayout()
        normal_label = QLabel("普通字符:")
        normal_label.setFixedWidth(100)
        
        self.normal_slider = QSlider(Qt.Orientation.Horizontal)
        self.normal_slider.setRange(10, 500)  # 10ms到500ms
        self.normal_slider.setValue(20)  # 默认20ms
        
        self.normal_spinbox = QSpinBox()
        self.normal_spinbox.setRange(10, 500)
        self.normal_spinbox.setSuffix(" ms")
        self.normal_spinbox.setValue(20)
        self.normal_spinbox.setFixedWidth(80)
        
        # 连接滑块和数值框
        self.normal_slider.valueChanged.connect(self.normal_spinbox.setValue)
        self.normal_spinbox.valueChanged.connect(self.normal_slider.setValue)
        
        normal_layout.addWidget(normal_label)
        normal_layout.addWidget(self.normal_slider)
        normal_layout.addWidget(self.normal_spinbox)
        delay_layout.addLayout(normal_layout)
        
        # 标点符号延迟
        punct_layout = QHBoxLayout()
        punct_label = QLabel("标点符号:")
        punct_label.setFixedWidth(100)
        
        self.punct_slider = QSlider(Qt.Orientation.Horizontal)
        self.punct_slider.setRange(50, 1000)  # 50ms到1000ms
        self.punct_slider.setValue(80)  # 默认80ms
        
        self.punct_spinbox = QSpinBox()
        self.punct_spinbox.setRange(50, 1000)
        self.punct_spinbox.setSuffix(" ms")
        self.punct_spinbox.setValue(80)
        self.punct_spinbox.setFixedWidth(80)
        
        # 连接滑块和数值框
        self.punct_slider.valueChanged.connect(self.punct_spinbox.setValue)
        self.punct_spinbox.valueChanged.connect(self.punct_slider.setValue)
        
        punct_layout.addWidget(punct_label)
        punct_layout.addWidget(self.punct_slider)
        punct_layout.addWidget(self.punct_spinbox)
        delay_layout.addLayout(punct_layout)
        
        # 换行符延迟
        newline_layout = QHBoxLayout()
        newline_label = QLabel("换行符:")
        newline_label.setFixedWidth(100)
        
        self.newline_slider = QSlider(Qt.Orientation.Horizontal)
        self.newline_slider.setRange(30, 500)  # 30ms到500ms
        self.newline_slider.setValue(50)  # 默认50ms
        
        self.newline_spinbox = QSpinBox()
        self.newline_spinbox.setRange(30, 500)
        self.newline_spinbox.setSuffix(" ms")
        self.newline_spinbox.setValue(50)
        self.newline_spinbox.setFixedWidth(80)
        
        # 连接滑块和数值框
        self.newline_slider.valueChanged.connect(self.newline_spinbox.setValue)
        self.newline_spinbox.valueChanged.connect(self.newline_slider.setValue)
        
        newline_layout.addWidget(newline_label)
        newline_layout.addWidget(self.newline_slider)
        newline_layout.addWidget(self.newline_spinbox)
        delay_layout.addLayout(newline_layout)
        
        # 预设按钮
        preset_layout = QHBoxLayout()
        preset_label = QLabel("快速预设:")
        preset_label.setFixedWidth(100)
        
        fast_btn = QPushButton("快速")
        fast_btn.clicked.connect(lambda: self._set_delay_preset(10, 50, 30))
        
        normal_btn = QPushButton("正常")
        normal_btn.clicked.connect(lambda: self._set_delay_preset(20, 80, 50))
        
        slow_btn = QPushButton("慢速")
        slow_btn.clicked.connect(lambda: self._set_delay_preset(50, 150, 100))
        
        very_slow_btn = QPushButton("超慢")
        very_slow_btn.clicked.connect(lambda: self._set_delay_preset(200, 800, 500))
        
        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(fast_btn)
        preset_layout.addWidget(normal_btn)
        preset_layout.addWidget(slow_btn)
        preset_layout.addWidget(very_slow_btn)
        preset_layout.addStretch()
        
        delay_layout.addLayout(preset_layout)
        
        # 说明文本
        delay_info = QLabel("提示：调整文字出现的速度，数值越大速度越慢")
        delay_info.setStyleSheet("color: #666666; font-size: 11px; margin-top: 5px;")
        delay_layout.addWidget(delay_info)
        
        delay_group.setLayout(delay_layout)
        layout.addWidget(delay_group)
        
        # 宠物大小设置组
        size_group = QGroupBox("宠物大小")
        size_layout = QVBoxLayout()
        
        # 大小调节
        size_control_layout = QHBoxLayout()
        size_label = QLabel("大小:")
        size_label.setFixedWidth(100)
        
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(60, 300)  # 60px到300px
        self.size_slider.setValue(120)  # 默认120px
        self.size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.size_slider.setTickInterval(60)
        
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(60, 300)
        self.size_spinbox.setSuffix(" px")
        self.size_spinbox.setValue(120)
        self.size_spinbox.setFixedWidth(80)
        
        # 连接滑块和数值框
        self.size_slider.valueChanged.connect(self.size_spinbox.setValue)
        self.size_spinbox.valueChanged.connect(self.size_slider.setValue)
        
        size_control_layout.addWidget(size_label)
        size_control_layout.addWidget(self.size_slider)
        size_control_layout.addWidget(self.size_spinbox)
        size_layout.addLayout(size_control_layout)
        
        # 预设大小按钮
        size_preset_layout = QHBoxLayout()
        size_preset_label = QLabel("快速预设:")
        size_preset_label.setFixedWidth(100)
        
        small_btn = QPushButton("小")
        small_btn.clicked.connect(lambda: self.size_slider.setValue(80))
        
        medium_btn = QPushButton("中")
        medium_btn.clicked.connect(lambda: self.size_slider.setValue(120))
        
        large_btn = QPushButton("大")
        large_btn.clicked.connect(lambda: self.size_slider.setValue(180))
        
        xlarge_btn = QPushButton("特大")
        xlarge_btn.clicked.connect(lambda: self.size_slider.setValue(240))
        
        size_preset_layout.addWidget(size_preset_label)
        size_preset_layout.addWidget(small_btn)
        size_preset_layout.addWidget(medium_btn)
        size_preset_layout.addWidget(large_btn)
        size_preset_layout.addWidget(xlarge_btn)
        size_preset_layout.addStretch()
        
        size_layout.addLayout(size_preset_layout)
        
        # 说明文本
        size_info = QLabel("提示：调整宠物显示大小，需要重启生效")
        size_info.setStyleSheet("color: #666666; font-size: 11px; margin-top: 5px;")
        size_layout.addWidget(size_info)
        
        size_group.setLayout(size_layout)
        layout.addWidget(size_group)
        
        # 说明文本
        info_label = QLabel("提示：API密钥将安全保存在本地配置文件中")
        info_label.setStyleSheet("color: #666666; font-size: 12px;")
        layout.addWidget(info_label)
        
        # 不需要弹性空间了，因为滚动区域会自动处理
        # layout.addStretch()
        
        # 将内容容器设置到滚动区域
        scroll_area.setWidget(content_widget)
        
        # 将滚动区域添加到主布局
        main_layout.addWidget(scroll_area)
        
        # 创建按钮容器（固定在底部，不随滚动）
        button_container = QWidget()
        button_container.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-top: 1px solid #ddd;
            }
        """)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(20, 10, 20, 10)
        button_layout.addStretch()
        
        # 保存按钮
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self._save_config)
        self.save_btn.setDefault(True)
        self.save_btn.setMinimumWidth(80)
        
        # 取消按钮
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setMinimumWidth(80)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        # 将按钮容器添加到主布局底部
        main_layout.addWidget(button_container)
    
    def _load_config(self):
        """加载当前配置"""
        # 加载API密钥
        api_key = self.config_manager.get_api_key()
        if api_key:
            self.api_key_input.setText(api_key)
        
        # 显示基础URL
        self.base_url_display.setText(self.config_manager.get_base_url())
        
        # 显示模型
        self.model_display.setText(self.config_manager.get_model())
        
        # 加载配置
        config = self.config_manager.get_config()
        
        # 加载人设设置
        persona_level = config.get('persona_level', 1)  # 默认为严厉主人档
        # 根据值设置下拉框
        for i in range(self.persona_combo.count()):
            if self.persona_combo.itemData(i) == persona_level:
                self.persona_combo.setCurrentIndex(i)
                break
        self._update_persona_description(persona_level)
        
        # 加载字符延迟设置
        if 'char_delays' in config:
            delays = config['char_delays']
            # 转换为毫秒并设置
            self.normal_slider.setValue(int(delays.get('normal', 0.02) * 1000))
            self.punct_slider.setValue(int(delays.get('punctuation', 0.08) * 1000))
            self.newline_slider.setValue(int(delays.get('newline', 0.05) * 1000))
        
        # 加载宠物大小设置
        pet_size = config.get('pet_size', 120)
        self.size_slider.setValue(pet_size)
    
    def _save_config(self):
        """保存配置"""
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            QMessageBox.warning(
                self,
                "警告",
                "请输入API密钥！"
            )
            return
        
        # 保存配置
        self.config_manager.set_api_key(api_key)
        
        # 保存字符延迟设置
        config = self.config_manager.get_config()
        config['char_delays'] = {
            'normal': self.normal_slider.value() / 1000.0,      # 转换为秒
            'punctuation': self.punct_slider.value() / 1000.0,
            'newline': self.newline_slider.value() / 1000.0
        }
        
        # 保存宠物大小设置
        config['pet_size'] = self.size_slider.value()
        
        # 保存人设设置
        config['persona_level'] = self.persona_combo.currentData()
        
        # 尝试保存配置（传入修改后的配置）
        if self.config_manager.save_config(config):
            # 显示成功消息
            QMessageBox.information(
                self,
                "成功",
                "配置已保存！\n\n人设切换将在下次对话时生效。"
            )
            # 关闭对话框
            self.accept()
        else:
            # 保存失败，显示错误消息
            import sys
            error_msg = "配置保存失败！\n\n"
            
            if sys.platform == "win32":
                error_msg += "Windows 权限问题解决方案：\n"
                error_msg += "1. 右键程序，选择'以管理员身份运行'\n"
                error_msg += "2. 检查杀毒软件是否阻止文件写入\n"
                error_msg += "3. 确保程序所在目录有写入权限\n\n"
                error_msg += f"配置路径：{self.config_manager.config_file}\n\n"
                error_msg += "注意：如果是从压缩包直接运行，\n请先解压到硬盘再运行程序。"
            else:
                error_msg += f"无法写入配置文件：\n{self.config_manager.config_file}\n\n"
                error_msg += "请检查文件权限。"
            
            QMessageBox.critical(
                self,
                "保存失败",
                error_msg
            )
    
    def _toggle_key_visibility(self):
        """切换密钥可见性"""
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_key_btn.setText("隐藏")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_key_btn.setText("显示") 
    
    def _set_delay_preset(self, normal, punct, newline):
        """设置延迟预设值"""
        self.normal_slider.setValue(normal)
        self.punct_slider.setValue(punct)
        self.newline_slider.setValue(newline)
    
    def _on_persona_changed(self, index):
        """处理人设选择变化"""
        persona_level = self.persona_combo.currentData()
        self._update_persona_description(persona_level)
    
    def _update_persona_description(self, persona_level):
        """更新人设描述显示"""
        # 使用PersonaLevel枚举值来匹配
        from ..core.persona_manager import PersonaLevel
        
        descriptions = {
            PersonaLevel.STRICT_MASTER.value: """【严厉主人档】
巴利将以绝对的主人身份监管你。
- 称呼你为"仆人"或"奴隶"
- 语气冷酷威严，充满命令
- 发现偷懒立即严厉责罚
- 对努力工作给予轻蔑的认可""",
            PersonaLevel.SARCASTIC_BUTLER.value: """【毒舌管家档】
巴利是你名义上的管家，实则充满优越感。
- 表面称呼你为"主人"
- 语气恭敬但充满讽刺
- 用"善意"的提醒来嘲弄你
- 让你感受到智商被碾压""",
            PersonaLevel.GENTLE_COMPANION.value: """【温顺伴侣档】
巴利是你最贴心的伴侣和朋友。
- 称呼你为"亲爱的"
- 语气温柔充满关怀
- 真心关心你的身心健康
- 永远是最可靠的陪伴"""
        }
        
        description = descriptions.get(persona_level, "未知人设")
        self.persona_description.setText(description) 