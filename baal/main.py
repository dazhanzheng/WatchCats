#!/usr/bin/env python
"""
Baal 项目主入口 - 桌面宠物助手

这是Baal项目的主入口点，用于启动桌面宠物助手。
该项目是一个基于ActivityWatch的桌面宠物助手，
能够与用户互动并提供数据分析和任务调度功能。

使用方法：
    1. 确保已激活虚拟环境：source venv/bin/activate (Unix) 或 venv\Scripts\activate (Windows)
    2. 运行命令：python -m baal.main
    或者：python baal/main.py
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入并启动桌面宠物
from baal.desktop_pet import main as desktop_pet_main


def main():
    """主程序入口"""
    print("正在启动 Baal 桌面宠物助手...")
    print(f"项目根目录: {project_root}")
    print(f"Python 版本: {sys.version}")
    
    # 检查虚拟环境
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ 正在虚拟环境中运行")
    else:
        print("⚠️  警告：建议在虚拟环境中运行")
        print("   请运行：python -m venv venv && source venv/bin/activate")
    
    print("-" * 50)
    
    # 启动桌面宠物
    try:
        desktop_pet_main()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n程序运行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
