import sys, os
from cx_Freeze import setup, Executable

version = open('Z:/Code/py/git/typeWorld/guiapp/currentVersion.txt', 'r').read().strip()

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

baseFolder = 'Z:/Code/py/git/typeWorld/guiapp/wxPython'

# Make dirs
destinationFolder = os.path.join('Z:\\Code\\TypeWorldApp\\apps\\Windows', version)

# if os.path.exists(destinationFolder):
#     import shutil
#     shutil.rmtree(destinationFolder)

# os.makedirs(destinationFolder)


setup(  name = "Type.World",
        version = version,
        description = "Type.World – One Click Font-Installer",
        options = {"build_exe": {
          'include_files': [
                os.path.join(baseFolder, 'htmlfiles'), 
                os.path.join(baseFolder, 'locales'), 
                ],
          'excludes': [],
          'packages': [],
          'optimize': 2,
          'build_exe': destinationFolder
        }},
        executables = [Executable(os.path.join(baseFolder, "app.py"), base=base, copyright='Copyright 2018 by Yanone', targetName = 'TypeWorld.exe', icon=os.path.join(baseFolder, 'icon', 'tw.ico'))])

setup(  name = "Type.World Subscription Opener",
        version = version,
        options = {"build_exe": {
         'optimize': 2,
          'build_exe': os.path.join(destinationFolder, 'URL Opening Agent'),
          'packages': [],
        }},
        executables = [Executable(os.path.join(baseFolder, "agent.py"), base=base, copyright='Copyright 2018 by Yanone', targetName = 'TypeWorld Subscription Opener.exe', icon=os.path.join(baseFolder, 'icon', 'tw.ico'))])

