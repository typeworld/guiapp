import os, sys, tempfile
from subprocess import Popen,PIPE,STDOUT

# List of commands as tuples of:
# - Description
# - Actual command
# - True if this command is essential to the build process (must exit with 0), otherwise False

from ynlib.web import GetHTTP
version = GetHTTP('https://api.type.world/latestUnpublishedVersion/world.type.guiapp/mac/')
if version == 'n/a':
    print('Can’t get version number')
    sys.exit(1)

# Upload
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(os.path.dirname(__file__), '..', 'typeworld2-559c851e351b.json')
from google.cloud import storage
storage_client = storage.Client()
bucket = storage_client.bucket('typeworld2')
blob = bucket.blob(f'downloads/guiapp/TypeWorldApp.{version}.dmg')
blob.upload_from_filename(filename=f'/Users/yanone/Code/TypeWorldApp/dmg/TypeWorldApp.{version}.dmg')
