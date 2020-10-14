import os
import sys
from google.cloud import storage

version = sys.argv[-2]
platform = sys.argv[-1]
ending = "dmg" if platform == "mac" else "exe"

print("PWD:", os.environ["PWD"])

# Google Cloud Storage
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "typeworld2-559c851e351b.json")
)

print(open(os.environ["GOOGLE_APPLICATION_CREDENTIALS"], "r").read())

storage_client = storage.Client()
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
