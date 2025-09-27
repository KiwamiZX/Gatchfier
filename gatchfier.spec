# gatchfier.spec
block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('icons/gatchfier_logo.png', 'icons'),
        ('icons/gatchfier_logo_dark.png', 'icons'),
        ('icons/gatchfier_icon.png', 'icons'),
        ('icons/splash.png', 'icons'),
        ('icons/splash_dark.png', 'icons'),
        ('icons/moon.png', 'icons'),
        ('icons/sun.png', 'icons'),
        ('config.json', '.'),
    ],
    hiddenimports=['ping3', 'whois'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='Gatchfier',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='icons/gatchfier_icon.png'
)
