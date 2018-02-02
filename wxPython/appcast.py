# -*- coding: utf-8 -*-

DELTASFORVERSIONS = 5



import os, glob, time, markdown
from ynlib.files import WriteToFile
from ynlib.system import Execute

version = Execute('cat ~/Code/TypeWorldApp/build/version')

# Delete files that are older than half a year, and delete appcast.xml
print 'Deleting old builds...'
Execute('rm ~/Code/TypeWorldApp/dmg/appcast.xml')
Execute('find ~/Code/TypeWorldApp/dmg/* -type f -mtime +30 -delete')

# Create new deltas
#print 'Creating new deltas...'
#print Execute('~/Code/Sparkle/bin/generate_appcast ~/Code/dsa_priv.pem ~/Code/TypeWorldApp/dmg')


# Create deltas
os.chdir(os.path.expanduser("~/Code/TypeWorldApp/apps"))
versions = []
for file in glob.glob("*"):
	version = file.replace('Type.World.', '').replace('.app', '')
	versions.append(version)
# Sort descending
versions.sort(key=lambda s: map(int, s.split('.')), reverse=True)
for version in versions[1:DELTASFORVERSIONS+1]:
	
	deltaPath = os.path.expanduser("~/Code/TypeWorldApp/dmg/TypeWorldApp.%s-%s.delta" % (versions[0], version))
	if not os.path.exists(deltaPath):
		print 'Create delta between %s and %s' % (versions[0], version)
		Execute('~/Code/Sparkle/bin/BinaryDelta create ~/Code/TypeWorldApp/apps/Type.World.%s.app ~/Code/TypeWorldApp/apps/Type.World.%s.app %s' % (version, versions[0], deltaPath))

# Sign all files that are unsigned (don't have an equivalent .dsa in ../dsa)
print 'Signing new files...'
os.chdir(os.path.expanduser("~/Code/TypeWorldApp/dmg"))
for file in glob.glob("*"):
	if not 'appcast.xml' in file:

		# no signature
		if not os.path.exists(os.path.expanduser("~/Code/TypeWorldApp/dsa/" + file + '.dsa')):
			print 'Signing', file
			dsa = Execute('~/Code/Sparkle/bin/sign_update ~/Code/TypeWorldApp/dmg/%s ~/Code/dsa_priv.pem' % file)
			dsa = dsa.replace(' ', '').replace('\n', '')
			print dsa
			WriteToFile(os.path.expanduser("~/Code/TypeWorldApp/dsa/" + file + '.dsa'), dsa)


# Write new appcast.xml

lines = []
lines.append('<?xml version="1.0" standalone="yes"?>')
lines.append('<rss xmlns:sparkle="http://www.andymatuschak.org/xml-namespaces/sparkle" version="2.0">')
lines.append('<channel>')
lines.append('<title>Type.World</title>\n')

os.chdir(os.path.expanduser("~/Code/TypeWorldApp/dmg"))
for file in glob.glob("*"):
	if '.dmg' in file:

		path = os.path.expanduser("~/Code/TypeWorldApp/dmg/" + file)
		version = file.replace('TypeWorldApp.', '').replace('.dmg', '')
		length = str(int(os.stat(path).st_size))
		dsa = Execute('cat ~/Code/TypeWorldApp/dsa/' + file + '.dsa')

		lines.append('<item>')
		lines.append('\t<title>' + version + '</title>')

		# Release notes
		md_path = os.path.expanduser("~/Code/TypeWorldApp/changelog/" + version + '.md')
		if os.path.exists(md_path):
			notes = Execute('cat ' + md_path)
			if notes:
				lines.append('\t<description><![CDATA[' + markdown.markdown(Execute('cat ' + md_path)) + ']]></description>')

		lines.append('\t<pubDate>' + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(os.path.getctime(path))) + '</pubDate>')
		lines.append('\t<sparkle:minimumSystemVersion>10.7</sparkle:minimumSystemVersion>')
		lines.append('\t<enclosure url="https://type.world/downloadlink?ID=guiapp&amp;version=' + version + '" sparkle:version="' + version + '" sparkle:shortVersionString="' + version + '" length="' + length + '" sparkle:dsaSignature="' + dsa + '" type="application/octet-stream" />')

		# Deltas
		deltas = []
		os.chdir(os.path.expanduser("~/Code/TypeWorldApp/dmg"))
		for delta in glob.glob("*"):
			if '.delta' in delta and 'TypeWorldApp.' + version + '-' in delta:

				path = os.path.expanduser("~/Code/TypeWorldApp/dmg/" + delta)
				previousVersion = delta.replace('TypeWorldApp.' + version + '-', '').replace('.delta', '')
				length = str(int(os.stat(path).st_size))
				dsa = Execute('cat ~/Code/TypeWorldApp/dsa/' + delta + '.dsa')
				deltas.append('\t\t<enclosure url="https://type.world/downloadlink?ID=guiapp&amp;version=' + version + '&amp;deltaFrom=' + previousVersion + '" sparkle:version="' + version + '" sparkle:shortVersionString="' + version + '" sparkle:deltaFrom="' + previousVersion + '" length="' + length + '" sparkle:dsaSignature="' + dsa + '" type="application/octet-stream" />')

		if deltas:
			lines.append('\t<sparkle:deltas>')
			lines.extend(deltas)
			lines.append('\t</sparkle:deltas>')

		lines.append('</item>\n')

lines.append('</channel>')
lines.append('</rss>')


appcastPath = os.path.expanduser('~/Code/TypeWorldApp/dmg/appcast.xml')
if os.path.exists(appcastPath):
	os.remove(appcastPath)
WriteToFile(appcastPath, '\n'.join(lines))
