# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_all

# 收集必要的数据文件
datas = []
hiddenimports = []
binaries = []

# 收集 PyQt6 平台插件和依赖
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

qt6_datas = collect_data_files('PyQt6')
qt6_binaries = collect_dynamic_libs('PyQt6')
datas += qt6_datas
binaries += qt6_binaries

# 关键修复：确保包含所有 Qt 平台插件（这是 Windows 闪退的主要原因）
try:
    # PyInstaller 6.x 使用不同的方式收集 Qt 插件
    from PyInstaller.utils.hooks import collect_submodules, collect_all
    
    # 收集所有 PyQt6 相关的二进制文件和数据
    pyqt6_all = collect_all('PyQt6')
    datas += pyqt6_all[0]  # datas
    binaries += pyqt6_all[1]  # binaries
    hiddenimports += pyqt6_all[2]  # hiddenimports
    
    # 额外收集 Qt6 核心组件
    qt6_all = collect_all('PyQt6.Qt6')
    datas += qt6_all[0]
    binaries += qt6_all[1]
    hiddenimports += qt6_all[2]
    
    print("✓ PyQt6 collected via collect_all")
except Exception as e:
    print(f"Warning: Could not use collect_all: {e}")

# 手动确保包含关键的 Qt 插件
try:
    import PyQt6
    import os
    qt6_path = os.path.dirname(PyQt6.__file__)
    
    # 查找并添加插件目录
    plugin_base = os.path.join(qt6_path, 'Qt6', 'plugins')
    if os.path.exists(plugin_base):
        # 平台插件（关键！Windows 必须）
        platforms_path = os.path.join(plugin_base, 'platforms')
        if os.path.exists(platforms_path):
            for file in os.listdir(platforms_path):
                if file.endswith('.dll'):
                    binaries.append((os.path.join(platforms_path, file), 'PyQt6/Qt6/plugins/platforms'))
            print(f"✓ Added platform plugins from {platforms_path}")
        
        # 样式插件
        styles_path = os.path.join(plugin_base, 'styles')
        if os.path.exists(styles_path):
            for file in os.listdir(styles_path):
                if file.endswith('.dll'):
                    binaries.append((os.path.join(styles_path, file), 'PyQt6/Qt6/plugins/styles'))
        
        # 图像格式插件
        imageformats_path = os.path.join(plugin_base, 'imageformats')
        if os.path.exists(imageformats_path):
            for file in os.listdir(imageformats_path):
                if file.endswith('.dll'):
                    binaries.append((os.path.join(imageformats_path, file), 'PyQt6/Qt6/plugins/imageformats'))
        
        # 图标引擎插件
        iconengines_path = os.path.join(plugin_base, 'iconengines')
        if os.path.exists(iconengines_path):
            for file in os.listdir(iconengines_path):
                if file.endswith('.dll'):
                    binaries.append((os.path.join(iconengines_path, file), 'PyQt6/Qt6/plugins/iconengines'))
        
        # 添加 Windows 特定的 Qt 二进制文件
        qt6_bin_path = os.path.join(qt6_path, 'Qt6', 'bin')
        if os.path.exists(qt6_bin_path):
            # 关键的 Qt 运行时库
            important_dlls = [
                'Qt6Core.dll', 'Qt6Gui.dll', 'Qt6Widgets.dll',
                'Qt6Network.dll', 'Qt6Svg.dll', 'Qt6PrintSupport.dll',
                'd3dcompiler_47.dll', 'opengl32sw.dll'
            ]
            for dll in important_dlls:
                dll_path = os.path.join(qt6_bin_path, dll)
                if os.path.exists(dll_path):
                    binaries.append((dll_path, '.'))
                    print(f"✓ Added {dll}")
    else:
        print(f"Warning: Qt plugin directory not found at {plugin_base}")
        
except Exception as e:
    print(f"Error manually adding Qt plugins: {e}")

# 收集 aw-client 和 aw-core 模块
aw_client_datas, aw_client_binaries, aw_client_hiddenimports = collect_all('aw_client')
aw_core_datas, aw_core_binaries, aw_core_hiddenimports = collect_all('aw_core')

datas += aw_client_datas + aw_core_datas
binaries += aw_client_binaries + aw_core_binaries
hiddenimports += aw_client_hiddenimports + aw_core_hiddenimports

# 添加 baal 资源文件
datas += [
    ('baal/resources/cat.png', 'baal/resources'),
    ('baal/references/*.md', 'baal/references'),
    ('动作表情拆分/*.png', '动作表情拆分'),
    ('动作表情拆分/*.gif', '动作表情拆分'),
]

# 添加隐藏导入
hiddenimports += [
    'aw_client',
    'aw_client.client',
    'aw_core',
    'aw_core.models',
    'aw_transform',
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.QtNetwork',
    'PyQt6.QtPrintSupport',  # Windows 上可能需要
    'PyQt6.sip',
    'PyQt6.uic',
    'httpx',
    'volcengine_python_sdk',
    'requests',
    'langchain',
    'langchain_openai',
    'langchain_core',
    'langchain_core.messages',
    'langchain_core.prompts',
    'langchain_core.runnables',
    'persist_queue',
    'appdirs',
    'iso8601',
    'peewee',
    'jsonschema',
    'icalendar',
    'baal.scheduler',
    'baal.scheduler.manager',
    'baal.scheduler.models',
    'baal.scheduler.goals',
    'baal.scheduler.schedule_trigger',
    'baal.desktop_pet.supervision_mode',
    'baal.desktop_pet.core.single_instance',
    'baal.desktop_pet.core.logger_config',
    'baal.desktop_pet.ui.developer_console',
    'pytz',
    'dateutil',
    'dateutil.parser',
    'dateutil.rrule',
    'dateutil.tz',
    'pydantic',
    'pydantic.deprecated',
    'pydantic.deprecated.decorator',
    'pydantic._internal',
    'pydantic._internal._validators'
]

a = Analysis(
    ['run_desktop_pet.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook_pyqt6.py'],  # 添加运行时钩子，修复 Qt 插件路径问题
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'numpy',
        'pandas',
        'notebook',
        'jupyter',
        'IPython',
        'test',
        'tests',
        'PyQt5',
        'PyQt5_sip',
        'PySide2',
        'PySide6'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Windows独立EXE文件
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
    upx=False,  # Disabled to prevent potential crashes
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='baal/resources/app_icon.ico' if os.path.exists('baal/resources/app_icon.ico') else None,  # Windows需要.ico格式图标
    version_file=None,
    uac_admin=False,  # 不需要管理员权限
    uac_uiaccess=False
)