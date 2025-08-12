"""
持久化存储层

使用JSON文件存储日程数据，支持自动保存和加载。
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from .models import Schedule


class ScheduleStorage:
    """日程存储管理器
    
    使用JSON文件进行持久化存储，支持自动保存和加载。
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """初始化存储管理器
        
        Args:
            storage_path: 存储文件路径，默认为当前目录下的schedules.json
        """
        if storage_path is None:
            # 默认存储在用户主目录下的.baal_scheduler文件夹中
            home_dir = Path.home()
            storage_dir = home_dir / '.baal_scheduler'
            storage_dir.mkdir(exist_ok=True)
            storage_path = str(storage_dir / 'schedules.json')
            
            # 确保Windows路径正确处理
            if os.name == 'nt':  # Windows
                storage_path = storage_path.replace('/', '\\')
        
        self.storage_path = storage_path
        self.logger = logging.getLogger(__name__)
        
        # 确保存储目录存在
        storage_dir = os.path.dirname(self.storage_path)
        if storage_dir:
            os.makedirs(storage_dir, exist_ok=True)
    
    def save_schedules(self, schedules: List[Schedule]) -> bool:
        """保存日程列表到文件
        
        Args:
            schedules: 日程列表
            
        Returns:
            是否保存成功
        """
        try:
            # 转换为可序列化的格式
            data = {
                'version': '1.0',
                'updated_at': datetime.now().isoformat(),
                'schedules': [schedule.to_dict() for schedule in schedules]
            }
            
            # 写入文件（使用临时文件避免损坏）
            temp_path = f"{self.storage_path}.tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 原子性替换文件
            if os.path.exists(self.storage_path):
                os.replace(temp_path, self.storage_path)
            else:
                os.rename(temp_path, self.storage_path)
            
            self.logger.info(f"成功保存 {len(schedules)} 个日程到 {self.storage_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存日程失败: {e}")
            # 清理临时文件
            temp_path = f"{self.storage_path}.tmp"
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False
    
    def load_schedules(self) -> List[Schedule]:
        """从文件加载日程列表
        
        Returns:
            日程列表，如果文件不存在或读取失败则返回空列表
        """
        try:
            if not os.path.exists(self.storage_path):
                self.logger.info(f"存储文件不存在: {self.storage_path}")
                return []
            
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查版本兼容性
            version = data.get('version', '1.0')
            if version != '1.0':
                self.logger.warning(f"存储文件版本不匹配: {version}")
            
            # 反序列化日程
            schedules = []
            for schedule_data in data.get('schedules', []):
                try:
                    schedule = Schedule.from_dict(schedule_data)
                    schedules.append(schedule)
                except Exception as e:
                    self.logger.error(f"加载日程失败: {e}, 数据: {schedule_data}")
            
            self.logger.info(f"成功加载 {len(schedules)} 个日程")
            return schedules
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {e}")
            return []
        except Exception as e:
            self.logger.error(f"加载日程失败: {e}")
            return []
    
    def backup(self) -> bool:
        """创建存储文件的备份
        
        Returns:
            是否备份成功
        """
        try:
            if not os.path.exists(self.storage_path):
                return True
            
            # 创建带时间戳的备份文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{self.storage_path}.backup_{timestamp}"
            
            # 复制文件
            with open(self.storage_path, 'r', encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            self.logger.info(f"创建备份成功: {backup_path}")
            
            # 清理旧备份（保留最近5个）
            self._cleanup_old_backups()
            
            return True
            
        except Exception as e:
            self.logger.error(f"创建备份失败: {e}")
            return False
    
    def _cleanup_old_backups(self, keep_count: int = 5):
        """清理旧的备份文件
        
        Args:
            keep_count: 保留的备份数量
        """
        try:
            # 获取所有备份文件
            storage_dir = os.path.dirname(self.storage_path)
            base_name = os.path.basename(self.storage_path)
            backup_pattern = f"{base_name}.backup_"
            
            backup_files = []
            for filename in os.listdir(storage_dir):
                if filename.startswith(backup_pattern):
                    full_path = os.path.join(storage_dir, filename)
                    backup_files.append((full_path, os.path.getctime(full_path)))
            
            # 按创建时间排序
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # 删除超过保留数量的备份
            for backup_path, _ in backup_files[keep_count:]:
                os.remove(backup_path)
                self.logger.info(f"删除旧备份: {backup_path}")
                
        except Exception as e:
            self.logger.error(f"清理备份失败: {e}")
    
    def export_to_dict(self, schedules: List[Schedule]) -> Dict[str, Any]:
        """导出日程为字典格式
        
        Args:
            schedules: 日程列表
            
        Returns:
            包含所有日程数据的字典
        """
        return {
            'version': '1.0',
            'exported_at': datetime.now().isoformat(),
            'schedules': [schedule.to_dict() for schedule in schedules]
        }
    
    def import_from_dict(self, data: Dict[str, Any]) -> List[Schedule]:
        """从字典导入日程
        
        Args:
            data: 包含日程数据的字典
            
        Returns:
            导入的日程列表
        """
        schedules = []
        for schedule_data in data.get('schedules', []):
            try:
                schedule = Schedule.from_dict(schedule_data)
                schedules.append(schedule)
            except Exception as e:
                self.logger.error(f"导入日程失败: {e}, 数据: {schedule_data}")
        
        return schedules 