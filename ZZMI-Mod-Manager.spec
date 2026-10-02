# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['zzmi_manager.py'],
    pathex=[],
    binaries=[],
    datas=[('ui.html', '.'), ('bg.jpg', '.'), ('installer/app.ico', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # telethon: v1.5.22 蓝飞机下线; numpy/scipy: 主程序不用, 但系统 Python 装了
    # 就会被连带收进 exe(实测 16.3MB -> 31MB), 打包环境换机器时务必保留这条。
    excludes=["telethon", "numpy", "scipy", "pandas", "matplotlib"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ZZMI-Mod-Manager',
    debug=False,
    uac_admin=True,  # 默认以管理员权限启动(嵌 requireAdministrator 清单)
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['installer/app.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ZZMI-Mod-Manager',
)
