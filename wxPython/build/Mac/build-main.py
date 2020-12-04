import os, sys
from subprocess import Popen, PIPE, STDOUT

# List of commands as tuples of:
# - Description
# - Actual command
# - True if this command is essential to the build process (must exit with 0), otherwise False

version = sys.argv[-1]

sparkle = "sparkle/Sparkle.framework"
sitePackages = os.getenv("SITEPACKAGES")

profile = ["normal", "sign"]  # normal/sign/agent

import zmq

print(f"build-main.py {zmq.zmq_version()} {zmq.pyzmq_version()}")


def execute(command):
    out = Popen(command, stderr=STDOUT, stdout=PIPE, shell=True)
    output, exitcode = out.communicate()[0].decode(), out.returncode
    return output, exitcode


def executeCommands(commands, printOutput=False, returnOutput=False):
    for description, command, mustSucceed in commands:

        # Print which step we’re currently in
        print(description, "...")

        # Execute the command, fetch both its output as well as its exit code
        out = Popen(command, stderr=STDOUT, stdout=PIPE, shell=True)
        output, exitcode = out.communicate()[0].decode(), out.returncode

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
        elif returnOutput:
            return output
        elif printOutput:
            print(output)


def signApp(path, bundleType="app"):

    # Delete symlinks
    symlinks, code = execute('find -L "%s" -type l' % path)
    symlinks = symlinks.split("\n")
    # print(symlinks)
    for filepath in symlinks:
        if filepath:
            os.remove(filepath)
            print("Deleted symlink %s" % filepath)

    import mimetypes

    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)

            # if 'docktileplugin' in filepath:
            # 	print('... ', filepath)

            if (
                mimetypes.guess_type(filepath)[0] == "application/octet-stream"
                or filename == "python"
                or filename.endswith(".dylib")
            ):
                # or filename == 'plugin' \

                command = (
                    "Signing %s" % filename,
                    'codesign --options runtime -s "Jan Gerner" --deep --timestamp --entitlements "wxPython/build/Mac/entitlements.plist" -f "%s"'
                    % filepath,
                    True,
                )
                executeCommands([command])

        if dirpath.endswith(".framework"):
            command = (
                "Signing %s" % dirpath,
                'codesign --options runtime -s "Jan Gerner" --deep --timestamp --entitlements "wxPython/build/Mac/entitlements.plist" -f "%s"'
                % dirpath,
                True,
            )
            executeCommands([command])

    commands = (
        (
            "Signing Outer App",
            'codesign --options runtime --deep -s "Jan Gerner" --timestamp --entitlements "wxPython/build/Mac/entitlements.plist" -f "%s"'
            % path,
            bundleType in ["app", "plugin"],
        ),
        (
            "Verify signature",
            'codesign -dv --verbose=4 "%s"' % path,
            bundleType in ["app", "plugin"],
        ),
        (
            "Verify signature",
            'codesign --verify --deep --strict --verbose=20 "%s"' % path,
            bundleType in ["app", "plugin"],
        ),
        (
            "Verify signature",
            'spctl -a -t exec -vvvv "%s"' % path,
            bundleType in ["app"],
        ),
    )
    executeCommands(commands)


if "agent" in profile:
    executeCommands(
        (("Agent build", "python wxPython/build/Mac/setup_daemon.py py2app", True),)
    )

    if "sign" in profile:
        signApp("dist/Type.World Agent.app")

    executeCommands(
        (
            (
                "Zipping agent",
                'tar -cjf dist/agent.tar.bz2 -C "dist/" "Type.World Agent.app"',
                True,
            ),
        )
    )

executeCommands(
    (
        ("Main App build", "python wxPython/build/Mac/setup.py py2app", True),
        (
            "Copying Sparkle",
            "cp -R sparkle/Sparkle.framework dist/Type.World.app/Contents/Frameworks/",
            True,
        ),
    )
)

os.remove("dist/Type.World.app/Contents/Frameworks/liblzma.5.dylib")

if "sign" in profile:
    signApp(
        "dist/Type.World.app/Contents/Frameworks/Sparkle.framework/Versions/A/Resources/Autoupdate.app"
    )

if "agent" in profile:
    executeCommands(
        (
            (
                "Copying agent",
                "cp dist/agent.tar.bz2 dist/Type.World.app/Contents/Resources/",
                True,
            ),
        )
    )

# executeCommands(
#     (
#         (
#             "Copying google",
#             f"cp -R {sitePackages}/google dist/Type.World.app/Contents/Resources/lib/python3.7",
#             True,
#         ),
#         (
#             "Copying google-api-core",
#             f"cp -R {sitePackages}/google_api_core-*.pth dist/Type.World.app/Contents/Resources/lib/python3.7",
#             True,
#         ),
#         (
#             "Copying google-api-core",
#             f"cp -R {sitePackages}/google_api_core-*.dist-info dist/Type.World.app/Contents/Resources/lib/python3.7",
#             True,
#         ),
#         (
#             "Copying google-cloud-pubsub",
#             f"cp -R {sitePackages}/google_cloud_pubsub-*.pth dist/Type.World.app/Contents/Resources/lib/python3.7",
#             True,
#         ),
#         (
#             "Copying google-cloud-pubsub",
#             f"cp -R {sitePackages}/google_cloud_pubsub-*.dist-info dist/Type.World.app/Contents/Resources/lib/python3.7",
#             True,
#         ),
#     )
# )

executeCommands(
    (
        # 	('Moving ynlib', 'mv ynlib/Lib/ynlib dist/Type.World.app/Contents/Resources/lib/python3.7/', True),
        (
            "Moving ynlib",
            "mv ynlib/Lib/ynlib dist/Type.World.app/Contents/Resources/lib/python3.7/",
            True,
        ),
        (
            "Remove ynlib.pdf",
            "rm -r dist/Type.World.app/Contents/Resources/lib/python3.7/ynlib/pdf",
            True,
        ),
    )
)

# executeCommands((
# 	('ynlib', 'ls -la dist/Type.World.app/Contents/Resources/lib/python3.7/', True),
# 	('ynlib', 'ls -la dist/Type.World.app/Contents/Resources/lib/python3.7/ynlib/', True),
# ), printOutput=True)

if "normal" in profile:

    # CTYPES error
    # https://github.com/powerline/powerline/issues/1947
    path = "dist/Type.World.app/Contents/Resources/lib/python3.7/ctypes/__init__.py"
    code = open(path).read()
    code = code.replace(
        "CFUNCTYPE(c_int)(lambda: None)", "#CFUNCTYPE(c_int)(lambda: None)"
    )
    f = open(path, "w")
    f.write(code)
    f.close()

    executeCommands(
        (
            (
                "Extract compressed Python",
                "ditto -x -k dist/Type.World.app/Contents/Resources/lib/python37.zip "
                + os.path.expanduser("~")
                + "/Desktop/zip",
                True,
            ),
        )
    )

    if "sign" in profile:
        signApp(os.path.expanduser("~") + "/Desktop/zip", bundleType="zip")

    executeCommands(
        (
            (
                "Re-compress Python",
                "ditto -c -k --sequesterRsrc --keepParent "
                + os.path.expanduser("~")
                + "/Desktop/zip dist/Type.World.app/Contents/Resources/lib/python37.zip",
                True,
            ),
            (
                "Delete zip folder",
                "rm -r " + os.path.expanduser("~") + "/Desktop/zip",
                True,
            ),
        )
    )

    if "sign" in profile:
        signApp("dist/Type.World.app")

    executeCommands(
        (("Self Test", "dist/Type.World.app/Contents/MacOS/Type.World selftest", True),)
    )


if not "sign" in profile:
    print(f"WARNING: Apps aren’t signed (profile: {profile})")

print("Finished successfully.")
print()
