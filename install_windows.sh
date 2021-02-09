# Code Signing
# https://stackoverflow.com/questions/5171117/import-pfx-file-into-particular-certificate-store-from-command-line
certutil -user -p $JANGERNER_PFX_PASSWORD -importPFX wxPython\\build\\Windows\\codesigning\\jangerner.pfx NoRoot

# Common
sh install_common.sh

# Update pip
python -m pip install --upgrade pip

# Install requirements
python -m pip install -r requirements_windows.txt

# Download Sparkle
curl -O -L https://github.com/vslavik/winsparkle/releases/download/v0.7.0/WinSparkle-0.7.0.zip
mkdir sparkle
unzip WinSparkle-0.7.0.zip -d sparkle

# Copy ynlib
export SITEPACKAGES=`python -c 'import site; print(site.getsitepackages()[0])'`\\Lib\\site-packages
cp -R ynlib/Lib/ynlib $SITEPACKAGES

