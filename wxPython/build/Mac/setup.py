from setuptools import setup
import os
import sys

import urllib.request, ssl, certifi

request = urllib.request.Request(
    f"https://api.type.world/latestUnpublishedVersion/world.type.guiapp/mac/?APPBUILD_KEY={os.environ['APPBUILD_KEY']}"
)
sslcontext = ssl.create_default_context(cafile=certifi.where())
response = urllib.request.urlopen(request, context=sslcontext)
version = response.read().decode()

import zmq

print(f"setup.py {sys.version} {zmq} {zmq.zmq_version()} {zmq.pyzmq_version()}")
print(sys.path)


options = {
    "py2app": {
        "argv_emulation": False,  # this puts the names of dropped files into sys.argv when starting the app.
        "iconfile": "wxPython/icon/tw.icns",
        "includes": [
            "importlib_metadata",
            "os",
            # "html",
            # "/Users/appveyor/.localpython3.7.9/lib/python3.7/html",
        ],
        "excludes": ["numpy", "distutils", "encodings", "pytz"],
        "frameworks": ["Python.framework"],
        "resources": [
            "wxPython/build/Mac/InternetAccessPolicy.plist",
            "wxPython/build/Mac/Little Snitch Translations",
            "wxPython/htmlfiles",
            "wxPython/patrons",
            "wxPython/patrons",
            "wxPython/locales",
            "wxPython/typeworldguiapp",
            # "appbadge.docktileplugin",
        ],
        "packages": [
            "chardet",
            "zmq",
            "certifi",
            "distutils",
            "fonttools",
            "fractions",
            "statistics",
            "contextvars",
            "asyncio",
            "encodings",
            "codecs",
            "io",
            "abc",
            "os",
            "stat",
            "typeworld",
            "keyring",
            "importlib",
            "pystray",
            "markdown2",
            "pkg_resources",
            "_collections_abc",
            "posixpath",
            "genericpath",
            "linecache",
            "functools",
            "collections",
            "operator",
            "keyword",
            # "flask",  # flask
            # "jinja2",  # flask
            # "markupsafe",  # flask
            # "werkzeug",  # flask
            # # "html",  # flask
            # "itsdangerous",  # flask
            # "click",  # flask
            # "dataclasses",  # flask
            # "secrets",  # flask
            "heapq",
            "reprlib",
            "tokenize",
            "re",
            "enum",
            "types",
            "sre_compile",
            "sre_parse",
            "sre_constants",
            "copyreg",
            "token",
            "ctypes",
            "struct",
            "webbrowser",
            "shlex",
            "shutil",
            "fnmatch",
            "subprocess",
            "signal",
            "warnings",
            "selectors",
            "threading",
            "traceback",
            "_weakrefset",
            "urllib",
            "base64",
            "bisect",
            "email",
            "hashlib",
            "http",
            "string",
            "quopri",
            "random",
            "socket",
            "datetime",
            "calendar",
            "locale",
            "uu",
            "tempfile",
            "weakref",
            "contextlib",
            "plistlib",
            "xml",
            "json",
            "semver",
            "__future__",
            "argparse",
            "gettext",
            "platform",
            "logging",
            "wx",
            "multiprocessing",
            "pickle",
            "_compat_pickle",
            "ssl",
            "inspect",
            "dis",
            "opcode",
            "copy",
            "zipfile",
            "markdown2",
            "optparse",
            "textwrap",
            "AppKit",
            "objc",
            "pkgutil",
            "ntpath",
            "pyparsing",
            "pkg_resources",
            "pprint",
            "sysconfig",
            "_osx_support",
            "_sysconfigdata_m_darwin_darwin",
            "typing",
            "Foundation",
            "six",
            # "grpc",
            "concurrent",
            "requests",
            "urllib3",
            "queue",
            "hmac",
            "mimetypes",
            "chardet",
            "idna",
            "stringprep",
            "pyasn1",
            "pyasn1_modules",
            "rsa",
            "cachetools",
            # "pytz",
            "uuid",
            "configparser",
            "importlib_metadata",
            "csv",
            "zipp",
            "more_itertools",
            "pathlib",
            "_strptime",
            "difflib",
            "jsonpickle",
            "decimal",
            "_pydecimal",
            "numbers",
            "ast",
            "site",
            "_sitebuiltins",
            "runpy",
        ],
        "bdist_base": "build",
        "dist_dir": "dist",
        "plist": {
            "CFBundleName": "Type.World",
            "CFBundleShortVersionString": version,  # must be in X.X.X format
            "CFBundleVersion": version,
            "CFBundleIdentifier": "world.type.guiapp",  # optional
            "NSHumanReadableCopyright": "@ Yanone 2020",  # optional
            "CFBundleDevelopmentRegion": "English",  # optional - English is default
            # 'NSDockTilePlugIn': '@executable_path/../Resources/AppBadge.docktileplugin',
            "CFBundleURLTypes": [
                {
                    "CFBundleURLName": "Type.World Font Installation Protocols",
                    "CFBundleURLSchemes": ["typeworld", "typeworldapp"],
                }
            ],
            #                'LSUIElement': True, # No dock icon
            # Sparkle
            "SUFeedURL": "https://api.type.world/appcast/world.type.guiapp/mac/normal/appcast.xml",
            "SUPublicEDKey": "ZwplGI76S+oA1VLkFmyugupUgvom8oFWXDUZsNb0jBc=",
            "SUEnableAutomaticChecks": True,
            "SUAllowsAutomaticUpdates": True,
            "LSMinimumSystemVersion": "10.14",
        },
        "strip": True,
        "optimize": 1,
    }
}


# Little Snitch Translations
folder = "wxPython/build/Mac/Little Snitch Translations"
options["py2app"]["resources"].extend([os.path.join(folder, x) for x in next(os.walk(folder))[1]])


setup(
    app=["wxPython/app.py"],
    data_files=[],
    options=options,
    setup_requires=["py2app"],
)


# # Attention: Hack!
# os.chdir('/Users/yanone/Code/TypeWorldApp/dist/Type.World.app/Contents/Resources/lib/python3.7/lib-dynload/wx/')
# for file in ['libwx_baseu-3.0.0.4.0.dylib', 'libwx_osx_cocoau_core-3.0.0.4.0.dylib', 'libwx_osx_cocoau_webview-3.0.0.4.0.dylib', 'libwx_baseu_net-3.0.0.4.0.dylib']:
#     assert os.system('ln -s ../../../../../Frameworks/%s %s' % (file, file)) == 0
