import os

keyfile = open(os.path.join(os.environ["PWD"], os.environ["CERTIFICATE"]), "r")
key = keyfile.read()
keyfile.close()
key = key.replace("\\n", "\r\n")
keyfile = open(os.path.join(os.environ["PWD"], os.environ["CERTIFICATE"]), "w")
keyfile.write(key)
keyfile.close()
