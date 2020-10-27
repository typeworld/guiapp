set -e
echo "Checking build version number availability for $1 platform"
APP_BUILD_VERSION=$(curl "https://api.type.world/latestUnpublishedVersion/world.type.guiapp/$1/?TYPEWORLD_APIKEY=$TYPEWORLD_APIKEY")

if [[ "$APP_BUILD_VERSION" == "n/a" ]]; then
    echo "No build version number available for $1 platform: n/a" 1>&2
    exit 1
else
    echo "Building version $APP_BUILD_VERSION for $1 platform"
fi
