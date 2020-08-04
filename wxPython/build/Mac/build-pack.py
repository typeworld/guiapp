import os, sys
from subprocess import Popen,PIPE,STDOUT

# List of commands as tuples of:
# - Description
# - Actual command
# - True if this command is essential to the build process (must exit with 0), otherwise False

version = sys.argv[-1]

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
    ('Validate notarization', 'spctl -a -vvv -t execute dist/Type.World.app', True),
    ('Staple notarization ticket to app', 'xcrun stapler staple dist/Type.World.app', True),
    ('Validate stapling', 'stapler validate dist/Type.World.app', True),
    ('Remove old dmg', 'rm dmg/TypeWorldApp.%s.dmg' % version, False),
    ('Create .dmg', 'dmgbuild -s wxPython/build/Mac/dmgbuild.py "Type.World App" dmg/TypeWorldApp.%s.dmg' % version, True),
    ('Sign .dmg', 'codesign -s "Jan Gerner" -f dmg/TypeWorldApp.%s.dmg' % version, True),
    ('Verify .dmg', 'codesign -dv --verbose=4  dmg/TypeWorldApp.%s.dmg' % version, True),
#    ('Create appcast', 'python wxPython/build/Mac/appcast.py', True),
    # ('Remove old app', 'rm -r apps/Mac/Type.World.%s.app' % version, False),
    # ('Copy app to archive', 'cp -R dist/Type.World.app apps/Mac/Type.World.%s.app' % version, True),
))

print('Finished successfully.')
print()
