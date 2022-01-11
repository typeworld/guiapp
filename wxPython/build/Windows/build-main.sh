set -e

echo
echo "Python build"
python wxPython/build/Windows/setup.py build > nul # muting too much output

echo
echo "/build content"
/bin/ls -la build

echo
echo "/build/lib content"
/bin/ls -la build\\lib

echo
echo "$SITEPACKAGES"
/bin/ls -la $SITEPACKAGES

echo "Add Windows App Manifest"
"$WINDOWSKITBIN\\mt.exe" -manifest "wxPython/build/Windows/windowsAppManifest.xml" -outputresource:build\\TypeWorld.exe;#1

# echo "Copy Google Code"
# cp -r $SITEPACKAGES/google build/lib/
# cp -r $SITEPACKAGES/googleapis_common_protos-*.dist-info build/lib/
# cp -r $SITEPACKAGES/google_api_core-*.dist-info build/lib/
# cp -r $SITEPACKAGES/google_auth-*.dist-info build/lib/
# cp -r $SITEPACKAGES/google_cloud_pubsub-*.dist-info build/lib/

echo "Copy ynlib"
/bin/cp -r ynlib/Lib/ynlib build/lib/

echo "Copy importlib_metadata"
/bin/cp $SITEPACKAGES\\importlib_metadata-4.10.0.dist-info build\\lib\\

echo "Delete stuff"
/bin/rm -r build/lib/wx/locale

echo "App Self Test"
"build/TypeWorld.exe" selftest
