# Append PATH
#$env:Path += ";$PYTHON;$PYTHON\\Scripts"
echo $PATH
$ENV:PATH="$ENV:PATH;$PYTHONPS"
$ENV:PATH="$ENV:PATH;$PYTHONPS/Scripts"
echo $PATH

# Update pip
$PYTHON\\python.exe -m pip install --upgrade pip

# Install requirements
$PYTHON\\python.exe -m pip install -r requirements_windows.txt

