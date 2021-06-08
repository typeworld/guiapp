import os
import sys
import platform
from google.cloud import storage

WIN = platform.system() == "Windows"

version = os.getenv("APP_BUILD_VERSION", "undefined")
assert version != "undefined"

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
bucket = storage_client.bucket("storage2")
blob = bucket.blob(f"app/TypeWorldApp.{version}.{ending}")
blob.upload_from_filename(filename=f"dmg/TypeWorldApp.{ending}")
