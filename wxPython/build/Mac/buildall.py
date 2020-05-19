import os, sys, time
from subprocess import Popen,PIPE,STDOUT

# List of commands as tuples of:
# - Description
# - Actual command
# - True if this command is essential to the build process (must exit with 0), otherwise False

version = open('/Users/yanone/Code/py/git/typeworld/guiapp/currentVersion.txt', 'r').read().strip()

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

print(f'Building {version}')

executeCommands((
    ('Build', 'python /Users/yanone/Code/py/git/typeworld/guiapp/wxPython/build/Mac/00-build.py', True),
    ('Upload for notarization', 'python /Users/yanone/Code/py/git/typeworld/guiapp/wxPython/build/Mac/01-notarize.py', True),
    ('Wait for notarization', 'python /Users/yanone/Code/py/git/typeworld/guiapp/wxPython/build/Mac/02-wait.py', True),
    ('Pack', 'python /Users/yanone/Code/py/git/typeworld/guiapp/wxPython/build/Mac/03-pack.py', True),
))

    

print('Finished successfully.')
print()