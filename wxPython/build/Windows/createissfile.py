import os


version = open('Z:/Code/py/git/typeWorld/guiapp/currentVersion.txt', 'r').read().strip()

# Write .iss

iss = open('Z:/Code/py/git/typeWorld/guiapp/wxPython/build/Windows/TypeWorld.iss', 'w')
iss.write('''[Setup]
AppName=Type.World
AppVersion=%s
DefaultDirName={pf}\\Type.World
DisableDirPage=yes
DefaultGroupName=Type.World
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\\TypeWorld.exe
Compression=lzma2
SolidCompression=yes
OutputDir=Z:\\Code\\TypeWorldApp\\dmg\\
OutputBaseFilename=TypeWorldApp.%s
DisableReadyPage=yes
CloseApplications=force

[Registry]
Root: HKCR; Subkey: "typeworld"; Flags: uninsdeletekey
Root: HKCR; Subkey: "typeworld"; ValueType: string; ValueData: "URL:typeworld"
Root: HKCR; Subkey: "typeworld"; ValueType: string; ValueName: "URL Protocol"
Root: HKCR; Subkey: "typeworld\\shell\\open\\command"; ValueType: string; ValueData: "\"\"{app}\\TypeWorld Subscription Opener.exe\"\" \"\"%%1\"\""

[Run]
Filename: "{app}\\TypeWorld.exe"; Parameters: "restartAgent"; Flags: runascurrentuser

[UninstallRun]
Filename: "{app}\\TypeWorld.exe"; Parameters: "uninstallAgent"; Flags: runascurrentuser

[Icons]
Name: "{group}\\Type.World"; Filename: "{app}\\TypeWorld.exe"

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    DeleteFile(ExpandConstant('{userappdata}\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Type.World.lnk'));
  end;
end;

[Files]
''' % (version, version))


# Filename: "cmd /min /C ""set __COMPAT_LAYER=RUNASINVOKER && start """" ""{app}\\TypeWorld.exe"" restartAgent"

specialLines = {
#  'TypeWorld Taskbar Agent.exe': '; BeforeInstall: "{app}\\TypeWorld.exe killAgent"',
#  'TypeWorld Taskbar Agent.exe': '; Flags: ignoreversion; BeforeInstall: TaskKill(\'TypeWorld Taskbar Agent.exe\')',
}

# [Run]
# Filename: "{app}\\TypeWorld.exe"; Parameters: "killAgent"


lines = []
lines.append('[Files]')

rootdir = "Z:\\Code\\TypeWorldApp\\apps\\Windows\\%s" % version

for subdir, dirs, files in os.walk(rootdir):
  for file in files:

    if not file.startswith('.'):

      path = os.path.join(subdir, file)
      destsubfolder = subdir[len(rootdir) + 1:]

      special = ''
      for key in specialLines:
        if key in path:
          special = specialLines[key]

      iss.write('Source: "%s"; DestDir: "{app}%s%s"%s\n' % (path, "\\" if destsubfolder else "", destsubfolder, special))


iss.write('''


[Code]
procedure TaskKill(FileName: String);
var
  ResultCode: Integer;
begin
    Exec(ExpandConstant('taskkill.exe'), '/f /im ' + '"' + FileName + '"', '', SW_HIDE,
     ewWaitUntilTerminated, ResultCode);
end;

''')




iss.close()
