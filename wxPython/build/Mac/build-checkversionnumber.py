import os
import sys

version = sys.argv[-1]

import typeworld.api

if typeworld.api.VERSION != version:
    print(
        f"typeworld.api doesn't hold the up-to-date version number {version}")
    sys.exit(1)
