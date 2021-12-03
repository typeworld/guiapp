set -e

export APP_BUILD_VERSION=$(curl "https://api.type.world/latestUnpublishedVersion/world.type.guiapp/windows/?APPBUILD_KEY=$APPBUILD_KEY")
export SITEPACKAGES=`python -c 'import site; print(site.getsitepackages()[0])'`\\Lib\\site-packages
export WINDOWSKITBIN="C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.19041.0\\x86"

# echo "Check if typeworld.api holds correct version number"
# python wxPython/build/build-checkversionnumber.py

echo "Check if can upload to GCS"
python wxPython/build/build-canupload.py windows

# First round of main build with "Console" base, as error output will be routed to the
# console instead of popup message windows, to read output of self test in the build
echo "Main Build, Console base, export"
export BUILDBASE="Console"
echo "Main Build, Console base"
$SHELL wxPython/build/Windows/build-main.sh

# Clear build folder
rm -rf build
mkdir build

# Second round with "Win32GUI" base (no console window appears on Windows)
echo "Main Build, GUI base"
export BUILDBASE="Win32GUI"
$SHELL wxPython/build/Windows/build-main.sh

