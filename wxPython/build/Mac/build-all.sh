set -e
export APP_BUILD_VERSION=$(curl "https://api.type.world/latestUnpublishedVersion/world.type.guiapp/mac/?TYPEWORLD_APIKEY=$TYPEWORLD_APIKEY")
export SITEPACKAGES=`python -c 'import site; print(site.getsitepackages()[0])'`

echo "Check if typeworld.api holds correct version number"
python wxPython/build/Mac/build-checkversionnumber.py $APP_BUILD_VERSION

echo "Check if can upload to GCS"
python wxPython/build/Mac/build-canupload.py $APP_BUILD_VERSION

echo proto
ls -la ~/venv3.7.7/lib/python3.7/site-packages/google/cloud/pubsub_v1/proto

echo "Build"
python wxPython/build/Mac/build-main.py $APP_BUILD_VERSION

# echo "\nBuild folder"
# ls -la build
# echo "\nDist folder"
# ls -la dist

echo "Pack for notarization"
echo "Create .dmg"
dmgbuild -s wxPython/build/Mac/dmgbuild.py "Type.World App" dist/TypeWorldApp.dmg
echo "Sign .dmg"
codesign -vvvv -s "Jan Gerner" dist/TypeWorldApp.dmg
echo "Verify .dmg"
codesign -vvvv -dv dist/TypeWorldApp.dmg

echo "Notarization"
python wxPython/build/Mac/build-notarize.py $APP_BUILD_VERSION

echo "Pack"
sh wxPython/build/Mac/build-pack.sh

echo "Check again if can upload to GCS"
python wxPython/build/Mac/build-canupload.py $APP_BUILD_VERSION

echo "Upload"
python wxPython/build/Mac/build-upload.py $APP_BUILD_VERSION

echo "Upload Sparkle signature"
python wxPython/build/Mac/build-uploadsignature.py $APP_BUILD_VERSION
