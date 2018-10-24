#!/bin/sh

# Sign inner
codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/libwx_baseu-3.0.0.4.0.dylib
codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/libwx_baseu_net-3.0.0.4.0.dylib
codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/libwx_osx_cocoau_core-3.0.0.4.0.dylib
codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/libwx_osx_cocoau_webview-3.0.0.4.0.dylib
codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/Python.framework/Versions/3.6
codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/Sparkle.framework/Versions/A
codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app/Contents/MacOS/python

# Sign
codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app

# Verify
codesign -dv --verbose=4  ~/Code/TypeWorldApp/dist/Type.World.app
spctl --assess --verbose ~/Code/TypeWorldApp/dist/Type.World.app
codesign --verify --deep --strict --verbose=2 ~/Code/TypeWorldApp/dist/Type.World.app

# DMG
rm ~/Code/TypeWorldApp/dmg/TypeWorldApp.`cat ~/Code/py/git/typeWorld/guiapp/currentVersion.txt`.dmg
hdiutil create -size 100m -fs HFS+ -srcfolder ~/Code/TypeWorldApp/dist -volname "Type.World App" ~/Code/TypeWorldApp/dmg/TypeWorldApp.`cat ~/Code/py/git/typeWorld/guiapp/currentVersion.txt`.dmg
codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dmg/TypeWorldApp.`cat ~/Code/py/git/typeWorld/guiapp/currentVersion.txt`.dmg

# Sparkle
python3 appcast.py

exit 0