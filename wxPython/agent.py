
# This app is called through the custom protocol handlers typeworldgithub:// and typeworldjson:// and distributes the calls back to the main Type.World app.
# I'm using this detour to prevent the app from opening twice (with the nasty elevated permissions dialog)


import os, sys, ctypes

# Adjust __file__ to point to executable on runtime
try:
    __file__ = os.path.abspath(__file__)
except:
    __file__ = sys.executable


from appdirs import user_data_dir
openURLFilePath = os.path.join(user_data_dir('Type.World', 'Type.World'), 'url.txt')
urlFile = open(openURLFilePath, 'w')
urlFile.write(str(sys.argv[-1]))
urlFile.close()


def PID():
    import psutil
    PROCNAME = "TypeWorld.exe"
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME and proc.pid != os.getpid():
            return proc.pid

pid = PID()

if pid:

    # Another PID already exists. See if we can activate it, then exit()
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.AppActivate(pid)

    # That didn't work. Let's execute the main app directly (with elevated privileges)
    except:
        exe = os.path.join(os.path.dirname(__file__), 'TypeWorld.exe')
        ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, '', None, 1)


else:
    exe = os.path.join(os.path.dirname(__file__), 'TypeWorld.exe')
    ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, '', None, 1)

