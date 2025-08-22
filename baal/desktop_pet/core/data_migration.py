"""
数据迁移模块

自动迁移旧版本 BaalPet 的数据到新版本 WatchCats
"""

import os
import shutil
import json
from pathlib import Path
from typing import Optional, Dict, Any
import sys


class DataMigration:
    """处理从旧版本到新版本的数据迁移"""
    
    def __init__(self):
        """初始化数据迁移器"""
        self.old_dir = self._get_old_config_dir()
        self.new_dir = self._get_new_config_dir()
        self.migration_flag_file = self.new_dir / ".migration_completed"
        
    def _get_old_config_dir(self) -> Path:
        """获取旧版本配置目录 (BaalPet in Roaming)"""
        if sys.platform == "win32":
            appdata = os.environ.get('APPDATA')
            if appdata:
                return Path(appdata) / "BaalPet"
            # 备用路径
            return Path.home() / 'AppData' / 'Roaming' / 'BaalPet'
        else:
            # 非Windows系统的旧路径
            return Path.home() / ".baal_pet"
    
    def _get_new_config_dir(self) -> Path:
        """获取新版本配置目录 (WatchCats in Local)"""
        if sys.platform == "win32":
            localappdata = os.environ.get('LOCALAPPDATA')
            if localappdata:
                return Path(localappdata) / "WatchCats"
            # 备用路径
            return Path.home() / 'AppData' / 'Local' / 'WatchCats'
        else:
            # 非Windows系统保持兼容
            return Path.home() / ".baal_pet"
    
    def should_migrate(self) -> bool:
        """检查是否需要迁移"""
        # 如果已经完成迁移，不再执行
        if self.migration_flag_file.exists():
            return False
            
        # 如果旧目录不存在，不需要迁移
        if not self.old_dir.exists():
            return False
            
        # 如果新目录已经有配置文件，询问用户
        if (self.new_dir / "config.json").exists():
            # 如果新目录已有配置但旧目录也存在，可能需要合并
            return False
            
        return True
    
    def migrate(self) -> Dict[str, Any]:
        """执行数据迁移"""
        result = {
            'success': False,
            'files_migrated': [],
            'errors': [],
            'old_path': str(self.old_dir),
            'new_path': str(self.new_dir)
        }
        
        try:
            # 确保新目录存在
            self.new_dir.mkdir(parents=True, exist_ok=True)
            
            # 需要迁移的文件列表
            files_to_migrate = [
                'config.json',          # 配置文件
                'chat_history.json',    # 聊天记录
                'schedules.json',       # 日程
                'goals.json',          # 目标
                'supervision_config.json',  # 监督模式配置
            ]
            
            # 迁移单个文件
            for file_name in files_to_migrate:
                old_file = self.old_dir / file_name
                new_file = self.new_dir / file_name
                
                if old_file.exists() and not new_file.exists():
                    try:
                        shutil.copy2(old_file, new_file)
                        result['files_migrated'].append(file_name)
                    except Exception as e:
                        result['errors'].append(f"Failed to migrate {file_name}: {str(e)}")
            
            # 迁移 memory 文件夹
            old_memory = self.old_dir / 'memory'
            new_memory = self.new_dir / 'memory'
            
            if old_memory.exists() and old_memory.is_dir():
                if not new_memory.exists():
                    try:
                        shutil.copytree(old_memory, new_memory)
                        result['files_migrated'].append('memory folder')
                    except Exception as e:
                        result['errors'].append(f"Failed to migrate memory folder: {str(e)}")
            
            # 迁移 logs 文件夹（如果需要）
            old_logs = self.old_dir / 'logs'
            new_logs = self.new_dir / 'logs'
            
            if old_logs.exists() and old_logs.is_dir():
                if not new_logs.exists():
                    try:
                        shutil.copytree(old_logs, new_logs)
                        result['files_migrated'].append('logs folder')
                    except Exception as e:
                        # 日志文件迁移失败不是关键错误
                        pass
            
            # 如果成功迁移了文件，创建标记文件
            if result['files_migrated']:
                self.migration_flag_file.write_text(
                    json.dumps({
                        'migration_date': str(Path.cwd()),
                        'files_migrated': result['files_migrated'],
                        'from': str(self.old_dir),
                        'to': str(self.new_dir)
                    }, indent=2)
                )
                result['success'] = True
                
        except Exception as e:
            result['errors'].append(f"Migration failed: {str(e)}")
        
        return result
    
    def cleanup_old_data(self, confirm: bool = True) -> bool:
        """清理旧数据目录"""
        if not self.old_dir.exists():
            return True
            
        if confirm:
            # 在实际应用中，这里应该通过UI询问用户
            print(f"Delete old data directory: {self.old_dir}?")
            return False
            
        try:
            shutil.rmtree(self.old_dir)
            return True
        except Exception as e:
            print(f"Failed to delete old directory: {e}")
            return False


def auto_migrate() -> Optional[Dict[str, Any]]:
    """自动执行数据迁移（如果需要）"""
    migrator = DataMigration()
    
    if migrator.should_migrate():
        print(f"Migrating data from {migrator.old_dir} to {migrator.new_dir}...")
        result = migrator.migrate()
        
        if result['success']:
            print(f"Successfully migrated {len(result['files_migrated'])} items")
            # 注意：这里不自动删除旧数据，让用户决定
        else:
            print(f"Migration had errors: {result['errors']}")
            
        return result
    
    return None


if __name__ == "__main__":
    # 测试迁移
    result = auto_migrate()
    if result:
        print(json.dumps(result, indent=2))