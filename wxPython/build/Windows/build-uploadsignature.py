# -*- coding: utf-8 -*-

import os, sys

version = sys.argv[-1]


def Execute(command):
    """\
	Execute system command, return output.
	"""

    import sys, os, platform

    if sys.version.startswith("2.3") or platform.system() == "Windows":

        p = os.popen(command, "r")
        response = p.read()
        p.close()
        return response

    else:

        import subprocess

        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, shell=True, close_fds=True
        )
        os.waitpid(process.pid, 0)
        response = process.stdout.read().strip()
        process.stdout.close()
        return response


def PostHTTP(
    url, values={}, data=None, authentication=None, contentType=None, files=[]
):
    """\
	POST HTTP responses from the net. Values are dictionary {argument: value}
	Authentication as "username:password".
	Files as list of paths.
	"""

    import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, base64

    if data:
        data = urllib.parse.urlencode(data).encode("ascii")
    elif values:
        data = urllib.parse.urlencode(values).encode("ascii")

    headers = {}

    if contentType:
        headers["Content-Type"] = contentType
        headers["Accept"] = contentType

    if authentication and type(authentication) == str:
        base64string = base64.encodestring(authentication.encode())
        headers["Authorization"] = "Basic %s" % base64string

    elif authentication and type(authentication) in (tuple, list):
        base64string = base64.encodestring(
            b"%s:%s" % (authentication[0].encode(), authentication[1].encode())
        )
        headers["Authorization"] = "Basic %s" % base64string

    request = urllib.request.Request(url, data=data, headers=headers)
    response = urllib.request.urlopen(request, cafile=certifi.where())
    return response.read()


def getEdDSA(file):
    path = '"%s/Code/Sparkle/bin/sign_update" "%s"' % (os.path.expanduser("~"), file)
    dsa = Execute(path).decode()
    return dsa


def getDSA(file):
    path = '"%s/Code/Sparkle/bin/old_dsa_scripts/sign_update" "%s" "%s"' % (
        os.path.expanduser("~"),
        file,
        os.path.expanduser("~/Code/Certificates/Type.World Sparkle/dsa_priv.pem"),
    )
    dsa = Execute(path).decode()
    dsa = dsa.replace(" ", "").replace("\n", "")
    return f'sparkle:dsaSignature="{dsa}" length="0"'


signature = getDSA(f"/Users/yanone/Code/TypeWorldApp/dmg/TypeWorldApp.{version}.exe")

response = PostHTTP(
    "https://api.type.world/setSparkleSignature",
    values={
        "appKey": "world.type.guiapp",
        "version": version,
        "platform": "windows",
        "signature": signature,
    },
).decode()
if not response == "ok":
    print("Uploading Sparkle signature failed:", response)
    sys.exit(1)
