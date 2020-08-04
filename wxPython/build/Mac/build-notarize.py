import os, sys, time
from subprocess import Popen,PIPE,STDOUT

# List of commands as tuples of:
# - Description
# - Actual command
# - True if this command is essential to the build process (must exit with 0), otherwise False

def executeCommands(commands, printOutput = False, returnOutput = False):
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
        elif exitcode == 0 and returnOutput:
            return output
        elif exitcode == 0 and printOutput:
            print(output)

executeCommands((
#    ('Remove old .dmg', 'rm dist/TypeWorldApp.forNotarization.dmg', False),
    ('Create .dmg', 'dmgbuild -s wxPython/build/Mac/dmgbuild.py "Type.World App" dist/TypeWorldApp.forNotarization.dmg', True),
    ('Sign .dmg', 'codesign -s "Jan Gerner" -f dist/TypeWorldApp.forNotarization.dmg', True),
    ('Verify .dmg', 'codesign -dv --verbose=4  dist/TypeWorldApp.forNotarization.dmg', True),
))

notarization = executeCommands((
   ('Upload for Notarization', f'xcrun altool --primary-bundle-id "Type.World" --notarize-app --username "post@yanone.de" --password "{os.environ["NOTARIZATION_PASSWORD"]}" --file dist/TypeWorldApp.forNotarization.dmg', True),
), returnOutput=True)

RequestUUID = None
for line in notarization.split('\n'):
    if 'RequestUUID' in line:
        RequestUUID = line.split('=')[1].strip()

if not RequestUUID:
    print('No RequestUUID returned')
    sys.exit(1)

f = open(os.path.join(os.path.dirname(__file__), 'world.type.guiapp.notarization.UUID'), 'w')
f.write(RequestUUID)
f.close()


print('Finished successfully.')
print()