# -*- coding: utf-8 -*-

import os
from ynlib.web import GetHTTP
from ynlib.files import WriteToFile, ReadFromFile
from ynlib.system import Execute
import json
import patreon
import urllib

secrets = json.loads(ReadFromFile('/Users/yanone/Code/TypeWorldApp/misc/Patreon/api_secrets.json'))

patrons = []

url = "https://www.patreon.com/api/oauth2/api/campaigns/%s/pledges?include=patron.null" % secrets['campaign_id']

import urllib.request, urllib.error, urllib.parse, base64, certifi
request = urllib.request.Request(url)
request.add_header("Authorization", "Bearer %s" % secrets['creator_access_token'])   
result = urllib.request.urlopen(request, cafile=certifi.where())
if result.getcode() == 200:

	content = json.loads(result.read().decode())

	for d in content['data']:
		link = d['relationships']['patron']['links']['related']
		user = json.loads(GetHTTP(link).decode())
		name = user['data']['attributes']['full_name']
		patrons.append(name)
		print('Added %s' % name)

path = os.path.join(os.path.dirname(__file__), 'patrons', 'patrons.json')
WriteToFile(path, json.dumps(patrons))

print('Done...')
