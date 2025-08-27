"""
应用分类管理器
管理用户自定义的应用分类规则
"""

import json
import os
import re
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
import logging

from aw_transform.classify import Rule

logger = logging.getLogger(__name__)


class CategoryManager:
    """应用分类管理器"""
    
    def __init__(self):
        """初始化分类管理器"""
        self.config_dir = self._get_config_dir()
        self.config_file = os.path.join(self.config_dir, "categories.json")
        self.user_categories = []
        self.load_categories()
    
    def _get_config_dir(self) -> str:
        """获取配置目录"""
        if os.name == 'nt':  # Windows
            base_dir = os.environ.get('APPDATA', os.path.expanduser('~'))
            config_dir = os.path.join(base_dir, 'BaalPet')
        else:  # macOS/Linux
            config_dir = os.path.expanduser('~/.baal_pet')
        
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
        
        return config_dir
    
    def load_categories(self):
        """从配置文件加载用户自定义分类"""
        if not os.path.exists(self.config_file):
            self._save_default_categories()
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.user_categories = data.get('categories', [])
                logger.info(f"加载了 {len(self.user_categories)} 个用户分类规则")
        except Exception as e:
            logger.error(f"加载分类配置失败: {e}")
            self.user_categories = []
    
    def save_categories(self):
        """保存用户分类到配置文件"""
        try:
            data = {
                'categories': self.user_categories,
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"保存了 {len(self.user_categories)} 个分类规则")
            return True
        except Exception as e:
            logger.error(f"保存分类配置失败: {e}")
            return False
    
    def _save_default_categories(self):
        """保存默认分类（示例）"""
        default_categories = [
            {
                "name": "工作/我的项目",
                "category_path": ["工作", "我的项目"],
                "rules": [
                    {"type": "app", "pattern": "myproject", "case_sensitive": False},
                    {"type": "title", "pattern": "项目代码", "case_sensitive": False}
                ],
                "description": "我的项目相关活动",
                "is_productive": True
            },
            {
                "name": "学习/在线课程",
                "category_path": ["学习", "在线课程"],
                "rules": [
                    {"type": "title", "pattern": "慕课|MOOC|网课", "case_sensitive": False}
                ],
                "description": "在线学习平台",
                "is_productive": True
            }
        ]
        
        data = {
            'categories': default_categories,
            'updated_at': datetime.now().isoformat()
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存默认分类失败: {e}")
    
    def add_category(self, name: str, category_path: List[str], rules: List[Dict], 
                    description: str = "", is_productive: bool = None) -> bool:
        """
        添加新的分类规则
        
        Args:
            name: 分类名称（用于显示）
            category_path: 分类路径，如 ["工作", "开发"]
            rules: 规则列表，每个规则包含 type(app/title), pattern, case_sensitive
            description: 分类描述
            is_productive: 是否为生产性活动
        
        Returns:
            是否添加成功
        """
        try:
            new_category = {
                "name": name,
                "category_path": category_path,
                "rules": rules,
                "description": description,
                "is_productive": is_productive,
                "created_at": datetime.now().isoformat()
            }
            
            # 检查是否已存在同名分类
            for i, cat in enumerate(self.user_categories):
                if cat['name'] == name:
                    # 更新现有分类
                    self.user_categories[i] = new_category
                    logger.info(f"更新分类: {name}")
                    return self.save_categories()
            
            # 添加新分类
            self.user_categories.append(new_category)
            logger.info(f"添加新分类: {name}")
            return self.save_categories()
            
        except Exception as e:
            logger.error(f"添加分类失败: {e}")
            return False
    
    def remove_category(self, name: str) -> bool:
        """删除分类规则"""
        try:
            original_count = len(self.user_categories)
            self.user_categories = [cat for cat in self.user_categories if cat['name'] != name]
            
            if len(self.user_categories) < original_count:
                logger.info(f"删除分类: {name}")
                return self.save_categories()
            else:
                logger.warning(f"未找到分类: {name}")
                return False
                
        except Exception as e:
            logger.error(f"删除分类失败: {e}")
            return False
    
    def get_categories_list(self) -> List[Dict]:
        """获取所有用户分类列表"""
        return self.user_categories.copy()
    
    def get_aw_transform_rules(self) -> List[Tuple[List[str], Rule]]:
        """
        将用户分类转换为 aw_transform 可用的规则格式
        
        Returns:
            [(category_path, Rule), ...]
        """
        transform_rules = []
        
        for category in self.user_categories:
            category_path = category['category_path']
            
            # 为每个规则创建一个 Rule 对象
            for rule_config in category['rules']:
                pattern = rule_config['pattern']
                case_sensitive = rule_config.get('case_sensitive', False)
                rule_type = rule_config.get('type', 'any')  # app, title, or any
                
                # 构建正则表达式
                if not case_sensitive:
                    regex_pattern = f"(?i){re.escape(pattern)}"
                else:
                    regex_pattern = re.escape(pattern)
                
                # 如果指定了规则类型，可以在描述中说明
                # 但 Rule 类本身不区分，需要在模式中处理
                if rule_type == 'app':
                    # 可以在未来优化为只匹配 app 字段
                    pass
                elif rule_type == 'title':
                    # 可以在未来优化为只匹配 title 字段
                    pass
                
                try:
                    rule = Rule({'regex': regex_pattern})
                    transform_rules.append((category_path, rule))
                except Exception as e:
                    logger.error(f"创建规则失败 {pattern}: {e}")
        
        return transform_rules
    
    def test_categorization(self, app_name: str, window_title: str) -> Optional[List[str]]:
        """
        测试给定的应用和窗口标题会被分到哪个类别
        
        Args:
            app_name: 应用名称
            window_title: 窗口标题
            
        Returns:
            匹配的分类路径，如 ["工作", "开发"]
        """
        test_text = f"{app_name} {window_title}"
        
        for category in self.user_categories:
            for rule_config in category['rules']:
                pattern = rule_config['pattern']
                case_sensitive = rule_config.get('case_sensitive', False)
                rule_type = rule_config.get('type', 'any')
                
                # 根据规则类型选择要匹配的文本
                if rule_type == 'app':
                    text_to_match = app_name
                elif rule_type == 'title':
                    text_to_match = window_title
                else:
                    text_to_match = test_text
                
                # 执行匹配
                if case_sensitive:
                    if pattern in text_to_match:
                        return category['category_path']
                else:
                    if pattern.lower() in text_to_match.lower():
                        return category['category_path']
        
        return None
    
    def get_productivity_classification(self) -> Dict[str, bool]:
        """
        获取生产力分类映射
        
        Returns:
            {分类名称: 是否为生产性活动}
        """
        productivity_map = {}
        
        for category in self.user_categories:
            name = " > ".join(category['category_path'])
            is_productive = category.get('is_productive')
            if is_productive is not None:
                productivity_map[name] = is_productive
        
        return productivity_map
    
    def import_categories(self, file_path: str) -> bool:
        """从文件导入分类配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                imported = data.get('categories', [])
                
                # 合并导入的分类
                existing_names = {cat['name'] for cat in self.user_categories}
                
                for cat in imported:
                    if cat['name'] not in existing_names:
                        self.user_categories.append(cat)
                    else:
                        # 更新现有分类
                        for i, existing in enumerate(self.user_categories):
                            if existing['name'] == cat['name']:
                                self.user_categories[i] = cat
                                break
                
                self.save_categories()
                logger.info(f"导入了 {len(imported)} 个分类规则")
                return True
                
        except Exception as e:
            logger.error(f"导入分类失败: {e}")
            return False
    
    def export_categories(self, file_path: str) -> bool:
        """导出分类配置到文件"""
        try:
            data = {
                'categories': self.user_categories,
                'exported_at': datetime.now().isoformat()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"导出了 {len(self.user_categories)} 个分类规则到 {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出分类失败: {e}")
            return False