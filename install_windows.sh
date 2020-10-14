dir "C:\\Program Files (x86)\\Windows Kits\\10\\bin\\"

# Common
sh install_common.sh

# Update pip
python -m pip install --upgrade pip

# Install requirements
python -m pip install -r requirements_windows.txt
