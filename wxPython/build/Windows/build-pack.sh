export APP_BUILD_VERSION=$(curl "https://api.type.world/latestUnpublishedVersion/world.type.guiapp/windows/?TYPEWORLD_APIKEY=$TYPEWORLD_APIKEY")
export SITEPACKAGES=`python -c 'import site; print(site.getsitepackages()[0])'`\\Lib\\site-packages
export WINDOWSKITBIN="C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.19041.0\\x86"

echo "Create InnoSetup .iss file"
python "wxPython/build/Windows/createissfile.py"

echo "Create InnoSetup Installer"
"C:\\Program Files (x86)\\Inno Setup 6\\iscc.exe" "wxPython/build/Windows/TypeWorld.iss"
