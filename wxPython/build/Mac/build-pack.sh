set -e

echo "Validate notarization"
spctl -a -vvv -t execute dist/Type.World.app

echo "Staple notarization ticket to app"
xcrun --verbose stapler staple dist/Type.World.app

echo "Create .dmg"
dmgbuild -s wxPython/build/Mac/dmgbuild.py "Type.World App" dmg/TypeWorldApp.$APP_BUILD_VERSION.dmg

echo "Sign .dmg"
codesign --verbose=4 -s "Jan Gerner" dmg/TypeWorldApp.$APP_BUILD_VERSION.dmg

echo "Verify .dmg"
codesign --verbose=4 -dv dmg/TypeWorldApp.$APP_BUILD_VERSION.dmg
