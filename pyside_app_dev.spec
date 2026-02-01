# -*- mode: python ; coding: utf-8 -*-

added_files = [
    # Pythonモジュール（scrapingとutils）
    ('scraping', 'scraping'),
    ('utils', 'utils'),
    ('components', 'components'),

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
    ['pyside_app.py'],
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
        'PySide6.QtCore',
        'PySide6.QtWidgets',
        'PySide6.QtGui',
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
    [],
    exclude_binaries=True,
    name='pyside_app',
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

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='pyside_app',
)

app = BUNDLE(
    coll,
    name='ポケセンオンライン自動化ツール.app',
    icon=None,
    bundle_identifier='com.sample.pyside_sample',
)
