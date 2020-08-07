set -e
export APP_BUILD_VERSION=$(curl "https://api.type.world/latestUnpublishedVersion/world.type.guiapp/mac/?TYPEWORLD_APIKEY=$TYPEWORLD_APIKEY")

echo "Check if typeworld.api holds correct version number"
python wxPython/build/Mac/build-checkversionnumber.py $APP_BUILD_VERSION

echo "Check if can upload to GCS"
python wxPython/build/Mac/build-canupload.py $APP_BUILD_VERSION

echo "Build"
python wxPython/build/Mac/build-main.py $APP_BUILD_VERSION

echo "\nBuild folder"
ls -la build
echo "\nDist folder"
ls -la dist

echo "Pack for notarization"
echo "Create .dmg"
dmgbuild -s wxPython/build/Mac/dmgbuild.py "Type.World App" dist/TypeWorldApp.forNotarization.dmg
echo "Sign .dmg"
codesign -s "Jan Gerner" -f dist/TypeWorldApp.forNotarization.dmg
echo "Verify .dmg"
codesign -dv --verbose=4  dist/TypeWorldApp.forNotarization.dmg

echo "Notarization"
python wxPython/build/Mac/build-notarize.py $APP_BUILD_VERSION

#echo "Pack"
#sh wxPython/build/Mac/build-pack.sh

echo "Check again if can upload to GCS"
python wxPython/build/Mac/build-canupload.py $APP_BUILD_VERSION

echo "Upload"
python wxPython/build/Mac/build-upload.py $APP_BUILD_VERSION

echo "Upload Sparkle signature"
python wxPython/build/Mac/build-uploadsignature.py $APP_BUILD_VERSION
