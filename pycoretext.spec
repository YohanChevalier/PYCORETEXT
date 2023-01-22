# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['pycoretext.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('.\docs\demo.gif', '.'),
        ('.\docs\schema_pycoretext.jpg', '.'),
        ('.\docs\CGU_open_data_V8.pdf', '.'),
        ('.\docs\specifications_techniques.rst', '.'),
        ('README.rst', '.'),
        ('LICENCE.txt', '.'),
        ('pycoretext.spec', '.'),
        ('.\\pycoretext\\views\\image_login.png', '.'),
        ('.\\pycoretext\\views\\origine_donnees.txt', '.'),
        ('.\\pycoretext\\pycoretext.ico', '.')
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
    [],
    exclude_binaries=True,
    name='pycoretext',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='.\\pycoretext\\pycoretext.ico'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='pycoretext',
)
