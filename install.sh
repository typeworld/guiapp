xcode-select --install

python -m pip install -r requirements.txt

# Download Sparkle
curl -O -L https://github.com/sparkle-project/Sparkle/releases/download/1.23.0/Sparkle-1.23.0.tar.bz2
mkdir sparkle
tar -xf Sparkle-1.23.0.tar.bz2 --directory sparkle

# Google Cloud Storage Key
echo $GOOGLE_APPLICATION_CREDENTIALS_KEY > "typeworld2-559c851e351b.json"

# ynlib
git clone https://github.com/yanone/ynlib.git
export PYTHONPATH="ynlib/Lib"

# Build target folder
mkdir build
mkdir dist

# Mac Code Signing
sh install_mac_codesigning.sh

# Python
ls -la .localpython3.7.7/lib/
ln -s .localpython3.7.7/lib/libpython3.7m.dylib .localpython3.7.7/lib/libpython3.7.dylib
