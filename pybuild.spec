# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

options = [
    ("v", None, "OPTION"),
]

a = Analysis(
    ["gui_main.py"],  # 主入口文件
    pathex=[],
    binaries=[],
    datas=[
        (".env", "."),
        ("key.pem", "."),
        ("cert.pem", "."),
        ("static/touchpad.html", "./static/"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name="Touchpad",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="static/icon.ico",
)
