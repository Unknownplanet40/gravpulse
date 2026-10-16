# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

# Sync version_info.txt with VERSION file if present
ver_file = Path("VERSION")
if ver_file.exists():
    ver_str = ver_file.read_text(encoding="utf-8").strip()
    parts = [int(p) if p.isdigit() else 0 for p in ver_str.split(".")]
    while len(parts) < 4:
        parts.append(0)
    file_ver = tuple(parts[:4])
    vinfo_content = f'''# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={file_ver},
    prodvers={file_ver},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          '040904B0',
          [
            StringStruct('CompanyName', 'GravPulse'),
            StringStruct('FileDescription', 'GravPulse - Real-time AI Quota Monitor for Antigravity'),
            StringStruct('FileVersion', '{ver_str}'),
            StringStruct('InternalName', 'GravPulse'),
            StringStruct('LegalCopyright', 'Copyright (c) 2026 GravPulse. All rights reserved.'),
            StringStruct('OriginalFilename', 'GravPulse.exe'),
            StringStruct('ProductName', 'GravPulse'),
            StringStruct('ProductVersion', '{ver_str}'),
            StringStruct('Comments', 'Track Antigravity AI quotas and models in real-time.')
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
'''
    Path("version_info.txt").write_text(vinfo_content, encoding="utf-8")

a = Analysis(
    ['main.pyw'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='GravPulse',
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
    icon=['assets/ico/app.ico'],
    version='version_info.txt',
)
