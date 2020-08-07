import os, sys, tempfile
from subprocess import Popen,PIPE,STDOUT

# List of commands as tuples of:
# - Description
# - Actual command
# - True if this command is essential to the build process (must exit with 0), otherwise False

version = sys.argv[-1]

# Upload
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'typeworld2-559c851e351b.json'
from google.cloud import storage
storage_client = storage.Client()
bucket = storage_client.bucket('typeworld2')
blob = bucket.blob(f'downloads/guiapp/TypeWorldApp.{version}.dmg')
blob.upload_from_filename(filename=f'dist/TypeWorldApp.dmg')
