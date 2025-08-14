#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to diagnose Windows environment issues
"""

import sys
import os
import traceback

print("=" * 60)
print("Windows Environment Test")
print("=" * 60)

# Test 1: Python version
print(f"\n1. Python Version: {sys.version}")
print(f"   Platform: {sys.platform}")

# Test 2: Encoding
print(f"\n2. Encoding:")
print(f"   Default encoding: {sys.getdefaultencoding()}")
print(f"   Filesystem encoding: {sys.getfilesystemencoding()}")
print(f"   Stdout encoding: {sys.stdout.encoding if hasattr(sys.stdout, 'encoding') else 'N/A'}")

# Test 3: PyQt6 import
print("\n3. Testing PyQt6 import...")
try:
    from PyQt6 import QtCore, QtGui, QtWidgets
    print("   ✓ PyQt6 imported successfully")
    print(f"   Qt version: {QtCore.QT_VERSION_STR}")
    print(f"   PyQt version: {QtCore.PYQT_VERSION_STR}")
    
    # Check for platform plugin
    from PyQt6.QtCore import QCoreApplication
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    print("   ✓ Qt application created successfully")
    
except Exception as e:
    print(f"   ✗ PyQt6 import failed: {e}")
    traceback.print_exc()

# Test 4: Check critical modules
print("\n4. Testing critical module imports...")
modules_to_test = [
    'baal.desktop_pet',
    'baal.desktop_pet.core.config_manager',
    'baal.desktop_pet.core.logger_config',
    'baal.desktop_pet.ui.pet_window',
    'langchain',
    'aw_client',
    'httpx',
    'pydantic',
]

for module in modules_to_test:
    try:
        __import__(module)
        print(f"   ✓ {module}")
    except ImportError as e:
        print(f"   ✗ {module}: {e}")
    except Exception as e:
        print(f"   ✗ {module}: Unexpected error: {e}")

# Test 5: Check resource files
print("\n5. Checking resource files...")
resource_paths = [
    'baal/resources',
    '动作表情拆分',
    'baal/references',
]

for path in resource_paths:
    if os.path.exists(path):
        files = os.listdir(path)
        print(f"   ✓ {path}: {len(files)} files found")
    else:
        print(f"   ✗ {path}: Directory not found")

# Test 6: Check for Unicode path issues
print("\n6. Testing Unicode path handling...")
try:
    test_path = "测试路径/test.txt"
    print(f"   Can handle path: {repr(test_path)}")
    
    # Test current directory
    cwd = os.getcwd()
    print(f"   Current directory: {repr(cwd)}")
    
    if "动作表情拆分" in os.listdir('.'):
        print("   ✓ Can list directories with Chinese characters")
    
except Exception as e:
    print(f"   ✗ Unicode path error: {e}")

# Test 7: Test main entry point
print("\n7. Testing main entry point...")
try:
    import run_desktop_pet
    print("   ✓ run_desktop_pet.py imported successfully")
    
    # Check if main function exists
    if hasattr(run_desktop_pet, 'main'):
        print("   ✓ main() function found")
    else:
        print("   ✗ main() function not found")
        
except Exception as e:
    print(f"   ✗ Failed to import run_desktop_pet: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test complete. Check for any errors above.")
print("=" * 60)