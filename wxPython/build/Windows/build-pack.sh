echo "Create InnoSetup .iss file"
python "wxPython/build/Windows/createissfile.py"

dir "C:\\Program Files (x86)"
dir "C:\\Program Files (x86)\\Inno Setup 5"

echo "Create InnoSetup Installer"
"C:\\Program Files (x86)\\Inno Setup 5\\iscc.exe" "wxPython/build/Windows/TypeWorld.iss"
