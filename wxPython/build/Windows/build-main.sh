set -e

# ls -la C:\\projects\\guiapp\\build\\lib\\zmq\\
# ls -la C:\\projects\\guiapp\\build\\lib\\zmq\\.libs\\

#C:\projects\guiapp\build\lib\

echo "Python build"
python wxPython/build/Windows/setup.py build > nul # muting too much output

echo "/build content"
dir build

echo "/build/lib content"
dir build\\lib

echo "Add Windows App Manifest"
"$WINDOWSKITBIN\\mt.exe" -manifest "wxPython/build/Windows/windowsAppManifest.xml" -outputresource:build\\TypeWorld.exe;#1

# echo "Copy Google Code"
# cp -r $SITEPACKAGES/google build/lib/
# cp -r $SITEPACKAGES/googleapis_common_protos-*.dist-info build/lib/
# cp -r $SITEPACKAGES/google_api_core-*.dist-info build/lib/
# cp -r $SITEPACKAGES/google_auth-*.dist-info build/lib/
# cp -r $SITEPACKAGES/google_cloud_pubsub-*.dist-info build/lib/

echo "Copy ynlib"
cp -r ynlib/Lib/ynlib build/lib/

echo "Copy importlib_metadata"
cp -r $SITEPACKAGES/importlib_metadata-*.dist-info build/lib/

echo "App Self Test"
"build/TypeWorld.exe" selftest
