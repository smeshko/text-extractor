# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller build specification for Document Data Extractor.

Target: Windows 10/11 64-bit
Build type: Single executable file
GUI: No console window

Usage:
    pyinstaller build.spec

Output:
    dist/DocumentExtractor.exe
"""

import sys
import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect all PyMuPDF dependencies
pymupdf_datas, pymupdf_binaries, pymupdf_hiddenimports = collect_all('pymupdf')

a = Analysis(
    ['src/main.py'],
    pathex=['src'],  # Add src directory to module search path
    binaries=pymupdf_binaries,
    datas=pymupdf_datas + [
        # ('bin/antiword.exe', '.'),  # Bundle antiword for .doc parsing (optional - download separately)
    ],
    hiddenimports=[
        'tkinterdnd2',
        'tkinterdnd2.TkinterDnD',
        'fitz',  # PyMuPDF
        'docx',  # python-docx
        'docx.oxml',
        'docx.text',
        'docx.shared',
        'olefile',  # OLE file reading for .doc
    ] + pymupdf_hiddenimports,
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
    name='DocumentExtractor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Enable UPX compression
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application, no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
