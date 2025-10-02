"""Custom PyInstaller hook for PyMuPDF to bundle all necessary DLLs."""
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files, collect_submodules

# Collect all submodules
hiddenimports = collect_submodules('pymupdf')
hiddenimports += collect_submodules('fitz')

# Collect all dynamic libraries (DLLs)
binaries = collect_dynamic_libs('pymupdf')
binaries += collect_dynamic_libs('fitz')

# Collect all data files
datas = collect_data_files('pymupdf')
datas += collect_data_files('fitz')
