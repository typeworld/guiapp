import os, sys

from subprocess import Popen, PIPE, STDOUT

version = sys.argv[-1]


def executeCommands(commands):
    for description, command, mustSucceed in commands:

        # Print which step we’re currently in
        print(description, "...")

        # Execute the command, fetch both its output as well as its exit code
        out = Popen(command, stderr=STDOUT, stdout=PIPE, shell=True)
        output, exitcode = out.communicate()[0], out.returncode

        # If the exit code is not zero and this step is marked as necessary to succeed, print the output and quit the script.
        if exitcode != 0 and mustSucceed:
            print(output)
            print()
            print(command)
            print()
            print('Step "%s" failed! See above.' % description)
            print("Command used: %s" % command)
            print()
            sys.exit(666)


windowskitbin = "C:\\Program Files (x86)\\Windows Kits\\10.0\\bin\\x64"

executeCommands(
    [
        [
            "Create InnoSetup .iss file",
            'python "wxPython/build/Windows/createissfile.py"',
            True,
        ],
        [
            "Create InnoSetup Installer",
            '"C:\\Program Files (x86)\\Inno Setup 5\\ISCC.exe" "wxPython/build/Windows/TypeWorld.iss"',
            True,
        ],
        [
            "Signing Installer Package",
            f'"{windowskitbin}\\signtool.exe" sign /tr http://timestamp.digicert.com /debug /td sha256 /fd SHA256 /a /n "Jan Gerner" "dmg/TypeWorldApp.{version}.exe"',
            True,
        ],
        [
            "Verify signature",
            f'"{windowskitbin}\\signtool.exe" verify /pa /v "dmg/TypeWorldApp.{version}.exe"',
            True,
        ],
    ]
)


print("Done.")
