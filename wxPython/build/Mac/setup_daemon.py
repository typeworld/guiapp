from setuptools import setup
import os

version = open('/Users/yanone/Code/py/git/typeWorld/guiapp/currentVersion.txt', 'r').read().strip()

os.system('rm -rf ~/Code/TypeWorldApp/apps/Mac/Type.World.%s.app' % version)

setup(
    app=['/Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/daemon.py'],
    data_files=[],
    options={'py2app': {'argv_emulation': False, # this puts the names of dropped files into sys.argv when starting the app.
           'iconfile': '/Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/icon/tw.icns',
#           'includes': ['locales'],
 #          'excludes': [],
 #          'frameworks': ['Python.framework'],
           'resources': ['/Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/icon/MacSystemTrayIcon.pdf', '/Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/icon/MacSystemTrayIcon_Notification.pdf', '/Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/locales'], #, 'appbadge.docktileplugin'
           # 'packages': ['certifi'],
           'bdist_base': '%s/Code/TypeWorldApp/build/' % os.path.expanduser('~'),
           'dist_dir': '%s/Code/TypeWorldApp/dist/' % os.path.expanduser('~'),
           'plist': {
                'CFBundleName': 'Type.World Agent',
                'CFBundleShortVersionString':version, # must be in X.X.X format
                'CFBundleVersion': version,
                'CFBundleIdentifier':'world.type.agent', #optional
                'NSHumanReadableCopyright': '@ Yanone 2020', #optional
                'CFBundleDevelopmentRegion': 'English', #optional - English is default
                'LSUIElement': True, # daemon mode, no dock icon
                },
           'strip': True,
           'optimize': 10,
     'semi_standalone': False,
           }},
    setup_requires=['py2app'],
)


