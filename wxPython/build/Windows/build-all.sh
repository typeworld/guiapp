set -e
export APP_BUILD_VERSION=$(curl "https://api.type.world/latestUnpublishedVersion/world.type.guiapp/windows/?TYPEWORLD_APIKEY=$TYPEWORLD_APIKEY")
export SITEPACKAGES=`python -c 'import site; print(site.getsitepackages()[0])'`\\Lib\\site-packages
export WINDOWSKITBIN="C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.19041.0\\x86"
#10.0.19041.0
#10.0.18362.0
echo $SITEPACKAGES
#dir $SITEPACKAGES

env

echo "Check if typeworld.api holds correct version number"
python wxPython/build/build-checkversionnumber.py $APP_BUILD_VERSION

echo "Check if can upload to GCS"
python wxPython/build/build-canupload.py $APP_BUILD_VERSION windows

# First round of main build with "Console" base, as error output will be routed to the
# console instead of popup message windows, to read output of self test in the build
echo "Main Build, Console base"
export BUILDBASE="Console"
sh wxPython/build/Windows/build-main.sh

# Clear build folder
rmdir /s build
mkdir build

# Second round with "Win32GUI" base (no console window appears on Windows)
echo "Main Build, GUI base"
export BUILDBASE="Win32GUI"
sh wxPython/build/Windows/build-main.sh

echo "Pack"
sh wxPython/build/Windows/build-pack.sh

echo "Upload"
python wxPython/build/build-upload.py $APP_BUILD_VERSION windows

echo "Upload Sparkle signature"
python wxPython/build/Windows/build-uploadsignature.py $APP_BUILD_VERSION

echo "Finished successfully."
