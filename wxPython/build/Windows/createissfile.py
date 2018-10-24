import os


version = open('Z:/Code/py/git/typeWorld/guiapp/currentVersion.txt', 'r').read().strip()

# Write .iss

iss = open('Z:/Code/py/git/typeWorld/guiapp/wxPython/build/Windows/TypeWorld.iss', 'w')
iss.write('''[Setup]
AppName=Type.World
AppVersion=%s
DefaultDirName={pf}\\Type.World
DefaultGroupName=Type.World
UninstallDisplayIcon={app}\\TypeWorld.exe
Compression=lzma2
SolidCompression=yes
OutputDir=Z:\\Code\\TypeWorldApp\\dmg\\
OutputBaseFilename=TypeWorldApp.%s

[Registry]
Root: HKCR; Subkey: "typeworldjson"; Flags: uninsdeletekey
Root: HKCR; Subkey: "typeworldjson"; ValueType: string; ValueData: "URL:typeworldjson"
Root: HKCR; Subkey: "typeworldjson"; ValueType: string; ValueName: "URL Protocol"
Root: HKCR; Subkey: "typeworldjson\\shell\\open\\command"; ValueType: string; ValueData: "\"\"{app}\\URL Opening Agent\\TypeWorld Subscription Opener.exe\"\" \"\"%%1\"\""
Root: HKCR; Subkey: "typeworldgithub"; Flags: uninsdeletekey
Root: HKCR; Subkey: "typeworldgithub"; ValueType: string; ValueData: "URL:typeworldgithub"
Root: HKCR; Subkey: "typeworldgithub"; ValueType: string; ValueName: "URL Protocol"
Root: HKCR; Subkey: "typeworldgithub\\shell\\open\\command"; ValueType: string; ValueData: "\"\"{app}\\URL Opening Agent\\TypeWorld Subscription Opener.exe\"\" \"\"%%1\"\""

[Icons]
Name: "{group}\\Type.World"; Filename: "{app}\\TypeWorld.exe"

[Files]
''' % (version, version))


lines = []
lines.append('[Files]')

rootdir = "Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s" % version

for subdir, dirs, files in os.walk(rootdir):
  for file in files:

    if not file.startswith('.'):

      path = os.path.join(subdir, file)
      destsubfolder = subdir[len(rootdir) + 1:]

      iss.write('Source: "%s"; DestDir: "{app}%s%s"\n' % (path, "\\" if destsubfolder else "", destsubfolder))

iss.close()
