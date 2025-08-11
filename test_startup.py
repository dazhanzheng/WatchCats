#!/usr/bin/env python
"""测试桌面宠物启动"""
import sys
import os

# 处理 SSL 错误
os.environ['PYTHONWARNINGS'] = 'ignore'

print("Python version:", sys.version)
print("Python executable:", sys.executable)

# 测试导入
try:
    print("Importing PyQt6...")
    from PyQt6.QtWidgets import QApplication
    print("✓ PyQt6 imported successfully")
except Exception as e:
    print(f"✗ PyQt6 import failed: {e}")
    sys.exit(1)

try:
    print("Importing baal modules...")
    from baal.desktop_pet.ui import PetWindow
    print("✓ Baal modules imported successfully")
except Exception as e:
    print(f"✗ Baal import failed: {e}")
    sys.exit(1)

# 创建应用
print("Creating QApplication...")
app = QApplication(sys.argv)
print("✓ QApplication created")

# 创建主窗口
print("Creating PetWindow...")
pet_window = PetWindow()
print("✓ PetWindow created")

# 显示窗口
print("Showing window...")
pet_window.show()
print("✓ Window shown")

print("Starting event loop...")
sys.exit(app.exec())