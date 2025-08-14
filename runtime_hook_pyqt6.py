#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyQt6 运行时钩子 - 确保 Qt 能找到其插件
这个文件在打包的应用启动时运行，设置必要的环境变量
"""

import os
import sys

def setup_qt_plugins():
    """设置 Qt 插件路径，防止 Windows 闪退"""
    
    # 只在打包的应用中执行
    if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
        # 构建 Qt 插件路径
        qt_plugin_paths = [
            os.path.join(sys._MEIPASS, 'PyQt6', 'Qt6', 'plugins'),
            os.path.join(sys._MEIPASS, 'PyQt6', 'plugins'),
            os.path.join(sys._MEIPASS, 'Qt6', 'plugins'),
            os.path.join(sys._MEIPASS, 'plugins'),
        ]
        
        # 找到存在的插件路径
        valid_paths = []
        for path in qt_plugin_paths:
            if os.path.exists(path):
                valid_paths.append(path)
                print(f"[Runtime Hook] Found Qt plugin path: {path}")
                
                # 检查关键的平台插件
                platforms_path = os.path.join(path, 'platforms')
                if os.path.exists(platforms_path):
                    dll_files = [f for f in os.listdir(platforms_path) if f.endswith('.dll')]
                    if dll_files:
                        print(f"[Runtime Hook] Found platform plugins: {dll_files}")
        
        if valid_paths:
            # 设置 QT_PLUGIN_PATH 环境变量
            os.environ['QT_PLUGIN_PATH'] = os.pathsep.join(valid_paths)
            print(f"[Runtime Hook] QT_PLUGIN_PATH set to: {os.environ['QT_PLUGIN_PATH']}")
        else:
            print("[Runtime Hook] WARNING: No Qt plugin paths found!")
        
        # 设置其他有用的 Qt 环境变量
        # 禁用 OpenGL 以避免某些 Windows 系统上的问题
        if sys.platform == 'win32':
            # 使用软件渲染作为后备
            os.environ.setdefault('QT_QUICK_BACKEND', 'software')
            # 尝试使用 ANGLE (DirectX) 而不是 OpenGL
            os.environ.setdefault('QT_OPENGL', 'angle')
            print("[Runtime Hook] Set Windows-specific Qt environment variables")

# 执行设置
setup_qt_plugins()

print("[Runtime Hook] PyQt6 runtime hook completed")