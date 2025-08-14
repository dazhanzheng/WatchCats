#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Windows 崩溃修复工具
自动诊断和修复常见的 Windows 启动问题
"""

import os
import sys
import subprocess
from pathlib import Path

def check_and_fix():
    """检查并修复常见问题"""
    
    print("=" * 60)
    print("Windows 崩溃修复工具")
    print("=" * 60)
    
    issues_found = []
    fixes_applied = []
    
    # 1. 检查 Visual C++ Redistributables
    print("\n1. 检查 Visual C++ Redistributables...")
    vcredist_check = subprocess.run(
        ['wmic', 'product', 'where', 'name like "%Visual C++%"', 'get', 'name,version'],
        capture_output=True, text=True, shell=True
    )
    
    if "2015" not in vcredist_check.stdout and "2019" not in vcredist_check.stdout:
        issues_found.append("缺少 Visual C++ Redistributables")
        print("   ✗ 未找到 Visual C++ 2015-2019 Redistributables")
        print("   建议：从以下链接下载并安装：")
        print("   https://aka.ms/vs/17/release/vc_redist.x64.exe")
    else:
        print("   ✓ Visual C++ Redistributables 已安装")
    
    # 2. 检查 Qt 平台插件
    print("\n2. 检查 Qt 平台插件...")
    if os.path.exists("dist"):
        qt_paths = [
            "dist/PyQt6/Qt6/plugins/platforms/qwindows.dll",
            "dist/PyQt6/plugins/platforms/qwindows.dll",
            "dist/Qt6/plugins/platforms/qwindows.dll",
            "dist/plugins/platforms/qwindows.dll",
        ]
        
        found = False
        for path in qt_paths:
            if os.path.exists(path):
                print(f"   ✓ 找到 Qt 平台插件: {path}")
                found = True
                break
        
        if not found:
            issues_found.append("Qt 平台插件缺失")
            print("   ✗ 未找到 qwindows.dll")
            print("   建议：重新构建应用")
    
    # 3. 检查并设置环境变量
    print("\n3. 设置环境变量...")
    env_fixes = {
        'QT_PLUGIN_PATH': os.path.abspath('dist/PyQt6/Qt6/plugins'),
        'QT_QPA_PLATFORM_PLUGIN_PATH': os.path.abspath('dist/PyQt6/Qt6/plugins/platforms'),
        'QT_OPENGL': 'angle',  # 使用 DirectX 而不是 OpenGL
        'QT_QUICK_BACKEND': 'software',  # 使用软件渲染
    }
    
    for key, value in env_fixes.items():
        os.environ[key] = value
        print(f"   设置 {key} = {value}")
        fixes_applied.append(f"设置环境变量 {key}")
    
    # 4. 创建修复后的启动脚本
    print("\n4. 创建修复启动脚本...")
    
    fixed_bat_content = f"""@echo off
echo 运行修复后的启动脚本...

REM 设置修复环境变量
set QT_PLUGIN_PATH={os.path.abspath('dist/PyQt6/Qt6/plugins')}
set QT_QPA_PLATFORM_PLUGIN_PATH={os.path.abspath('dist/PyQt6/Qt6/plugins/platforms')}
set QT_OPENGL=angle
set QT_QUICK_BACKEND=software
set BAAL_DEBUG=true

echo 环境变量已设置

REM 启动应用
if exist "dist\\WatchCats.exe" (
    echo 启动 WatchCats.exe...
    "dist\\WatchCats.exe"
) else (
    echo 错误：找不到 dist\\WatchCats.exe
    pause
)
"""
    
    with open("start_fixed.bat", "w", encoding='utf-8') as f:
        f.write(fixed_bat_content)
    
    print("   ✓ 创建 start_fixed.bat")
    fixes_applied.append("创建修复启动脚本 start_fixed.bat")
    
    # 5. 总结
    print("\n" + "=" * 60)
    print("诊断结果：")
    
    if issues_found:
        print("\n发现的问题：")
        for issue in issues_found:
            print(f"  - {issue}")
    else:
        print("\n✓ 未发现明显问题")
    
    if fixes_applied:
        print("\n应用的修复：")
        for fix in fixes_applied:
            print(f"  - {fix}")
    
    print("\n建议：")
    print("1. 运行 start_fixed.bat 尝试启动应用")
    print("2. 如果仍然崩溃，运行 debug_windows.bat 查看详细错误")
    print("3. 确保已安装 Visual C++ Redistributables")
    
    print("=" * 60)

if __name__ == "__main__":
    check_and_fix()
    print("\n按 Enter 键退出...")
    input()