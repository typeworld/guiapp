import os, sys
from subprocess import Popen,PIPE,STDOUT

# List of commands as tuples of:
# - Description
# - Actual command
# - True if this command is essential to the build process (must exit with 0), otherwise False

version = open('/Users/yanone/Code/py/git/typeWorld/guiapp/currentVersion.txt', 'r').read().strip()

commands = (
    ('Remove old .dmg', 'rm ~/Code/TypeWorldApp/dist/TypeWorldApp.forNotarization.dmg', False),
    ('Create .dmg', 'dmgbuild -s /Users/yanone/Code/py/git/typeWorld/guiapp/wxPython/build/Mac/dmgbuild.py "Type.World App" ~/Code/TypeWorldApp/dist/TypeWorldApp.forNotarization.dmg', True),
    ('Sign .dmg', 'codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dist/TypeWorldApp.forNotarization.dmg', True),
    ('Verify .dmg', 'codesign -dv --verbose=4  ~/Code/TypeWorldApp/dist/TypeWorldApp.forNotarization.dmg', True),
    ('Upload for Notarization', 'xcrun altool --primary-bundle-id "Type.World" --notarize-app --username "post@yanone.de" --password "@keychain:Code Signing" --file ~/Code/TypeWorldApp/dist/TypeWorldApp.forNotarization.dmg', True),
)


for description, command, mustSucceed in commands:

    # Print which step we’re currently in
    print(description, '...')

    # Execute the command, fetch both its output as well as its exit code
    out = Popen(command, stderr=STDOUT,stdout=PIPE, shell=True)
    output, exitcode = out.communicate()[0].decode(), out.returncode

    # If the exit code is not zero and this step is marked as necessary to succeed, print the output and quit the script.
    if exitcode != 0 and mustSucceed:
        print(output)
        print()
        print(command)
        print()
        print('Step "%s" failed! See above.' % description)
        print('Command used: %s' % command)
        print()
        sys.exit(666)

print('Finished successfully.')
print()