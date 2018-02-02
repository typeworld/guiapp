#!/bin/sh

rm -rf ~/Code/TypeWorldApp/build
rm -rf ~/Code/TypeWorldApp/dist
rm ~/Code/TypeWorldApp/dmg/TypeWorldApp.`cat ~/Code/TypeWorldApp/build/version`.dmg

# Build
python setup.py py2app

cp -R ~/Code/Sparkle/Sparkle.framework ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/

#mkdir versions/`cat build/version`
#mv dist/Type.World.app versions/`cat build/version`

# Sign inner
codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/libwx_baseu-3.0.0.4.0.dylib
codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/libwx_baseu_net-3.0.0.4.0.dylib
codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/libwx_osx_cocoau_core-3.0.0.4.0.dylib
codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/libwx_osx_cocoau_webview-3.0.0.4.0.dylib
codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/Python.framework/Versions/2.7
codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/Sparkle.framework/Versions/A
codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app/Contents/MacOS/python

# Sign
codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/Type.World.app

# Verify
codesign -dv --verbose=4  ~/Code/TypeWorldApp/dist/Type.World.app
spctl --assess --verbose ~/Code/TypeWorldApp/dist/Type.World.app
codesign --verify --deep --strict --verbose=2 ~/Code/TypeWorldApp/dist/Type.World.app


# DMG
#ln -s /Applications dist/Applications
hdiutil create -size 100m -fs HFS+ -srcfolder ~/Code/TypeWorldApp/dist -volname "Type.World App" ~/Code/TypeWorldApp/dmg/TypeWorldApp.`cat ~/Code/TypeWorldApp/build/version`.dmg
#codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dmg/TypeWorldApp.`cat ~/Code/TypeWorldApp/build/version`.dmg
#codesign --verify --deep --strict --verbose=2 ~/Code/TypeWorldApp/dmg/TypeWorldApp.`cat ~/Code/TypeWorldApp/build/version`.dmg

mv ~/Code/TypeWorldApp/dist/Type.World.app ~/Code/TypeWorldApp/apps/Type.World.`cat ~/Code/TypeWorldApp/build/version`.app

# Sparkle
python appcast.py

exit 0