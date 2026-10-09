# -*- mode: python ; coding: utf-8 -*-

import importlib.util as _ilu

# ===========================================================================
# v1.5.68 构建前置检查 —— 打包环境必须有 Pillow, 否则连拍会静默失效
# ---------------------------------------------------------------------------
# 血泪教训: buildenv 是个手工维护的 venv(include-system-site-packages=false)。
# 2026-10-07 16:35 重建 buildenv 时只装了 pyinstaller, 漏了 Pillow —— 之后
# v1.5.59 起所有安装包都不含 PIL, 连拍(ImageGrab)一直报
#   ImportError: cannot import name 'ImageGrab' from 'PIL' (unknown location)
# 而源码运行用的是系统 Python(有 Pillow) + 测试用注入的假 grab, 全都测不出来,
# 表现为"更新几次连拍就坏"。这里直接把检查卡在打包入口, 缺库就中止构建。
# ===========================================================================
if _ilu.find_spec("PIL") is None:
    raise SystemExit(
        "\n" + "=" * 66 + "\n"
        "[打包中止] 打包环境缺少 Pillow —— 连拍功能会坏！\n"
        "  症状: ImportError: cannot import name 'ImageGrab' from 'PIL'\n"
        "  修复: buildenv\\Scripts\\pip install Pillow\n"
        + "=" * 66 + "\n")


a = Analysis(
    ['zzmi_manager.py'],
    pathex=[],
    binaries=[],
    datas=[('ui.html', '.'), ('bg.jpg', '.'), ('installer/app.ico', '.')],
    # v1.5.68: 连拍用 PIL。PIL.JpegImagePlugin 是保存 JPEG 时才延迟导入的,
    # PyInstaller 静态分析抓不到, 必须显式列出来(否则打包后存图报
    # "encoder jpeg not available")。
    hiddenimports=[
        'PIL', 'PIL.Image', 'PIL.ImageFile', 'PIL.ImageGrab', 'PIL.ImageOps',
        'PIL.JpegImagePlugin', 'PIL.BmpImagePlugin', 'PIL.PngImagePlugin',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # telethon: v1.5.59 起蓝飞机已整体移除, 全代码不再 import telethon; 留这条纯防误装
    # numpy/scipy: 主程序不用, 但系统 Python 装了就会被连带收进 exe(实测 16.3MB -> 31MB),
    # 打包环境换机器时务必保留这条。
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


# ===========================================================================
# v1.5.68 构建后自检 —— PIL 必须真的落进包, 否则连拍(ImageGrab)会静默失效
# ---------------------------------------------------------------------------
# 光有构建前检查还不够: 万一 hiddenimports 写错、或 UPX/exclude 误伤,
# 仍然可能产出"没有 PIL 的包"。这里在 COLLECT 之后直接查产物目录, 缺了就报错。
# ===========================================================================
import os as _os
_pil_pkg = _os.path.join(DISTPATH, 'ZZMI-Mod-Manager', '_internal', 'PIL')
if not _os.path.isdir(_pil_pkg):
    raise SystemExit(
        "\n" + "=" * 66 + "\n"
        "[打包自检失败] 产物里没有 PIL 目录 —— 连拍功能会坏！\n"
        "  期望路径: %s\n"
        "  请检查 buildenv 是否装了 Pillow: buildenv\\Scripts\\pip install Pillow\n"
        % _pil_pkg + "=" * 66 + "\n")
_c_ext = [f for f in _os.listdir(_pil_pkg) if f.startswith("_imaging.") and f.endswith(".pyd")]
if not _c_ext:
    raise SystemExit(
        "\n[打包自检失败] PIL 目录在, 但缺 C 扩展 _imaging*.pyd —— 截图会报错！\n")
print("[spec 自检] PIL 已进包: %s | C 扩展: %s" % (_pil_pkg, _c_ext))
