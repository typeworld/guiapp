# -*- coding: utf-8 -*-

import re, os
import json

content = json.load(open(os.path.join(os.path.dirname(__file__), 'content.json'), 'r'))


# content = {
# 	'Add': {
# 		'de': u'Hinzufügen',
# 		},
# 	'Cancel': {
# 		'de': u'Abbrechen',
# 		},
# 	'About': {
# 		'de': u'Über',
# 		},
# 	'Preferences': {
# 		'de': u'Einstellungen',
# 		},
# 	'Foundries': {
# 		'de': u'Foundrys',
# 		},
# 	'Publisher': {
# 		'de': u'Verlag',
# 		},
# 	'Publishers': {
# 		'de': u'Verlage',
# 		},
# 	'Add Publisher': {
# 		'de': u'Verlag hinzufügen',
# 		},
# 	'Reload': {
# 		'de': u'Neu laden',
# 		},
# 	'Remove': {
# 		'de': u'Entfernen',
# 		},
# 	'Install': {
# 		'de': u'Installieren',
# 		},
# 	'Installed': {
# 		'de': u'Installiert',
# 		},
# 	'Installing': {
# 		'de': u'Installiere',
# 		},
# 	'Install All': {
# 		'de': u'Alle installieren',
# 		},
# 	'Not Installed': {
# 		'de': u'Nicht installiert',
# 		},
# 	'Remove': {
# 		'de': u'Entfernen',
# 		},
# 	'Removing': {
# 		'de': u'Entferne',
# 		},
# 	'Remove All': {
# 		'de': u'Alle entfernen',
# 		},
# 	'WelcomeMessage': {
# 		'en': u'Welcome to Type.World.<br />Click here to add a publisher.',
# 		'de': u'Willkommen bei Type.World.<br />Klicke hier, um einen Verlag hinzuzufügen.',
# 		},
# }


def makeHTML(string, html):
	if html:
		string = string.replace('\n', '<br />')
	return string

def localize(key, languages = ['en'], html = False):
	u'''\
	Return localized version of key, if found. Otherwise try English, if found.u
	'''

	string = None
	if content.has_key(key):
		for language in languages:
			if content[key].has_key(language):
				return makeHTML(content[key][language], html)
			elif content[key].has_key('en'):
				return makeHTML(content[key]['en'], html)

	return makeHTML(key, html)

def localizeString(source, languages = ['en'], html = False):
	u'''\
	Replace all occurrences of $(key) with their localized content
	'''

	def my_replace(match):
		return localize(match.group(2), languages, html)

	return re.sub(r'(\#\((.+?)\))', my_replace, source)


if __name__ == '__main__':
	print localizeString('$(Many) $(Foundries) ,,,', ['de'])
