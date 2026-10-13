# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec: build with `make package` (output in dist/pac-man/).
import sys

a = Analysis(
    ["src/__main__.py"],
    pathex=["src"],
    datas=[("src/ui/assets", "ui/assets")],
    excludes=["mypy", "flake8", "pycodestyle", "pyflakes", "tkinter"],
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="pac-man",
    # No terminal window behind the game on Windows
    console=sys.platform != "win32",
)
coll = COLLECT(exe, a.binaries, a.datas, name="pac-man")
