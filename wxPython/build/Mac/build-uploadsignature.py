# -*- coding: utf-8 -*-

import os, sys

from ynlib.web import GetHTTP, PostHTTP
version = GetHTTP('https://api.type.world/latestUnpublishedVersion/world.type.guiapp/mac/')
if version == 'n/a':
    print('Can’t get version number')
    sys.exit(1)

from ynlib.system import Execute

def getEdDSA(file):
	path = '"%s/Code/Sparkle/bin/sign_update" "%s"' % (os.path.expanduser('~'), file)
	dsa = Execute(path).decode()
	return dsa

def getDSA(file):
	path = '"%s/Code/Sparkle/bin/old_dsa_scripts/sign_update" "%s" "%s"' % (os.path.expanduser('~'), file, os.path.expanduser('~/Code/Certificates/Type.World Sparkle/dsa_priv.pem'))
	dsa = Execute(path).decode()
	dsa = dsa.replace(' ', '').replace('\n', '')
	return f'sparkle:dsaSignature="{dsa}" length="0"'

signature = getEdDSA(f'/Users/yanone/Code/TypeWorldApp/dmg/TypeWorldApp.{version}.dmg')

response = PostHTTP('https://api.type.world/setSparkleSignature', values = {'appKey': 'world.type.guiapp', 'version': version, 'platform': 'mac', 'signature': signature}).decode()
if not response == 'ok':
	print('Uploading Sparkle signature failed:', response)
	sys.exit(1)
