#!/usr/bin/env python3
"""
Windows 配置保存调试工具

用于诊断 PyInstaller 打包后的配置保存问题
"""

import sys
import os
import json
import platform
from pathlib import Path


def debug_environment():
    """调试环境信息"""
    print("="*70)
    print("Windows 配置保存调试工具")
    print("="*70)
    
    print("\n1. 系统信息:")
    print(f"   操作系统: {platform.system()} {platform.version()}")
    print(f"   Python版本: {sys.version}")
    print(f"   是否PyInstaller打包: {getattr(sys, 'frozen', False)}")
    if getattr(sys, 'frozen', False):
        print(f"   执行文件路径: {sys.executable}")
        print(f"   临时目录: {getattr(sys, '_MEIPASS', 'N/A')}")
    
    print("\n2. 环境变量:")
    env_vars = ['APPDATA', 'LOCALAPPDATA', 'USERPROFILE', 'TEMP', 'TMP', 'HOMEPATH', 'HOMEDRIVE']
    for var in env_vars:
        value = os.environ.get(var, '未设置')
        print(f"   {var}: {value}")
    
    print("\n3. 用户目录:")
    print(f"   Path.home(): {Path.home()}")
    print(f"   expanduser('~'): {os.path.expanduser('~')}")
    
    print("\n4. 可能的配置路径:")
    paths = []
    
    # 方法1: APPDATA
    if os.environ.get('APPDATA'):
        path1 = Path(os.environ['APPDATA']) / 'BaalPet'
        paths.append(('APPDATA/BaalPet', path1))
    
    # 方法2: LOCALAPPDATA
    if os.environ.get('LOCALAPPDATA'):
        path2 = Path(os.environ['LOCALAPPDATA']) / 'BaalPet'
        paths.append(('LOCALAPPDATA/BaalPet', path2))
    
    # 方法3: Home目录
    path3 = Path.home() / 'BaalPet'
    paths.append(('Home/BaalPet', path3))
    
    # 方法4: Home目录隐藏文件夹
    path4 = Path.home() / '.baal_pet'
    paths.append(('Home/.baal_pet', path4))
    
    # 方法5: 程序所在目录（不推荐，但测试用）
    if getattr(sys, 'frozen', False):
        exe_dir = Path(sys.executable).parent
        path5 = exe_dir / 'config'
        paths.append(('程序目录/config', path5))
    
    for name, path in paths:
        exists = path.exists() if path else False
        print(f"\n   {name}:")
        print(f"      路径: {path}")
        print(f"      存在: {exists}")
        if exists:
            print(f"      是目录: {path.is_dir()}")
            print(f"      可写: {os.access(path, os.W_OK)}")


def test_file_operations():
    """测试文件操作"""
    print("\n" + "="*70)
    print("5. 文件操作测试:")
    print("="*70)
    
    # 确定测试目录
    test_dir = None
    if os.environ.get('APPDATA'):
        test_dir = Path(os.environ['APPDATA']) / 'BaalPet'
    elif os.environ.get('LOCALAPPDATA'):
        test_dir = Path(os.environ['LOCALAPPDATA']) / 'BaalPet'
    else:
        test_dir = Path.home() / 'BaalPet'
    
    print(f"\n   测试目录: {test_dir}")
    
    # 测试创建目录
    try:
        test_dir.mkdir(parents=True, exist_ok=True)
        print(f"   ✓ 成功创建/访问目录")
    except Exception as e:
        print(f"   ✗ 创建目录失败: {e}")
        return
    
    # 测试写入文件
    test_file = test_dir / 'test_config.json'
    test_data = {
        "test": "data",
        "timestamp": str(platform.node()),
        "python_version": sys.version
    }
    
    print(f"\n   测试文件: {test_file}")
    
    # 直接写入测试
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
        print(f"   ✓ 直接写入成功")
    except Exception as e:
        print(f"   ✗ 直接写入失败: {e}")
    
    # 临时文件重命名测试
    temp_file = test_dir / 'test_config.tmp'
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
        print(f"   ✓ 临时文件写入成功")
        
        # 尝试重命名
        if test_file.exists():
            test_file.unlink()
        temp_file.rename(test_file)
        print(f"   ✓ 文件重命名成功")
    except Exception as e:
        print(f"   ✗ 临时文件操作失败: {e}")
        
        # 尝试 shutil.move
        try:
            import shutil
            shutil.move(str(temp_file), str(test_file))
            print(f"   ✓ shutil.move 成功")
        except Exception as e2:
            print(f"   ✗ shutil.move 失败: {e2}")
    
    # 读取验证
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        print(f"   ✓ 文件读取成功")
        print(f"   数据匹配: {loaded_data.get('test') == 'data'}")
    except Exception as e:
        print(f"   ✗ 文件读取失败: {e}")
    
    # 清理测试文件
    try:
        if test_file.exists():
            test_file.unlink()
        print(f"   ✓ 测试文件清理成功")
    except Exception as e:
        print(f"   ✗ 清理失败: {e}")


def check_actual_config():
    """检查实际配置文件"""
    print("\n" + "="*70)
    print("6. 实际配置文件检查:")
    print("="*70)
    
    # 所有可能的配置位置
    possible_paths = []
    
    if os.environ.get('APPDATA'):
        possible_paths.append(Path(os.environ['APPDATA']) / 'BaalPet' / 'config.json')
    if os.environ.get('LOCALAPPDATA'):
        possible_paths.append(Path(os.environ['LOCALAPPDATA']) / 'BaalPet' / 'config.json')
    
    possible_paths.extend([
        Path.home() / 'BaalPet' / 'config.json',
        Path.home() / '.baal_pet' / 'config.json',
    ])
    
    found = False
    for config_path in possible_paths:
        if config_path.exists():
            found = True
            print(f"\n   发现配置文件: {config_path}")
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"   ✓ 配置文件可读")
                print(f"   包含的键: {list(config.keys())}")
                
                # 尝试写入测试
                config['_test_timestamp'] = str(platform.node())
                try:
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2)
                    print(f"   ✓ 配置文件可写")
                    
                    # 恢复原始内容
                    del config['_test_timestamp']
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2)
                except Exception as e:
                    print(f"   ✗ 配置文件不可写: {e}")
                    
            except Exception as e:
                print(f"   ✗ 读取配置失败: {e}")
    
    if not found:
        print("\n   未找到现有配置文件")
        print("   程序首次运行时会创建配置文件")


def main():
    """主函数"""
    try:
        debug_environment()
        test_file_operations()
        check_actual_config()
        
        print("\n" + "="*70)
        print("调试完成!")
        print("="*70)
        
        print("\n建议:")
        if sys.platform == "win32":
            print("1. 如果看到权限错误，请以管理员身份运行程序")
            print("2. 确保程序解压到有写入权限的目录（避免 Program Files）")
            print("3. 检查杀毒软件是否阻止文件操作")
            print("4. 尝试在不同位置运行程序（如 D:\\Apps）")
        
    except Exception as e:
        print(f"\n严重错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n按回车键退出...")
    input()


if __name__ == "__main__":
    main()