set -e

echo "Validate notarization"
spctl -a -vvv -t execute dist/Type.World.app

echo "Staple notarization ticket to app"
xcrun --verbose stapler staple dist/Type.World.app

echo "Create .dmg"
dmgbuild -s wxPython/build/Mac/dmgbuild.py "Type.World App" dmg/TypeWorldApp.dmg

echo "Sign .dmg"
codesign -vvvv -s "Jan Gerner" dmg/TypeWorldApp.dmg

echo "Verify .dmg"
codesign -vvvv -dv dmg/TypeWorldApp.dmg
