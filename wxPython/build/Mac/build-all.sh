set -e
export APP_BUILD_VERSION=$(curl "https://api.type.world/latestUnpublishedVersion/world.type.guiapp/mac/?TYPEWORLD_APIKEY=$TYPEWORLD_APIKEY")
echo $APP_BUILD_VERSION

echo "Check if typeworld.api holds correct version number"
python wxPython/build/Mac/build-checkversionnumber.py $APP_BUILD_VERSION

echo "Check if can upload to GCS"
python wxPython/build/Mac/build-canupload.py $APP_BUILD_VERSION

echo "Build"
python wxPython/build/Mac/build-canupload.py $APP_BUILD_VERSION

echo "Upload for notarization"
python wxPython/build/Mac/build-notarize.py $APP_BUILD_VERSION

echo "Wait for notarization"
python wxPython/build/Mac/build-wait.py $APP_BUILD_VERSION

echo "Pack"
python wxPython/build/Mac/build-pack.py $APP_BUILD_VERSION

echo "Check again if can upload to GCS"
python wxPython/build/Mac/build-canupload.py $APP_BUILD_VERSION

echo "Upload"
python wxPython/build/Mac/build-upload.py $APP_BUILD_VERSION

echo "Upload Sparkle signature"
python wxPython/build/Mac/build-uploadsignature.py $APP_BUILD_VERSION

# executeCommands((
#     ('Check if can upload to GCS', f'python wxPython/build/Mac/build-canupload.py $APP_BUILD_VERSION', True),
#     ('Build', f'python wxPython/build/Mac/build-main.py $APP_BUILD_VERSION', True),
#     ('Upload for notarization', f'python wxPython/build/Mac/build-notarize.py $APP_BUILD_VERSION', True),
#     ('Wait for notarization', f'python wxPython/build/Mac/build-wait.py $APP_BUILD_VERSION', True),
#     ('Pack', f'python wxPython/build/Mac/build-pack.py $APP_BUILD_VERSION', True),
#     ('Check again if can upload to GCS', f'python wxPython/build/Mac/build-canupload.py $APP_BUILD_VERSION', True),
#     ('Upload', f'python wxPython/build/Mac/build-upload.py $APP_BUILD_VERSION', True),
#     ('Upload Sparkle signature', f'python wxPython/build/Mac/build-uploadsignature.py $APP_BUILD_VERSION', True),
# ))
