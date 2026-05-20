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
    excludes=[
        # 测试框架
        'unittest',

        # 数据格式
        'xml',
        'json',

        # 压缩格式
        'bz2',
        'lzma',
        'gzip',

        # 数据库
        'sqlite3',

        # 网络客户端
        'ftplib',
        'smtplib',
        'poplib',
        'imaplib',

        # 数学计算
        'math',
        'cmath',
        'decimal',
        'fractions',
        'statistics',

        # 进程管理
        'multiprocessing',

        # 文件系统
        'glob',        

        # 其他
        'gettext',
        'argparse',
        'cmd',
        'code',
        'compileall',
        'py_compile',        

        'cryptography',
        'pytest',
    ],
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
    strip=True,
    upx=True,
    upx_exclude=[
        '*.dll',
        '*.pyd',
    ],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="static/icon.ico",
    onefile=True,
)
