#!/usr/bin/env python3
"""
Windows 配置管理测试脚本（增强版）
用于测试和诊断 Windows 平台上的配置保存问题
"""

import sys
import os
import json
import tempfile
import traceback
from pathlib import Path
from datetime import datetime

# 添加项目路径到系统路径
sys.path.insert(0, str(Path(__file__).parent))

# 设置临时环境变量来模拟 Windows
if len(sys.argv) > 1 and sys.argv[1] == '--simulate-windows':
    # 模拟 Windows 环境
    original_platform = sys.platform
    sys.platform = 'win32'
    
    # 设置模拟的 Windows 环境变量
    temp_dir = tempfile.mkdtemp(prefix='baal_test_')
    os.environ['APPDATA'] = os.path.join(temp_dir, 'AppData', 'Roaming')
    os.environ['LOCALAPPDATA'] = os.path.join(temp_dir, 'AppData', 'Local')
    os.environ['USERPROFILE'] = temp_dir
    
    # 创建模拟的目录结构
    os.makedirs(os.environ['APPDATA'], exist_ok=True)
    os.makedirs(os.environ['LOCALAPPDATA'], exist_ok=True)
    
    print(f"模拟 Windows 环境:")
    print(f"  APPDATA: {os.environ['APPDATA']}")
    print(f"  LOCALAPPDATA: {os.environ['LOCALAPPDATA']}")
    print(f"  USERPROFILE: {os.environ['USERPROFILE']}")
    print()

def test_config_manager():
    """测试配置管理器的完整功能"""
    print("\n" + "="*60)
    print("配置管理器测试")
    print("="*60)
    
    try:
        from baal.desktop_pet.core.config_manager import ConfigManager
        
        # 创建配置管理器实例
        print("\n1. 创建配置管理器...")
        config_manager = ConfigManager()
        print(f"   ✓ 配置目录: {config_manager.config_dir}")
        print(f"   ✓ 配置文件: {config_manager.config_file}")
        
        # 测试默认配置
        print("\n2. 检查默认配置...")
        config = config_manager.get_config()
        print(f"   ✓ 配置键数量: {len(config)}")
        for key in config:
            if key != 'api_key':
                print(f"     - {key}: {config[key]}")
            else:
                print(f"     - api_key: {'已设置' if config[key] else '未设置'}")
        
        # 测试设置和保存
        print("\n3. 测试配置保存...")
        test_api_key = "test_key_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        config_manager.set_api_key(test_api_key)
        
        # 验证内存中的配置
        if config_manager.get_api_key() == test_api_key:
            print("   ✓ 内存中的API密钥设置成功")
        else:
            print("   ✗ 内存中的API密钥设置失败")
            return False
        
        # 重新加载配置管理器以验证持久化
        print("\n4. 验证配置持久化...")
        config_manager2 = ConfigManager()
        loaded_key = config_manager2.get_api_key()
        
        if loaded_key == test_api_key:
            print("   ✓ 配置成功保存并重新加载")
            print(f"   ✓ 保存的API密钥: {loaded_key[:10]}...")
        else:
            print("   ✗ 配置未能正确保存")
            print(f"     期望: {test_api_key}")
            print(f"     实际: {loaded_key}")
            return False
        
        # 测试窗口位置保存
        print("\n5. 测试窗口位置保存...")
        config_manager2.set_window_position(200, 300)
        
        # 重新加载验证
        config_manager3 = ConfigManager()
        position = config_manager3.get_window_position()
        if position['x'] == 200 and position['y'] == 300:
            print("   ✓ 窗口位置保存成功")
            print(f"   ✓ 位置: x={position['x']}, y={position['y']}")
        else:
            print("   ✗ 窗口位置保存失败")
            print(f"     期望: x=200, y=300")
            print(f"     实际: x={position['x']}, y={position['y']}")
            return False
        
        # 测试复杂配置更新
        print("\n6. 测试复杂配置更新...")
        full_config = config_manager3.get_config()
        full_config['test_field'] = 'test_value'
        full_config['test_number'] = 42
        full_config['test_list'] = [1, 2, 3]
        
        if config_manager3.save_config(full_config):
            print("   ✓ 复杂配置保存成功")
            
            # 验证
            config_manager4 = ConfigManager()
            loaded_config = config_manager4.get_config()
            
            if (loaded_config.get('test_field') == 'test_value' and
                loaded_config.get('test_number') == 42 and
                loaded_config.get('test_list') == [1, 2, 3]):
                print("   ✓ 复杂配置验证成功")
            else:
                print("   ✗ 复杂配置验证失败")
                return False
        else:
            print("   ✗ 复杂配置保存失败")
            return False
        
        print("\n✅ 所有配置管理器测试通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ 配置管理器测试失败:")
        print(f"   错误: {e}")
        traceback.print_exc()
        return False

def test_file_operations():
    """测试文件操作权限"""
    print("\n" + "="*60)
    print("文件操作测试")
    print("="*60)
    
    # 获取测试目录
    if sys.platform == 'win32':
        appdata = os.environ.get('APPDATA')
        if not appdata:
            appdata = os.path.expanduser('~')
        test_dir = Path(appdata) / 'BaalPet' / 'test'
    else:
        test_dir = Path.home() / '.baal_pet' / 'test'
    
    print(f"\n测试目录: {test_dir}")
    
    try:
        # 1. 创建目录
        print("\n1. 创建目录...")
        test_dir.mkdir(parents=True, exist_ok=True)
        print("   ✓ 目录创建成功")
        
        # 2. 写入文件
        print("\n2. 写入测试文件...")
        test_file = test_dir / 'test.json'
        test_data = {
            'timestamp': datetime.now().isoformat(),
            'test': True,
            'data': [1, 2, 3]
        }
        
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
        print("   ✓ 文件写入成功")
        
        # 3. 读取文件
        print("\n3. 读取测试文件...")
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        if loaded_data == test_data:
            print("   ✓ 文件读取成功，数据一致")
        else:
            print("   ✗ 文件读取失败，数据不一致")
            return False
        
        # 4. 更新文件
        print("\n4. 更新测试文件...")
        test_data['updated'] = True
        test_data['update_time'] = datetime.now().isoformat()
        
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
        print("   ✓ 文件更新成功")
        
        # 5. 使用临时文件和重命名
        print("\n5. 测试临时文件和重命名...")
        temp_file = test_file.with_suffix('.tmp')
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump({'temp': True}, f)
        print("   ✓ 临时文件创建成功")
        
        # 备份原文件
        backup_file = test_file.with_suffix('.bak')
        if test_file.exists():
            if backup_file.exists():
                backup_file.unlink()
            test_file.rename(backup_file)
            print("   ✓ 原文件备份成功")
        
        # 重命名临时文件
        temp_file.rename(test_file)
        print("   ✓ 临时文件重命名成功")
        
        # 6. 清理测试文件
        print("\n6. 清理测试文件...")
        for file in [test_file, backup_file]:
            if file.exists():
                file.unlink()
                print(f"   ✓ 删除文件: {file.name}")
        
        # 删除测试目录（如果为空）
        try:
            test_dir.rmdir()
            print("   ✓ 删除测试目录")
        except:
            print("   - 测试目录不为空，跳过删除")
        
        print("\n✅ 所有文件操作测试通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ 文件操作测试失败:")
        print(f"   错误: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("="*60)
    print("Windows 配置管理增强测试")
    print("="*60)
    print(f"操作系统: {sys.platform}")
    print(f"Python版本: {sys.version}")
    
    # 显示环境变量
    print("\n环境变量:")
    for var in ['APPDATA', 'LOCALAPPDATA', 'USERPROFILE', 'HOME']:
        value = os.environ.get(var)
        if value:
            print(f"  {var}: {value}")
        else:
            print(f"  {var}: 未设置")
    
    # 运行测试
    results = []
    
    # 文件操作测试
    results.append(('文件操作', test_file_operations()))
    
    # 配置管理器测试
    results.append(('配置管理器', test_config_manager()))
    
    # 显示总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试通过!")
    else:
        print("\n⚠️ 部分测试失败，请检查上面的错误信息")
    
    # 清理模拟环境
    if len(sys.argv) > 1 and sys.argv[1] == '--simulate-windows':
        print("\n清理模拟环境...")
        import shutil
        try:
            shutil.rmtree(temp_dir)
            print("✓ 模拟环境已清理")
        except:
            print("✗ 清理失败，请手动删除:", temp_dir)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())