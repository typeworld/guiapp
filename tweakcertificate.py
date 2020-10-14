import os

keyfile = open(os.path.join(os.environ["PWD"], os.environ["CERTIFICATE_CRT"]), "r")
key = keyfile.read()
keyfile.close()
key = key.replace("\\\\n", "\\r\\n")
keyfile = open(os.path.join(os.environ["PWD"], os.environ["CERTIFICATE_CRT"]), "w")
keyfile.write(key)
keyfile.close()
