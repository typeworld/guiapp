import os, sys
from subprocess import Popen,PIPE,STDOUT

# List of commands as tuples of:
# - Description
# - Actual command
# - True if this command is essential to the build process (must exit with 0), otherwise False

version = open('/Users/yanone/Code/py/git/typeworld/guiapp/currentVersion.txt', 'r').read().strip()

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

if not 'syncdownloads.sh' in os.listdir(os.getcwd()):
    print('Not in Google App Engine folder!')
    sys.exit(1)

executeCommands((
    ('Sync files to Google Cloud Storage', './syncdownloads.sh', True),
))

print('Finished successfully.')
print()
