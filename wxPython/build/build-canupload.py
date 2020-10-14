import os
import sys
import json
from google.cloud import storage

version = sys.argv[-2]
platform = sys.argv[-1]
ending = "dmg" if platform == "mac" else "exe"

print("PWD:", os.environ["PWD"])

# # Google Cloud Storage
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
#     os.environ["PWD"], "typeworld2-559c851e351b.json"
# )

keyfile = open(os.path.join(os.environ["PWD"], "typeworld2-559c851e351b.json"), "r")
key = keyfile.read()
keyfile.close()
key = key.replace("\\\\n", "\r\n")
keyfile = open(os.path.join(os.environ["PWD"], "typeworld2-559c851e351b.json"), "w")
keyfile.write(key)
keyfile.close()
print(key)
print(json.loads(key))

storage_client = storage.Client.from_service_account_json(
    os.path.join(os.environ["PWD"], "typeworld2-559c851e351b.json")
)
bucket = storage_client.bucket("typeworld2")
blobPath = f"downloads/guiapp/TypeWorldApp.{version}.{ending}"
blob = bucket.get_blob(blobPath)
if blob:
    print(f"File {blobPath} already exists in Cloud Storage.")
    sys.exit(1)

# Version number check
if os.environ["APP_BUILD_VERSION"] == "n/a":
    print("No build target version number available: n/a")
    sys.exit(1)
