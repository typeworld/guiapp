# -*- coding: utf-8 -*-

import os
from ynlib.web import GetHTTP
from ynlib.files import WriteToFile, ReadFromFile
import json

print('Calling server...')

url = 'https://type.world/downloadLocalization?authKey=8KW8jyBtEW3my2U'
j = GetHTTP(url)

print('Received response...')

a = json.loads(j)
locales = []
for keyword in a:
	for locale in a[keyword]:
		if not locale in locales:
			locales.append(locale)

print('Received locales:', locales)


path = os.path.join(os.path.dirname(__file__), 'localization.json')
WriteToFile(path, json.dumps(a))


languages = []
for word in a:
	for lang in a[word]:
		if not lang in languages:
			languages.append(lang)

# count = 0
# for word in a[app]:
# 	english = word
# 	if 'en' in a[app][word]:
# 		english = a[app][word]['en']
# 	count += len(english)

# print('Letter count: %s' % count)
# print('Google Translate Costs: $%s' % (20*count/10**6))



# Little Snitch Internet Access Policy
from __init__ import localizeString
strings = ReadFromFile(os.path.join(os.path.dirname(__file__), '..', 'build', 'Mac', 'InternetAccessPolicy.strings'))

folder = os.path.join(os.path.dirname(__file__), '..', 'build', 'Mac', 'Little Snitch Translations')
os.system('rm -rf "%s"' % folder)
os.makedirs(folder)

for language in languages:
	os.makedirs(os.path.join(folder, '%s.lproj' % language))
	WriteToFile(os.path.join(folder, '%s.lproj' % language, 'InternetAccessPolicy.strings'), localizeString(strings, languages = [language]))

print('Done.')