import sys
import os
import json
from cx_Freeze import setup, Executable


import urllib.request, ssl, certifi

request = urllib.request.Request(
    f"https://api.type.world/latestUnpublishedVersion/world.type.guiapp/windows/?APPBUILD_KEY={os.environ['APPBUILD_KEY']}"
)
sslcontext = ssl.create_default_context(cafile=certifi.where())
response = urllib.request.urlopen(request, context=sslcontext)
version = response.read().decode()

profile = json.loads(open(os.path.join(os.path.dirname(__file__), "buildProfile.json")).read())

baseFolder = "wxPython"
destinationFolder = "build"

executables = [
    Executable(
        os.path.join(baseFolder, "app.py"),
        base=os.getenv("BUILDBASE"),
        copyright="Copyright 2018 by Yanone",
        targetName="TypeWorld.exe",
        icon=os.path.join(baseFolder, "icon", "tw.ico"),
    ),
    Executable(
        os.path.join(baseFolder, "agent.py"),
        base=os.getenv("BUILDBASE"),
        copyright="Copyright 2018 by Yanone",
        targetName="TypeWorld Subscription Opener.exe",
        icon=os.path.join(baseFolder, "icon", "tw.ico"),
    ),
]
if "agent" in profile:
    executables.append(
        Executable(
            os.path.join(baseFolder, "daemon.py"),
            base=os.getenv("BUILDBASE"),
            copyright="Copyright 2018 by Yanone",
            targetName="TypeWorld Taskbar Agent.exe",
            icon=os.path.join(baseFolder, "icon", "tw.ico"),
        )
    )


setup(
    name="Type.World",
    version=version.split("-")[0],
    description="Type.World – One Click Font-Installer",
    options={
        "build_exe": {
            "include_files": [
                os.path.join(baseFolder, "htmlfiles"),
                os.path.join(baseFolder, "locales"),
                os.path.join(baseFolder, "icon"),
                os.path.join(baseFolder, "patrons"),
                os.path.join(baseFolder, "intercom"),
                os.path.join(baseFolder, "typeworldguiapp"),
            ],
            "excludes": ["win32ctypes", "tkinter", "test", "numpy", "pytz"],
            "packages": [
                "appdirs",
                "google-cloud-pubsub",
                "typeworld",
                "packaging",
                "requests",
                "idna",
                "pyasn1",
                "rsa",
                "cachetools",
                "fontTools",
                "pyasn1_modules",
                "typeworld",
                "keyring",
                "markdown2",
                # "pytz",
                "winreg",
                "win32api",
                "plyer",
                "flask",
                "pywinsparkle",
                "win32timezone",
                "pkg_resources",
                # "numpy",
            ],
            "optimize": 1,
            "build_exe": destinationFolder,
        }
    },
    executables=executables,
)
