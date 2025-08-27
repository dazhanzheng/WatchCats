"""
应用分类管理对话框
允许用户添加、编辑和删除应用分类规则
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QListWidget, QListWidgetItem,
    QGroupBox, QComboBox, QCheckBox, QTextEdit,
    QMessageBox, QFileDialog, QSplitter, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor
from typing import List, Dict, Optional

from ..core.category_manager import CategoryManager


class CategoryDialog(QDialog):
    """应用分类管理对话框"""
    
    # 信号：分类规则已更新
    categories_updated = pyqtSignal()
    
    def __init__(self, parent=None):
        """初始化对话框"""
        super().__init__(parent)
        self.category_manager = CategoryManager()
        self.current_category = None
        self.init_ui()
        self.load_categories()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("📊 应用分类管理")
        self.setModal(True)
        self.setMinimumSize(900, 600)
        
        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                min-height: 28px;
                border-radius: 4px;
                padding: 0 10px;
            }
            QListWidget, QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("🎯 自定义应用分类规则")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 主要内容区域（使用分割器）
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：分类列表
        left_widget = QGroupBox("分类列表")
        left_layout = QVBoxLayout()
        
        # 分类列表
        self.category_list = QListWidget()
        self.category_list.itemSelectionChanged.connect(self.on_category_selected)
        left_layout.addWidget(self.category_list)
        
        # 列表操作按钮
        list_buttons = QHBoxLayout()
        
        self.add_category_btn = QPushButton("➕ 新建")
        self.add_category_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.add_category_btn.clicked.connect(self.add_new_category)
        list_buttons.addWidget(self.add_category_btn)
        
        self.delete_category_btn = QPushButton("🗑 删除")
        self.delete_category_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.delete_category_btn.clicked.connect(self.delete_category)
        self.delete_category_btn.setEnabled(False)
        list_buttons.addWidget(self.delete_category_btn)
        
        left_layout.addLayout(list_buttons)
        left_widget.setLayout(left_layout)
        
        # 右侧：分类详情编辑
        right_widget = QGroupBox("分类详情")
        right_layout = QVBoxLayout()
        
        # 分类名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("名称:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("例如：工作/我的项目")
        name_layout.addWidget(self.name_edit)
        right_layout.addLayout(name_layout)
        
        # 分类路径
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("分类路径:"))
        self.main_category = QComboBox()
        self.main_category.setEditable(True)
        self.main_category.addItems(["工作", "学习", "娱乐", "通讯", "浏览器", "系统", "其他"])
        path_layout.addWidget(self.main_category)
        
        path_layout.addWidget(QLabel(">"))
        self.sub_category = QLineEdit()
        self.sub_category.setPlaceholderText("子分类（可选）")
        path_layout.addWidget(self.sub_category)
        right_layout.addLayout(path_layout)
        
        # 描述
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("描述:"))
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        self.description_edit.setPlaceholderText("对这个分类的简短描述...")
        desc_layout.addWidget(self.description_edit)
        right_layout.addLayout(desc_layout)
        
        # 生产力分类
        productivity_layout = QHBoxLayout()
        self.is_productive_check = QCheckBox("标记为生产性活动")
        self.is_productive_check.setToolTip("勾选表示这是有助于提高生产力的活动")
        productivity_layout.addWidget(self.is_productive_check)
        productivity_layout.addStretch()
        right_layout.addLayout(productivity_layout)
        
        # 规则列表
        rules_label = QLabel("匹配规则:")
        right_layout.addWidget(rules_label)
        
        # 规则表格
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(4)
        self.rules_table.setHorizontalHeaderLabels(["类型", "匹配文本", "大小写", "操作"])
        self.rules_table.horizontalHeader().setStretchLastSection(False)
        self.rules_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.rules_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        right_layout.addWidget(self.rules_table)
        
        # 添加规则
        add_rule_layout = QHBoxLayout()
        
        self.rule_type = QComboBox()
        self.rule_type.addItems(["任意", "应用名", "窗口标题"])
        self.rule_type.setFixedWidth(100)
        add_rule_layout.addWidget(self.rule_type)
        
        self.rule_pattern = QLineEdit()
        self.rule_pattern.setPlaceholderText("输入要匹配的文本...")
        add_rule_layout.addWidget(self.rule_pattern)
        
        self.case_sensitive = QCheckBox("区分大小写")
        add_rule_layout.addWidget(self.case_sensitive)
        
        self.add_rule_btn = QPushButton("➕ 添加规则")
        self.add_rule_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.add_rule_btn.clicked.connect(self.add_rule)
        add_rule_layout.addWidget(self.add_rule_btn)
        
        right_layout.addLayout(add_rule_layout)
        
        # 测试区域
        test_group = QGroupBox("测试分类")
        test_layout = QVBoxLayout()
        
        test_input_layout = QHBoxLayout()
        test_input_layout.addWidget(QLabel("应用:"))
        self.test_app = QLineEdit()
        self.test_app.setPlaceholderText("例如：Chrome")
        test_input_layout.addWidget(self.test_app)
        
        test_input_layout.addWidget(QLabel("标题:"))
        self.test_title = QLineEdit()
        self.test_title.setPlaceholderText("例如：GitHub - Code")
        test_input_layout.addWidget(self.test_title)
        
        self.test_btn = QPushButton("🧪 测试")
        self.test_btn.clicked.connect(self.test_categorization)
        test_input_layout.addWidget(self.test_btn)
        
        test_layout.addLayout(test_input_layout)
        
        self.test_result = QLabel("测试结果将显示在这里")
        self.test_result.setStyleSheet("""
            padding: 10px;
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 4px;
        """)
        test_layout.addWidget(self.test_result)
        
        test_group.setLayout(test_layout)
        right_layout.addWidget(test_group)
        
        # 保存按钮
        self.save_btn = QPushButton("💾 保存当前分类")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.save_btn.clicked.connect(self.save_current_category)
        self.save_btn.setEnabled(False)
        right_layout.addWidget(self.save_btn)
        
        right_widget.setLayout(right_layout)
        
        # 添加到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        
        # 底部按钮
        bottom_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("📥 导入")
        self.import_btn.clicked.connect(self.import_categories)
        bottom_layout.addWidget(self.import_btn)
        
        self.export_btn = QPushButton("📤 导出")
        self.export_btn.clicked.connect(self.export_categories)
        bottom_layout.addWidget(self.export_btn)
        
        bottom_layout.addStretch()
        
        self.close_btn = QPushButton("✅ 完成")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.close_btn.clicked.connect(self.accept)
        bottom_layout.addWidget(self.close_btn)
        
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
    
    def load_categories(self):
        """加载分类列表"""
        self.category_list.clear()
        categories = self.category_manager.get_categories_list()
        
        for cat in categories:
            item = QListWidgetItem(cat['name'])
            item.setData(Qt.ItemDataRole.UserRole, cat)
            self.category_list.addItem(item)
    
    def on_category_selected(self):
        """选中分类时加载详情"""
        current_item = self.category_list.currentItem()
        if not current_item:
            self.clear_details()
            return
        
        self.current_category = current_item.data(Qt.ItemDataRole.UserRole)
        self.load_category_details(self.current_category)
        self.delete_category_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
    
    def load_category_details(self, category: Dict):
        """加载分类详情到编辑区域"""
        self.name_edit.setText(category['name'])
        
        # 设置分类路径
        path = category['category_path']
        if path:
            self.main_category.setEditText(path[0])
            if len(path) > 1:
                self.sub_category.setText(path[1])
            else:
                self.sub_category.clear()
        
        self.description_edit.setText(category.get('description', ''))
        
        # 设置生产力标记
        is_productive = category.get('is_productive')
        if is_productive is None:
            self.is_productive_check.setCheckState(Qt.CheckState.PartiallyChecked)
        else:
            self.is_productive_check.setChecked(is_productive)
        
        # 加载规则列表
        self.rules_table.setRowCount(0)
        for rule in category.get('rules', []):
            self.add_rule_to_table(rule)
    
    def add_rule_to_table(self, rule: Dict):
        """添加规则到表格"""
        row = self.rules_table.rowCount()
        self.rules_table.insertRow(row)
        
        # 类型
        type_map = {'any': '任意', 'app': '应用名', 'title': '窗口标题'}
        type_item = QTableWidgetItem(type_map.get(rule.get('type', 'any'), '任意'))
        self.rules_table.setItem(row, 0, type_item)
        
        # 模式
        pattern_item = QTableWidgetItem(rule['pattern'])
        self.rules_table.setItem(row, 1, pattern_item)
        
        # 大小写
        case_item = QTableWidgetItem('是' if rule.get('case_sensitive', False) else '否')
        self.rules_table.setItem(row, 2, case_item)
        
        # 删除按钮
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(lambda: self.delete_rule(row))
        self.rules_table.setCellWidget(row, 3, delete_btn)
    
    def add_rule(self):
        """添加新规则"""
        pattern = self.rule_pattern.text().strip()
        if not pattern:
            QMessageBox.warning(self, "提示", "请输入匹配文本")
            return
        
        type_map = {"任意": "any", "应用名": "app", "窗口标题": "title"}
        rule = {
            "type": type_map[self.rule_type.currentText()],
            "pattern": pattern,
            "case_sensitive": self.case_sensitive.isChecked()
        }
        
        self.add_rule_to_table(rule)
        
        # 清空输入
        self.rule_pattern.clear()
        self.case_sensitive.setChecked(False)
    
    def delete_rule(self, row: int):
        """删除规则"""
        self.rules_table.removeRow(row)
        # 更新其他行的删除按钮
        for i in range(self.rules_table.rowCount()):
            delete_btn = self.rules_table.cellWidget(i, 3)
            if delete_btn:
                delete_btn.clicked.disconnect()
                delete_btn.clicked.connect(lambda _, r=i: self.delete_rule(r))
    
    def clear_details(self):
        """清空详情编辑区域"""
        self.name_edit.clear()
        self.main_category.setEditText("")
        self.sub_category.clear()
        self.description_edit.clear()
        self.is_productive_check.setChecked(False)
        self.rules_table.setRowCount(0)
        self.delete_category_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
    
    def add_new_category(self):
        """添加新分类"""
        self.clear_details()
        self.name_edit.setText("新分类")
        self.name_edit.selectAll()
        self.name_edit.setFocus()
        self.current_category = None
        self.save_btn.setEnabled(True)
        
        # 取消列表选择
        self.category_list.clearSelection()
    
    def save_current_category(self):
        """保存当前编辑的分类"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请输入分类名称")
            return
        
        # 构建分类路径
        main_cat = self.main_category.currentText().strip()
        sub_cat = self.sub_category.text().strip()
        
        if not main_cat:
            QMessageBox.warning(self, "提示", "请选择主分类")
            return
        
        category_path = [main_cat]
        if sub_cat:
            category_path.append(sub_cat)
        
        # 收集规则
        rules = []
        for row in range(self.rules_table.rowCount()):
            type_item = self.rules_table.item(row, 0)
            pattern_item = self.rules_table.item(row, 1)
            case_item = self.rules_table.item(row, 2)
            
            if type_item and pattern_item:
                type_map = {"任意": "any", "应用名": "app", "窗口标题": "title"}
                rule = {
                    "type": type_map.get(type_item.text(), "any"),
                    "pattern": pattern_item.text(),
                    "case_sensitive": case_item.text() == '是'
                }
                rules.append(rule)
        
        if not rules:
            QMessageBox.warning(self, "提示", "请至少添加一条匹配规则")
            return
        
        # 确定生产力标记
        is_productive = None
        if self.is_productive_check.checkState() != Qt.CheckState.PartiallyChecked:
            is_productive = self.is_productive_check.isChecked()
        
        # 保存分类
        success = self.category_manager.add_category(
            name=name,
            category_path=category_path,
            rules=rules,
            description=self.description_edit.toPlainText().strip(),
            is_productive=is_productive
        )
        
        if success:
            QMessageBox.information(self, "成功", f"分类 '{name}' 已保存")
            self.load_categories()
            self.categories_updated.emit()
            
            # 选中刚保存的分类
            for i in range(self.category_list.count()):
                item = self.category_list.item(i)
                if item.text() == name:
                    self.category_list.setCurrentItem(item)
                    break
        else:
            QMessageBox.warning(self, "错误", "保存分类失败")
    
    def delete_category(self):
        """删除选中的分类"""
        current_item = self.category_list.currentItem()
        if not current_item:
            return
        
        name = current_item.text()
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除分类 '{name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.category_manager.remove_category(name):
                self.load_categories()
                self.clear_details()
                self.categories_updated.emit()
                QMessageBox.information(self, "成功", f"分类 '{name}' 已删除")
    
    def test_categorization(self):
        """测试分类"""
        app_name = self.test_app.text().strip()
        window_title = self.test_title.text().strip()
        
        if not app_name and not window_title:
            self.test_result.setText("请输入应用名或窗口标题")
            return
        
        # 测试所有分类
        matched_category = self.category_manager.test_categorization(app_name, window_title)
        
        if matched_category:
            category_str = " > ".join(matched_category)
            self.test_result.setText(f"✅ 匹配分类: {category_str}")
            self.test_result.setStyleSheet("""
                padding: 10px;
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 4px;
                color: #155724;
            """)
        else:
            self.test_result.setText("❌ 未匹配到任何分类")
            self.test_result.setStyleSheet("""
                padding: 10px;
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                border-radius: 4px;
                color: #721c24;
            """)
    
    def import_categories(self):
        """导入分类配置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择要导入的分类配置",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            if self.category_manager.import_categories(file_path):
                self.load_categories()
                self.categories_updated.emit()
                QMessageBox.information(self, "成功", "分类配置已导入")
            else:
                QMessageBox.warning(self, "错误", "导入失败")
    
    def export_categories(self):
        """导出分类配置"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出分类配置",
            "categories.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            if self.category_manager.export_categories(file_path):
                QMessageBox.information(self, "成功", f"分类配置已导出到:\n{file_path}")
            else:
                QMessageBox.warning(self, "错误", "导出失败")