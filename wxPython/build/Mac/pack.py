import os, sys

from subprocess import Popen,PIPE,STDOUT



version = open('/Users/yanone/Code/py/git/typeWorld/guiapp/currentVersion.txt', 'r').read().strip()

findSymlinks = 'find -L ~/Code/TypeWorldApp/dist/Type.World.app -type l'

_list = [

# Archive
['Copy app to archive', 'cp -r ~/Code/TypeWorldApp/dist/Type.World.app /Users/yanone/Code/TypeWorldApp/dmg/TypeWorldApp.%s.dmg' % version],

# DMG
#['Create dmg background image', 'tiffutil -cathidpicheck /Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/build/Mac/dmgbackground.tiff /Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/build/Mac/dmgbackground@2x.tiff -out /Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/build/Mac/dmgbackground_final.tiff'],

['Remove old dmg', 'rm ~/Code/TypeWorldApp/dmg/TypeWorldApp.%s.dmg' % version, None, [0, 1]],
['Create .dmg', '/Users/yanone/Library/Python/3.6/bin/dmgbuild -s /Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/build/Mac/dmgbuild.py "Type.World App" /Users/yanone/Code/TypeWorldApp/dmg/TypeWorldApp.%s.dmg' % version],
['Sign .dmg', 'codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dmg/TypeWorldApp.%s.dmg' % version],
['Verify .dmg', 'codesign -dv --verbose=4  ~/Code/TypeWorldApp/dmg/TypeWorldApp.%s.dmg' % version],
['Create appcast', 'python3 /Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/build/Mac/appcast.py'],
]

for l in _list:

	exitcodes = [0]

	alt = None
	if len(l) == 2:
		desc, cmd = l
	if len(l) == 3:
		desc, cmd, alt = l
	if len(l) == 4:
		desc, cmd, alt, exitcodes = l


	print(desc, '...')

	out = Popen(cmd, stderr=STDOUT,stdout=PIPE, shell=True)
	output, exitcode = out.communicate()[0].decode(), out.returncode

	if not exitcode in exitcodes:
		print ('Exit code:', exitcode)
		print(output)
		print()
		print(cmd)
		print()
		print('%s failed! See above.' % desc)
		print()
		if alt:
			print('Debugging output:')
			os.system(alt)
		sys.exit(0)

print('Done.')
print()




# # Verify
# codesign -dv --verbose=4  ~/Code/TypeWorldApp/dist/Type.World.app
# spctl --assess --verbose ~/Code/TypeWorldApp/dist/Type.World.app
# codesign --verify --deep --strict --verbose=2 ~/Code/TypeWorldApp/dist/Type.World.app

# # DMG
# rm ~/Code/TypeWorldApp/dmg/TypeWorldApp.`cat ~/Code/py/git/typeWorld/guiapp/currentVersion.txt`.dmg
# hdiutil create -size 100m -fs HFS+ -srcfolder ~/Code/TypeWorldApp/dist -volname "Type.World App" ~/Code/TypeWorldApp/dmg/TypeWorldApp.`cat ~/Code/py/git/typeWorld/guiapp/currentVersion.txt`.dmg
# codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dmg/TypeWorldApp.`cat ~/Code/py/git/typeWorld/guiapp/currentVersion.txt`.dmg

# # Sparkle
# python3 appcast.py

# exit 0