set -e

echo "Validate notarization"
spctl -a -vvv -t execute dist/Type.World.app

echo "Staple notarization ticket to app"
xcrun stapler staple dist/Type.World.app

echo "Create .dmg"
dmgbuild -s wxPython/build/Mac/dmgbuild.py "Type.World App" dmg/TypeWorldApp.$APP_BUILD_VERSION.dmg

echo "Sign .dmg"
codesign -s "Jan Gerner" dmg/TypeWorldApp.$APP_BUILD_VERSION.dmg

echo "Verify .dmg"
codesign -dv --verbose=4  dmg/TypeWorldApp.$APP_BUILD_VERSION.dmg
