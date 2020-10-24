echo "Signing TypeWorld.exe"
"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.19041.0\\x86\\signtool.exe" sign /tr http://timestamp.digicert.com /td sha256 /fd SHA256 /n "Jan Gerner" /v "build\\TypeWorld.exe"

echo "Signing TypeWorld Subscription Opener.exe"
"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.19041.0\\x86\\signtool.exe" sign /tr http://timestamp.digicert.com /td sha256 /fd SHA256 /n "Jan Gerner" /v "build\\TypeWorld Subscription Opener.exe"

echo "Verify signature"
"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.19041.0\\x86\\signtool.exe" verify /pa /v "build\\TypeWorld.exe"
"C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.19041.0\\x86\\signtool.exe" verify /pa /v "build\\TypeWorld Subscription Opener.exe"
