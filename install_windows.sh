# Append PATH
$env:PATH += ";$PYTHON;$PYTHON\\Scripts"

# Update pip
$PYTHON\\python.exe -m pip install --upgrade pip

# Install requirements
$PYTHON\\python.exe -m pip install -r requirements_windows.txt

