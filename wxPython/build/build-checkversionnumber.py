import os
import sys
import typeworld.api

version = os.getenv("APP_BUILD_VERSION", "undefined")
assert version != "undefined"

if not version.startswith(typeworld.api.VERSION):
    print(
        f"typeworld.api doesn’t hold the up-to-date version number {typeworld.api.VERSION}"
    )
    sys.exit(1)
