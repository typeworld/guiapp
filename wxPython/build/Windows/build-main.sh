set -e

echo "Python build"
python wxPython/build/Windows/setup.py build > nul # muting too much output

echo "/build content"
dir build

echo "Add Windows App Manifest"
"$WINDOWSKITBIN\\mt.exe" -manifest "wxPython/build/Windows/windowsAppManifest.xml" -outputresource:build\\TypeWorld.exe;#1

dir $SITEPACKAGES
echo "Copy Google Code"
# Using Python for copying instead of xcopy as I couldn't get it to copy on AppVeyor.
# https://stackoverflow.com/questions/64424550/xcopy-fails-in-appveyor-works-at-home-invalid-number-of-parameters
echo 1
#xcopy "$SITEPACKAGES\\google\\" "build\\lib\\google\\" /i /e /h
python -c "import shutil; shutil.copytree('$SITEPACKAGES\\google', 'build\\lib\\google')"
echo 2
#xcopy "$SITEPACKAGES\\googleapis_common_protos-1.52.0.dist-info\\" "build\\lib\\googleapis_common_protos-1.52.0.dist-info\\" /i /e /h
python -c "import shutil; shutil.copytree('$SITEPACKAGES\\googleapis_common_protos-1.52.0.dist-info', 'build\\lib\\googleapis_common_protos-1.52.0.dist-info')"
echo 3
#xcopy "$SITEPACKAGES\\google_api_core-1.22.4.dist-info" "build\\lib\\google_api_core-1.22.4.dist-info" /i /e /h
python -c "import shutil; shutil.copytree('$SITEPACKAGES\\google_api_core-1.22.4.dist-info', 'build\\lib\\google_api_core-1.22.4.dist-info')"
echo 4
#xcopy "$SITEPACKAGES\\google_auth-1.22.1.dist-info" "build\\lib\\google_auth-1.22.1.dist-info" /i /e /h
python -c "import shutil; shutil.copytree('$SITEPACKAGES\\google_auth-1.22.1.dist-info', 'build\\lib\\google_auth-1.22.1.dist-info')"
echo 5
#xcopy "$SITEPACKAGES\\google_cloud_pubsub-2.1.0.dist-info" "build\\lib\\google_cloud_pubsub-2.1.0.dist-info" /i /e /h
python -c "import shutil; shutil.copytree('$SITEPACKAGES\\google_cloud_pubsub-2.1.0.dist-info', 'build\\lib\\google_cloud_pubsub-2.1.0.dist-info')"

echo "Copy ynlib"
#xcopy ynlib "build\\lib\\ynlib" /i /e /h
python -c "import shutil; shutil.copytree('ynlib\\Lib\\ynlib', 'build\\lib\\ynlib')"

echo "Copy importlib_metadata"
#xcopy "$SITEPACKAGES\\importlib_metadata" "build\\lib\\importlib_metadata"  /i /e /h
# python -c "import shutil; shutil.copytree('$SITEPACKAGES\\importlib_metadata', 'build\\lib\\importlib_metadata')"
#xcopy "$SITEPACKAGES\\importlib_metadata-1.7.0.dist-info" "build\\lib\\importlib_metadata-1.7.0.dist-info" /i /e /h
python -c "import shutil; shutil.copytree('$SITEPACKAGES\\importlib_metadata-1.7.0.dist-info', 'build\\lib\\importlib_metadata-1.7.0.dist-info')"

echo "Signing TypeWorld.exe"
# Export key from Windows: https://www.ca.kit.edu/129.php 
# python -c "import os; command = '\"$WINDOWSKITBIN\\signtool.exe\" sign /tr http://timestamp.digicert.com /td sha256 /fd SHA256 /n \"Jan Gerner\" /v /debug \"build\\TypeWorld.exe\"'; print(command); os.system(command)"
# echo "$WINDOWSKITBIN"\\signtool.exe sign /tr http://timestamp.digicert.com /td sha256 /fd SHA256 /n "Jan Gerner" /v /debug "build\\TypeWorld.exe"
#"$WINDOWSKITBIN\\signtool.exe" sign /v /tr http://timestamp.digicert.com /td sha256 /fd SHA256 /f jangerner.pfx /p $JANGERNER_P12_PASSWORD "build\\TypeWorld.exe"
# "$WINDOWSKITBIN\\signtool.exe" sign /tr http://timestamp.digicert.com /td sha256 /fd SHA256 /n "Jan Gerner" /v /debug "build\\TypeWorld.exe"

#certutil -user -p $JANGERNER_P12_PASSWORD -importPFX jangerner.pfx NoRoot

echo "Signing TypeWorld Subscription Opener.exe"
#python -c "import os; os.system('\"$WINDOWSKITBIN\\signtool.exe\" sign /tr http://timestamp.digicert.com /td sha256 /fd SHA256 /n \"Jan Gerner\" /v /debug \"build\\TypeWorld Subscription Opener.exe\"')"
#"$WINDOWSKITBIN\\signtool.exe" sign /tr http://timestamp.digicert.com /td sha256 /fd SHA256 /n "Jan Gerner" /v /debug "build\\TypeWorld Subscription Opener.exe"
# "$WINDOWSKITBIN\\signtool.exe" sign /v /tr http://timestamp.digicert.com /debug /td sha256 /fd SHA256 /f jangerner.pfx /p $JANGERNER_P12_PASSWORD "build\\TypeWorld Subscription Opener.exe"

echo "Verify signature"
# "$WINDOWSKITBIN\\signtool.exe" verify /pa /v "build\\TypeWorld.exe"
# "$WINDOWSKITBIN\\signtool.exe" verify /pa /v "build\\TypeWorld Subscription Opener.exe"


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
