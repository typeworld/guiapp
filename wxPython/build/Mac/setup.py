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
                '/Users/yanone/Code/dsa_pub.pem',
            ], #, 'appbadge.docktileplugin'
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
                'CFBundleURLTypes': [{'CFBundleURLName': 'Type.World Font Installation Protocols', 'CFBundleURLSchemes': ['typeworldjson', 'typeworldgithub', 'typeworldapp']}],
#                'LSUIElement': True, # No dock icon

                # Sparkle
                'SUFeedURL': 'https://type.world/downloads/guiapp/appcast.xml',
                'SUEnableAutomaticChecks': True,
                'SUPublicDSAKeyFile': 'dsa_pub.pem',
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
os.chdir('/Users/yanone/Code/TypeWorldApp/dist/Type.World.app/Contents/Resources/lib/python3.6/lib-dynload/wx/')
for file in ['libwx_baseu-3.0.0.4.0.dylib', 'libwx_osx_cocoau_core-3.0.0.4.0.dylib', 'libwx_osx_cocoau_webview-3.0.0.4.0.dylib', 'libwx_baseu_net-3.0.0.4.0.dylib']:
    assert os.system('ln -s ../../../../../Frameworks/%s %s' % (file, file)) == 0