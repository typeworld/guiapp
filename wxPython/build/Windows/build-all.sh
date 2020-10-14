set -e
export APP_BUILD_VERSION=$(curl "https://api.type.world/latestUnpublishedVersion/world.type.guiapp/windows/?TYPEWORLD_APIKEY=$TYPEWORLD_APIKEY")
export SITEPACKAGES=`python -c 'import site; print(site.getsitepackages()[0])'`

echo "Check if typeworld.api holds correct version number"
python wxPython/build/build-checkversionnumber.py $APP_BUILD_VERSION

echo "Check if can upload to GCS"
python wxPython/build/build-canupload.py $APP_BUILD_VERSION windows

echo "Main Build"
python wxPython/build/Windows/build-main.py $APP_BUILD_VERSION

echo "Pack"
python wxPython/build/Windows/build-pack.py $APP_BUILD_VERSION

echo "Upload"
python wxPython/build/build-upload.py $APP_BUILD_VERSION windows

echo "Upload Sparkle signature"
python wxPython/build/Windows/build-uploadsignature.py $APP_BUILD_VERSION

echo "Finished successfully."
