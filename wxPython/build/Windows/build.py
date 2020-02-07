# -*- coding: utf-8 -*-
import os, sys


def executeCommands(commands):
	for description, command, mustSucceed in commands:

		# Print which step we’re currently in
		print(description, '...')

		# Execute the command, fetch both its output as well as its exit code
		out = Popen(command, stderr=STDOUT,stdout=PIPE, shell=True)
		output, exitcode = out.communicate()[0], out.returncode

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


def PID():
    import psutil
    PROCNAME = "TypeWorld.exe"
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME and proc.pid != os.getpid():
            return proc.pid

pid = PID()
if pid:
	raise RuntimeError('Type.World seems to be running.')

from subprocess import Popen,PIPE,STDOUT
flavour = sys.argv[-1]

version = open('Z:/Code/py/git/typeWorld/guiapp/currentVersion.txt', 'r').read().strip()
profile = 'nosign' # 'normal'


executeCommands([
['Python build', 'python Z:\\Code\\py\\git\\typeworld\\guiapp\\wxPython\\build\\Windows\\setup.py build', True],
['Add Windows App Manifest', '"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.18362.0\\x86\\mt.exe" -manifest "Z:\\Code\\py\\git\\typeworld\\guiapp\\wxPython\\build\\Windows\\windowsAppManifest.xml" -outputresource:Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s\\TypeWorld.exe;#1' % version, True],
#['Signing TypeWorld.exe', '"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.17134.0\\x64\\signtool.exe" sign /debug /fd SHA256 /a /n "Open Source Developer, Jan Gerner" "Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s\\TypeWorld.exe"' % version, None, 'nosign'],
#['Signing TypeWorld Taskbar Agent.exe', '"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.17134.0\\x64\\signtool.exe" sign /debug /fd SHA256 /a /n "Open Source Developer, Jan Gerner" "Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s\\TypeWorld Taskbar Agent.exe"' % version, profile in ['normal']],
#['Signing TypeWorld Subscription Opener.exe', '"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.17134.0\\x64\\signtool.exe" sign /debug /fd SHA256 /a /n "Open Source Developer, Jan Gerner" "Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s\\TypeWorld Subscription Opener.exe"' % version, profile in ['normal']],
#['Verify signature', '"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.17134.0\\x64\\signtool.exe" verify /pa /v "Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s\\TypeWorld.exe"' % version, profile in ['normal']],
#['Verify signature', '"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.17134.0\\x64\\signtool.exe" verify /pa /v "Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s\\TypeWorld Taskbar Agent.exe"' % version, profile in ['normal']],
#['Verify signature', '"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.17134.0\\x64\\signtool.exe" verify /pa /v "Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s\\TypeWorld Subscription Opener.exe"' % version, profile in ['normal']],
])


print('Done.')


