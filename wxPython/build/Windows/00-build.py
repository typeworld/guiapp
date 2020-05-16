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


def PID(PROCNAME):
    import psutil
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME and proc.pid != os.getpid():
            return proc.pid

pid = PID("TypeWorld.exe")
if PID("TypeWorld.exe"):
	raise RuntimeError('Type.World seems to be running.')
if PID("TypeWorld Taskbar Agent.exe"):
	raise RuntimeError('Type.World Taskbar Agent seems to be running.')

from subprocess import Popen,PIPE,STDOUT
flavour = sys.argv[-1]

version = open('Z:/Code/py/git/typeworld/guiapp/currentVersion.txt', 'r').read().strip()
profile = 'nosign' # 'normal'


executeCommands([
['Python build', 'python Z:\\Code\\py\\git\\typeworld\\guiapp\\wxPython\\build\\Windows\\setup.py build', True],
['Add Windows App Manifest', '"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.18362.0\\x86\\mt.exe" -manifest "Z:\\Code\\py\\git\\typeworld\\guiapp\\wxPython\\build\\Windows\\windowsAppManifest.xml" -outputresource:Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s\\TypeWorld.exe;#1' % version, True],

['Copy dsa_pub.pem', f'xcopy Z:\\Code\\Certificates\\Type.World Sparkle\\dsa_pub.pem Z:\\Code\\TypeWorldApp\\apps\\Windows\\{version}\\ /s /e /h /I /y', True],

['Copy Google Code', f'xcopy C:\\Python36\\Lib\\site-packages\\googleapis_common_protos-1.6.0.dist-info Z:\\Code\\TypeWorldApp\\apps\\Windows\\{version}\\lib\\googleapis_common_protos-1.6.0.dist-info  /s /e /h /I /y', True],
['Copy Google Code', f'xcopy C:\\Python36\\Lib\\site-packages\\google Z:\\Code\\TypeWorldApp\\apps\\Windows\\{version}\\lib\\google  /s /e /h /I /y', True],
['Copy Google Code', f'xcopy C:\\Python36\\Lib\\site-packages\\google_api_core-1.14.3.dist-info Z:\\Code\\TypeWorldApp\\apps\\Windows\\{version}\\lib\\google_api_core-1.14.3.dist-info  /s /e /h /I /y', True],
['Copy Google Code', f'xcopy C:\\Python36\\Lib\\site-packages\\google_auth-1.11.0.dist-info Z:\\Code\\TypeWorldApp\\apps\\Windows\\{version}\\lib\\google_auth-1.11.0.dist-info  /s /e /h /I /y', True],
['Copy Google Code', f'xcopy C:\\Python36\\Lib\\site-packages\\google_cloud_pubsub-1.0.2.dist-info Z:\\Code\\TypeWorldApp\\apps\\Windows\\{version}\\lib\\google_cloud_pubsub-1.0.2.dist-info  /s /e /h /I /y', True],
['Copy Google Code', f'xcopy C:\\Python36\\Lib\\site-packages\\googleapis_common_protos-1.6.0.dist-info Z:\\Code\\TypeWorldApp\\apps\\Windows\\{version}\\lib\\googleapis_common_protos-1.6.0.dist-info  /s /e /h /I /y', True],

['Copy importlib_metadata', f'xcopy C:\\Python36\\Lib\\site-packages\\importlib_metadata Z:\\Code\\TypeWorldApp\\apps\\Windows\\{version}\\lib\\importlib_metadata  /s /e /h /I /y', True],
['Copy importlib_metadata', f'xcopy C:\\Python36\\Lib\\site-packages\\importlib_metadata-1.5.0.dist-info Z:\\Code\\TypeWorldApp\\apps\\Windows\\{version}\\lib\\importlib_metadata-1.5.0.dist-info  /s /e /h /I /y', True],


['Signing TypeWorld.exe', 						'"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.17134.0\\x64\\signtool.exe" sign /tr http://timestamp.digicert.com /debug /td sha256 /fd SHA256 /a /n "Jan Gerner" "Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s\\TypeWorld.exe"' % version, profile in ['normal']],
['Signing TypeWorld Taskbar Agent.exe', 		'"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.17134.0\\x64\\signtool.exe" sign /tr http://timestamp.digicert.com /debug /td sha256 /fd SHA256 /a /n "Jan Gerner" "Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s\\TypeWorld Taskbar Agent.exe"' % version, profile in ['normal']],
['Signing TypeWorld Subscription Opener.exe', 	'"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.17134.0\\x64\\signtool.exe" sign /tr http://timestamp.digicert.com /debug /td sha256 /fd SHA256 /a /n "Jan Gerner" "Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s\\TypeWorld Subscription Opener.exe"' % version, profile in ['normal']],
['Verify signature', '"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.17134.0\\x64\\signtool.exe" verify /pa /v "Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s\\TypeWorld.exe"' % version, profile in ['normal']],
['Verify signature', '"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.17134.0\\x64\\signtool.exe" verify /pa /v "Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s\\TypeWorld Taskbar Agent.exe"' % version, profile in ['normal']],
['Verify signature', '"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.17134.0\\x64\\signtool.exe" verify /pa /v "Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s\\TypeWorld Subscription Opener.exe"' % version, profile in ['normal']],
])


print('Done.')


