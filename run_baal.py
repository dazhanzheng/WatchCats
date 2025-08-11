#!/usr/bin/env python
"""
Baal 项目启动脚本

这个脚本用于在项目根目录启动Baal桌面宠物助手。
它会自动检查并提示使用虚拟环境。

使用方法：
    1. 如果还没有创建虚拟环境：
       python -m venv venv
       
    2. 激活虚拟环境：
       - Unix/MacOS: source venv/bin/activate
       - Windows: venv\Scripts\activate
       
    3. 安装依赖（首次运行）：
       pip install -r requirements.txt
       
    4. 运行程序：
       python run_baal.py
"""

import sys
import subprocess
from pathlib import Path

# 检查是否在虚拟环境中运行
def in_virtualenv():
    return hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

def main():
    if not in_virtualenv():
        print("⚠️  警告：您没有在虚拟环境中运行！")
        print("\n建议的操作步骤：")
        print("1. 创建虚拟环境：python -m venv venv")
        print("2. 激活虚拟环境：")
        print("   - Unix/MacOS: source venv/bin/activate")
        print("   - Windows: venv\\Scripts\\activate")
        print("3. 安装依赖：pip install -r requirements.txt")
        print("4. 重新运行：python run_baal.py")
        print("\n" + "="*50 + "\n")
        
        response = input("是否仍要继续运行？(y/N): ").strip().lower()
        if response != 'y':
            print("已取消运行。")
            sys.exit(0)
    
    # 使用 -m 参数运行 baal.main 模块
    try:
        subprocess.run([sys.executable, "-m", "baal.main"], check=True)
    except subprocess.CalledProcessError:
        print("\n运行失败。请检查错误信息。")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n程序被用户中断。")
        sys.exit(0)

if __name__ == "__main__":
    main() 