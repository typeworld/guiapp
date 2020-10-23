echo "Signing TypeWorld.exe"
"%WINDOWSKITBIN%\\signtool.exe" sign /tr http://timestamp.digicert.com /td sha256 /fd SHA256 /n "Jan Gerner" /v "build\\TypeWorld.exe"

echo "Signing TypeWorld Subscription Opener.exe"
"%WINDOWSKITBIN%\\signtool.exe" sign /tr http://timestamp.digicert.com /td sha256 /fd SHA256 /n "Jan Gerner" /v /debug "build\\TypeWorld Subscription Opener.exe"

echo "Verify signature"
"%WINDOWSKITBIN%\\signtool.exe" verify /pa /v "build\\TypeWorld.exe"
"%WINDOWSKITBIN%\\signtool.exe" verify /pa /v "build\\TypeWorld Subscription Opener.exe"
