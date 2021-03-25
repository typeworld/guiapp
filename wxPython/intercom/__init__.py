# System imports

import threading, time, sys, os, traceback, plistlib
from threading import Thread
import platform
from ynlib.system import Execute

WIN = platform.system() == "Windows"
MAC = platform.system() == "Darwin"

if WIN:
    import ctypes

DEBUG = True
APPVERSION = "n/a"

LOOPDURATION = 60
UPDATESEARCHINTERVAL = 24 * 60 * 60
PULLSERVERUPDATEINTERVAL = 60

# Adjust __file__ to point to executable on runtime
try:
    __file__ = os.path.abspath(__file__)
except:
    __file__ = sys.executable

sys.path.insert(0, os.path.dirname(__file__))

if WIN:
    from appdirs import user_data_dir

    prefDir = user_data_dir("Type.World", "Type.World")
elif MAC:
    prefDir = os.path.expanduser("~/Library/Preferences/")

import logging

if WIN and DEBUG:
    filename = os.path.join(prefDir, os.path.basename(__file__) + ".txt")
    if os.path.exists(filename):
        os.remove(filename)
    logging.basicConfig(filename=filename, level=logging.DEBUG)


def log(message):
    if DEBUG:
        if WIN:
            logging.debug(message)
        if MAC:
            from AppKit import NSLog

            NSLog("Type.World Agent: %s" % message)


try:

    # Application quit locks

    global locks
    locks = 0

    def lock():
        global locks
        locks += 1

    def unlock():
        global locks
        if locks > 0:
            locks -= 1

    def locked():
        global locks
        return locks > 0

    if MAC:
        import objc
        from AppKit import (
            NSObject,
            NSApp,
            NSLog,
            NSApplication,
            NSUserNotification,
            NSUserNotificationCenter,
            NSApplicationActivationPolicyProhibited,
            NSRunningApplication,
            NSApplicationActivateAllWindows,
            NSWorkspace,
            NSImage,
            NSBundle,
        )
    if WIN:
        import pystray._util.win32 as win32
        import win32gui, win32con

    from multiprocessing.connection import Client

    from ynlib.system import Execute

    def getFileProperties(fname):
        """
        Read all properties of the given file return them as a dictionary.
        """
        import win32api

        propNames = (
            "Comments",
            "InternalName",
            "ProductName",
            "CompanyName",
            "LegalCopyright",
            "ProductVersion",
            "FileDescription",
            "LegalTrademarks",
            "PrivateBuild",
            "FileVersion",
            "OriginalFilename",
            "SpecialBuild",
        )

        props = {"FixedFileInfo": None, "StringFileInfo": None, "FileVersion": None}

        try:
            # backslash as parm returns dictionary of numeric info corresponding to VS_FIXEDFILEINFO struc
            fixedInfo = win32api.GetFileVersionInfo(fname, "\\")
            props["FixedFileInfo"] = fixedInfo
            props["FileVersion"] = "%d.%d.%d.%d" % (
                fixedInfo["FileVersionMS"] / 65536,
                fixedInfo["FileVersionMS"] % 65536,
                fixedInfo["FileVersionLS"] / 65536,
                fixedInfo["FileVersionLS"] % 65536,
            )

            # \VarFileInfo\Translation returns list of available (language, codepage)
            # pairs that can be used to retreive string info. We are using only the first pair.
            lang, codepage = win32api.GetFileVersionInfo(
                fname, "\\VarFileInfo\\Translation"
            )[0]

            # any other must be of the form \StringfileInfo\%04X%04X\parm_name, middle
            # two are language/codepage pair returned from above

            strInfo = {}
            for propName in propNames:
                strInfoPath = u"\\StringFileInfo\\%04X%04X\\%s" % (
                    lang,
                    codepage,
                    propName,
                )
                ## print str_info
                strInfo[propName] = win32api.GetFileVersionInfo(fname, strInfoPath)

            props["StringFileInfo"] = strInfo
        except:
            pass

        return props

    def appIsRunning(ID):

        if MAC:
            # App is running, so activate it
            apps = list(
                NSRunningApplication.runningApplicationsWithBundleIdentifier_(ID)
            )

            if apps:
                mainApp = apps[0]
                return True

        if WIN:
            return PID(ID) is not None

    def PID(PROCNAME):
        import psutil

        for proc in psutil.process_iter():
            if proc.name() == PROCNAME and proc.pid != os.getpid():
                return proc.pid

    class IntercomDelegate(object):
        def exitSignalCalled(self, *args):
            pass

    class TypeWorldApp(object):
        def __init__(self, delegate=IntercomDelegate()):
            self.delegate = delegate
            self.communicationInProgress = False

            # Exit Signals
            import signal

            # signal.signal(signal.SIGBREAK, self.delegate.exitSignalCalled)
            signal.signal(signal.SIGTERM, self.delegate.exitSignalCalled)
            signal.signal(signal.SIGINT, self.delegate.exitSignalCalled)

            if WIN:
                """ Testing Windows shutdown events """

                import win32con
                import win32api
                import win32gui
                import sys
                import time

                def wndproc(hwnd, msg, wparam, lparam):

                    log("wndproc: %s" % msg)
                    log("wndproc wparam: %s" % wparam)
                    log("wndproc lparamparam: %s" % lparam)

                    if msg == win32con.WM_QUERYENDSESSION and lparam == 1:
                        self.delegate.exitSignalCalled()
                        return True

                    if msg == win32con.WM_ENDSESSION:
                        self.delegate.exitSignalCalled()
                        return 0

                    if msg == win32con.WM_CLOSE:
                        self.delegate.exitSignalCalled()

                    if msg == win32con.WM_DESTROY:
                        self.delegate.exitSignalCalled()

                    if msg == win32con.WM_QUIT:
                        self.delegate.exitSignalCalled()

                hinst = win32api.GetModuleHandle(None)
                wndclass = win32gui.WNDCLASS()
                wndclass.hInstance = hinst
                wndclass.lpszClassName = "testWindowClass"
                messageMap = {
                    win32con.WM_QUERYENDSESSION: wndproc,
                    win32con.WM_ENDSESSION: wndproc,
                    win32con.WM_QUIT: wndproc,
                    win32con.WM_DESTROY: wndproc,
                    win32con.WM_CLOSE: wndproc,
                }

                wndclass.lpfnWndProc = messageMap

                # try:
                myWindowClass = win32gui.RegisterClass(wndclass)
                hwnd = win32gui.CreateWindowEx(
                    win32con.WS_EX_LEFT,
                    myWindowClass,
                    "testMsgWindow",
                    0,
                    0,
                    0,
                    win32con.CW_USEDEFAULT,
                    win32con.CW_USEDEFAULT,
                    0,  # not win32con.HWND_MESSAGE (see https://stackoverflow.com/questions/1411186/python-windows-shutdown-events)
                    0,
                    hinst,
                    None,
                )
                if hwnd is None:
                    log("hwnd is none!")
                else:
                    log("hwnd: %s" % hwnd)

        def notification(self, text, data-tippy-content=None):

            if MAC:
                notification = NSUserNotification.alloc().init()
                if title:
                    notification.setTitle_(title)
                notification.setInformativeText_(text)
                notificationCenter.deliverNotification_(notification)

            if WIN:
                from win10toast import ToastNotifier

                toaster = ToastNotifier()
                toaster.show_toast(title, text, duration=10)

        def path(self):
            if MAC:
                return str(
                    NSWorkspace.sharedWorkspace().URLForApplicationWithBundleIdentifier_(
                        "world.type.guiapp"
                    )
                )[7:]
            if WIN:
                return os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "TypeWorld.exe")
                )

        def version(self):

            APPVERSION = None

            if MAC:
                plist = plistlib.readPlist(
                    os.path.join(os.path.dirname(__file__), "..", "Info.plist")
                )
                APPVERSION = plist["CFBundleShortVersionString"]

            elif WIN:
                APPVERSION = getFileProperties(__file__)["StringFileInfo"][
                    "ProductVersion"
                ].strip()

                if len(APPVERSION.split(".")) == 4:
                    APPVERSION = ".".join(APPVERSION.split(".")[0:-1])

            return APPVERSION

        def ID(self):
            if WIN:
                return "TypeWorld.exe"
            if MAC:
                return "world.type.guiapp"

        def isOpen(self):
            return appIsRunning(self.ID())

        def speak(self, command):

            self.communicationInProgress = True

            log("app.speak(%s)" % command)

            reply = None

            if self.isOpen():

                log("app is running, connecting to host")

                address = ("localhost", 65500)
                conn = Client(address)
                conn.send(command)
                reply = conn.recv()

                conn.close()

            else:

                log("app is not running")

                if self.path():

                    if WIN:
                        log("about to start app with startListener command")

                        call = '"%s" startListener' % self.path()

                        startListenerThread = Thread(target=execute, args=(call,))
                        startListenerThread.start()

                        log("started app with startListener command")

                        loop = 0
                        while True:

                            if PID("TypeWorld.exe"):
                                break

                            time.sleep(0.5)
                            loop += 1

                        time.sleep(0.5)

                        address = ("localhost", 65500)
                        conn = Client(address)
                        conn.send(command)
                        reply = conn.recv()
                        conn.close()

                        log("received reply after %s loops" % loop)

                        address = ("localhost", 65500)
                        conn = Client(address)
                        conn.send("closeListener")
                        conn.close()

                        log("shut down app with closeListener")

                    if MAC:
                        log("about to start app with %s command" % command)
                        call = '"%s" %s' % (
                            os.path.join(
                                self.path(), "Contents", "MacOS", "Type.World"
                            ),
                            command,
                        )
                        log("call: %s" % call)
                        response = Execute(call).strip()
                        if response:
                            log(response)
                        reply = response

            self.communicationInProgress = False
            return reply

        def open(self):

            log("app.open()")

            while self.communicationInProgress:
                time.sleep(0.5)

            if WIN:

                pid = PID(self.ID())

                if pid:
                    # Another PID already exists. See if we can activate it, then exit()
                    try:
                        import win32com.client

                        shell = win32com.client.Dispatch("WScript.Shell")
                        shell.AppActivate(pid)

                    # That didn't work. Let's execute the main app directly (with elevated privileges)
                    except:
                        exe = os.path.join(os.path.dirname(__file__), "TypeWorld.exe")
                        ctypes.windll.shell32.ShellExecuteW(
                            None, "runas", exe, "", None, 1
                        )

                else:
                    exe = os.path.join(os.path.dirname(__file__), "TypeWorld.exe")
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, "", None, 1)

            if MAC:
                # App is running, so activate it
                apps = list(
                    NSRunningApplication.runningApplicationsWithBundleIdentifier_(
                        self.ID()
                    )
                )
                if apps:
                    mainApp = apps[0]
                    mainApp.activateWithOptions_(1 << 1)

                # Not running, launch it
                else:
                    NSWorkspace.sharedWorkspace().launchAppWithBundleIdentifier_options_additionalEventParamDescriptor_launchIdentifier_(
                        self.ID(), 0, None, None
                    )


except:
    log(traceback.format_exc())

if __name__ == "__main__":
    app = TypeWorldApp()
    app.open()
# 	print('searchAppUpdate', app.speak('searchAppUpdate'))
