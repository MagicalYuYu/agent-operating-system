# -*- mode: python ; coding: utf-8 -*-
"""
AOS Viewer PyInstaller 打包配置（onefile 模式）
onefile 模式生成单个自包含 EXE，无需 _internal/ 目录，便于分发
"""

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# 收集 webview 的依赖数据
datas = []
datas += collect_data_files('webview')
datas += collect_data_files('clr_loader')
datas += collect_data_files('pythonnet')

# 添加 AOS Viewer 的静态资源（prototype 目录）
aos_viewer_dir = os.path.dirname(os.path.abspath(SPEC))
prototype_dir = os.path.join(aos_viewer_dir, 'prototype')
for root, dirs, files in os.walk(prototype_dir):
    for file in files:
        src = os.path.join(root, file)
        rel = os.path.relpath(root, aos_viewer_dir)
        dst = rel
        datas.append((src, dst))

# 添加 aos_generate_data.py 脚本（作为模块导入）
scripts_dir = os.path.join(os.path.dirname(aos_viewer_dir), 'scripts')
datas.append((os.path.join(scripts_dir, 'aos_generate_data.py'), 'scripts'))

a = Analysis(
    ['aos_viewer_server.py'],
    pathex=[
        aos_viewer_dir,
        scripts_dir,
    ],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'webview',
        'webview.platforms.edgechromium',
        'webview.platforms.winforms',
        'webview.platforms.cocoa',
        'webview.platforms.gtk',
        'webview.platforms.qt',
        'clr_loader',
        'pythoncom',
        'win32com',
        'win32com.client',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# onefile 模式：所有依赖打包进单个 EXE 文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    a.zipfiles,
    [],
    exclude_binaries=False,  # onefile: 包含所有二进制文件
    name='AOS Viewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,  # 使用系统临时目录解压
    console=False,  # 隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='aos_viewer.ico',
    version='version_info.txt',  # EXE 版本信息（嵌入 FileVersion/ProductName 等)
)
