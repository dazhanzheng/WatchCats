# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_all, collect_dynamic_libs, collect_submodules

# 收集必要的数据文件
datas = []
hiddenimports = []
binaries = []

# 收集 PyQt6 完整依赖
from PyInstaller.utils.hooks.qt import get_qt_binaries
qt6_datas = collect_data_files('PyQt6', include_py_files=True)
qt6_binaries = collect_dynamic_libs('PyQt6')
datas += qt6_datas
binaries += qt6_binaries

# 确保 Qt 平台插件被包含
qt_plugins_path = os.path.join(sys.prefix, 'Lib', 'site-packages', 'PyQt6', 'Qt6', 'plugins')
if os.path.exists(qt_plugins_path):
    datas += [(qt_plugins_path, 'PyQt6/Qt6/plugins')]

# 收集 aw-client 和 aw-core 模块
try:
    aw_client_datas, aw_client_binaries, aw_client_hiddenimports = collect_all('aw_client')
    aw_core_datas, aw_core_binaries, aw_core_hiddenimports = collect_all('aw_core')
    datas += aw_client_datas + aw_core_datas
    binaries += aw_client_binaries + aw_core_binaries
    hiddenimports += aw_client_hiddenimports + aw_core_hiddenimports
except:
    print("Warning: Could not collect aw modules")

# 收集 langchain 相关模块
langchain_modules = [
    'langchain',
    'langchain_openai',
    'langchain_core',
    'langchain_community',
]

for module in langchain_modules:
    try:
        module_datas, module_binaries, module_hiddenimports = collect_all(module)
        datas += module_datas
        binaries += module_binaries
        hiddenimports += module_hiddenimports
    except:
        print(f"Warning: Could not collect {module}")

# 添加 baal 资源文件
resource_files = [
    ('baal/resources', 'baal/resources'),
    ('baal/references', 'baal/references'),
    ('动作表情拆分', '动作表情拆分'),
]

for src, dst in resource_files:
    if os.path.exists(src):
        if os.path.isdir(src):
            for root, dirs, files in os.walk(src):
                for file in files:
                    src_path = os.path.join(root, file)
                    dst_path = os.path.join(dst, os.path.relpath(src_path, src))
                    datas.append((src_path, os.path.dirname(dst_path)))
        else:
            datas.append((src, dst))

# 添加所有必要的隐藏导入
hiddenimports += [
    # Core modules
    'baal',
    'baal.desktop_pet',
    'baal.desktop_pet.main',
    'baal.desktop_pet.core',
    'baal.desktop_pet.core.config_manager',
    'baal.desktop_pet.core.llm_handler',
    'baal.desktop_pet.core.emotion_manager',
    'baal.desktop_pet.core.persona_manager',
    'baal.desktop_pet.core.single_instance',
    'baal.desktop_pet.core.logger_config',
    'baal.desktop_pet.ui',
    'baal.desktop_pet.ui.pet_window',
    'baal.desktop_pet.ui.chat_bubble',
    'baal.desktop_pet.ui.settings_dialog',
    'baal.desktop_pet.ui.supervision_dialog',
    'baal.desktop_pet.ui.goals_dialog',
    'baal.desktop_pet.ui.calendar_dialog_modern',
    'baal.desktop_pet.ui.developer_console',
    'baal.desktop_pet.supervision_mode',
    
    # LLM Assistant
    'baal.llm_assistant',
    'baal.llm_assistant.assistant',
    'baal.llm_assistant.binary_intent_classifier',
    'baal.llm_assistant.parsers',
    
    # AW Stats
    'baal.aw_stats',
    'baal.aw_stats.stats_processor',
    
    # Scheduler
    'baal.scheduler',
    'baal.scheduler.schedule_manager',
    'baal.scheduler.manager',
    'baal.scheduler.models',
    'baal.scheduler.goals',
    'baal.scheduler.schedule_trigger',
    
    # PyQt6
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.QtNetwork',
    'PyQt6.sip',
    'PyQt6.uic',
    
    # Dependencies
    'httpx',
    'httpcore',
    'h11',
    'volcengine_python_sdk',
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna',
    'persist_queue',
    'appdirs',
    'iso8601',
    'peewee',
    'jsonschema',
    'icalendar',
    'pytz',
    'dateutil',
    'dateutil.parser',
    'dateutil.rrule',
    'dateutil.tz',
    'pydantic',
    'pydantic.deprecated',
    'pydantic.deprecated.decorator',
    'pydantic._internal',
    'pydantic._internal._validators',
    'typing_extensions',
    'annotated_types',
    
    # AW modules
    'aw_client',
    'aw_client.client',
    'aw_core',
    'aw_core.models',
    'aw_transform',
    
    # Additional imports that might be missing
    'encodings',
    'encodings.utf_8',
    'encodings.cp1252',
    'encodings.mbcs',
    'win32com',
    'win32com.client',
    'pythoncom',
]

a = Analysis(
    ['run_desktop_pet.py'],
    pathex=['.', 'baal'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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

# Windows调试版EXE文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WatchCats_debug',
    debug=True,  # 启用调试模式
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 禁用UPX压缩避免潜在崩溃
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台窗口以查看错误信息
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='baal/resources/app_icon.ico' if os.path.exists('baal/resources/app_icon.ico') else None,
    version_file=None,
    uac_admin=False,
    uac_uiaccess=False
)