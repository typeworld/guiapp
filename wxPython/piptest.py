import wpipe, sys

pclient = wpipe.Client('mypipe', wpipe.Mode.Master)
pclient.write(b'hello')
reply = pclient.read()

print('closed')
sys.exit(0)