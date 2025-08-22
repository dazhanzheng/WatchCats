#!/usr/bin/env python3
"""
测试数据迁移功能
Test data migration functionality
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from baal.desktop_pet.core.data_migration import DataMigration


def create_test_old_data(old_dir: Path):
    """创建测试用的旧版本数据"""
    old_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建旧版本的配置文件（使用旧的model）
    config_data = {
        "api_key": "test-key-123",
        "model": "gpt-3.5-turbo",  # 旧的model，应该被更新
        "always_on_top": True
    }
    with open(old_dir / "config.json", 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2)
    
    # 创建旧版本的聊天历史（旧名称）
    chat_history = {
        "messages": [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！我是巴利。"}
        ]
    }
    with open(old_dir / "chat_history.json", 'w', encoding='utf-8') as f:
        json.dump(chat_history, f, indent=2)
    
    # 创建旧版本的目标文件
    goals_data = {
        "goal": "学习Python编程",
        "tasks": ["完成基础教程", "写一个小项目", "学习高级特性"],
        "updated_at": "2024-01-01T10:00:00"
    }
    with open(old_dir / "goals.json", 'w', encoding='utf-8') as f:
        json.dump(goals_data, f, indent=2)
    
    # 创建旧版本的监督配置
    supervision_config = {
        "long_term_goal": "成为全栈开发者",
        "short_term_goals": ["学习前端", "学习后端", "学习数据库"],
        "updated_at": "2024-01-02T10:00:00"
    }
    with open(old_dir / "supervision_config.json", 'w', encoding='utf-8') as f:
        json.dump(supervision_config, f, indent=2)
    
    # 创建日程文件
    schedules_data = {
        "events": [
            {
                "title": "团队会议",
                "start": "2024-01-15T14:00:00",
                "end": "2024-01-15T15:00:00"
            }
        ]
    }
    with open(old_dir / "schedules.json", 'w', encoding='utf-8') as f:
        json.dump(schedules_data, f, indent=2)
    
    # 创建 memory 文件夹
    memory_dir = old_dir / "memory"
    memory_dir.mkdir(exist_ok=True)
    
    # 创建一些记忆文件
    for i in range(3):
        memory_file = memory_dir / f"memory_{i}.json"
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump({"memory_id": i, "content": f"Memory {i}"}, f)
    
    print(f"✓ 创建旧版本数据在: {old_dir}")


def test_migration():
    """测试数据迁移"""
    print("=" * 60)
    print("测试数据迁移功能")
    print("=" * 60)
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 模拟旧版本和新版本路径
        if sys.platform == "win32":
            old_dir = temp_path / "Roaming" / "BaalPet"
            new_dir = temp_path / "Local" / "WatchCats"
        else:
            old_dir = temp_path / ".baal_pet"
            new_dir = temp_path / ".baal_pet_new"
        
        # 创建测试数据
        create_test_old_data(old_dir)
        
        # 创建自定义的迁移器
        class TestDataMigration(DataMigration):
            def __init__(self):
                super().__init__()
                self.old_dir = old_dir
                self.new_dir = new_dir
                self.migration_flag_file = new_dir / ".migration_completed"
        
        # 执行迁移
        migrator = TestDataMigration()
        
        print(f"\n检查是否需要迁移: {migrator.should_migrate()}")
        
        if migrator.should_migrate():
            print("\n开始迁移...")
            result = migrator.migrate()
            
            print(f"\n迁移结果:")
            print(f"  成功: {result['success']}")
            print(f"  迁移的文件: {result['files_migrated']}")
            if result['errors']:
                print(f"  错误: {result['errors']}")
            
            # 验证迁移结果
            print("\n验证迁移结果:")
            
            # 1. 检查配置文件
            config_file = new_dir / "config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"  ✓ config.json 已迁移")
                print(f"    - API Key: {config.get('api_key', 'N/A')}")
                print(f"    - Model: {config.get('model', 'N/A')}")
                
                # 验证model是否被更新
                if config.get('model') == 'doubao-seed-1-6-flash-250715':
                    print(f"    ✓ Model已更新为新版本")
                    if '_old_model' in config:
                        print(f"    - 旧Model: {config.get('_old_model')}")
                else:
                    print(f"    ✗ Model未更新: {config.get('model')}")
            else:
                print(f"  ✗ config.json 未迁移")
            
            # 2. 检查对话历史
            history_file = new_dir / "conversation_history.json"
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                print(f"  ✓ conversation_history.json 已迁移")
                print(f"    - 消息数: {len(history.get('messages', []))}")
            else:
                print(f"  ✗ conversation_history.json 未迁移")
            
            # 3. 检查监督目标
            supervision_file = new_dir / "supervision.json"
            if supervision_file.exists():
                with open(supervision_file, 'r', encoding='utf-8') as f:
                    supervision = json.load(f)
                print(f"  ✓ supervision.json 已迁移")
                print(f"    - 长期目标: {supervision.get('long_term_goal', 'N/A')}")
                print(f"    - 短期目标数: {len(supervision.get('short_term_goals', []))}")
                
                # 验证格式转换
                if 'goal' in supervision or 'tasks' in supervision:
                    print(f"    ⚠ 警告: 检测到旧格式字段")
            else:
                print(f"  ✗ supervision.json 未迁移")
            
            # 4. 检查日程
            schedules_file = new_dir / "schedules.json"
            if schedules_file.exists():
                print(f"  ✓ schedules.json 已迁移")
            else:
                print(f"  ✗ schedules.json 未迁移")
            
            # 5. 检查 memory 文件夹
            memory_dir = new_dir / "memory"
            if memory_dir.exists() and memory_dir.is_dir():
                memory_files = list(memory_dir.glob("*.json"))
                print(f"  ✓ memory 文件夹已迁移")
                print(f"    - 文件数: {len(memory_files)}")
            else:
                print(f"  ✗ memory 文件夹未迁移")
            
            # 6. 检查迁移标记
            if migrator.migration_flag_file.exists():
                print(f"  ✓ 迁移标记已创建")
                with open(migrator.migration_flag_file, 'r') as f:
                    flag_data = json.load(f)
                print(f"    - 迁移日期: {flag_data.get('migration_date', 'N/A')}")
            else:
                print(f"  ✗ 迁移标记未创建")
            
            # 测试重复迁移
            print("\n测试重复迁移...")
            should_migrate_again = migrator.should_migrate()
            print(f"  应该再次迁移: {should_migrate_again}")
            if not should_migrate_again:
                print(f"  ✓ 正确: 不应重复迁移")
            else:
                print(f"  ✗ 错误: 不应该重复迁移")
            
            # 测试配置文件已存在时的model更新
            print("\n测试配置文件已存在时的model更新...")
            
            # 修改config.json的model为旧值
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            config['model'] = 'gpt-4'  # 设置为另一个旧值
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            # 删除迁移标记以允许再次迁移
            migrator.migration_flag_file.unlink()
            
            # 再次执行迁移（此时config.json已存在）
            result2 = migrator.migrate()
            
            # 检查model是否被更新
            with open(config_file, 'r', encoding='utf-8') as f:
                updated_config = json.load(f)
            
            if updated_config.get('model') == 'doubao-seed-1-6-flash-250715':
                print(f"  ✓ 已存在配置的model更新成功")
                print(f"    - 旧Model: {updated_config.get('_old_model', 'N/A')}")
            else:
                print(f"  ✗ 已存在配置的model更新失败")
            
            # 测试合并场景
            print("\n测试supervision.json合并场景...")
            # 在新目录创建一个空的 supervision.json
            new_supervision = new_dir / "supervision.json"
            new_supervision.unlink()  # 删除现有文件
            with open(new_supervision, 'w', encoding='utf-8') as f:
                json.dump({"long_term_goal": "", "short_term_goals": []}, f)
            
            # 删除迁移标记以允许再次迁移
            migrator.migration_flag_file.unlink()
            
            # 再次执行迁移
            result2 = migrator.migrate()
            
            # 检查是否合并了数据
            with open(new_supervision, 'r', encoding='utf-8') as f:
                merged_data = json.load(f)
            
            if merged_data.get('long_term_goal') or merged_data.get('merged_from'):
                print(f"  ✓ 数据合并成功")
                print(f"    - 合并来源: {merged_data.get('merged_from', 'N/A')}")
            else:
                print(f"  ⚠ 数据未合并")
        
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    test_migration()