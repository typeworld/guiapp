set -e

echo "Python build"
python wxPython/build/Windows/setup.py build > nul # muting too much output

echo "/build content"
dir build

echo "Add Windows App Manifest"
"$WINDOWSKITBIN\\mt.exe" -manifest "wxPython/build/Windows/windowsAppManifest.xml" -outputresource:build\\TypeWorld.exe;#1

echo "Copy Google Code",
xcopy $SITEPACKAGES\\googleapis_common_protos-*.dist-info build\\lib\\  /s /e /h /I /y
xcopy $SITEPACKAGES\\google build\\lib\\  /s /e /h /I /y
xcopy $SITEPACKAGES\\google_api_core-*.dist-info build\\lib\\  /s /e /h /I /y
xcopy $SITEPACKAGES\\google_auth-*.dist-info build\\lib\\  /s /e /h /I /y
xcopy $SITEPACKAGES\\google_cloud_pubsub-*.dist-info build\\lib\\  /s /e /h /I /y
xcopy $SITEPACKAGES\\googleapis_common_protos-*.dist-info build\\lib\\  /s /e /h /I /y

echo "Copy ynlib"
xcopy ynlib build\\lib\\ /s /e /h /I /y

echo "Copy importlib_metadata"
xcopy $SITEPACKAGES\\importlib_metadata build\\lib\\  /s /e /h /I /y
xcopy $SITEPACKAGES\\importlib_metadata-*.dist-info build\\lib\\  /s /e /h /I /y

echo "Signing TypeWorld.exe"
"$WINDOWSKITBIN\\signtool.exe" sign /tr http://timestamp.digicert.com /debug /td sha256 /fd SHA256 /f jan_gerner.p12 /p $JANGERNER_P12_PASSWORD "build\\TypeWorld.exe"
# $WINDOWSKITBIN\\signtool.exe" sign /tr http://timestamp.digicert.com /debug /td sha256 /fd SHA256 /n "Jan Gerner" "build\\TypeWorld.exe"',

echo "Signing TypeWorld Subscription Opener.exe"
"$WINDOWSKITBIN\\signtool.exe" sign /tr http://timestamp.digicert.com /debug /td sha256 /fd SHA256 /f jan_gerner.p12 /p $JANGERNER_P12_PASSWORD "build\\TypeWorld Subscription Opener.exe"
# $WINDOWSKITBIN\\signtool.exe" sign /tr http://timestamp.digicert.com /debug /td sha256 /fd SHA256 /n "Jan Gerner" "build\\TypeWorld Subscription Opener.exe"',

echo "Verify signature"
"$WINDOWSKITBIN\\signtool.exe" verify /pa /v "build\\TypeWorld.exe"
"$WINDOWSKITBIN\\signtool.exe" verify /pa /v "build\\TypeWorld Subscription Opener.exe"


    # if "agent" in profile:
    #     executeCommands(
    #         [
    #             [
    #                 "Signing TypeWorld Taskbar Agent.exe",
    #                 $WINDOWSKITBIN\\signtool.exe" sign /tr http://timestamp.digicert.com /debug /td sha256 /fd SHA256 /a /n "Jan Gerner" "build\\TypeWorld Taskbar Agent.exe"',
    #                 True,
    #             ],
    #             [
    #                 "Verify signature",
    #                 $WINDOWSKITBIN\\signtool.exe" verify /pa /v "build\\TypeWorld Taskbar Agent.exe"',
    #                 True,
    #             ],
    #         ]        )

echo "App Self Test"
"build\\TypeWorld.exe" selftest
