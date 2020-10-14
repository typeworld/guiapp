import os
import sys
import platform
from google.cloud import storage

WIN = platform.system() == "Windows"

version = sys.argv[-2]
platform = sys.argv[-1]
ending = "dmg" if platform == "mac" else "exe"

if WIN:
    keyfile = open(os.path.join(os.environ["PWD"], "typeworld2-559c851e351b.json"), "r")
    key = keyfile.read()
    keyfile.close()
    key = key.replace("\\\\n", "\\r\\n")
    keyfile = open(os.path.join(os.environ["PWD"], "typeworld2-559c851e351b.json"), "w")
    keyfile.write(key)
    keyfile.close()

storage_client = storage.Client.from_service_account_json(
    os.path.join(os.environ["PWD"], "typeworld2-559c851e351b.json")
)

# Upload
bucket = storage_client.bucket("typeworld2")
blob = bucket.blob(f"downloads/guiapp/TypeWorldApp.{version}.{ending}")
blob.upload_from_filename(filename=f"dmg/TypeWorldApp.{version}.{ending}")
