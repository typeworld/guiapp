
# This app is called through the custom protocol handlers typeworldgithub:// and typeworldjson:// and distributes the calls back to the main Type.World app.
# I'm using this detour to prevent the app from opening twice (with the nasty elevated permissions dialog)


import os, sys, ctypes

# Adjust __file__ to point to executable on runtime
try:
    __file__ = os.path.abspath(__file__)
except:
    __file__ = sys.executable


# See if we can find the PID in the file system
lockFilePath = os.path.join(os.path.dirname(__file__), '..', 'pid.txt')

if os.path.exists(lockFilePath):
    lockFile = open(lockFilePath, 'r')
    PID = int(lockFile.read().strip())
    lockFile.close()

    # Another PID already exists. See if we can activate it, then exit()
    from pywinauto import Application
    try:
        openURLFilePath = os.path.join(os.path.dirname(__file__), '..', 'url.txt')
        urlFile = open(openURLFilePath, 'w')
        urlFile.write(str(sys.argv[-1]))
        urlFile.close()

        app = Application().connect(process = PID)
        app.top_window().set_focus()

    # That didn't work. Let's execute the main app directly (with elevated privileges)
    except:
        exe = os.path.join(os.path.dirname(__file__), '..', 'TypeWorld.exe')
        ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, '', None, 1)

