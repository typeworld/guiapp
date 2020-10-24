# Code Signing
sh install_windows_codesigning.sh

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
