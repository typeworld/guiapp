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


notarization = executeCommands((
   ('Upload for Notarization', f'xcrun altool --primary-bundle-id "Type.World" --notarize-app --username "post@yanone.de" --password "{os.environ["NOTARIZATION_PASSWORD"]}" --file dist/TypeWorldApp.forNotarization.dmg', True),
), returnOutput=True)

RequestUUID = None
for line in notarization.split('\n'):
    if 'RequestUUID' in line:
        print(f'Notarization UUID: {RequestUUID}')
        RequestUUID = line.split('=')[1].strip()

if not RequestUUID:
    print('No RequestUUID returned')
    sys.exit(1)

while True:

    time.sleep(30)

    check = executeCommands((
        ('Check for notarization results', f'xcrun altool --notarization-info {RequestUUID} --username "post@yanone.de" --password "{os.environ["NOTARIZATION_PASSWORD"]}"', True),
    ), returnOutput = True)

    if not RequestUUID in check:
        print(f'No {RequestUUID} in xcrun altool --notarization-history')
        sys.exit(1)

    if RequestUUID in check and 'Status: success' in check:
        sys.exit(0)

    if RequestUUID in check and 'Status: invalid' in check:
        print(check)
        sys.exit(1)

    if RequestUUID in check and 'Status: in progress' in check:
        pass

print('Finished successfully.')
print()