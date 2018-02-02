from setuptools import setup
import os

# A custom plist for letting it associate with all files.
Plist = dict(CFBundleDocumentTypes= [dict(CFBundleTypeExtensions=["*"],
                                          #CFBundleTypeName="kUTTypeText", # this should be text files, but I'm not sure the details.
                                          CFBundleTypeRole="Editor"),
                                    ]
             )

version = '0.1.1'

APP = ['app.py']
DATA_FILES = []
OPTIONS = {'argv_emulation': False, # this puts the names of dropped files into sys.argv when starting the app.
           'iconfile': 'icon/tw.icns',
           'plist': Plist,
           'includes': ['ynlib', 'wx', 'os', 'webbrowser', 'urllib', 'base64', 'threading'],
           'frameworks': ['Python.framework'],
           'resources': ['html', 'locales', '/Users/yanone/Code/dsa_pub.pem'],
           'packages': ['./AppBadge.docktileplugin'],
           'bdist_base': '%s/Code/TypeWorldApp/build/' % os.path.expanduser('~'),
           'dist_dir': '%s/Code/TypeWorldApp/dist/' % os.path.expanduser('~'),
           'plist': {
                'CFBundleName': 'Type.World',
                'CFBundleShortVersionString':version, # must be in X.X.X format
                'CFBundleVersion': version,
                'CFBundleIdentifier':'world.type.guiapp', #optional
                'NSHumanReadableCopyright': '@ Yanone 2018', #optional
                'CFBundleDevelopmentRegion': 'English', #optional - English is default
                'NSDockTilePlugIn': '@executable_path/../Resources/lib/python2.7/AppBadge.docktileplugin.py',

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



setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)


os.system('echo "%s" > %s/Code/TypeWorldApp/build/version' % (OPTIONS['plist']['CFBundleShortVersionString'], os.path.expanduser('~')))
