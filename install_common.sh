# Google Cloud Storage Key
echo $GOOGLE_APPLICATION_CREDENTIALS_KEY > "typeworld2-559c851e351b.json"
# Unix
export GOOGLE_APPLICATION_CREDENTIALS=typeworld2-559c851e351b.json
# Windows
set GOOGLE_APPLICATION_CREDENTIALS=typeworld2-559c851e351b.json
echo "Credentials file: $GOOGLE_APPLICATION_CREDENTIALS"

# ynlib
git clone https://github.com/yanone/ynlib.git

# Build target folder
mkdir build
mkdir dist
mkdir dmg
