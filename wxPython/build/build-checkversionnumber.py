import sys
import typeworld.api

version = sys.argv[-1]

desiredversion = "0.2.3-beta"

if typeworld.api.VERSION != desiredversion:
    print(f"typeworld.api doesn’t hold the up-to-date version number {desiredversion}")
    sys.exit(1)
