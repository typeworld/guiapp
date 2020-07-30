import os
import sys

version = sys.argv[-1]

apiCode = open(
    '/Users/yanone/Code/py/git/typeworld/typeworld/Lib/typeworld/api/__init__.py', 'r').read()

if not f'VERSION = "{version}"' in apiCode:
    print(
        f'typeworld.api doesn’t hold the up-to-date version number {version}')
    sys.exit(1)
