# -*- coding: utf-8 -*-
import os
import sys
import json
import psutil
from subprocess import Popen, PIPE, STDOUT


profile = json.loads(
    open(os.path.join(os.path.dirname(__file__), "buildProfile.json")).read()
)
version = sys.argv[-1]


def executeCommands(commands):
    for description, command, mustSucceed in commands:

        # Print which step we’re currently in
        print(description, "...")

        # Execute the command, fetch both its output as well as its exit code
        out = Popen(command, stderr=STDOUT, stdout=PIPE, shell=True)
        output, exitcode = out.communicate()[0], out.returncode

        # If the exit code is not zero and this step is marked as necessary to
        #  succeed, print the output and quit the script.
        if exitcode != 0 and mustSucceed:
            print(output)
            print()
            print(command)
            print()
            print('Step "%s" failed! See above.' % description)
            print("Command used: %s" % command)
            print()
            sys.exit(666)


# Needed only for local builds, as the apps might be running
def PID(PROCNAME):
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME and proc.pid != os.getpid():
            return proc.pid


pid = PID("TypeWorld.exe")
if PID("TypeWorld.exe"):
    raise RuntimeError("Type.World seems to be running.")
if PID("TypeWorld Taskbar Agent.exe"):
    raise RuntimeError("Type.World Taskbar Agent seems to be running.")


windowskitbin = os.getenv("WINDOWSKITBIN")
p12password = os.getenv("JANGERNER_P12_PASSWORD")

if "normal" in profile:
    executeCommands(
        [
            [
                "Python build",
                "python wxPython/build/Windows/setup.py build",
                True,
            ],
            [
                "Add Windows App Manifest",
                f'"{windowskitbin}\\mt.exe" -manifest "wxPython/build/Windows/windowsAppManifest.xml" -outputresource:build\\TypeWorld.exe;#1',
                True,
            ],
            [
                "Copy Google Code",
                f"xcopy {os.getenv('SITEPACKAGES')}\\googleapis_common_protos-*.dist-info build\\lib\\  /s /e /h /I /y",
                True,
            ],
            [
                "Copy Google Code",
                f"xcopy {os.getenv('SITEPACKAGES')}\\google build\\lib\\  /s /e /h /I /y",
                True,
            ],
            [
                "Copy Google Code",
                f"xcopy {os.getenv('SITEPACKAGES')}\\google_api_core-*.dist-info build\\lib\\  /s /e /h /I /y",
                True,
            ],
            [
                "Copy Google Code",
                f"xcopy {os.getenv('SITEPACKAGES')}\\google_auth-*.dist-info build\\lib\\  /s /e /h /I /y",
                True,
            ],
            [
                "Copy Google Code",
                f"xcopy {os.getenv('SITEPACKAGES')}\\google_cloud_pubsub-*.dist-info build\\lib\\  /s /e /h /I /y",
                True,
            ],
            [
                "Copy Google Code",
                f"xcopy {os.getenv('SITEPACKAGES')}\\googleapis_common_protos-*.dist-info build\\lib\\  /s /e /h /I /y",
                True,
            ],
            [
                "Copy ynlib",
                f"xcopy ynlib build\\lib\\ /s /e /h /I /y",
                True,
            ],
            [
                "Copy importlib_metadata",
                f"xcopy {os.getenv('SITEPACKAGES')}\\importlib_metadata build\\lib\\  /s /e /h /I /y",
                True,
            ],
            [
                "Copy importlib_metadata",
                f"xcopy {os.getenv('SITEPACKAGES')}\\importlib_metadata-*.dist-info build\\lib\\  /s /e /h /I /y",
                True,
            ],
        ]
    )

if "sign" in profile:
    executeCommands(
        [
            [
                "Signing TypeWorld.exe",
                f'"{windowskitbin}\\signtool.exe" sign /tr http://timestamp.digicert.com /debug /td sha256 /fd SHA256 /n "Jan Gerner" /f JANGERNER.pfx /p "{p12password}" "build\\TypeWorld.exe"',
                # f'"{windowskitbin}\\signtool.exe" sign /tr http://timestamp.digicert.com /debug /td sha256 /fd SHA256 /n "Jan Gerner" "build\\TypeWorld.exe"',
                True,
            ],
            [
                "Signing TypeWorld Subscription Opener.exe",
                f'"{windowskitbin}\\signtool.exe" sign /tr http://timestamp.digicert.com /debug /td sha256 /fd SHA256 /n "Jan Gerner" /f JANGERNER.pfx /p "{p12password}" "build\\TypeWorld Subscription Opener.exe"',
                # f'"{windowskitbin}\\signtool.exe" sign /tr http://timestamp.digicert.com /debug /td sha256 /fd SHA256 /n "Jan Gerner" "build\\TypeWorld Subscription Opener.exe"',
                True,
            ],
            [
                "Verify signature",
                f'"{windowskitbin}\\signtool.exe" verify /pa /v "build\\TypeWorld.exe"',
                True,
            ],
            [
                "Verify signature",
                f'"{windowskitbin}\\signtool.exe" verify /pa /v "build\\TypeWorld Subscription Opener.exe"',
                True,
            ],
        ]
    )

    if "agent" in profile:
        executeCommands(
            [
                [
                    "Signing TypeWorld Taskbar Agent.exe",
                    f'"{windowskitbin}\\signtool.exe" sign /tr http://timestamp.digicert.com /debug /td sha256 /fd SHA256 /a /n "Jan Gerner" "build\\TypeWorld Taskbar Agent.exe"',
                    True,
                ],
                [
                    "Verify signature",
                    f'"{windowskitbin}\\signtool.exe" verify /pa /v "build\\TypeWorld Taskbar Agent.exe"',
                    True,
                ],
            ]
        )

if "normal" in profile:
    executeCommands(
        [
            [
                "App Self Test",
                f'"build\\TypeWorld.exe" selftest',
                True,
            ],
        ]
    )

print("Done.")
