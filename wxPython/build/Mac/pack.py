import os, sys

from subprocess import Popen,PIPE,STDOUT



version = open('/Users/yanone/Code/py/git/typeWorld/guiapp/currentVersion.txt', 'r').read().strip()

findSymlinks = 'find -L ~/Code/TypeWorldApp/dist/Type.World.app -type l'

_list = [
['Unlink site.pyo', 'unlink ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Resources/lib/python3.6/site.pyo'],

['Signing inner components', 'codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/libwx_baseu-3.0.0.4.0.dylib'],
['Signing inner components', 'codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/libwx_osx_cocoau_core-3.0.0.4.0.dylib'],
['Signing inner components', 'codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/libwx_osx_cocoau_webview-3.0.0.4.0.dylib'],
['Signing inner components', 'codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/libwx_baseu_net-3.0.0.4.0.dylib'],
['Signing inner components', 'codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/Python.framework/Versions/3.6'],
['Signing inner components', 'codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/Sparkle.framework/Versions/A'],
['Signing inner components', 'codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app/Contents/MacOS/python'],

['Signing app', 'codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app'],

['Verify signature', 'codesign -dv --verbose=4  ~/Code/TypeWorldApp/dist/Type.World.app'],
['Verify signature', 'codesign --verify --deep --strict --verbose=20 ~/Code/TypeWorldApp/dist/Type.World.app', findSymlinks],
['Verify signature', 'spctl -a -t exec -vvvv ~/Code/TypeWorldApp/dist/Type.World.app', findSymlinks],

['Remove old dmg', 'rm ~/Code/TypeWorldApp/dmg/TypeWorldApp.%s.dmg' % version],
['Create .dmg', 'hdiutil create -size 100m -fs HFS+ -srcfolder ~/Code/TypeWorldApp/dist -volname "Type.World App" ~/Code/TypeWorldApp/dmg/TypeWorldApp.%s.dmg' % version],
['Sign .dmg', 'codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dmg/TypeWorldApp.%s.dmg' % version],
['Verify .dmg', 'codesign -dv --verbose=4  ~/Code/TypeWorldApp/dmg/TypeWorldApp.%s.dmg' % version],
['Create appcast', 'python3 /Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/build/Mac/appcast.py'],
]

for l in _list:

	alt = None
	if len(l) == 2:
		desc, cmd = l
	if len(l) == 3:
		desc, cmd, alt = l


	print(desc, '...')

	out = Popen(cmd, stderr=STDOUT,stdout=PIPE, shell=True)
	output, exitcode = out.communicate()[0].decode(), out.returncode

	if exitcode != 0:
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