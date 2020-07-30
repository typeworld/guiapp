import os, sys, time
from subprocess import Popen,PIPE,STDOUT

# List of commands as tuples of:
# - Description
# - Actual command
# - True if this command is essential to the build process (must exit with 0), otherwise False


import ssl
import certifi
import urllib.request

request = urllib.request.Request("https://api.type.world/latestUnpublishedVersion/world.type.guiapp/mac/")
sslcontext = ssl.create_default_context(cafile=certifi.where())
response = urllib.request.urlopen(request, context=sslcontext)
version = response.read().decode()


#version = os.system('curl https://api.type.world/latestUnpublishedVersion/world.type.guiapp/mac/')
if version == 'n/a':
    print("Can't get version number")
    sys.exit(1)

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
    ('Check if typeworld.api holds correct version number', f'python wxPython/build/Mac/build-checkversionnumber.py {version}', True),
    ('Check if can upload to GCS', f'python wxPython/build/Mac/build-canupload.py {version}', True),
    ('Build', f'python wxPython/build/Mac/build-main.py {version}', True),
    ('Upload for notarization', f'python wxPython/build/Mac/build-notarize.py {version}', True),
    ('Wait for notarization', f'python wxPython/build/Mac/build-wait.py {version}', True),
    ('Pack', f'python wxPython/build/Mac/build-pack.py {version}', True),
    ('Check again if can upload to GCS', f'python wxPython/build/Mac/build-canupload.py {version}', True),
    ('Upload', f'python wxPython/build/Mac/build-upload.py {version}', True),
    ('Upload Sparkle signature', f'python wxPython/build/Mac/build-uploadsignature.py {version}', True),
))

    

print('Finished successfully.')
print()