# -*- coding: utf-8 -*-

import os, sys

version = os.getenv("APP_BUILD_VERSION", "undefined")
assert version != "undefined"


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


# def getEdDSA(file):
#     path = f'"sparkle/WinSparkle-0.7.0/bin/sign_update" "{file}"'
#     dsa = Execute(path).decode()
#     return dsa


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


def getDSA(file):
    path = f'"sparkle/WinSparkle-0.7.0/bin/sign_update" "{file}" "wxPython/build/Windows/winsparkle/dsa_priv.pem"'
    dsa, exitcode = execute(path)
    dsa = dsa.replace(" ", "").replace("\n", "")
    return f'sparkle:dsaSignature="{dsa}" length="0"'


signature = getDSA(f"dmg/TypeWorldApp.exe")

response = http(
    "https://api.type.world/setSparkleSignature",
    data={
        "appKey": "world.type.guiapp",
        "version": version,
        "platform": "windows",
        "signature": signature,
        "TYPEWORLD_APIKEY": os.getenv("TYPEWORLD_APIKEY"),
    },
)
if not response == "ok":
    print("Uploading Sparkle signature failed:", response)
    sys.exit(1)
