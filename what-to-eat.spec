# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

site_packages = Path(r"C:\Repos\python\what-to-eat\venv\Lib\site-packages")

# Collect all dist-info directories for packages that need metadata at runtime
metadata_packages = [
    'streamlit', 'altair', 'pydeck', 'pandas', 'numpy', 'pillow',
    'jinja2', 'click', 'tornado', 'protobuf', 'pyarrow', 'packaging',
    'narwhals', 'blinker', 'cachetools', 'gitpython', 'toml', 'requests',
    'jsonschema', 'typing_extensions', 'tenacity', 'watchdog',
]
metadata_datas = []
for dist_info in site_packages.glob('*.dist-info'):
    metadata_datas.append((str(dist_info), dist_info.name))

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app.py', '.'),
        ('assets', 'assets'),
        ('lib', 'lib'),
        (str(site_packages / 'streamlit'), 'streamlit'),
        (str(site_packages / 'altair'), 'altair'),
        (str(site_packages / 'webview'), 'webview'),
    ] + metadata_datas,
    hiddenimports=[
        'streamlit',
        'streamlit.web.cli',
        'streamlit.runtime.scriptrunner',
        'streamlit.runtime.scriptrunner.magic_funcs',
        'webview',
        'bottle',
        'proxy_tools',
        'clr',
        'pythonnet',
        'lib',
        'lib.db',
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
    [],
    exclude_binaries=True,
    name='what-to-eat',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='what-to-eat',
)
