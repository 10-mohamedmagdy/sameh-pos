# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_menu.py'],
    pathex=[],
    binaries=[],
    datas=[('sales_inventory.db', '.'), ('*.py', '.')],
    hiddenimports=['PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'cv2', 'numpy', 'PIL', 'pyzbar', 'dateutil', 'reportlab', 'arabic_reshaper', 'bidi', 'win32print', 'barcode', 'escpos', 'escpos.printer', 'sqlite3'],
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
    name='main_menu',
    debug=False,
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
    name='main_menu',
)
