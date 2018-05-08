#!/bin/sh

rm -rf ./build
rm -rf ./dist

# Build
python setup.py py2app


exit 0