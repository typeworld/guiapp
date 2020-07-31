import os, sys
from subprocess import Popen,PIPE,STDOUT

# List of commands as tuples of:
# - Description
# - Actual command
# - True if this command is essential to the build process (must exit with 0), otherwise False

version = sys.argv[-1]

sparkle = 'sparkle/Sparkle.framework'

profile = ['normal', 'sign'] # normal/sign/agent

def executeCommands(commands, returnOutput = False):
	for description, command, mustSucceed in commands:

		# Print which step we’re currently in
		print(description, '...')

		# Execute the command, fetch both its output as well as its exit code
		out = Popen(command, stderr=STDOUT,stdout=PIPE, shell=True)
		output, exitcode = out.communicate()[0].decode(), out.returncode

		# If the exit code is not zero and this step is marked as necessary to succeed, print the output and quit the script.
		if exitcode != 0 and mustSucceed:
			print(output)
			print()
			print(command)
			print()
			print('Step "%s" failed! See above.' % description)
			print('Command used: %s' % command)
			print()
			sys.exit(666)

def signApp(path, bundleType = 'app'):

	# Delete symlinks
	symlinks = Execute('find -L "%s" -type l' % path).decode().split('\n')
	# print(symlinks)
	for filepath in symlinks:
		if filepath:
			os.remove(filepath)
			print('Deleted symlink %s' % filepath)

	import mimetypes

	for dirpath, dirnames, filenames in os.walk(path):
		for filename in filenames:
			filepath = os.path.join(dirpath, filename)

			# if 'docktileplugin' in filepath:
			# 	print('... ', filepath)

			if mimetypes.guess_type(filepath)[0] == 'application/octet-stream' \
					or filename == 'python' \
					or filename.endswith('.dylib') \
					:
					# or filename == 'plugin' \

				command = ('Signing %s' % filename, 'codesign --options runtime -s "Jan Gerner" -f "%s"' % filepath, True)
				executeCommands([command])

		if dirpath.endswith('.framework'):
			command = ('Signing %s' % dirpath, 'codesign --options runtime -s "Jan Gerner" -f "%s"' % dirpath, True)
			executeCommands([command])

	commands = (
		('Signing Outer App', 'codesign --options runtime --deep -s "Jan Gerner" --entitlements "wxPython/build/Mac/entitlements.plist" -f "%s"' % path, bundleType in ['app', 'plugin']),
		('Verify signature', 'codesign -dv --verbose=4 "%s"' % path, bundleType in ['app', 'plugin']),
		('Verify signature', 'codesign --verify --deep --strict --verbose=20 "%s"' % path, bundleType in ['app', 'plugin']),
		('Verify signature', 'spctl -a -t exec -vvvv "%s"' % path, bundleType in ['app'])
		)
	executeCommands(commands)

if 'agent' in profile:
	executeCommands((
		('Agent build', 'python wxPython/build/Mac/setup_daemon.py py2app', True),
	))

	if 'sign' in profile:
		signApp('dist/Type.World Agent.app')

	executeCommands((
		('Zipping agent', 'tar -cjf dist/agent.tar.bz2 -C "dist/" "Type.World Agent.app"', True),
	))

executeCommands((
	('Main App build', 'python wxPython/build/Mac/setup.py py2app', True),
	('Copying Sparkle', 'cp -R sparkle/Sparkle.framework dist/Type.World.app/Contents/Frameworks/', True),
))

os.remove('dist/Type.World.app/Contents/Frameworks/liblzma.5.dylib')

if 'sign' in profile:
	signApp('dist/Type.World.app/Contents/Frameworks/Sparkle.framework/Versions/A/Resources/Autoupdate.app')

if 'agent' in profile:
	executeCommands((
		('Copying agent', 'cp dist/agent.tar.bz2 dist/Type.World.app/Contents/Resources/', True),
	))

executeCommands((
	('Copying google', 'cp -R /usr/local/lib/python3.7/site-packages/google dist/Type.World.app/Contents/Resources/lib/python3.7', True),
	('Copying google-api-core', 'cp -R /usr/local/lib/python3.7/site-packages/google_api_core-1.16.0-py3.8-nspkg.pth dist/Type.World.app/Contents/Resources/lib/python3.7', True),
	('Copying google-api-core', 'cp -R /usr/local/lib/python3.7/site-packages/google_api_core-1.16.0.dist-info dist/Type.World.app/Contents/Resources/lib/python3.7', True),
	('Copying google-cloud-pubsub', 'cp -R /usr/local/lib/python3.7/site-packages/google_cloud_pubsub-1.2.0-py3.8-nspkg.pth dist/Type.World.app/Contents/Resources/lib/python3.7', True),
	('Copying google-cloud-pubsub', 'cp -R /usr/local/lib/python3.7/site-packages/google_cloud_pubsub-1.2.0.dist-info dist/Type.World.app/Contents/Resources/lib/python3.7', True),

	('Copying Google Cloud Authentication key', 'cp -R /Users/yanone/Code/py/git/typeworld/typeworld/Lib/typeworld/client/typeworld2-cfd080814f09.json dist/Type.World.app/Contents/Resources', True),
))

if 'normal' in profile:


	# CTYPES error
	# https://github.com/powerline/powerline/issues/1947
	path = 'dist/Type.World.app/Contents/Resources/lib/python3.7/ctypes/__init__.py'
	code = open(path).read()
	code = code.replace('CFUNCTYPE(c_int)(lambda: None)', '#CFUNCTYPE(c_int)(lambda: None)')
	f = open(path, 'w')
	f.write(code)
	f.close()


	executeCommands((
		('Extract compressed Python', 'ditto -x -k dist/Type.World.app/Contents/Resources/lib/python37.zip /Users/yanone/Desktop/zip', True),
	))

	if 'sign' in profile:
		signApp('/Users/yanone/Desktop/zip', bundleType = 'zip')

	executeCommands((
		('Re-compress Python', 'ditto -c -k --sequesterRsrc --keepParent /Users/yanone/Desktop/zip dist/Type.World.app/Contents/Resources/lib/python37.zip', True),
		('Delete zip folder', 'rm -r /Users/yanone/Desktop/zip', True),
	))

	executeCommands((
		('Remove ynlib.pdf', 'rm -rf "dist/Type.World.app/Contents/Resources/lib/python3.7/ynlib/pdf"', True),
	))

	if 'sign' in profile:
		signApp('dist/Type.World.app')

	executeCommands((
		('Self Test', 'dist/Type.World.app/Contents/MacOS/Type.World selftest', True),
	))


if not 'sign' in profile:
	print(f'WARNING: Apps aren’t signed (profile: {profile})')

print('Finished successfully.')
print()




# # Main app
# ['Main App build', 'python wxPython/build/Mac/setup.py py2app', None, ''],
# ['Copying Sparkle', 'cp -R %s dist/Type.World.app/Contents/Frameworks/' % sparkle],
# ['Copying Docktileplugin', 'cp -R appbadge/AppBadge.docktileplugin dist/Type.World.app/Contents/Resources/'],
# ['Copying agent', 'cp dist/agent.tar.bz2 dist/Type.World.app/Contents/Resources/', None, ''],
# ['Unlink site.pyo', 'unlink ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Resources/lib/python3.7/site.pyo', None, ''],

# ['Copying google-api-core', 'cp -R /usr/local/lib/python3.7/site-packages/google_api_core-1.16.0-py3.8-nspkg.pth dist/Type.World.app/Contents/Resources/lib/python3.7', None, ''],
# ['Copying google-api-core', 'cp -R /usr/local/lib/python3.7/site-packages/google_api_core-1.16.0.dist-info dist/Type.World.app/Contents/Resources/lib/python3.7', None, ''],
# ['Copying google-cloud-pubsub', 'cp -R /usr/local/lib/python3.7/site-packages/google_cloud_pubsub-1.2.0-py3.8-nspkg.pth dist/Type.World.app/Contents/Resources/lib/python3.7', None, ''],
# ['Copying google-cloud-pubsub', 'cp -R /usr/local/lib/python3.7/site-packages/google_cloud_pubsub-1.2.0.dist-info dist/Type.World.app/Contents/Resources/lib/python3.7', None, ''],

# ['Copying Google Cloud Authentication key', 'cp -R /Users/yanone/Code/py/git/typeworld/typeworld/Lib/typeworld/client/typeworld2-cfd080814f09.json dist/Type.World.app/Contents/Resources', None, ''],


# ['Signing inner components', 'codesign --options runtime -s "Jan Gerner" -f dist/Type.World.app/Contents/Frameworks/libwx_baseu-3.0.0.4.0.dylib', None, 'nosign'],
# ['Signing inner components', 'codesign --options runtime -s "Jan Gerner" -f dist/Type.World.app/Contents/Frameworks/libwx_osx_cocoau_core-3.0.0.4.0.dylib', None, 'nosign'],
# ['Signing inner components', 'codesign --options runtime -s "Jan Gerner" -f dist/Type.World.app/Contents/Frameworks/libwx_osx_cocoau_webview-3.0.0.4.0.dylib', None, 'nosign'],
# ['Signing inner components', 'codesign --options runtime -s "Jan Gerner" -f dist/Type.World.app/Contents/Frameworks/libwx_baseu_net-3.0.0.4.0.dylib', None, 'nosign'],
# ['Signing inner components', 'codesign --options runtime -s "Jan Gerner" -f dist/Type.World.app/Contents/Frameworks/libcrypto.1.1.dylib', None, 'nosign'],
# ['Signing inner components', 'codesign --options runtime -s "Jan Gerner" -f dist/Type.World.app/Contents/Frameworks/libgdbm.6.dylib', None, 'nosign'],
# ['Signing inner components', 'codesign --options runtime -s "Jan Gerner" -f dist/Type.World.app/Contents/Frameworks/liblzma.5.dylib', None, 'nosign'],
# ['Signing inner components', 'codesign --options runtime -s "Jan Gerner" -f dist/Type.World.app/Contents/Frameworks/libssl.1.1.dylib', None, 'nosign'],
# ['Signing inner components', 'codesign --options runtime -s "Jan Gerner" -f dist/Type.World.app/Contents/Frameworks/Python.framework/Versions/3.7', None, 'nosign'],
# ['Signing inner components', 'codesign --options runtime -s "Jan Gerner" -f dist/Type.World.app/Contents/Frameworks/Sparkle.framework/Versions/A', None, 'nosign'],
# ['Signing inner components', 'codesign --options runtime -s "Jan Gerner" -f dist/Type.World.app/Contents/MacOS/python', None, 'nosign'],

# ['Signing app', 'codesign --options runtime --deep -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app', None, 'nosign'],
# ['Verify signature', 'codesign -dv --verbose=4  ~/Code/TypeWorldApp/dist/Type.World.app', None, 'nosign'],
# ['Verify signature', 'codesign --verify --deep --strict --verbose=20 ~/Code/TypeWorldApp/dist/Type.World.app', findSymlinks, 'nosign'],
# ['Verify signature', 'spctl -a -t exec -vvvv ~/Code/TypeWorldApp/dist/Type.World.app', findSymlinks, 'nosign'],

# ['Move app to archive folder', 'cp -R dist/Type.World.app /Users/yanone/Code/TypeWorldApp/apps/Mac/Type.World.%s.app' % version],
# ]

# for l in _list:

# 	alt = None
# 	excludeCondition = None
# 	if len(l) == 2:
# 		desc, cmd = l
# 	if len(l) == 3:
# 		desc, cmd, alt = l
# 	if len(l) == 4:
# 		desc, cmd, alt, excludeCondition = l


# 	if not excludeCondition or excludeCondition != flavour:

# 		print(desc, '...')

# 		out = Popen(cmd, stderr=STDOUT,stdout=PIPE, shell=True)
# 		output, exitcode = out.communicate()[0].decode(), out.returncode

# 		if exitcode != 0:
# 			print(output)
# 			print()
# 			print(cmd)
# 			print()
# 			print('%s failed! See above.' % desc)
# 			print()
# 			if alt:
# 				print('Debugging output:')
# 				os.system(alt)
# 			sys.exit(0)

# print('Done.')
# print()

