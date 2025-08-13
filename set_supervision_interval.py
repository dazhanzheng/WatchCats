#!/usr/bin/env python3
"""
快速设置监督模式检查间隔

使用方法：
    python set_supervision_interval.py 5      # 设置为5秒（调试）
    python set_supervision_interval.py 300    # 设置为300秒（正常）
    python set_supervision_interval.py        # 显示当前设置
"""

import sys
import os
from pathlib import Path

def get_current_interval():
    """获取当前设置的间隔"""
    # 读取supervision_mode.py文件
    file_path = Path(__file__).parent / "baal" / "desktop_pet" / "supervision_mode.py"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 查找当前设置
    import re
    match = re.search(r"SUPERVISION_CHECK_INTERVAL.*?['\"](\d+)['\"].*?#.*?(\d+)秒", content)
    if match:
        return int(match.group(1))
    return None

def set_interval(seconds):
    """设置检查间隔"""
    file_path = Path(__file__).parent / "baal" / "desktop_pet" / "supervision_mode.py"
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 修改相关行
    modified = False
    for i, line in enumerate(lines):
        # 修改默认值行
        if "SUPERVISION_CHECK_INTERVAL" in line and "os.environ.get" in line:
            if seconds == 5:
                lines[i] = "        self.check_interval = int(os.environ.get('SUPERVISION_CHECK_INTERVAL', '5'))  # 调试模式：5秒\n"
            elif seconds == 300:
                lines[i] = "        self.check_interval = int(os.environ.get('SUPERVISION_CHECK_INTERVAL', '300'))  # 默认5分钟\n"
            else:
                lines[i] = f"        self.check_interval = int(os.environ.get('SUPERVISION_CHECK_INTERVAL', '{seconds}'))  # 自定义：{seconds}秒\n"
            modified = True
        
        # 修改检查条件行
        elif "if self.check_interval !=" in line:
            if seconds == 5:
                lines[i] = "        if self.check_interval != 5:  # 调试时期望值是5秒\n"
            elif seconds == 300:
                lines[i] = "        if self.check_interval != 300:\n"
            else:
                lines[i] = f"        if self.check_interval != {seconds}:  # 自定义期望值\n"
    
    if modified:
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    return False

def main():
    """主函数"""
    print("\n" + "="*50)
    print("监督模式间隔设置工具")
    print("="*50)
    
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
            
            # 验证合理范围
            if interval < 1:
                print("❌ 错误：间隔必须至少为1秒")
                return
            if interval > 3600:
                print("❌ 错误：间隔不能超过3600秒（1小时）")
                return
            
            # 设置间隔
            print(f"\n正在设置监督模式检查间隔为 {interval} 秒...")
            
            if set_interval(interval):
                print(f"✅ 成功设置间隔为 {interval} 秒")
                
                if interval <= 10:
                    print("\n⚠️ 注意：间隔设置过短，仅用于调试！")
                    print("   生产环境建议使用 300 秒（5分钟）")
                elif interval >= 60:
                    print(f"\n📊 间隔设置为 {interval} 秒（{interval/60:.1f} 分钟）")
                
                print("\n💡 使用方法：")
                print("   1. 重启应用生效")
                print("   2. 或使用环境变量临时覆盖：")
                print(f"      SUPERVISION_CHECK_INTERVAL={interval} ./venv/bin/python run_desktop_pet.py")
            else:
                print("❌ 设置失败，请检查文件")
                
        except ValueError:
            print(f"❌ 错误：'{sys.argv[1]}' 不是有效的数字")
    else:
        # 显示当前设置
        current = get_current_interval()
        if current:
            print(f"\n📊 当前监督模式检查间隔：{current} 秒", end="")
            if current >= 60:
                print(f"（{current/60:.1f} 分钟）")
            else:
                print()
            
            if current <= 10:
                print("   ⚠️ 当前为调试模式")
            elif current == 300:
                print("   ✅ 当前为默认设置")
            
            print("\n💡 快速切换：")
            print("   python set_supervision_interval.py 5     # 调试模式（5秒）")
            print("   python set_supervision_interval.py 300   # 正常模式（5分钟）")
            print("   python set_supervision_interval.py 60    # 自定义（1分钟）")
        else:
            print("❌ 无法读取当前设置")
    
    print("="*50)

if __name__ == "__main__":
    main()