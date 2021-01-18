import sys
import typeworld.api

desiredversion = "0.2.4-beta"

if typeworld.api.VERSION != desiredversion:
    print(f"typeworld.api doesn’t hold the up-to-date version number {desiredversion}")
    sys.exit(1)
