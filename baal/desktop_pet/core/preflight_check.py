#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
预检查系统 - 在启动主程序前验证环境
帮助诊断和预防启动失败
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional

class PreflightChecker:
    """预检查器，验证运行环境"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
    
    def check_python_version(self) -> bool:
        """检查 Python 版本"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 9):
            self.errors.append(f"Python version too old: {sys.version}. Required: 3.9+")
            return False
        self.info.append(f"✓ Python version: {sys.version}")
        return True
    
    def check_pyqt6(self) -> bool:
        """检查 PyQt6 是否可用"""
        try:
            import PyQt6
            import PyQt6.QtCore
            import PyQt6.QtGui
            import PyQt6.QtWidgets
            self.info.append(f"✓ PyQt6 version: {PyQt6.QtCore.QT_VERSION_STR}")
            
            # 检查平台插件（Windows 特别重要）
            if getattr(sys, 'frozen', False) and sys.platform == 'win32':
                if hasattr(sys, '_MEIPASS'):
                    plugin_path = Path(sys._MEIPASS) / 'PyQt6' / 'Qt6' / 'plugins' / 'platforms'
                    if not plugin_path.exists():
                        # 尝试其他路径
                        alt_paths = [
                            Path(sys._MEIPASS) / 'PyQt6' / 'plugins' / 'platforms',
                            Path(sys._MEIPASS) / 'Qt6' / 'plugins' / 'platforms',
                            Path(sys._MEIPASS) / 'plugins' / 'platforms',
                        ]
                        found = False
                        for alt_path in alt_paths:
                            if alt_path.exists():
                                plugin_path = alt_path
                                found = True
                                break
                        
                        if not found:
                            self.errors.append("Qt platform plugins not found! This will cause crash on Windows.")
                            return False
                    
                    # 检查 Windows 平台插件
                    qwindows_dll = plugin_path / 'qwindows.dll'
                    if not qwindows_dll.exists():
                        self.errors.append(f"qwindows.dll not found in {plugin_path}")
                        return False
                    
                    self.info.append(f"✓ Qt platform plugin found: {qwindows_dll}")
            
            return True
        except ImportError as e:
            self.errors.append(f"PyQt6 not available: {e}")
            return False
    
    def check_resources(self) -> bool:
        """检查资源文件"""
        try:
            from baal.desktop_pet.core.resource_manager import ResourceManager
            rm = ResourceManager.get_instance()
            
            # 验证资源
            if not rm.verify_resources():
                self.warnings.append("Some resources are missing, but app may still work")
            else:
                self.info.append("✓ All resources verified")
            
            return True
        except Exception as e:
            self.warnings.append(f"Could not verify resources: {e}")
            return True  # 不是致命错误
    
    def check_config_access(self) -> bool:
        """检查配置文件访问权限"""
        try:
            if sys.platform == 'win32':
                config_dir = Path(os.environ.get('APPDATA', Path.home())) / 'BaalPet'
            else:
                config_dir = Path.home() / '.baal_pet'
            
            # 尝试创建目录
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # 尝试写入测试文件
            test_file = config_dir / '.test_write'
            test_file.write_text('test')
            test_file.unlink()
            
            self.info.append(f"✓ Config directory accessible: {config_dir}")
            return True
        except Exception as e:
            self.warnings.append(f"Config directory may not be writable: {e}")
            return True  # 不是致命错误
    
    def check_qt_environment(self) -> bool:
        """检查 Qt 环境变量"""
        if sys.platform == 'win32':
            qt_plugin_path = os.environ.get('QT_PLUGIN_PATH')
            if qt_plugin_path:
                self.info.append(f"✓ QT_PLUGIN_PATH set: {qt_plugin_path}")
            else:
                if getattr(sys, 'frozen', False):
                    self.warnings.append("QT_PLUGIN_PATH not set, runtime hook may not have run")
            
            # 检查 OpenGL 设置
            qt_opengl = os.environ.get('QT_OPENGL')
            if qt_opengl:
                self.info.append(f"✓ QT_OPENGL set to: {qt_opengl}")
        
        return True
    
    def check_dependencies(self) -> bool:
        """检查关键依赖"""
        required_modules = [
            'langchain',
            'httpx',
            'pydantic',
            'pytz',
        ]
        
        missing = []
        for module in required_modules:
            try:
                __import__(module)
                self.info.append(f"✓ Module {module} available")
            except ImportError:
                missing.append(module)
        
        if missing:
            self.warnings.append(f"Optional modules missing: {missing}")
        
        return True
    
    def run_all_checks(self) -> bool:
        """运行所有检查"""
        print("=" * 50)
        print("Running Preflight Checks...")
        print("=" * 50)
        
        checks = [
            ("Python Version", self.check_python_version),
            ("PyQt6", self.check_pyqt6),
            ("Qt Environment", self.check_qt_environment),
            ("Resources", self.check_resources),
            ("Config Access", self.check_config_access),
            ("Dependencies", self.check_dependencies),
        ]
        
        all_passed = True
        for name, check_func in checks:
            try:
                result = check_func()
                if not result:
                    all_passed = False
                    print(f"✗ {name} check failed")
            except Exception as e:
                self.warnings.append(f"{name} check error: {e}")
                print(f"⚠ {name} check error: {e}")
        
        # 显示结果
        if self.info:
            print("\nInfo:")
            for msg in self.info:
                print(f"  {msg}")
        
        if self.warnings:
            print("\nWarnings:")
            for msg in self.warnings:
                print(f"  ⚠ {msg}")
        
        if self.errors:
            print("\nErrors:")
            for msg in self.errors:
                print(f"  ✗ {msg}")
            print("\nPreflight checks FAILED! The application may not start properly.")
        else:
            print("\n✓ All critical checks passed!")
        
        print("=" * 50)
        
        return len(self.errors) == 0
    
    def get_diagnostic_info(self) -> str:
        """获取诊断信息"""
        lines = [
            "Diagnostic Information",
            "=" * 50,
            f"Platform: {sys.platform}",
            f"Python: {sys.version}",
            f"Frozen: {getattr(sys, 'frozen', False)}",
        ]
        
        if hasattr(sys, '_MEIPASS'):
            lines.append(f"Bundle path: {sys._MEIPASS}")
        
        lines.append(f"Working directory: {os.getcwd()}")
        lines.append(f"Executable: {sys.executable}")
        
        # Qt 相关信息
        try:
            from PyQt6.QtCore import QT_VERSION_STR
            lines.append(f"Qt version: {QT_VERSION_STR}")
        except:
            pass
        
        # 环境变量
        important_env = ['QT_PLUGIN_PATH', 'QT_OPENGL', 'QT_QUICK_BACKEND']
        for var in important_env:
            value = os.environ.get(var)
            if value:
                lines.append(f"{var}: {value}")
        
        return "\n".join(lines)


def run_preflight_check() -> bool:
    """运行预检查的便捷函数"""
    checker = PreflightChecker()
    return checker.run_all_checks()

def get_diagnostic_info() -> str:
    """获取诊断信息的便捷函数"""
    checker = PreflightChecker()
    return checker.get_diagnostic_info()