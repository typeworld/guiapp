z:
cd Z:\Code\py\git\typeWorld\guiapp\wxPython\
python Z:\Code\py\git\typeWorld\guiapp\wxPython\setup_windows.py build
"Z:\Code\Windows\Dev Tools\mt.exe" -manifest Z:\Code\py\git\typeWorld\guiapp\wxPython\windowsAppManifest.xml -outputresource:Z:\Code\TypeWorldApp\Windows\Main\TypeWorld.exe;#1
mkdir "Z:\Code\TypeWorldApp\Windows\Main\URL Opening Agent"
xcopy "Z:\Code\TypeWorldApp\Windows\Agent" "Z:\Code\TypeWorldApp\Windows\Main\URL Opening Agent" /s /e /y