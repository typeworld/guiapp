set -e
VERSION=$(curl "https://api.type.world/latestUnpublishedVersion/world.type.guiapp/mac/?TYPEWORLD_APIKEY=$TYPEWORLD_APIKEY")
echo $VERSION

# executeCommands((
#     ('Check if typeworld.api holds correct version number', f'python wxPython/build/Mac/build-checkversionnumber.py {version}', True),
#     ('Check if can upload to GCS', f'python wxPython/build/Mac/build-canupload.py {version}', True),
#     ('Build', f'python wxPython/build/Mac/build-main.py {version}', True),
#     ('Upload for notarization', f'python wxPython/build/Mac/build-notarize.py {version}', True),
#     ('Wait for notarization', f'python wxPython/build/Mac/build-wait.py {version}', True),
#     ('Pack', f'python wxPython/build/Mac/build-pack.py {version}', True),
#     ('Check again if can upload to GCS', f'python wxPython/build/Mac/build-canupload.py {version}', True),
#     ('Upload', f'python wxPython/build/Mac/build-upload.py {version}', True),
#     ('Upload Sparkle signature', f'python wxPython/build/Mac/build-uploadsignature.py {version}', True),
# ))
