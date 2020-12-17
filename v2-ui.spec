# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

BASE_DIR = os.path.abspath('')

datas = [
  (os.path.join(BASE_DIR, 'bin'), './bin'),
  (os.path.join(BASE_DIR, 'templates'), './templates'),
  (os.path.join(BASE_DIR, 'translations'), './translations'),
  (os.path.join(BASE_DIR, 'static'), './static'),
  (os.path.join(BASE_DIR, 'template_config.json'), '.'),
  (os.path.join(BASE_DIR, 'v2-ui.service'), '.'),
]

a = Analysis(['v2-ui.py'],
             pathex=[BASE_DIR],
             binaries=[],
             datas=datas,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='v2-ui',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='v2-ui')