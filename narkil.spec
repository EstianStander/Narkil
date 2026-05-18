# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Narkil ERP
# Build:  pyinstaller narkil.spec

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets',  'assets'),
        ('core',    'core'),
        ('modules', 'modules'),
        ('ui',      'ui'),
    ],
    hiddenimports=[
        'pymongo',
        'pymongo.mongo_client',
        'pymongo.collection',
        'pymongo.uri_parser',
        'bcrypt',
        'bson',
        'bson.objectid',
        'email.message',
        'smtplib',
        'secrets',
        'datetime',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Narkil',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # No console / black window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app-icon.ico',
)
