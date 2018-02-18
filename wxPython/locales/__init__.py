# -*- coding: utf-8 -*-

import re, os
import json
import localization
#content = json.load(open(os.path.join(os.path.dirname(__file__), 'localization.json'), 'r'))

content = json.loads(localization.localization.replace("\n", "\\n"))
locales = (('ab', 'Abkhazian'), ('aa', 'Afar'), ('af', 'Afrikaans'), ('ak', 'Akan'), ('sq', 'Albanian'), ('am', 'Amharic'), ('ar', 'Arabic'), ('an', 'Aragonese'), ('hy', 'Armenian'), ('as', 'Assamese'), ('av', 'Avaric'), ('ae', 'Avestan'), ('ay', 'Aymara'), ('az', 'Azerbaijani'), ('bm', 'Bambara'), ('ba', 'Bashkir'), ('eu', 'Basque'), ('be', 'Belarusian'), ('bn', 'Bengali'), ('bh', 'Bihari languages'), ('bi', 'Bislama'), ('bs', 'Bosnian'), ('br', 'Breton'), ('bg', 'Bulgarian'), ('my', 'Burmese'), ('ca', 'Catalan, Valencian'), ('ch', 'Chamorro'), ('ce', 'Chechen'), ('ny', 'Chichewa, Chewa, Nyanja'), ('zh', 'Chinese'), ('cv', 'Chuvash'), ('kw', 'Cornish'), ('co', 'Corsican'), ('cr', 'Cree'), ('hr', 'Croatian'), ('cs', 'Czech'), ('da', 'Danish'), ('dv', 'Divehi, Dhivehi, Maldivian'), ('nl', 'Dutch, Flemish'), ('dz', 'Dzongkha'), ('en', 'English'), ('eo', 'Esperanto'), ('et', 'Estonian'), ('ee', 'Ewe'), ('fo', 'Faroese'), ('fj', 'Fijian'), ('fi', 'Finnish'), ('fr', 'French'), ('ff', 'Fulah'), ('gl', 'Galician'), ('ka', 'Georgian'), ('de', 'German'), ('el', 'Greek (modern)'), ('gn', 'Guaraní'), ('gu', 'Gujarati'), ('ht', 'Haitian, Haitian Creole'), ('ha', 'Hausa'), ('he', 'Hebrew (modern)'), ('hz', 'Herero'), ('hi', 'Hindi'), ('ho', 'Hiri Motu'), ('hu', 'Hungarian'), ('ia', 'Interlingua'), ('id', 'Indonesian'), ('ie', 'Interlingue'), ('ga', 'Irish'), ('ig', 'Igbo'), ('ik', 'Inupiaq'), ('io', 'Ido'), ('is', 'Icelandic'), ('it', 'Italian'), ('iu', 'Inuktitut'), ('ja', 'Japanese'), ('jv', 'Javanese'), ('kl', 'Kalaallisut, Greenlandic'), ('kn', 'Kannada'), ('kr', 'Kanuri'), ('ks', 'Kashmiri'), ('kk', 'Kazakh'), ('km', 'Central Khmer'), ('ki', 'Kikuyu, Gikuyu'), ('rw', 'Kinyarwanda'), ('ky', 'Kirghiz, Kyrgyz'), ('kv', 'Komi'), ('kg', 'Kongo'), ('ko', 'Korean'), ('ku', 'Kurdish'), ('kj', 'Kuanyama, Kwanyama'), ('la', 'Latin'), ('lb', 'Luxembourgish, Letzeburgesch'), ('lg', 'Ganda'), ('li', 'Limburgan, Limburger, Limburgish'), ('ln', 'Lingala'), ('lo', 'Lao'), ('lt', 'Lithuanian'), ('lu', 'Luba-Katanga'), ('lv', 'Latvian'), ('gv', 'Manx'), ('mk', 'Macedonian'), ('mg', 'Malagasy'), ('ms', 'Malay'), ('ml', 'Malayalam'), ('mt', 'Maltese'), ('mi', 'Maori'), ('mr', 'Marathi'), ('mh', 'Marshallese'), ('mn', 'Mongolian'), ('na', 'Nauru'), ('nv', 'Navajo, Navaho'), ('nd', 'North Ndebele'), ('ne', 'Nepali'), ('ng', 'Ndonga'), ('nb', 'Norwegian Bokmål'), ('nn', 'Norwegian Nynorsk'), ('no', 'Norwegian'), ('ii', 'Sichuan Yi, Nuosu'), ('nr', 'South Ndebele'), ('oc', 'Occitan'), ('oj', 'Ojibwa'), ('cu', 'Church Slavic, Church Slavonic, Old Church Slavonic, Old Slavonic, Old Bulgarian'), ('om', 'Oromo'), ('or', 'Oriya'), ('os', 'Ossetian, Ossetic'), ('pa', 'Panjabi, Punjabi'), ('pi', 'Pali'), ('fa', 'Persian'), ('pl', 'Polish'), ('ps', 'Pashto, Pushto'), ('pt', 'Portuguese'), ('qu', 'Quechua'), ('rm', 'Romansh'), ('rn', 'Rundi'), ('ro', 'Romanian, Moldavian, Moldovan'), ('ru', 'Russian'), ('sa', 'Sanskrit'), ('sc', 'Sardinian'), ('sd', 'Sindhi'), ('se', 'Northern Sami'), ('sm', 'Samoan'), ('sg', 'Sango'), ('sr', 'Serbian'), ('gd', 'Gaelic, Scottish Gaelic'), ('sn', 'Shona'), ('si', 'Sinhala, Sinhalese'), ('sk', 'Slovak'), ('sl', 'Slovenian'), ('so', 'Somali'), ('st', 'Southern Sotho'), ('es', 'Spanish, Castilian'), ('su', 'Sundanese'), ('sw', 'Swahili'), ('ss', 'Swati'), ('sv', 'Swedish'), ('ta', 'Tamil'), ('te', 'Telugu'), ('tg', 'Tajik'), ('th', 'Thai'), ('ti', 'Tigrinya'), ('bo', 'Tibetan'), ('tk', 'Turkmen'), ('tl', 'Tagalog'), ('tn', 'Tswana'), ('to', 'Tonga (Tonga Islands)'), ('tr', 'Turkish'), ('ts', 'Tsonga'), ('tt', 'Tatar'), ('tw', 'Twi'), ('ty', 'Tahitian'), ('ug', 'Uighur, Uyghur'), ('uk', 'Ukrainian'), ('ur', 'Urdu'), ('uz', 'Uzbek'), ('ve', 'Venda'), ('vi', 'Vietnamese'), ('vo', 'Volapük'), ('wa', 'Walloon'), ('cy', 'Welsh'), ('wo', 'Wolof'), ('fy', 'Western Frisian'), ('xh', 'Xhosa'), ('yi', 'Yiddish'), ('yo', 'Yoruba'), ('za', 'Zhuang, Chuang'), ('zu', 'Zulu'))


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
	print localizeString('#(Many) #(Foundries) ,,,', ['de'])
	print localize('Add', ['de'])
