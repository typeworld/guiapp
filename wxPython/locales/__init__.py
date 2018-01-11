# -*- coding: utf-8 -*-

import re


content = {
	'About': {
		'de': u'Über',
		},
	'Preferences': {
		'de': u'Einstellungen',
		},
	'Foundries': {
		'de': u'Foundrys',
		},
	'Publisher': {
		'de': u'Verlag',
		},
	'Publishers': {
		'de': u'Verlage',
		},
}

def localize(key, languages = ['en']):
	u'''\
	Return localized version of key, if found. Otherwise try English, if found.u
	'''
	if content.has_key(key):
		for language in languages:
			if content[key].has_key(language):
				return content[key][language]
			elif content[key].has_key('en'):
				return content[key]['en']
	return key

def localizeString(source, languages = ['en']):
	u'''\
	Replace all occurrences of $(key) with their localized content
	'''

	def my_replace(match):
		return localize(match.group(2), languages)

	return re.sub(r'(\%\((.+?)\))', my_replace, source)


if __name__ == '__main__':
	print localizeString('$(Many) $(Foundries) ,,,', ['de'])
