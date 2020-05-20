# -*- coding: utf-8 -*-

import os, sys

version = sys.argv[-1]

from ynlib.system import Execute
from ynlib.web import PostHTTP

def getEdDSA(file):
	path = '"%s/Code/Sparkle/bin/sign_update" "%s"' % (os.path.expanduser('~'), file)
	dsa = Execute(path).decode()
	return dsa

def getDSA(file):
	path = '"%s/Code/Sparkle/bin/old_dsa_scripts/sign_update" "%s" "%s"' % (os.path.expanduser('~'), file, os.path.expanduser('~/Code/Certificates/Type.World Sparkle/dsa_priv.pem'))
	dsa = Execute(path).decode()
	dsa = dsa.replace(' ', '').replace('\n', '')
	return f'sparkle:dsaSignature="{dsa}" length="0"'

signature = getDSA(f'/Users/yanone/Code/TypeWorldApp/dmg/TypeWorldApp.{version}.exe')

response = PostHTTP('https://api.type.world/setSparkleSignature', values = {'appKey': 'world.type.guiapp', 'version': version, 'platform': 'windows', 'signature': signature}).decode()
if not response == 'ok':
	print('Uploading Sparkle signature failed:', response)
	sys.exit(1)
