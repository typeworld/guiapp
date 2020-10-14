import os
import sys
import base64

file = sys.argv[-1]

keyfile = open(os.path.join(os.environ["PWD"], file), "rb")
key = keyfile.read()
keyfile.close()
key = base64.b32encode(key)
keyfile = open(os.path.join(os.environ["PWD"], file), "wb")
keyfile.write(key)
keyfile.close()
