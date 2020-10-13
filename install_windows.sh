# Append PATH
$env:PATH += ";$PYTHON"
$env:PATH += ";$PYTHON\\Scripts"

# Update pip
$PYTHON\\python.exe -m pip install --upgrade pip

# Install requirements
$PYTHON\\python.exe -m pip install -r requirements_windows.txt

