import os
import sys
import subprocess
import urllib
import urllib.request
import ssl
import certifi


def http(url, data=None):
    if data:
        data = urllib.parse.urlencode(data).encode("ascii")
    request = urllib.request.Request(url, data=data)
    sslcontext = ssl.create_default_context(cafile=certifi.where())
    response = urllib.request.urlopen(request, context=sslcontext)
    return response.read().decode()


platform = sys.argv[-1]

version = http(
    f"https://api.type.world/latestUnpublishedVersion/world.type.guiapp/{platform}/?TYPEWORLD_APIKEY={os.getenv('TYPEWORLD_APIKEY')}"
)

# Version number check
if version == "n/a":
    print("No build target version number available: n/a")
    sys.exit(1)

# Success
print("Building version", os.getenv("APP_BUILD_VERSION", "undefined"))
