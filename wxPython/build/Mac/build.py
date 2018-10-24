import os, sys

from subprocess import Popen,PIPE,STDOUT



version = open('/Users/yanone/Code/py/git/typeWorld/guiapp/currentVersion.txt', 'r').read().strip()


_list = [
['Remove old build folder', 'rm -rf /Users/yanone/Code/TypeWorldApp/build'],
['Remove old dist folder', 'rm -rf /Users/yanone/Code/TypeWorldApp/dist'],
['Python build', '/usr/local/bin/python3 /Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/build/Mac/setup.py py2app'],
['Copying Sparkle', 'cp -R /Users/yanone/Code/Sparkle-1.19.0/Sparkle.framework /Users/yanone/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/'],
['Move app to archive folder', 'cp -R /Users/yanone/Code/TypeWorldApp/dist/Type.World.app /Users/yanone/Code/TypeWorldApp/apps/Mac/Type.World.%s.app' % version],
]

for desc, cmd in _list:

	print(desc, '...')

	out = Popen(cmd, stderr=STDOUT,stdout=PIPE, shell=True)
	output, exitcode = out.communicate()[0].decode(), out.returncode

	if exitcode != 0:
		print(output)
		print()
		print(cmd)
		print()
		print('%s failed! See above.' % desc)
		sys.exit(0)

print('Done.')
print()


# rm -rf ~/Code/TypeWorldApp/build
# rm -rf ~/Code/TypeWorldApp/dist


# # Build
# python3 /Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/build/Mac/setup.py py2app

# # Copy Sparkle over
# cp -R ~/Code/Sparkle-1.19.0/Sparkle.framework ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/

# # Copy docktileplugin
# # cp -R /Users/yanone/Code/py/git/typeWorld/guiapp/appbadge/dist/appbadge.docktileplugin ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Resources/

# # Move app to archive folder
# cp -R ~/Code/TypeWorldApp/dist/Type.World.app ~/Code/TypeWorldApp/apps/Mac/Type.World.`cat /Users/yanone/Code/py/git/typeWorld/guiapp/currentVersion.txt`.app

# exit 0