set /p Version=<Z:\Code\py\git\typeWorld\guiapp\currentVersion.txt

rem ## Installer file
python "Z:\Code\py\git\typeWorld\guiapp\wxPython\build\Windows\createissfile.py"

rem InnoSetup
"C:\Program Files (x86)\Inno Setup 5\ISCC.exe" "Z:\Code\py\git\typeWorld\guiapp\wxPython\build\Windows\TypeWorld.iss"

"C:\Program Files (x86)\Windows Kits\10\bin\10.0.17134.0\x64\signtool.exe" sign /fd "SHA256" /f "Z:\Code\py\git\typeWorld\guiapp\wxPython\build\Windows\signature.pfx" /p "foobar123" "Z:\Code\TypeWorldApp\dmg\TypeWorldApp.%Version%.exe"

rem # .appx packing
rem z:
rem cd Z:\Code\py\git\typeWorld\guiapp\wxPython\
rem python "Z:\Code\py\git\typeWorld\guiapp\wxPython\Build on Windows\createmappingfile.py"
rem del "Z:\Code\py\git\typeWorld\guiapp\wxPython\TypeWorld.appx"
rem "C:\Program Files (x86)\Windows Kits\10\bin\10.0.17134.0\x64\makeappx.exe" pack /v /m "Z:\Code\py\git\typeWorld\guiapp\wxPython\Build on Windows\Package.appxmanifest" /f "Z:\Code\py\git\typeWorld\guiapp\wxPython\Build on Windows\mapping.txt" /p TypeWorld.appx
rem ### ./signtool.exe sign /fd "SHA256" /f "C:\users\yanone\TypeWorld.app\signature.pfx" /p "foobar123" "C:\users\yanone\TypeWorld.app\TypeWorld.appx"