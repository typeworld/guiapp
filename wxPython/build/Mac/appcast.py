# -*- coding: utf-8 -*-

DELTASFORVERSIONS = 5



import os, glob, time, markdown
from ynlib.files import WriteToFile, ReadFromFile
from ynlib.system import Execute

version = Execute('cat /Users/yanone/Code/py/git/typeWorld/guiapp/currentVersion.txt')
dmgFolder = os.path.expanduser('~/Code/TypeWorldApp/dmg')
dsaFolder = os.path.expanduser('~/Code/TypeWorldApp/dsa')


def getDSA(file):
	path = '~/Code/Sparkle/bin/sign_update %s ~/Code/dsa_priv.pem' % file
	dsa = Execute(path).decode()
	dsa = dsa.replace(' ', '').replace('\n', '')
	print(path)
	return dsa


for OS in ('windows', 'mac'):

	if OS == 'windows':
		appcastFilename = 'appcast_windows.xml'
	if OS == 'mac':
		appcastFilename = 'appcast.xml'


	# Delete files that are older than half a year, and delete appcast.xml
	print('Deleting old builds...')
	if os.path.exists(os.path.join(dmgFolder, appcastFilename)):
		os.remove(os.path.join(dmgFolder, appcastFilename))
	Execute('find ~/Code/TypeWorldApp/dmg/* -type f -mtime +30 -delete')

	if False:
#	if OS == 'mac':
		# Create deltas
		os.chdir(os.path.expanduser("~/Code/TypeWorldApp/apps/Mac"))
		versions = []
		for file in glob.glob("*"):
			version = file.replace('Type.World.', '').replace('.app', '')
			versions.append(version)
		# Sort descending
		versions.sort(key=lambda s: list(map(int, s.split('.'))), reverse=True)
		for version in versions[1:DELTASFORVERSIONS+1]:
			
			deltaPath = os.path.expanduser("~/Code/TypeWorldApp/dmg/TypeWorldApp.%s-%s.delta" % (versions[0], version))
			if not os.path.exists(deltaPath):
				print('Create delta between %s and %s' % (versions[0], version))
				Execute('~/Code/Sparkle/bin/BinaryDelta create ~/Code/TypeWorldApp/apps/Type.World.%s.app ~/Code/TypeWorldApp/apps/Type.World.%s.app %s' % (version, versions[0], deltaPath))


	# Write new appcast.xml

	lines = []
	lines.append('<?xml version="1.0" standalone="yes"?>')
	lines.append('<rss xmlns:sparkle="http://www.andymatuschak.org/xml-namespaces/sparkle" version="2.0">')
	lines.append('<channel>')
	lines.append('<title>Type.World</title>\n')

	os.chdir(os.path.expanduser("~/Code/TypeWorldApp/dmg"))
	for file in reversed(sorted(glob.glob("*"))):

		if OS == 'mac' and '.dmg' in file or OS == 'windows' and '.exe' in file:

			if OS == 'windows':
				ending = '.exe'
			if OS == 'mac':
				ending = '.dmg'


			path = os.path.expanduser("~/Code/TypeWorldApp/dmg/" + file)
			version = file.replace('TypeWorldApp.', '').replace(ending, '')
			length = str(int(os.stat(path).st_size))
			dsa = getDSA(os.path.join(dmgFolder, file))

			lines.append('<item>')
			lines.append('\t<title>' + version + '</title>')

			# Release notes
			md_path = os.path.expanduser("~/Code/TypeWorldApp/changelog/" + version + '.md')
			if os.path.exists(md_path):
				notes = ReadFromFile(md_path)
				if notes:
					notes += '\n\nPrevious release notes at [https://type.world/app/](https://type.world/app/)'
					lines.append('\t<description><![CDATA[' + markdown.markdown(notes) + ']]></description>')

			lines.append('\t<pubDate>' + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(os.path.getmtime(path))) + '</pubDate>')
			
			if OS == 'mac':
				lines.append('\t<sparkle:minimumSystemVersion>10.7</sparkle:minimumSystemVersion>')

			if OS == 'windows':
				sparkleOS = ' sparkle:installerArguments="/SILENT /SP- /NOICONS /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS" sparkle:os="windows" '
			else:
				sparkleOS = ''

			lines.append('\t<enclosure url="https://type.world/downloadlink?ID=guiapp&amp;platform=' + OS + '&amp;version=' + version + '" ' + sparkleOS + 'sparkle:version="' + version + '" sparkle:shortVersionString="' + version + '" length="' + length + '" sparkle:dsaSignature="' + dsa + '" type="application/octet-stream" />')

			if OS == 'mac':
				# Deltas
				deltas = []
				os.chdir(os.path.expanduser("~/Code/TypeWorldApp/dmg"))
				for delta in glob.glob("*"):
					if '.delta' in delta and 'TypeWorldApp.' + version + '-' in delta:

						path = os.path.expanduser("~/Code/TypeWorldApp/dmg/" + delta)
						previousVersion = delta.replace('TypeWorldApp.' + version + '-', '').replace('.delta', '')
						length = str(int(os.stat(path).st_size))
						dsa = getDSA(os.path.join(dmgFolder, delta))
						deltas.append('\t\t<enclosure url="https://type.world/downloadlink?ID=guiapp&amp;platform=' + OS + '&amp;version=' + version + '&amp;deltaFrom=' + previousVersion + '" sparkle:version="' + version + '" sparkle:shortVersionString="' + version + '" sparkle:deltaFrom="' + previousVersion + '" length="' + length + '" sparkle:dsaSignature="' + dsa + '" type="application/octet-stream" />')

				if deltas:
					lines.append('\t<sparkle:deltas>')
					lines.extend(deltas)
					lines.append('\t</sparkle:deltas>')

			lines.append('</item>\n')

	lines.append('</channel>')
	lines.append('</rss>')



	appcastPath = os.path.join(dmgFolder, appcastFilename)

	f = open(appcastPath, 'w')
	f.write('\n'.join(lines))
	f.close()
