set -e

echo "Validate notarization"
spctl -a -vvv -t execute dist/Type.World.app

echo "Staple notarization ticket to app"
xcrun --verbose stapler staple dist/Type.World.app

echo "Create .dmg"
dmgbuild -s wxPython/build/Mac/dmgbuild.py "Type.World App" dmg/TypeWorldApp.$APP_BUILD_VERSION.dmg

echo "Sleep 5m"
sleep 5m

# echo "Upload preliminary dmg"
# python wxPython/build/Mac/build-upload.py $APP_BUILD_VERSION

echo "Sign .dmg"
xattr -cr dmg/TypeWorldApp.$APP_BUILD_VERSION.dmg
security unlock-keychain -p travis $KEYCHAIN;
codesign -vvvv -s "Developer ID Application: Jan Gerner" dmg/TypeWorldApp.$APP_BUILD_VERSION.dmg

echo "Verify .dmg"
codesign -vvvv -dv dmg/TypeWorldApp.$APP_BUILD_VERSION.dmg
