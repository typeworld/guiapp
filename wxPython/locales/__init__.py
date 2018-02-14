# -*- coding: utf-8 -*-

import re, os
import json
import localization
#content = json.load(open(os.path.join(os.path.dirname(__file__), 'localization.json'), 'r'))

content = json.loads(localization.localization.replace("\n", "\\n"))


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
