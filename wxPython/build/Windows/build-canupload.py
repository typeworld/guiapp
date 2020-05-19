import os, sys

from ynlib.web import GetHTTP
version = GetHTTP('https://api.type.world/latestUnpublishedVersion/world.type.guiapp/windows/')
if version == 'n/a':
    print('Can’t get version number')
    sys.exit(1)

# Google Cloud Storage
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(os.path.dirname(__file__), '..', 'typeworld2-559c851e351b.json')
from google.cloud import storage
storage_client = storage.Client()
bucket = storage_client.bucket('typeworld2')
blobPath = f'downloads/guiapp/TypeWorldApp.{version}.exe'
blob = bucket.get_blob(blobPath)
if blob:
    print(f'File {blobPath} already exists in Cloud Storage. WARNING: This should have been checked in the beginning of the build process already. If you see this at the end of the build process, this should mean that someone else has uploaded that file in the meantime.')
    sys.exit(1)
