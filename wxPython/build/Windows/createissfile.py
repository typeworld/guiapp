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
