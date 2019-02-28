# -*- coding: utf-8 -*-

import os
from ynlib.web import GetHTTP
from ynlib.files import WriteToFile, ReadFromFile
from ynlib.system import Execute
import json
import patreon
import urllib

# secrets = json.loads(ReadFromFile('/Users/yanone/Code/TypeWorldApp/misc/Patreon/api_secrets.json'))

patrons = []

# url = "https://www.patreon.com/api/oauth2/api/campaigns/%s/pledges?include=patron.null" % secrets['campaign_id']

# import urllib.request, urllib.error, urllib.parse, base64, certifi
# request = urllib.request.Request(url)
# request.add_header("Authorization", "Bearer %s" % secrets['creator_access_token'])   
# result = urllib.request.urlopen(request, cafile=certifi.where())
# if result.getcode() == 200:

# 	content = json.loads(result.read().decode())

# 	for d in content['data']:
# 		link = d['relationships']['patron']['links']['related']
# 		user = json.loads(GetHTTP(link).decode())
# 		name = user['data']['attributes']['full_name']
# 		patrons.append(name)
# 		print('Added %s' % name)


import glob
files = sorted(glob.glob("/Users/yanone/Code/TypeWorldApp/Patreon/*.csv"))

import csv

with open(files[0], "rt", encoding='utf-8') as csvfile:
	spamreader = csv.reader(csvfile)
	for row in list(spamreader)[1:]:
		# print(', '.join(row))
	# 	patrons.append(row[0])
		if 'Active' in row[3]:
			patrons.append(row[0])
			print(row[0])

path = os.path.join(os.path.dirname(__file__), 'patrons', 'patrons.json')
WriteToFile(path, json.dumps(patrons))

print('Done...')
