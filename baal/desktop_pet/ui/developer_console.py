"""
开发者控制台窗口

显示实时日志信息，用于调试和监控
"""

import sys
import logging
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QComboBox, QLabel, QCheckBox,
                             QSplitter, QTabWidget, QWidget, QLineEdit)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QFont
from collections import deque
from typing import Dict, List, Optional
import json


class LogHandler(logging.Handler):
    """自定义日志处理器，将日志发送到控制台"""
    
    def __init__(self, console_widget):
        super().__init__()
        self.console_widget = console_widget
        
    def emit(self, record):
        """发送日志记录"""
        try:
            msg = self.format(record)
            self.console_widget.add_log(record.levelname, msg, record.name)
        except Exception:
            self.handleError(record)


class DeveloperConsole(QDialog):
    """开发者控制台窗口"""
    
    # 日志级别颜色映射
    LEVEL_COLORS = {
        'DEBUG': QColor(128, 128, 128),
        'INFO': QColor(0, 0, 0),
        'WARNING': QColor(255, 140, 0),
        'ERROR': QColor(255, 0, 0),
        'CRITICAL': QColor(139, 0, 0),
        'SUPERVISION': QColor(0, 128, 0),  # 监督模式专用颜色
        'PERFORMANCE': QColor(0, 0, 255),  # 性能日志专用颜色
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("开发者控制台")
        self.setGeometry(100, 100, 1000, 700)
        
        # 日志缓存
        self.log_buffer = deque(maxlen=10000)  # 最多保存10000条日志
        self.filtered_logs = []
        
        # 日志处理器
        self.log_handler = None
        
        # 初始化UI
        self._init_ui()
        
        # 设置日志处理器
        self._setup_logging()
        
        # 启动自动刷新
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.refresh_logs)
        self.auto_refresh_timer.start(500)  # 每500ms刷新一次
        
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 顶部控制栏
        control_layout = QHBoxLayout()
        
        # 日志级别过滤
        control_layout.addWidget(QLabel("日志级别:"))
        self.level_filter = QComboBox()
        self.level_filter.addItems(['ALL', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
        self.level_filter.setCurrentText('ALL')
        self.level_filter.currentTextChanged.connect(self.apply_filter)
        control_layout.addWidget(self.level_filter)
        
        # 模块过滤
        control_layout.addWidget(QLabel("模块:"))
        self.module_filter = QComboBox()
        self.module_filter.addItems(['ALL', 'supervision', 'llm', 'ui', 'core', 'scheduler'])
        self.module_filter.setCurrentText('ALL')
        self.module_filter.currentTextChanged.connect(self.apply_filter)
        control_layout.addWidget(self.module_filter)
        
        # 搜索框
        control_layout.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索...")
        self.search_input.textChanged.connect(self.apply_filter)
        control_layout.addWidget(self.search_input)
        
        # 自动滚动
        self.auto_scroll_check = QCheckBox("自动滚动")
        self.auto_scroll_check.setChecked(True)
        control_layout.addWidget(self.auto_scroll_check)
        
        # 清空按钮
        clear_btn = QPushButton("清空日志")
        clear_btn.clicked.connect(self.clear_logs)
        control_layout.addWidget(clear_btn)
        
        # 导出按钮
        export_btn = QPushButton("导出日志")
        export_btn.clicked.connect(self.export_logs)
        control_layout.addWidget(export_btn)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        
        # 主日志选项卡
        self.main_log_widget = self._create_log_widget()
        self.tab_widget.addTab(self.main_log_widget, "主日志")
        
        # 监督模式日志选项卡
        self.supervision_log_widget = self._create_log_widget()
        self.tab_widget.addTab(self.supervision_log_widget, "监督模式")
        
        # 性能日志选项卡
        self.performance_log_widget = self._create_log_widget()
        self.tab_widget.addTab(self.performance_log_widget, "性能监控")
        
        # 统计信息选项卡
        self.stats_widget = self._create_stats_widget()
        self.tab_widget.addTab(self.stats_widget, "统计信息")
        
        layout.addWidget(self.tab_widget)
        
        # 状态栏
        self.status_label = QLabel("日志数量: 0")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def _create_log_widget(self):
        """创建日志显示组件"""
        log_text = QTextEdit()
        log_text.setReadOnly(True)
        log_text.setFont(QFont("Consolas", 9))
        return log_text
        
    def _create_stats_widget(self):
        """创建统计信息组件"""
        stats_text = QTextEdit()
        stats_text.setReadOnly(True)
        stats_text.setFont(QFont("Consolas", 10))
        return stats_text
        
    def _setup_logging(self):
        """设置日志处理器"""
        # 获取根日志记录器
        root_logger = logging.getLogger()
        
        # 创建并添加自定义处理器
        self.log_handler = LogHandler(self)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        self.log_handler.setFormatter(formatter)
        root_logger.addHandler(self.log_handler)
        
        # 设置日志级别为DEBUG以捕获所有日志
        root_logger.setLevel(logging.DEBUG)
        
    def add_log(self, level: str, message: str, module: str = ''):
        """添加日志到缓存"""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'module': module,
            'message': message
        }
        self.log_buffer.append(log_entry)
        
    def refresh_logs(self):
        """刷新日志显示"""
        # 应用过滤器
        self.apply_filter()
        
        # 更新统计信息
        self.update_stats()
        
    def apply_filter(self):
        """应用过滤器"""
        level_filter = self.level_filter.currentText()
        module_filter = self.module_filter.currentText()
        search_text = self.search_input.text().lower()
        
        # 过滤日志
        self.filtered_logs = []
        for log in self.log_buffer:
            # 级别过滤
            if level_filter != 'ALL' and log['level'] != level_filter:
                continue
            
            # 模块过滤
            if module_filter != 'ALL':
                if module_filter not in log['module'].lower():
                    continue
            
            # 搜索过滤
            if search_text and search_text not in log['message'].lower():
                continue
                
            self.filtered_logs.append(log)
        
        # 更新显示
        self.update_display()
        
    def update_display(self):
        """更新日志显示"""
        # 根据当前选项卡更新对应的日志显示
        current_tab = self.tab_widget.currentIndex()
        
        if current_tab == 0:  # 主日志
            self._update_log_widget(self.main_log_widget, self.filtered_logs)
        elif current_tab == 1:  # 监督模式
            supervision_logs = [log for log in self.filtered_logs 
                              if 'supervision' in log['module'].lower()]
            self._update_log_widget(self.supervision_log_widget, supervision_logs)
        elif current_tab == 2:  # 性能监控
            performance_logs = [log for log in self.filtered_logs 
                              if 'performance' in log['message'].lower() or
                                 'timer' in log['message'].lower()]
            self._update_log_widget(self.performance_log_widget, performance_logs)
        
        # 更新状态栏
        self.status_label.setText(f"日志数量: {len(self.filtered_logs)} / {len(self.log_buffer)}")
        
    def _update_log_widget(self, widget: QTextEdit, logs: List[Dict]):
        """更新日志组件内容"""
        # 保存当前滚动位置
        scrollbar = widget.verticalScrollBar()
        was_at_bottom = scrollbar.value() >= scrollbar.maximum() - 10
        
        # 清空并重新填充
        widget.clear()
        cursor = widget.textCursor()
        
        for log in logs:
            # 设置颜色
            color = self.LEVEL_COLORS.get(log['level'], QColor(0, 0, 0))
            
            # 格式化日志行
            log_line = f"[{log['timestamp']}] [{log['level']:8}] [{log['module']:15}] {log['message']}\n"
            
            # 设置格式并插入
            format = QTextCharFormat()
            format.setForeground(color)
            cursor.insertText(log_line, format)
        
        # 自动滚动到底部
        if self.auto_scroll_check.isChecked() and was_at_bottom:
            scrollbar.setValue(scrollbar.maximum())
            
    def update_stats(self):
        """更新统计信息"""
        stats = {
            'total_logs': len(self.log_buffer),
            'levels': {},
            'modules': {},
            'recent_errors': []
        }
        
        # 统计日志级别
        for log in self.log_buffer:
            level = log['level']
            stats['levels'][level] = stats['levels'].get(level, 0) + 1
            
            module = log['module'].split('.')[0] if log['module'] else 'unknown'
            stats['modules'][module] = stats['modules'].get(module, 0) + 1
            
            # 收集最近的错误
            if log['level'] in ['ERROR', 'CRITICAL']:
                stats['recent_errors'].append(log)
                
        # 只保留最近10个错误
        stats['recent_errors'] = stats['recent_errors'][-10:]
        
        # 格式化统计信息
        stats_text = f"""
========== 日志统计 ==========
总日志数: {stats['total_logs']}

========== 级别分布 ==========
"""
        for level, count in sorted(stats['levels'].items()):
            stats_text += f"{level:10}: {count:5} ({count*100/max(stats['total_logs'],1):.1f}%)\n"
            
        stats_text += "\n========== 模块分布 ==========\n"
        for module, count in sorted(stats['modules'].items(), key=lambda x: x[1], reverse=True)[:10]:
            stats_text += f"{module:15}: {count:5}\n"
            
        if stats['recent_errors']:
            stats_text += "\n========== 最近错误 ==========\n"
            for error in stats['recent_errors']:
                stats_text += f"[{error['timestamp']}] {error['message'][:100]}...\n"
                
        self.stats_widget.setText(stats_text)
        
    def clear_logs(self):
        """清空日志"""
        self.log_buffer.clear()
        self.filtered_logs.clear()
        self.main_log_widget.clear()
        self.supervision_log_widget.clear()
        self.performance_log_widget.clear()
        self.status_label.setText("日志数量: 0")
        
    def export_logs(self):
        """导出日志到文件"""
        from PyQt6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出日志", 
            f"baal_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;JSON Files (*.json)"
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    # 导出为JSON
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(list(self.log_buffer), f, ensure_ascii=False, indent=2)
                else:
                    # 导出为文本
                    with open(filename, 'w', encoding='utf-8') as f:
                        for log in self.log_buffer:
                            f.write(f"[{log['timestamp']}] [{log['level']:8}] [{log['module']:15}] {log['message']}\n")
                            
                self.status_label.setText(f"日志已导出到: {filename}")
            except Exception as e:
                self.status_label.setText(f"导出失败: {str(e)}")
                
    def closeEvent(self, event):
        """关闭事件"""
        # 移除日志处理器
        if self.log_handler:
            root_logger = logging.getLogger()
            root_logger.removeHandler(self.log_handler)
        
        # 停止定时器
        self.auto_refresh_timer.stop()
        
        event.accept()