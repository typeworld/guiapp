import os, sys
from subprocess import Popen,PIPE,STDOUT

# List of commands as tuples of:
# - Description
# - Actual command
# - True if this command is essential to the build process (must exit with 0), otherwise False

from ynlib.web import GetHTTP
version = GetHTTP('https://api.type.world/latestUnpublishedVersion/world.type.guiapp/mac/')
if version == 'n/a':
    print('Can’t get version number')
    sys.exit(1)

def executeCommands(commands, printOutput = False):
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
        elif exitcode == 0 and printOutput:
            print(output)

executeCommands((
    ('Validate notarization', 'spctl -a -vvv -t execute ~/Code/TypeWorldApp/dist/Type.World.app', True),
    ('Staple notarization ticket to app', 'xcrun stapler staple ~/Code/TypeWorldApp/dist/Type.World.app', True),
    ('Validate stapling', 'stapler validate ~/Code/TypeWorldApp/dist/Type.World.app', True),
    ('Remove old dmg', 'rm ~/Code/TypeWorldApp/dmg/TypeWorldApp.%s.dmg' % version, False),
    ('Create .dmg', 'dmgbuild -s /Users/yanone/Code/py/git/typeworld/guiapp/wxPython/build/Mac/dmgbuild.py "Type.World App" /Users/yanone/Code/TypeWorldApp/dmg/TypeWorldApp.%s.dmg' % version, True),
    ('Sign .dmg', 'codesign -s "Jan Gerner" -f ~/Code/TypeWorldApp/dmg/TypeWorldApp.%s.dmg' % version, True),
    ('Verify .dmg', 'codesign -dv --verbose=4  ~/Code/TypeWorldApp/dmg/TypeWorldApp.%s.dmg' % version, True),
#    ('Create appcast', 'python /Users/yanone/Code/py/git/typeworld/guiapp/wxPython/build/Mac/appcast.py', True),
    ('Copy app to archive', 'cp -R ~/Code/TypeWorldApp/dist/Type.World.app ~/Code/TypeWorldApp/apps/Mac/Type.World.%s.app' % version, True),
))

print('Finished successfully.')
print()
