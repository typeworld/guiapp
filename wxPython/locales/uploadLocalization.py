# -*- coding: utf-8 -*-

## This file parses all localized keywords from a bunch of relevant files and 

import os, re, keyring, urllib, urllib.request, certifi, ssl, json
sslcontext = ssl.create_default_context(cafile=certifi.where())
MOTHERSHIP = 'https://typeworld2.appspot.com'
#MOTHERSHIP = 'http://127.0.0.1:8080'

keywords = []

for path in (
		'../htmlfiles/main/index.html',
		'../app.py',
		'additional translations.txt',
		'/Users/yanone/Code/py/git/typeworld/typeworld/Lib/typeWorld/client/__init__.py',
		'/Users/yanone/Code/py/git/typeworld/typeworld/Lib/typeWorld/test.py',
		'/Users/yanone/Code/py/git/typeworld/guiapp/wxPython/build/Mac/InternetAccessPolicy.strings',
	):
	
	if not path.startswith('/'):
		path = os.path.join(os.path.dirname(__file__), path)

	content = []
	f = open(path, "r")
	for line in f.readlines():
		line = line.strip()
		if not (line.startswith('#') and not line.startswith('#(')):
			content.append(line)
		# else:
		# 	print(line)
	f.close()

	content = '\n'.join(content)

	for keyword in re.findall(r'#\((.+?)\)', content):
		if not keyword in keywords \
			and not '%s' in keyword \
			and not "'" in keyword \
			and not ('response.' in keyword and ' ' in keyword) \
			:
			keywords.append(keyword)

			if ',' in keyword:
				print('ALARM ALARM ALARM ALARM: Comma in %s' % keyword)



if not 'TRAVIS' in os.environ: authKey = keyring.get_password(MOTHERSHIP, 'revokeAppInstance')
else: authKey = os.environ['REVOKEAPPINSTANCEAUTHKEY']

# Announce subscription update
url = MOTHERSHIP + '/uploadTranslationKeywords'
parameters = {"authorizationKey": authKey,
			"keywords": ','.join(keywords),
			"inline": 'true',
			}
data = urllib.parse.urlencode(parameters).encode('ascii')
response = urllib.request.urlopen(url, data, context=sslcontext)
print(response.read().decode())
