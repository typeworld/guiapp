import os
import sys

file = sys.argv[-1]

keyfile = open(os.path.join(os.environ["PWD"], file), "r")
key = keyfile.read()
keyfile.close()
key = key.replace("\\n", "\r\n")
keyfile = open(os.path.join(os.environ["PWD"], file), "w")
keyfile.write(key)
keyfile.close()
