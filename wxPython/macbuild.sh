#!/bin/sh

rm -rf ~/Code/TypeWorldApp/build
rm -rf ~/Code/TypeWorldApp/dist


# Build
python3 setup_mac.py py2app

# Copy Sparkle over
cp -R ~/Code/Sparkle-1.19.0/Sparkle.framework ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/

# Copy docktileplugin
# cp -R /Users/yanone/Code/py/git/typeWorld/guiapp/appbadge/dist/appbadge.docktileplugin ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Resources/

# Move app to archive folder
cp -R ~/Code/TypeWorldApp/dist/Type.World.app ~/Code/TypeWorldApp/apps/Type.World.`cat ~/Code/TypeWorldApp/build/version`.app

exit 0