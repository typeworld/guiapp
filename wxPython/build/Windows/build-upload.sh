set -e

export APP_BUILD_VERSION=$(curl "https://api.type.world/latestUnpublishedVersion/world.type.guiapp/windows/?APPBUILD_KEY=$APPBUILD_KEY")
export SITEPACKAGES=`python -c 'import site; print(site.getsitepackages()[0])'`\\Lib\\site-packages
export WINDOWSKITBIN="C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.19041.0\\x86"

python wxPython/build/build-upload.py windows
python wxPython/build/Windows/build-uploadsignature.py
