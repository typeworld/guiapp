# -*- coding: utf-8 -*-

import os
from ynlib.web import GetHTTP
from ynlib.files import WriteToFile, ReadFromFile
import json

#j = GetHTTP('https://type.world/downloadLocalization')
j = GetHTTP('http://127.0.0.1:8080/downloadLocalization')

a = json.loads(j)

path = os.path.join(os.path.dirname(__file__), 'locales', 'localization.json')
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
import locales
strings = ReadFromFile(os.path.join(os.path.dirname(__file__), 'build', 'Mac', 'InternetAccessPolicy.strings'))

folder = os.path.join(os.path.dirname(__file__), 'build', 'Mac', 'Little Snitch Translations')
os.system('rm -rf "%s"' % folder)
os.makedirs(folder)

for language in languages:
	os.makedirs(os.path.join(folder, '%s.lproj' % language))
	WriteToFile(os.path.join(folder, '%s.lproj' % language, 'InternetAccessPolicy.strings'), locales.localizeString(strings, languages = [language]))

print('Done.')