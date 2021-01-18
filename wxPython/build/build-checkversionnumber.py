import os
import sys
import typeworld.api

version = os.getenv("APP_BUILD_VERSION", "undefined")
assert version != "undefined"

if typeworld.api.VERSION != version:
    print(f"typeworld.api doesn’t hold the up-to-date version number {version}")
    sys.exit(1)
