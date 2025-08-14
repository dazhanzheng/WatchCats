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