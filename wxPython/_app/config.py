import platform
import sys
import os

WIN = platform.system() == "Windows"
MAC = platform.system() == "Darwin"

# Environment
CI = os.getenv("CI", "false").lower() != "false"

# Mac executable
if "config.py" in __file__ and "/Contents/MacOS/python" in sys.executable:
    DESIGNTIME = False
    RUNTIME = True

elif not "config.py" in __file__:
    DESIGNTIME = False
    RUNTIME = True

else:
    DESIGNTIME = True
    RUNTIME = False

# Preferences
if WIN:
    from appdirs import user_data_dir

    PREFDIR = user_data_dir("Type.World", "Type.World")
    FILEDIR = os.path.join(PREFDIR, "Files")
elif MAC:
    PREFDIR = os.path.expanduser("~/Library/Preferences/")
    FILEDIR = os.path.expanduser("~/Library/Application Support/Type.World/Files")
if not os.path.exists(PREFDIR):
    os.makedirs(PREFDIR)
if not os.path.exists(FILEDIR):
    os.makedirs(FILEDIR)


print("WIN", WIN)
print("MAC", MAC)
print("DESIGNTIME", DESIGNTIME)
print("RUNTIME", RUNTIME)
print("CI", CI)
