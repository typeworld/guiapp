set -e
echo "Checking build version number availability for $1 platform"
APP_BUILD_VERSION=$(curl "https://api.type.world/latestUnpublishedVersion/world.type.guiapp/$1/?TYPEWORLD_APIKEY=$TYPEWORLD_APIKEY")

if [[ "$APP_BUILD_VERSION" == "n/a" ]]; then
    echo "No build version number available: n/a"
    exit 1
fi
