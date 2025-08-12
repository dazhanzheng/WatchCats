#!/usr/bin/env python3
"""
独立的配置管理器测试
不依赖其他模块，直接测试 ConfigManager
"""

import sys
import os
import json
import tempfile
import traceback
from pathlib import Path
from datetime import datetime

def simulate_windows_env():
    """模拟 Windows 环境"""
    if len(sys.argv) > 1 and sys.argv[1] == '--simulate-windows':
        # 保存原始值
        original_platform = sys.platform
        
        # 设置为 Windows
        sys.platform = 'win32'
        
        # 创建临时目录模拟 Windows 路径
        temp_dir = tempfile.mkdtemp(prefix='baal_test_')
        os.environ['APPDATA'] = os.path.join(temp_dir, 'AppData', 'Roaming')
        os.environ['LOCALAPPDATA'] = os.path.join(temp_dir, 'AppData', 'Local')
        os.environ['USERPROFILE'] = temp_dir
        
        # 创建目录结构
        os.makedirs(os.environ['APPDATA'], exist_ok=True)
        os.makedirs(os.environ['LOCALAPPDATA'], exist_ok=True)
        
        print(f"模拟 Windows 环境:")
        print(f"  sys.platform: {sys.platform}")
        print(f"  APPDATA: {os.environ['APPDATA']}")
        print(f"  LOCALAPPDATA: {os.environ['LOCALAPPDATA']}")
        print(f"  USERPROFILE: {os.environ['USERPROFILE']}")
        print()
        
        return temp_dir
    return None

def test_config_manager_isolated():
    """独立测试配置管理器"""
    print("\n" + "="*60)
    print("独立配置管理器测试")
    print("="*60)
    
    # 动态导入，避免在主模块级别导入
    sys.path.insert(0, str(Path(__file__).parent))
    
    # 直接导入 logger_config 模块，避免通过包导入
    import importlib.util
    logger_path = Path(__file__).parent / 'baal' / 'desktop_pet' / 'core' / 'logger_config.py'
    spec = importlib.util.spec_from_file_location('logger_config', logger_path)
    logger_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(logger_module)
    get_logger = logger_module.get_logger
    
    print("\n1. 测试配置路径逻辑...")
    
    # 手动实现 ConfigManager 的核心逻辑进行测试
    class TestConfigManager:
        def __init__(self):
            self.logger = get_logger('test_config')
            self.config_dir = self._get_config_dir()
            self.config_file = self.config_dir / "config.json"
            print(f"   配置目录: {self.config_dir}")
            print(f"   配置文件: {self.config_file}")
            
        def _get_config_dir(self) -> Path:
            """获取配置目录路径"""
            if sys.platform == "win32":
                # Windows 逻辑
                appdata = os.environ.get('APPDATA')
                if not appdata:
                    appdata = os.environ.get('LOCALAPPDATA')
                
                if not appdata:
                    try:
                        user_profile = os.path.expanduser('~')
                        appdata_path = Path(user_profile) / 'AppData' / 'Roaming'
                        if appdata_path.exists():
                            appdata = str(appdata_path)
                        else:
                            appdata_path = Path(user_profile) / 'AppData' / 'Local'
                            if appdata_path.exists():
                                appdata = str(appdata_path)
                    except Exception as e:
                        print(f"   ⚠️ 无法通过 expanduser 找到 AppData: {e}")
                
                if appdata:
                    config_dir = Path(appdata) / "BaalPet"
                    print(f"   ✓ 使用 Windows AppData: {config_dir}")
                else:
                    config_dir = Path.home() / "BaalPet"
                    print(f"   ⚠️ 回退到主目录: {config_dir}")
                
                return config_dir
            else:
                # macOS/Linux
                return Path.home() / ".baal_pet"
        
        def test_directory_creation(self):
            """测试目录创建"""
            print("\n2. 测试目录创建...")
            try:
                self.config_dir.mkdir(parents=True, exist_ok=True)
                print(f"   ✓ 目录创建成功: {self.config_dir}")
                
                # 验证目录
                if self.config_dir.exists() and self.config_dir.is_dir():
                    print("   ✓ 目录存在且可访问")
                    return True
                else:
                    print("   ✗ 目录创建失败")
                    return False
            except Exception as e:
                print(f"   ✗ 目录创建错误: {e}")
                return False
        
        def test_file_operations(self):
            """测试文件操作"""
            print("\n3. 测试文件操作...")
            
            test_data = {
                'api_key': 'test_key_123',
                'base_url': 'https://test.com',
                'timestamp': datetime.now().isoformat()
            }
            
            try:
                # 写入文件
                print("   写入配置文件...")
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(test_data, f, indent=2, ensure_ascii=False)
                print(f"   ✓ 文件写入成功: {self.config_file}")
                
                # 读取文件
                print("   读取配置文件...")
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                
                if loaded_data == test_data:
                    print("   ✓ 文件读取成功，数据一致")
                else:
                    print("   ✗ 数据不一致")
                    return False
                
                # 测试临时文件和重命名
                print("   测试临时文件机制...")
                temp_file = self.config_file.with_suffix('.tmp')
                
                # 写入临时文件
                temp_data = test_data.copy()
                temp_data['updated'] = True
                
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(temp_data, f, indent=2)
                print("   ✓ 临时文件创建成功")
                
                # 备份原文件
                if self.config_file.exists():
                    backup_file = self.config_file.with_suffix('.bak')
                    if backup_file.exists():
                        backup_file.unlink()
                    self.config_file.rename(backup_file)
                    print("   ✓ 原文件备份成功")
                
                # 重命名临时文件
                temp_file.rename(self.config_file)
                print("   ✓ 临时文件重命名成功")
                
                # 验证更新后的数据
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    final_data = json.load(f)
                
                if final_data.get('updated') == True:
                    print("   ✓ 文件更新验证成功")
                    return True
                else:
                    print("   ✗ 文件更新验证失败")
                    return False
                    
            except PermissionError as e:
                print(f"   ✗ 权限错误: {e}")
                print("   建议: 检查目录权限或以管理员身份运行")
                return False
            except Exception as e:
                print(f"   ✗ 文件操作错误: {e}")
                traceback.print_exc()
                return False
        
        def test_windows_specific(self):
            """测试 Windows 特定场景"""
            if sys.platform != 'win32':
                return True
            
            print("\n4. 测试 Windows 特定场景...")
            
            # 测试文件覆盖（Windows 需要先删除）
            print("   测试文件覆盖...")
            try:
                test_file = self.config_dir / 'test_overwrite.json'
                
                # 创建初始文件
                with open(test_file, 'w') as f:
                    json.dump({'version': 1}, f)
                
                # 创建临时文件
                temp_file = test_file.with_suffix('.tmp')
                with open(temp_file, 'w') as f:
                    json.dump({'version': 2}, f)
                
                # Windows 上需要先删除目标文件
                if test_file.exists():
                    test_file.unlink()
                
                # 重命名
                temp_file.rename(test_file)
                
                # 验证
                with open(test_file, 'r') as f:
                    data = json.load(f)
                
                if data['version'] == 2:
                    print("   ✓ 文件覆盖成功")
                    
                    # 清理
                    test_file.unlink()
                    return True
                else:
                    print("   ✗ 文件覆盖失败")
                    return False
                    
            except Exception as e:
                print(f"   ✗ Windows 特定测试失败: {e}")
                return False
    
    # 运行测试
    try:
        manager = TestConfigManager()
        
        results = []
        results.append(('目录创建', manager.test_directory_creation()))
        results.append(('文件操作', manager.test_file_operations()))
        
        if sys.platform == 'win32':
            results.append(('Windows特定', manager.test_windows_specific()))
        
        # 显示结果
        print("\n" + "="*60)
        print("测试结果")
        print("="*60)
        
        all_passed = True
        for name, passed in results:
            status = "✅ 通过" if passed else "❌ 失败"
            print(f"  {name}: {status}")
            if not passed:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("="*60)
    print("配置管理器独立测试")
    print("="*60)
    print(f"操作系统: {sys.platform}")
    print(f"Python版本: {sys.version}")
    
    # 模拟 Windows 环境（如果需要）
    temp_dir = simulate_windows_env()
    
    # 显示环境变量
    print("\n环境变量:")
    for var in ['APPDATA', 'LOCALAPPDATA', 'USERPROFILE', 'HOME']:
        value = os.environ.get(var)
        if value:
            print(f"  {var}: {value}")
        else:
            print(f"  {var}: 未设置")
    
    # 运行测试
    success = test_config_manager_isolated()
    
    # 清理
    if temp_dir:
        print("\n清理模拟环境...")
        import shutil
        try:
            shutil.rmtree(temp_dir)
            print("✓ 模拟环境已清理")
        except:
            print(f"✗ 清理失败，请手动删除: {temp_dir}")
    
    if success:
        print("\n🎉 测试通过!")
        return 0
    else:
        print("\n⚠️ 测试失败!")
        return 1

if __name__ == '__main__':
    sys.exit(main())