#!/usr/bin/env python3
"""
切换开发者模式的显示/隐藏

使用方法：
    python toggle_developer_mode.py        # 切换状态
    python toggle_developer_mode.py on     # 启用开发者模式
    python toggle_developer_mode.py off    # 禁用开发者模式
"""

import json
import sys
from pathlib import Path

def toggle_developer_mode(mode=None):
    """切换或设置开发者模式"""
    config_file = Path(__file__).parent / "developer_config.json"
    
    # 读取当前配置
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {
            "show_developer_mode": True,
            "developer_mode_comment": "将此设置为false可以隐藏开发者模式菜单选项",
            "note": "这个文件用于控制开发者模式的显示。发布时将show_developer_mode设置为false即可隐藏开发者选项。"
        }
    
    # 获取当前状态
    current_state = config.get("show_developer_mode", True)
    
    # 根据参数设置新状态
    if mode == "on":
        new_state = True
    elif mode == "off":
        new_state = False
    elif mode is None:
        new_state = not current_state
    else:
        print(f"❌ 无效参数: {mode}")
        print("使用方法: python toggle_developer_mode.py [on|off]")
        return
    
    # 更新配置
    config["show_developer_mode"] = new_state
    
    # 保存配置
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    # 显示结果
    print(f"🔧 开发者模式配置已更新")
    print(f"   之前状态: {'✅ 启用' if current_state else '❌ 禁用'}")
    print(f"   当前状态: {'✅ 启用' if new_state else '❌ 禁用'}")
    print(f"   配置文件: {config_file}")
    
    if not new_state:
        print("\n📦 发布提示：")
        print("   开发者模式已禁用，适合发布版本")
        print("   系统托盘菜单中将不会显示'开发者控制台'选项")
    else:
        print("\n🛠️ 开发提示：")
        print("   开发者模式已启用")
        print("   可以通过系统托盘菜单访问'开发者控制台'")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        toggle_developer_mode(sys.argv[1].lower())
    else:
        toggle_developer_mode()