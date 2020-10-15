echo "Create InnoSetup .iss file"
python "wxPython/build/Windows/createissfile.py"

echo "Create InnoSetup Installer"
"C:\\Program Files (x86)\\Inno Setup 5\\ISCC.exe" "wxPython/build/Windows/TypeWorld.iss"

echo "Signing Installer Package"
"$WINDOWSKITBIN\\signtool.exe" sign /tr http://timestamp.digicert.com /debug /td sha256 /fd SHA256 /a /n "Jan Gerner" "dmg/TypeWorldApp.$APP_BUILD_VERSION.exe"

echo "Verify signature"
"$WINDOWSKITBIN\\signtool.exe" verify /pa /v "dmg/TypeWorldApp.$APP_BUILD_VERSION.exe"
