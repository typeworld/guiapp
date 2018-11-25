import os, sys


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




version = open('Z:/Code/py/git/typeWorld/guiapp/currentVersion.txt', 'r').read().strip()


_list = [
['Python build', 'python Z:\\Code\\py\\git\\typeWorld\\guiapp\\wxPython\\build\\Windows\\setup.py build'],
['Add Windows App Manifest', '"Z:\\Code\\Windows\\Dev Tools\\mt.exe" -manifest "Z:\\Code\\py\\git\\typeWorld\\guiapp\\wxPython\\build\\Windows\\windowsAppManifest.xml" -outputresource:Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s\\TypeWorld.exe;#1' % version],
['Signing TypeWorld.exe', '"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.17134.0\\x64\\signtool.exe" sign /debug /fd SHA256 /a /n "Open Source Developer, Jan Gerner" "Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s\\TypeWorld.exe"' % version],
['Signing TypeWorld Taskbar Agent.exe', '"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.17134.0\\x64\\signtool.exe" sign /debug /fd SHA256 /a /n "Open Source Developer, Jan Gerner" "Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s\\TypeWorld Taskbar Agent.exe"' % version],
['Signing TypeWorld Subscription Opener.exe', '"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.17134.0\\x64\\signtool.exe" sign /debug /fd SHA256 /a /n "Open Source Developer, Jan Gerner" "Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s\\TypeWorld Subscription Opener.exe"' % version],
['Verify signature', '"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.17134.0\\x64\\signtool.exe" verify /pa /v "Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s\\TypeWorld.exe"' % version],
['Verify signature', '"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.17134.0\\x64\\signtool.exe" verify /pa /v "Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s\\TypeWorld Taskbar Agent.exe"' % version],
['Verify signature', '"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.17134.0\\x64\\signtool.exe" verify /pa /v "Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s\\TypeWorld Subscription Opener.exe"' % version],
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