echo "Create InnoSetup .iss file"
python "wxPython/build/Windows/createissfile.py"

echo "Create InnoSetup Installer"
"C:\\Program Files (x86)\\Inno Setup 6\\iscc.exe" "wxPython/build/Windows/TypeWorld.iss"
