import sys, os
from cx_Freeze import setup, Executable

version = open('Z:/Code/py/git/typeworld/guiapp/currentVersion.txt', 'r').read().strip()

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None

if sys.platform == "win32":
    base = "Win32GUI"

baseFolder = 'Z:/Code/py/git/typeworld/guiapp/wxPython'

# Make dirs
destinationFolder = os.path.join('Z:\\Code\\TypeWorldApp\\apps\\Windows', version)

# if os.path.exists(destinationFolder):
#     import shutil
#     shutil.rmtree(destinationFolder)

# os.makedirs(destinationFolder)



setup(  name = "Type.World",
        version = version.split('-')[0],
        description = "Type.World – One Click Font-Installer",
        options = {"build_exe": {
          'include_files': [
                os.path.join(baseFolder, 'htmlfiles'), 
                os.path.join(baseFolder, 'locales'), 
                os.path.join(baseFolder, 'icon'),
                os.path.join(baseFolder, 'patrons'),
                os.path.join(baseFolder, 'intercom'),
                ],
          'excludes': ['win32ctypes'],
          'packages': ['packaging', 'grpc', 'requests', 'idna', 'pyasn1', 'rsa', 'cachetools', 'grpc', 'cryptography', 'pyasn1_modules', 'typeworld', 'keyring'], # 'google-api-core', 'google-cloud-pubsub'
          'optimize': 2,
          'build_exe': destinationFolder,
        }},
        executables = [
          Executable(os.path.join(baseFolder, "app.py"), base=base, copyright='Copyright 2018 by Yanone', targetName = 'TypeWorld.exe', icon=os.path.join(baseFolder, 'icon', 'tw.ico')),
          Executable(os.path.join(baseFolder, "agent.py"), base=base, copyright='Copyright 2018 by Yanone', targetName = 'TypeWorld Subscription Opener.exe', icon=os.path.join(baseFolder, 'icon', 'tw.ico')),
          Executable(os.path.join(baseFolder, "daemon.py"), base=base, copyright='Copyright 2018 by Yanone', targetName = 'TypeWorld Taskbar Agent.exe', icon=os.path.join(baseFolder, 'icon', 'tw.ico')),
          ])

# setup(  name = "Type.World Subscription Opener",
#         version = version.split('-')[0],
#         options = {"build_exe": {
#          'optimize': 2,
#           'build_exe': os.path.join(destinationFolder, 'URL Opening Agent'),
# #          'build_exe': destinationFolder,
#           'packages': [],
#         }},
#         executables = [Executable(os.path.join(baseFolder, "agent.py"), base=base, copyright='Copyright 2018 by Yanone', targetName = 'TypeWorld Subscription Opener.exe', icon=os.path.join(baseFolder, 'icon', 'tw.ico'))])

# setup(  name = "Type.World Taskbar Agent",
#         version = version.split('-')[0],
#         options = {"build_exe": {
#          'optimize': 2,
# #          'build_exe': destinationFolder,
#           'build_exe': os.path.join(destinationFolder, 'Taskbar Agent'),
#           'packages': ['pystray'],
#           'include_files': [
#                 os.path.join(baseFolder, 'icon'), 
#                 ],
#         }},
#         executables = [Executable(os.path.join(baseFolder, "daemon.py"), base=base, copyright='Copyright 2018 by Yanone', targetName = 'TypeWorld Taskbar Agent.exe', icon=os.path.join(baseFolder, 'icon', 'tw.ico'))])

