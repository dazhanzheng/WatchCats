#!/usr/bin/env python3
"""
测试 Windows 配置保存功能

用于检查配置文件的保存路径和权限问题
"""

import sys
import os
import json
import platform
from pathlib import Path


def test_config_paths():
    """测试不同的配置路径"""
    print("="*60)
    print("Windows 配置路径测试")
    print("="*60)
    print(f"操作系统: {platform.system()}")
    print(f"Python版本: {sys.version}")
    print()
    
    # 测试环境变量
    print("环境变量检查:")
    print(f"  LOCALAPPDATA: {os.environ.get('LOCALAPPDATA', '未找到')}")
    print(f"  APPDATA: {os.environ.get('APPDATA', '未找到')}")
    print(f"  USERPROFILE: {os.environ.get('USERPROFILE', '未找到')}")
    print(f"  HOME: {Path.home()}")
    print()
    
    # 确定配置目录
    if sys.platform == "win32":
        appdata = os.environ.get('LOCALAPPDATA')
        if not appdata:
            appdata = os.environ.get('APPDATA')
        if appdata:
            config_dir = Path(appdata) / "BaalPet"
            print(f"推荐配置目录: {config_dir}")
        else:
            config_dir = Path.home() / ".baal_pet"
            print(f"回退配置目录: {config_dir}")
    else:
        config_dir = Path.home() / ".baal_pet"
        print(f"配置目录: {config_dir}")
    
    print()
    
    # 测试目录创建
    print("测试目录创建:")
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ 成功创建/访问目录: {config_dir}")
        print(f"    目录存在: {config_dir.exists()}")
        print(f"    是目录: {config_dir.is_dir()}")
        
        # 检查权限
        if sys.platform == "win32":
            import stat
            try:
                config_dir.chmod(stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                print(f"    ✓ 成功设置目录权限")
            except Exception as e:
                print(f"    ✗ 设置权限失败: {e}")
    except Exception as e:
        print(f"  ✗ 创建目录失败: {e}")
        return False
    
    print()
    
    # 测试文件写入
    print("测试文件写入:")
    test_file = config_dir / "test_config.json"
    test_data = {
        "test": "data",
        "timestamp": str(Path.ctime(Path(__file__)))
    }
    
    try:
        # 写入测试文件
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)
        print(f"  ✓ 成功写入测试文件: {test_file}")
        
        # 读取验证
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        print(f"  ✓ 成功读取测试文件")
        print(f"    数据匹配: {loaded_data == test_data}")
        
        # 清理测试文件
        test_file.unlink()
        print(f"  ✓ 成功删除测试文件")
        
    except PermissionError as e:
        print(f"  ✗ 权限错误: {e}")
        print()
        print("解决方案:")
        print("  1. 右键程序，选择'以管理员身份运行'")
        print("  2. 检查杀毒软件是否阻止文件写入")
        print("  3. 确保程序不是从压缩包中直接运行")
        return False
    except Exception as e:
        print(f"  ✗ 写入失败: {e}")
        return False
    
    print()
    
    # 测试实际配置文件
    print("测试实际配置文件:")
    config_file = config_dir / "config.json"
    
    if config_file.exists():
        print(f"  配置文件已存在: {config_file}")
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"  ✓ 成功读取现有配置")
            print(f"    包含API密钥: {'api_key' in config}")
            print(f"    包含base_url: {'base_url' in config}")
        except Exception as e:
            print(f"  ✗ 读取配置失败: {e}")
    else:
        print(f"  配置文件不存在 (首次运行)")
        # 创建默认配置
        default_config = {
            'api_key': '',
            'base_url': 'https://ark.cn-beijing.volces.com/api/v3',
            'model': 'deepseek-v3-250324'
        }
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print(f"  ✓ 成功创建默认配置文件")
        except Exception as e:
            print(f"  ✗ 创建配置文件失败: {e}")
    
    print()
    print("="*60)
    print("测试完成！")
    
    if sys.platform == "win32":
        print()
        print("Windows 用户注意事项:")
        print("1. 如果遇到权限问题，请以管理员身份运行")
        print("2. 确保程序已解压到硬盘，不要从压缩包直接运行")
        print("3. 检查杀毒软件是否阻止了文件操作")
    
    return True


if __name__ == "__main__":
    success = test_config_paths()
    
    if not success:
        print()
        print("测试失败！请按照上述建议解决问题。")
        sys.exit(1)
    
    print()
    input("按回车键退出...")