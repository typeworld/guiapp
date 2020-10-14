import sys
import os
import json
from cx_Freeze import setup, Executable

from ynlib.web import GetHTTP

version = GetHTTP(
    (
        f"https://api.type.world/latestUnpublishedVersion/world.type.guiapp/windows/"
        f"?TYPEWORLD_APIKEY={os.getenv('TYPEWORLD_APIKEY')}"
    )
)
if version == "n/a":
    print("Can’t get version number")
    sys.exit(1)

profile = json.loads(
    open(os.path.join(os.path.dirname(__file__), "buildProfile.json")).read()
)

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None

if sys.platform == "win32":
    base = "Win32GUI"

baseFolder = "wxPython"
destinationFolder = "build"

executables = [
    Executable(
        os.path.join(baseFolder, "app.py"),
        base=base,
        copyright="Copyright 2018 by Yanone",
        targetName="TypeWorld.exe",
        icon=os.path.join(baseFolder, "icon", "tw.ico"),
    ),
    Executable(
        os.path.join(baseFolder, "agent.py"),
        base=base,
        copyright="Copyright 2018 by Yanone",
        targetName="TypeWorld Subscription Opener.exe",
        icon=os.path.join(baseFolder, "icon", "tw.ico"),
    ),
]
if "agent" in profile:
    executables.append(
        Executable(
            os.path.join(baseFolder, "daemon.py"),
            base=base,
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
            ],
            "excludes": ["win32ctypes"],
            # 'google-api-core', 'google-cloud-pubsub'
            "packages": [
                "typeworld",
                "packaging",
                "grpc",
                "requests",
                "idna",
                "pyasn1",
                "rsa",
                "cachetools",
                "grpc",
                "cryptography",
                "pyasn1_modules",
                "typeworld",
                "keyring",
                "markdown2",
                "pytz",
                "winreg",
                "zroya",
            ],
            "optimize": 2,
            "build_exe": destinationFolder,
        }
    },
    executables=executables,
)
