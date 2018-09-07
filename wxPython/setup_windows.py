import sys
from cx_Freeze import setup, Executable


# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "Type.World",
        version = "0.1.3",
        description = "Type.World – One Click Font-Installer",
        options = {"build_exe": {
          'include_files': ['htmlfiles/'],
          'excludes': [],
          'packages': [],
          'optimize': 2,
          'build_exe': 'Z:\\Code\\TypeWorldApp\\Windows\\Main'
        }},
        executables = [Executable("app.py", base=base, copyright='Copyright 2018 by Yanone', targetName = 'TypeWorld.exe', icon='icon\\tw.ico')])

setup(  name = "Type.World Subscription Opener",
        version = "0.1.3",
        options = {"build_exe": {
         'optimize': 2,
          'build_exe': 'Z:\\Code\\TypeWorldApp\\Windows\\Agent'
        }},
        executables = [Executable("agent.py", base=base, copyright='Copyright 2018 by Yanone', targetName = 'TypeWorld Subscription Opener.exe', icon='icon\\tw.ico')])
