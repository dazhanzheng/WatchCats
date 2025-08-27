#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CI/CD Windows 构建修复脚本
专门用于 GitHub Actions 环境
"""

import os
import sys
import shutil
from pathlib import Path

# 设置UTF-8编码输出（解决Windows编码问题）
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')

def fix_pyinstaller_spec():
    """动态修改 spec 文件以适应 CI 环境"""
    
    print("=" * 60)
    print("CI/CD Windows Build Fixer")
    print("=" * 60)
    
    # 1. 查找 PyQt6 安装位置
    try:
        import PyQt6
        pyqt6_path = Path(PyQt6.__file__).parent
        print(f"[OK] Found PyQt6 at: {pyqt6_path}")
    except ImportError:
        print("[ERROR] PyQt6 not found! Installing...")
        os.system("pip install PyQt6==6.5.3")
        import PyQt6
        pyqt6_path = Path(PyQt6.__file__).parent
    
    # 2. 查找 Qt 插件
    plugin_paths = [
        pyqt6_path / "Qt6" / "plugins",
        pyqt6_path / "Qt" / "plugins",
        pyqt6_path / "plugins",
        pyqt6_path.parent / "PyQt6_Qt6" / "Qt" / "plugins",
    ]
    
    qt_plugins_path = None
    for path in plugin_paths:
        if path.exists():
            qt_plugins_path = path
            print(f"[OK] Found Qt plugins at: {qt_plugins_path}")
            break
    
    if not qt_plugins_path:
        print("[ERROR] Qt plugins not found!")
        # 尝试通过 pip show 查找
        import subprocess
        result = subprocess.run(
            ["pip", "show", "-f", "PyQt6-Qt6"],
            capture_output=True,
            text=True
        )
        print("PyQt6-Qt6 files:")
        print(result.stdout)
        sys.exit(1)
    
    # 3. 验证平台插件
    platforms_path = qt_plugins_path / "platforms"
    if not platforms_path.exists():
        print(f"[ERROR] Platforms directory not found: {platforms_path}")
        sys.exit(1)
    
    qwindows_dll = platforms_path / "qwindows.dll"
    if not qwindows_dll.exists():
        print(f"[ERROR] qwindows.dll not found: {qwindows_dll}")
        sys.exit(1)
    
    print(f"[OK] qwindows.dll found: {qwindows_dll}")
    print(f"  Size: {qwindows_dll.stat().st_size / 1024:.2f} KB")
    
    # 4. 生成 CI 专用的 spec 文件
    print("\nGenerating CI-specific spec file...")
    
    ci_spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# Auto-generated for CI/CD

import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_all, collect_dynamic_libs

block_cipher = None

# 收集数据和二进制文件
datas = []
binaries = []
hiddenimports = []

# 收集 PyQt6
pyqt6_all = collect_all('PyQt6')
datas += pyqt6_all[0]
binaries += pyqt6_all[1]
hiddenimports += pyqt6_all[2]

# 手动添加 Qt 插件（CI 环境关键）
qt_plugins_path = r"{qt_plugins_path}"
if os.path.exists(qt_plugins_path):
    import glob
    # 平台插件
    for dll in glob.glob(os.path.join(qt_plugins_path, "platforms", "*.dll")):
        binaries.append((dll, "PyQt6/Qt6/plugins/platforms"))
    # 样式插件
    for dll in glob.glob(os.path.join(qt_plugins_path, "styles", "*.dll")):
        binaries.append((dll, "PyQt6/Qt6/plugins/styles"))
    # 图像格式插件
    for dll in glob.glob(os.path.join(qt_plugins_path, "imageformats", "*.dll")):
        binaries.append((dll, "PyQt6/Qt6/plugins/imageformats"))
    print(f"Added Qt plugins from {{qt_plugins_path}}")

# 收集 aw-client 和 aw-core
try:
    aw_client_all = collect_all('aw_client')
    datas += aw_client_all[0]
    binaries += aw_client_all[1]
    hiddenimports += aw_client_all[2]
except:
    pass

try:
    aw_core_all = collect_all('aw_core')
    datas += aw_core_all[0]
    binaries += aw_core_all[1]
    hiddenimports += aw_core_all[2]
except:
    pass

# 添加应用资源
datas += [
    ('baal/resources/cat.png', 'baal/resources'),
    ('baal/references/*.md', 'baal/references'),
    ('动作表情拆分/*.png', '动作表情拆分'),
    ('动作表情拆分/*.gif', '动作表情拆分'),
]

# 隐藏导入
hiddenimports += [
    'aw_client', 'aw_client.client', 'aw_core', 'aw_core.models',
    'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets',
    'PyQt6.QtNetwork', 'PyQt6.QtPrintSupport', 'PyQt6.sip',
    'httpx', 'requests',
    'langchain', 'langchain_openai', 'langchain_core',
    'persist_queue', 'appdirs', 'iso8601', 'peewee',
    'jsonschema', 'icalendar', 'pytz', 'dateutil',
    'pydantic', 'pydantic.deprecated', 'pydantic._internal',
    'baal.scheduler', 'baal.desktop_pet.supervision_mode',
    'baal.desktop_pet.core.single_instance',
]

a = Analysis(
    ['run_desktop_pet.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=['runtime_hook_pyqt6.py'],
    excludes=['tkinter', 'matplotlib', 'scipy', 'numpy', 'pandas',
              'notebook', 'jupyter', 'IPython', 'test', 'tests',
              'PyQt5', 'PyQt5_sip', 'PySide2', 'PySide6'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WatchCats',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='baal/resources/app_icon.ico' if os.path.exists('baal/resources/app_icon.ico') else None,
)
'''
    
    with open("baal_windows_ci.spec", "w", encoding="utf-8") as f:
        f.write(ci_spec_content)
    
    print("[OK] Created baal_windows_ci.spec")
    
    # 5. 创建运行时环境设置脚本
    runtime_fix = '''import os
import sys

# CI/CD 环境运行时修复
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # 设置 Qt 插件路径
    plugin_paths = [
        os.path.join(sys._MEIPASS, 'PyQt6', 'Qt6', 'plugins'),
        os.path.join(sys._MEIPASS, 'PyQt6', 'plugins'),
        os.path.join(sys._MEIPASS, 'Qt6', 'plugins'),
        os.path.join(sys._MEIPASS, 'plugins'),
    ]
    
    for path in plugin_paths:
        if os.path.exists(path):
            os.environ['QT_PLUGIN_PATH'] = path
            print(f"Set QT_PLUGIN_PATH to: {path}")
            
            platforms = os.path.join(path, 'platforms')
            if os.path.exists(platforms):
                os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = platforms
                print(f"Set QT_QPA_PLATFORM_PLUGIN_PATH to: {platforms}")
            break
    
    # Windows 特定设置
    if sys.platform == 'win32':
        os.environ['QT_OPENGL'] = 'angle'
        os.environ['QT_QUICK_BACKEND'] = 'software'
        print("Set Windows-specific Qt environment variables")
'''
    
    with open("runtime_hook_ci.py", "w", encoding="utf-8") as f:
        f.write(runtime_fix)
    
    print("[OK] Created runtime_hook_ci.py")
    
    print("\n" + "=" * 60)
    print("CI/CD fixes applied successfully!")
    print("Use 'baal_windows_ci.spec' for building in CI")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = fix_pyinstaller_spec()
    sys.exit(0 if success else 1)