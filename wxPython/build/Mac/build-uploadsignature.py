# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import urllib
import urllib.request
import ssl
import certifi

version = sys.argv[-1]


def http(url, data=None):
    if data:
        data = urllib.parse.urlencode(data).encode("ascii")
    request = urllib.request.Request(url, data=data)
    sslcontext = ssl.create_default_context(cafile=certifi.where())
    response = urllib.request.urlopen(request, context=sslcontext)
    return response.read().decode()


def execute(command):
    out = subprocess.Popen(
        command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True
    )
    output, exitcode = out.communicate()[0].decode(), out.returncode
    return output, exitcode


def getEdDSA(file):
    path = f"sparkle/bin/sign_update -s {os.getenv('SPARKLE_KEY')} {file}"
    dsa, exitcode = execute(path)
    return dsa


signature = getEdDSA(f"dmg/TypeWorldApp.dmg")

response = http(
    "https://api.type.world/setSparkleSignature",
    data={
        "appKey": "world.type.guiapp",
        "version": version,
        "platform": "mac",
        "signature": signature,
        "APPBUILD_KEY": os.getenv("APPBUILD_KEY"),
    },
)
if not response == "ok":
    print("Uploading Sparkle signature failed:", response)
    sys.exit(1)
