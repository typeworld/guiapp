import os, sys

from subprocess import Popen,PIPE,STDOUT

version = open('Z:/Code/py/git/typeworld/guiapp/currentVersion.txt', 'r').read().strip()


_list = [
['Create InnoSetup .iss file', 'python "Z:\\Code\\py\\git\\typeworld\\guiapp\\wxPython\\build\\Windows\\createissfile.py"'],
['Create InnoSetup Installer', '"C:\\Program Files (x86)\\Inno Setup 5\\ISCC.exe" "Z:\\Code\\py\\git\\typeworld\\guiapp\\wxPython\\build\\Windows\\TypeWorld.iss"'],
['Signing Installer Package', '"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.17134.0\\x64\\signtool.exe" /tr http://timestamp.digicert.com /debug /td sha256 /fd SHA256 /a /n "Jan Gerner" "Z:\\Code\\TypeWorldApp\\dmg\\TypeWorldApp.%s.exe"' % version],
['Verify signature', '"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.17134.0\\x64\\signtool.exe" verify /pa /v "Z:\\Code\\TypeWorldApp\\dmg\\TypeWorldApp.%s.exe"' % version],
]

for desc, cmd in _list:

	print(desc, '...')
	out = Popen(cmd, stderr=STDOUT,stdout=PIPE)
	output, exitcode = out.communicate()[0].decode(), out.returncode

	if exitcode != 0:
		print(output)
		print()
		print(cmd)
		print()
		print('%s failed! See above.' % desc)
		sys.exit(0)

print ('Done.')
