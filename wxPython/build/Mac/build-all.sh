export PYTHON="pythonw"

set -e
export APP_BUILD_VERSION=$(curl "https://api.type.world/latestUnpublishedVersion/world.type.guiapp/mac/?TYPEWORLD_APIKEY=$TYPEWORLD_APIKEY")
export SITEPACKAGES=`$PYTHON -c 'import site; print(site.getsitepackages()[0])'`

echo "Check if typeworld.api holds correct version number"
$PYTHON wxPython/build/build-checkversionnumber.py $APP_BUILD_VERSION

echo "Check if can upload to GCS"
$PYTHON wxPython/build/build-canupload.py $APP_BUILD_VERSION mac

echo "Build"
$PYTHON wxPython/build/Mac/build-main.py $APP_BUILD_VERSION

# Pack for notarization
echo "Create .dmg"
dmgbuild -s wxPython/build/Mac/dmgbuild.py "Type.World App" dist/TypeWorldApp.notarize.dmg
echo "Sign .dmg"
codesign -vvvv -s "Jan Gerner" dist/TypeWorldApp.notarize.dmg
echo "Verify .dmg"
codesign -vvvv -dv dist/TypeWorldApp.notarize.dmg

echo "Notarization"
$PYTHON wxPython/build/Mac/build-notarize.py $APP_BUILD_VERSION

echo "Pack"
sh wxPython/build/Mac/build-pack.sh

echo "Upload"
$PYTHON wxPython/build/build-upload.py $APP_BUILD_VERSION mac

echo "Upload Sparkle signature"
$PYTHON wxPython/build/Mac/build-uploadsignature.py $APP_BUILD_VERSION
