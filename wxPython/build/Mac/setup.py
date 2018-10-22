from setuptools import setup
import os

version = open('/Users/yanone/Code/py/git/typeWorld/guiapp/currentVersion.txt', 'r').read().strip()

APP = ['/Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/app.py']
DATA_FILES = []
OPTIONS = {'argv_emulation': False, # this puts the names of dropped files into sys.argv when starting the app.
           'iconfile': 'icon/tw.icns',
           'includes': ['ynlib', 'wx', 'os', 'webbrowser', 'urllib', 'base64', 'threading', 'keyring'],
           'frameworks': ['Python.framework'],
            'resources': ['html', 'locales', '/Users/yanone/Code/dsa_pub.pem'], #, 'appbadge.docktileplugin'
           'packages': ['certifi'],
           'bdist_base': '%s/Code/TypeWorldApp/build/' % os.path.expanduser('~'),
           'dist_dir': '%s/Code/TypeWorldApp/dist/' % os.path.expanduser('~'),
           'plist': {
                'CFBundleName': 'Type.World',
                'CFBundleShortVersionString':version, # must be in X.X.X format
                'CFBundleVersion': version,
                'CFBundleIdentifier':'world.type.guiapp', #optional
                'NSHumanReadableCopyright': '@ Yanone 2018', #optional
                'CFBundleDevelopmentRegion': 'English', #optional - English is default
#                'NSDockTilePlugIn': '@executable_path/../Resources/lib/python2.7/AppBadge.docktileplugin.py',
                'NSDockTilePlugIn': 'appbadge.docktileplugin',
                'CFBundleURLTypes': [{'CFBundleURLName': 'Type.World Font Installation Protocols', 'CFBundleURLSchemes': ['typeworldjson', 'typeworldgithub']}],

                # Sparkle
                'SUFeedURL': 'https://type.world/downloads/guiapp/appcast.xml',
                'SUEnableAutomaticChecks': True,
                'SUPublicDSAKeyFile': 'dsa_pub.pem',
                'SUAllowsAutomaticUpdates': True,
                },
           'strip': True,
#           'debug-skip-macholib': True,
           'optimize': 2,
#			'semi_standalone': False,
#			'no-chdir': True,
           }



os.system('rm -rf ~/Code/TypeWorldApp/apps/Type.World.%s.app' % version)


setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)


