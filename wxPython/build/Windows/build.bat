z:
cd Z:\Code\py\git\typeWorld\guiapp\wxPython
python Z:\Code\py\git\typeWorld\guiapp\wxPython\build\Windows\setup.py build

set /p Version=<Z:\Code\py\git\typeWorld\guiapp\currentVersion.txt

"Z:\Code\Windows\Dev Tools\mt.exe" -manifest "Z:\Code\py\git\typeWorld\guiapp\wxPython\build\Windows\windowsAppManifest.xml" -outputresource:Z:\Code\TypeWorldApp\apps\Windows\%Version%\TypeWorld.exe;#1

"C:\Program Files (x86)\Windows Kits\10\bin\10.0.17134.0\x64\signtool.exe" sign /fd "SHA256" /f "Z:\Code\py\git\typeWorld\guiapp\wxPython\build\Windows\signature.pfx" /p "foobar123" "Z:\Code\TypeWorldApp\apps\Windows\%Version%\TypeWorld.exe"
