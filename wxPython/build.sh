#!/bin/sh

rm -rf ~/Code/TypeWorldApp/build
rm -rf ~/Code/TypeWorldApp/dist

# Build
python setup.py py2app

# Copy Sparkle over
cp -R ~/Code/Sparkle/Sparkle.framework ~/Code/TypeWorldApp/dist/Type.World.app/Contents/Frameworks/

# Move app to archive folder
cp -R ~/Code/TypeWorldApp/dist/Type.World.app ~/Code/TypeWorldApp/apps/Type.World.`cat ~/Code/TypeWorldApp/build/version`.app

exit 0