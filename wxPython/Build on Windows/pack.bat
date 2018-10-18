z:
cd Z:\Code\py\git\typeWorld\guiapp\wxPython\
python "Z:\Code\py\git\typeWorld\guiapp\wxPython\Build on Windows\createmappingfile.py"
del "Z:\Code\py\git\typeWorld\guiapp\wxPython\TypeWorld.appx"
"C:\Program Files (x86)\Windows Kits\10\bin\10.0.17134.0\x64\makeappx.exe" pack /v /m "Z:\Code\py\git\typeWorld\guiapp\wxPython\Build on Windows\Package.appxmanifest" /f "Z:\Code\py\git\typeWorld\guiapp\wxPython\Build on Windows\mapping.txt" /p TypeWorld.appx
### ./signtool.exe sign /fd "SHA256" /f "C:\users\yanone\TypeWorld.app\signature.pfx" /p "foobar123" "C:\users\yanone\TypeWorld.app\TypeWorld.appx"