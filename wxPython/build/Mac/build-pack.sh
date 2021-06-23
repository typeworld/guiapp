set -e

echo "Create .dmg"
dmgbuild -s wxPython/build/Mac/dmgbuild.py "Type.World App" dmg/TypeWorldApp.dmg

echo "Sign .dmg"
codesign -vvvv -s "Jan Gerner" dmg/TypeWorldApp.dmg

echo "Verify .dmg"
codesign -vvvv -dv dmg/TypeWorldApp.dmg
