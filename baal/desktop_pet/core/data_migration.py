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
from datetime import datetime


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
            
            # 需要迁移的文件列表（包括文件名映射）
            files_to_migrate = [
                ('config.json', 'config.json'),          # 配置文件
                ('chat_history.json', 'conversation_history.json'),    # 聊天记录（重命名）
                ('conversation_history.json', 'conversation_history.json'),  # 新格式的聊天记录
                ('schedules.json', 'schedules.json'),       # 日程
                ('goals.json', 'goals.json'),          # 目标
                ('supervision_config.json', 'supervision_config.json'),  # 监督模式配置
            ]
            
            # 迁移单个文件
            for old_name, new_name in files_to_migrate:
                old_file = self.old_dir / old_name
                new_file = self.new_dir / new_name
                
                if old_file.exists() and not new_file.exists():
                    try:
                        # 先读取文件内容，确保可以访问
                        with open(old_file, 'rb') as f:
                            content = f.read()
                        
                        # 写入到新位置
                        with open(new_file, 'wb') as f:
                            f.write(content)
                        
                        # 复制文件权限和时间戳
                        shutil.copystat(old_file, new_file)
                        
                        if old_name != new_name:
                            result['files_migrated'].append(f"{old_name} -> {new_name}")
                        else:
                            result['files_migrated'].append(old_name)
                    except PermissionError as e:
                        result['errors'].append(f"Permission denied for {old_name}: {str(e)}")
                    except Exception as e:
                        result['errors'].append(f"Failed to migrate {old_name}: {str(e)}")
            
            # 迁移 memory 文件夹
            old_memory = self.old_dir / 'memory'
            new_memory = self.new_dir / 'memory'
            
            if old_memory.exists() and old_memory.is_dir():
                if not new_memory.exists():
                    try:
                        # 创建目标目录
                        new_memory.mkdir(parents=True, exist_ok=True)
                        
                        # 逐个复制文件，更容易处理权限问题
                        copied_count = 0
                        for item in old_memory.iterdir():
                            try:
                                if item.is_file():
                                    dest = new_memory / item.name
                                    with open(item, 'rb') as f:
                                        content = f.read()
                                    with open(dest, 'wb') as f:
                                        f.write(content)
                                    copied_count += 1
                            except Exception as e:
                                result['errors'].append(f"Failed to copy {item.name}: {str(e)}")
                        
                        if copied_count > 0:
                            result['files_migrated'].append(f'memory folder ({copied_count} files)')
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
                        'migration_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
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
        """清理旧数据目录
        
        注意：不建议自动删除，应该让用户确认新版本正常运行后手动删除
        """
        if not self.old_dir.exists():
            return True
            
        if confirm:
            # 在实际应用中，这里应该通过UI询问用户
            print(f"Old data directory: {self.old_dir}")
            print("It is recommended to keep the old data until you confirm the new version works properly.")
            print("You can manually delete it later.")
            return False
            
        try:
            # 创建一个标记文件，表示可以删除
            marker_file = self.old_dir / '.can_be_deleted'
            marker_file.write_text(f"This directory can be safely deleted.\nMigrated to: {self.new_dir}\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Marked old directory for deletion: {self.old_dir}")
            # 不实际删除，让用户手动删除
            return False
        except Exception as e:
            print(f"Failed to mark old directory: {e}")
            return False


def auto_migrate() -> Optional[Dict[str, Any]]:
    """自动执行数据迁移（如果需要）"""
    migrator = DataMigration()
    
    if migrator.should_migrate():
        print(f"Migrating data from {migrator.old_dir} to {migrator.new_dir}...")
        result = migrator.migrate()
        
        if result['success']:
            print(f"Successfully migrated {len(result['files_migrated'])} items")
            print(f"Old data preserved at: {migrator.old_dir}")
            print("You can manually delete the old folder after confirming everything works.")
            
            # 创建一个说明文件在旧目录
            try:
                readme_file = migrator.old_dir / 'README_MIGRATION.txt'
                readme_content = f"""数据迁移说明 / Data Migration Notice
=====================================

此文件夹包含旧版本 BaalPet 的数据。
This folder contains old BaalPet data.

数据已成功迁移到新位置：
Data has been migrated to:
{migrator.new_dir}

迁移时间 / Migration date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

建议：
- 确认新版本 WatchCats 正常运行后再删除此文件夹
- 如果新版本有问题，可以从这里恢复数据

Recommendation:
- Delete this folder only after confirming WatchCats works properly
- If there are issues, you can restore data from here
"""
                readme_file.write_text(readme_content, encoding='utf-8')
            except:
                pass  # 创建说明文件失败不影响主流程
                
        else:
            print(f"Migration had errors: {result['errors']}")
            
        return result
    
    return None


if __name__ == "__main__":
    # 测试迁移
    result = auto_migrate()
    if result:
        print(json.dumps(result, indent=2))