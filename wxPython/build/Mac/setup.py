from setuptools import setup
import os

version = open('/Users/yanone/Code/py/git/typeWorld/guiapp/currentVersion.txt', 'r').read().strip()

os.system('rm -rf ~/Code/TypeWorldApp/apps/Mac/Type.World.%s.app' % version)

options = {'py2app': {'argv_emulation': False, # this puts the names of dropped files into sys.argv when starting the app.
           'iconfile': '/Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/icon/tw.icns',
           'includes': ['ynlib'],#, 'os', 'webbrowser', 'urllib', 'base64', 'keyring'],
           'frameworks': ['Python.framework'],
           'resources': [
                '/Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/build/Mac/InternetAccessPolicy.plist', 
                '/Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/build/Mac/Little Snitch Translations', 
                '/Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/htmlfiles', 
                '/Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/patrons', 
                '/Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/locales', 
                # Sparkle < 1.12.0
                '/Users/yanone/Code/Certificates/Type.World Sparkle/dsa_pub.pem',
            ], #, 'appbadge.docktileplugin'
           'packages': ['certifi'], # , 'google-api-core', 'google-cloud-pubsub'
           'bdist_base': '%s/Code/TypeWorldApp/build/' % os.path.expanduser('~'),
           'dist_dir': '%s/Code/TypeWorldApp/dist/' % os.path.expanduser('~'),
           'plist': {
                'CFBundleName': 'Type.World',
                'CFBundleShortVersionString':version, # must be in X.X.X format
                'CFBundleVersion': version,
                'CFBundleIdentifier':'world.type.guiapp', #optional
                'NSHumanReadableCopyright': '@ Yanone 2020', #optional
                'CFBundleDevelopmentRegion': 'English', #optional - English is default
                'NSDockTilePlugIn': '@executable_path/../Resources/AppBadge.docktileplugin',
#                'NSDockTilePlugIn': 'appbadge.docktileplugin',
                'CFBundleURLTypes': [{'CFBundleURLName': 'Type.World Font Installation Protocols', 'CFBundleURLSchemes': ['typeworld', 'typeworldapp']}],
#                'LSUIElement': True, # No dock icon

                # Sparkle
                'SUFeedURL': 'https://type.world/downloads/guiapp/appcast.xml',
                'SUEnableAutomaticChecks': True,

                # Sparkle < 1.20.0
                'SUPublicDSAKeyFile': 'dsa_pub.pem',
                # Sparkle >= 1.20.1
                'SUPublicEDKey': 'WCzTmqV1rYPS/fi26Os2vmQGsfshmsOqGJY5wANr4r0=',

                'SUAllowsAutomaticUpdates': True,
                },
           'strip': True,
#           'debug-skip-macholib': True,
           'optimize': 1,
#     'semi_standalone': False,
#     'no-chdir': True,
           }}


# Little Snitch Translations
folder = '/Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/build/Mac/Little Snitch Translations'
options['py2app']['resources'].extend([os.path.join(folder, x) for x in next(os.walk(folder))[1]])


setup(
    app=['/Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/app.py'],
    data_files=[],
    options=options,
    setup_requires=['py2app'],
)




# Attention: Hack!
os.chdir('/Users/yanone/Code/TypeWorldApp/dist/Type.World.app/Contents/Resources/lib/python3.7/lib-dynload/wx/')
for file in ['libwx_baseu-3.0.0.4.0.dylib', 'libwx_osx_cocoau_core-3.0.0.4.0.dylib', 'libwx_osx_cocoau_webview-3.0.0.4.0.dylib', 'libwx_baseu_net-3.0.0.4.0.dylib']:
    assert os.system('ln -s ../../../../../Frameworks/%s %s' % (file, file)) == 0