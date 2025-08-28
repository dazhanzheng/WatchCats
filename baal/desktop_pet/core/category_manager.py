"""
简化的工作软件管理器
只管理工作软件列表，用于生产力评估
"""

import json
import os
from typing import List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CategoryManager:
    """工作软件管理器"""
    
    def __init__(self):
        """初始化管理器"""
        self.config_dir = self._get_config_dir()
        self.config_file = os.path.join(self.config_dir, "work_apps.json")
        self.work_apps = []
        self.load_work_apps()
    
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
    
    def load_work_apps(self):
        """从配置文件加载工作软件列表"""
        if not os.path.exists(self.config_file):
            # 创建默认的工作软件列表
            self._save_default_work_apps()
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.work_apps = data.get('work_apps', [])
                logger.info(f"加载了 {len(self.work_apps)} 个工作软件")
        except Exception as e:
            logger.error(f"加载工作软件配置失败: {e}")
            self.work_apps = []
    
    def save_work_apps(self):
        """保存工作软件列表到配置文件"""
        try:
            data = {
                'work_apps': self.work_apps,
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"保存了 {len(self.work_apps)} 个工作软件")
            return True
        except Exception as e:
            logger.error(f"保存工作软件配置失败: {e}")
            return False
    
    def _save_default_work_apps(self):
        """保存默认的工作软件列表"""
        # 默认的工作软件列表
        default_apps = [
            "VSCode",
            "Visual Studio Code",
            "PyCharm",
            "IntelliJ IDEA",
            "Xcode",
            "Android Studio",
            "飞书",
            "钉钉",
            "企业微信",
            "Slack",
            "Microsoft Teams",
            "Zoom",
            "腾讯会议"
        ]
        
        data = {
            'work_apps': default_apps,
            'updated_at': datetime.now().isoformat()
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.work_apps = default_apps
            logger.info(f"创建了默认的工作软件列表 ({len(default_apps)}个)")
        except Exception as e:
            logger.error(f"保存默认工作软件失败: {e}")
    
    def add_work_app(self, app_name: str) -> bool:
        """
        添加工作软件
        
        Args:
            app_name: 软件名称
        
        Returns:
            是否添加成功
        """
        if app_name and app_name not in self.work_apps:
            self.work_apps.append(app_name)
            return self.save_work_apps()
        return False
    
    def remove_work_app(self, app_name: str) -> bool:
        """
        删除工作软件
        
        Args:
            app_name: 软件名称
        
        Returns:
            是否删除成功
        """
        if app_name in self.work_apps:
            self.work_apps.remove(app_name)
            return self.save_work_apps()
        return False
    
    def set_work_apps(self, apps: List[str]) -> bool:
        """
        设置工作软件列表（完全替换）
        
        Args:
            apps: 新的工作软件列表
        
        Returns:
            是否设置成功
        """
        self.work_apps = list(apps)  # 创建副本
        return self.save_work_apps()
    
    def get_work_apps(self) -> List[str]:
        """获取工作软件列表"""
        return self.work_apps.copy()
    
    def is_work_app(self, app_name: str) -> bool:
        """
        检查是否为工作软件
        
        Args:
            app_name: 软件名称
        
        Returns:
            是否为工作软件
        """
        if not app_name:
            return False
        
        # 不区分大小写的匹配
        app_lower = app_name.lower()
        for work_app in self.work_apps:
            if work_app.lower() in app_lower or app_lower in work_app.lower():
                return True
        
        return False
    
    def get_productivity_map(self) -> Dict[str, bool]:
        """
        获取生产力映射（用于兼容旧代码）
        
        Returns:
            应用名称到是否生产性的映射
        """
        # 所有工作软件都标记为生产性
        return {app: True for app in self.work_apps}
    
    # 兼容旧接口
    def get_productivity_classification(self) -> Dict[str, bool]:
        """兼容旧接口：获取生产力分类映射"""
        return self.get_productivity_map()
    
    def get_aw_transform_rules(self):
        """兼容旧接口：返回空规则列表（不再使用复杂的分类规则）"""
        return []
    
    def get_categories_list(self):
        """兼容旧接口：返回空列表"""
        return []