#!/usr/bin/env python3
"""
测试增强版配置管理器
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def test_enhanced_config():
    """测试增强版配置管理器"""
    print("="*60)
    print("测试增强版配置管理器")
    print("="*60)
    print(f"操作系统: {sys.platform}")
    print(f"Python版本: {sys.version}")
    
    # 导入增强版配置管理器
    from baal.desktop_pet.core.config_manager_enhanced import EnhancedConfigManager
    
    print("\n1. 创建配置管理器实例...")
    config_manager = EnhancedConfigManager()
    print(f"   ✓ 配置目录: {config_manager.config_dir}")
    print(f"   ✓ 配置文件: {config_manager.config_file}")
    
    print("\n2. 测试API密钥设置...")
    test_key = f"test_enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    config_manager.set_api_key(test_key)
    
    if config_manager.get_api_key() == test_key:
        print(f"   ✓ API密钥设置成功: {test_key[:15]}...")
    else:
        print("   ✗ API密钥设置失败")
        return False
    
    print("\n3. 重新加载验证持久化...")
    config_manager2 = EnhancedConfigManager()
    loaded_key = config_manager2.get_api_key()
    
    if loaded_key == test_key:
        print("   ✓ 配置持久化成功")
    else:
        print(f"   ✗ 配置持久化失败")
        print(f"     期望: {test_key}")
        print(f"     实际: {loaded_key}")
        return False
    
    print("\n4. 测试复杂配置...")
    config = config_manager2.get_config()
    config['test_field'] = 'enhanced_test'
    config['test_array'] = [1, 2, 3, 4, 5]
    config['test_nested'] = {'level1': {'level2': 'value'}}
    
    if config_manager2.save_config(config):
        print("   ✓ 复杂配置保存成功")
        
        # 重新加载验证
        config_manager3 = EnhancedConfigManager()
        loaded_config = config_manager3.get_config()
        
        if (loaded_config.get('test_field') == 'enhanced_test' and
            loaded_config.get('test_array') == [1, 2, 3, 4, 5] and
            loaded_config.get('test_nested', {}).get('level1', {}).get('level2') == 'value'):
            print("   ✓ 复杂配置验证成功")
        else:
            print("   ✗ 复杂配置验证失败")
            return False
    else:
        print("   ✗ 复杂配置保存失败")
        return False
    
    print("\n5. 测试导出/导入功能...")
    export_path = config_manager.config_dir / 'export_test.json'
    
    if config_manager3.export_config(export_path):
        print(f"   ✓ 配置导出成功: {export_path}")
        
        # 重置配置
        config_manager3.reset_config()
        print("   ✓ 配置已重置")
        
        # 导入配置
        if config_manager3.import_config(export_path):
            print("   ✓ 配置导入成功")
            
            # 验证导入的配置
            imported_config = config_manager3.get_config()
            if imported_config.get('test_field') == 'enhanced_test':
                print("   ✓ 导入配置验证成功")
            else:
                print("   ✗ 导入配置验证失败")
                return False
        else:
            print("   ✗ 配置导入失败")
            return False
        
        # 清理导出文件
        try:
            export_path.unlink()
            print("   ✓ 清理导出文件")
        except:
            pass
    else:
        print("   ✗ 配置导出失败")
        return False
    
    print("\n✅ 所有测试通过!")
    return True

def main():
    """主函数"""
    try:
        success = test_enhanced_config()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())