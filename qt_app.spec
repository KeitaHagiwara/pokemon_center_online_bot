# -*- mode: python ; coding: utf-8 -*-

added_files = [
    # Pythonモジュール（scrapingとutils）
    ('scraping', 'scraping'),
    ('utils', 'utils'),

    # env
    ('.env', '.'),

    # scripts file
    ('scripts', 'scripts'),

    # credential files
    ('credentials', 'credentials'),

    # icon file
    ('assets', 'assets')
]

a = Analysis(
    ['qt_app.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'config',
        'test_function',
        'initialize_gmail',
        'apply_lottery',
        'check_results',
        'create_user',
        'make_payment',
        'dotenv',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'PyQt6.sip',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='qt_app',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='サンプルアプリケーション.app',
    icon=None,
    bundle_identifier='com.sample.qtsample',
)

