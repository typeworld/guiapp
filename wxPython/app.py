#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys

# import faulthandler

# Adjust __file__ for Windows executable
try:
    __file__ = os.path.abspath(__file__)

except:
    __file__ = sys.executable

sys.path.insert(0, os.path.dirname(__file__))

# Environment
CI = os.getenv("CI", "false").lower() != "false"

# Mac executable
if "app.py" in __file__ and "/Contents/MacOS/python" in sys.executable:
    DESIGNTIME = False
    RUNTIME = True

elif not "app.py" in __file__:
    DESIGNTIME = False
    RUNTIME = True

else:
    DESIGNTIME = True
    RUNTIME = False

import wx, webbrowser, urllib.request, urllib.parse, urllib.error, base64, plistlib, json, datetime, traceback, semver, platform, logging, time
from threading import Thread
import threading
import wx.html2
import locales

import urllib.request, urllib.parse, urllib.error, time
from functools import partial
from wx.lib.delayedresult import startWorker
from multiprocessing.connection import Client
from threading import Thread
from string import Template

WIN = platform.system() == "Windows"
MAC = platform.system() == "Darwin"

from ynlib.files import ReadFromFile, WriteToFile
from ynlib.strings import *
from ynlib.web import GetHTTP
from ynlib.colors import Color

from typeworld.client import (
    APIClient,
    JSON,
    AppKitNSUserDefaults,
    TypeWorldClientDelegate,
    URL,
)
import typeworld.api

APPNAME = "Type.World"
APPVERSION = "n/a"
DEBUG = False
BUILDSTAGE = "beta"
PULLSERVERUPDATEINTERVAL = 60

# Is Online Helper Function
import socket


def internet(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False


if WIN:

    # Set DEBUG in Windows
    import winreg as wreg

    try:
        key = wreg.OpenKey(
            wreg.HKEY_CURRENT_USER, "Software\\Type.World\\Type.World", 0, wreg.KEY_READ
        )
        value, regtype = wreg.QueryValueEx(key, "debug")
        wreg.CloseKey(key)
    except:
        value = False
    if value == "true":
        DEBUG = True

    # Redirect stderr & stdout
    if sys.stdout is None:

        class dummyStream:
            def __init__(self):
                pass

            def write(self, data):
                pass

            def read(self, data):
                pass

            def flush(self):
                pass

            def close(self):
                pass

        # and now redirect all default streams to this dummyStream:
        sys.stdout = dummyStream()
        sys.stderr = dummyStream()
        sys.stdin = dummyStream()
        sys.__stdout__ = dummyStream()
        sys.__stderr__ = dummyStream()
        sys.__stdin__ = dummyStream()

global app
app = None
# faulthandler.enable()


if MAC:
    import objc

    # NSApplication = objc.lookUpClass("NSApplication")
    from AppKit import NSApp
    from AppKit import (
        NSObject,
        NSUserNotification,
        NSUserNotificationCenter,
        NSDistributedNotificationCenter,
    )
    from AppKit import NSView, NSToolbar
    from Foundation import NSPoint, NSSize, NSMakeRect, NSURL

    # NSPoint = objc.lookUpClass("NSPoint")
    # NSSize = objc.lookUpClass("NSSize")
    # NSMakeRect = objc.lookUpClass("NSMakeRect")
    from AppKit import NSRunningApplication
    from AppKit import NSScreen
    from AppKit import NSUserDefaults

    NSUserNotificationCenterDelegate = objc.protocolNamed(
        "NSUserNotificationCenterDelegate"
    )

    class NotificationDelegate(NSObject, protocols=[NSUserNotificationCenterDelegate]):
        def userNotificationCenter_didActivateNotification_(
            self, center, aNotification
        ):
            pass

    if not CI:
        userNotificationCenter = (
            NSUserNotificationCenter.defaultUserNotificationCenter()
        )
        userNotificationCenterDelegate = NotificationDelegate.alloc().init()
        userNotificationCenter.setDelegate_(userNotificationCenterDelegate)

    # Dark Mode
    class DarkModeDelegate(NSObject):
        def darkModeChanged_(self, sender):
            self.app.applyDarkMode()


if WIN:
    from appdirs import user_data_dir

    prefDir = user_data_dir("Type.World", "Type.World")
elif MAC:
    prefDir = os.path.expanduser("~/Library/Preferences/")


# Set up logging
if WIN and DEBUG:
    filename = os.path.join(prefDir, os.path.basename(__file__) + ".txt")
    if os.path.exists(filename):
        os.remove(filename)
    logging.basicConfig(filename=filename, level=logging.DEBUG)


# print ('__file__', __file__)
# print ('sys.executable ', sys.executable )

## Windows:
## Register Custom Protocol Handlers in the Registry. TODO: Later, this should be moved into the installer.

if WIN and RUNTIME:
    try:
        import winreg as wreg

        for handler in ["typeworld", "typeworldapp"]:
            key = wreg.CreateKey(wreg.HKEY_CLASSES_ROOT, handler)
            wreg.SetValueEx(key, None, 0, wreg.REG_SZ, "URL:%s" % handler)
            wreg.SetValueEx(key, "URL Protocol", 0, wreg.REG_SZ, "")
            key = wreg.CreateKey(key, "shell\\open\\command")
            wreg.SetValueEx(
                key,
                None,
                0,
                wreg.REG_SZ,
                '"%s" "%%1"'
                % os.path.join(
                    os.path.dirname(__file__), "TypeWorld Subscription Opener.exe"
                ),
            )
    except:
        pass


import sys, os, traceback, types


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


## Windows:
## Open other app instance if open


def PID(ID):
    import psutil

    PROCNAME = ID
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME and proc.pid != os.getpid():
            return proc.pid


def appIsRunning(ID):

    if MAC:
        # App is running, so activate it
        apps = list(NSRunningApplication.runningApplicationsWithBundleIdentifier_(ID))

        if apps:
            mainApp = apps[0]
            return True

    if WIN:
        return PID(ID) is not None


def notification(title, text):
    if MAC:
        notification = NSUserNotification.alloc().init()
        notification.setTitle_(title)
        notification.setInformativeText_(text)
        userNotificationCenter.deliverNotification_(notification)

    if WIN:

        import zroya

        zroya.init("Type.World", "Type.World", "Type.World", "guiapp", "Version")
        template = zroya.Template(zroya.TemplateType.ImageAndText4)
        template.setFirstLine(title)
        template.setSecondLine(text)
        expiration = 24 * 60 * 60 * 1000  # one day
        template.setExpiration(expiration)  # One day
        notificationID = zroya.show(template)  # , on_action=onAction


def subscriptionsUpdatedNotification(message):
    if type(message) == int:
        if message > 0:
            notification(
                localizeString("#(Subscriptions added)"),
                localizeString(
                    "#(SubscriptionAddedLongText)", replace={"number": abs(message)}
                ),
            )
        if message < 0:
            notification(
                localizeString("#(Subscriptions removed)"),
                localizeString(
                    "#(SubscriptionRemovedLongText)", replace={"number": abs(message)}
                ),
            )


# Read app version number


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
            strInfoPath = "\\StringFileInfo\\%04X%04X\\%s" % (lang, codepage, propName)
            ## print str_info
            strInfo[propName] = win32api.GetFileVersionInfo(fname, strInfoPath)

        props["StringFileInfo"] = strInfo
    except:
        pass

    return props


if DESIGNTIME:
    APPVERSION = typeworld.api.VERSION

elif RUNTIME:

    if MAC:
        try:
            with open(
                os.path.join(os.path.dirname(__file__), "..", "Info.plist"), "rb"
            ) as f:
                plist = plistlib.load(f)
                APPVERSION = plist["CFBundleShortVersionString"]
        except:
            pass

    elif WIN:
        APPVERSION = getFileProperties(__file__)["StringFileInfo"][
            "ProductVersion"
        ].strip()

        if len(APPVERSION.split(".")) == 4:
            APPVERSION = ".".join(APPVERSION.split(".")[0:-1])

        if BUILDSTAGE:
            APPVERSION += "-" + BUILDSTAGE


class ClientDelegate(TypeWorldClientDelegate):
    def fontWillInstall(self, font):
        # print('fontWillInstall', font)
        assert type(font) == typeworld.api.Font

    def fontHasInstalled(self, success, message, font):
        # print('fontHasInstalled', success, message, font)
        assert type(font) == typeworld.api.Font

    def fontWillUninstall(self, font):
        # print('fontWillUninstall', font)
        assert type(font) == typeworld.api.Font

    def fontHasUninstalled(self, success, message, font):
        # print('fontHasUninstalled', success, message, font)
        assert type(font) == typeworld.api.Font

    def userAccountUpdateNotificationHasBeenReceived(self):
        # print("userAccountUpdateNotificationHasBeenReceived()")
        self.app.frame.pullServerUpdates(force=True)

    def userAccountHasBeenUpdated(self):
        if self.app.frame.panelVisible == "preferences(userAccount)":
            self.app.frame.threadSafeExec('self.onPreferences(None, "userAccount")')

    def subscriptionHasBeenDeleted(self, subscription):
        # print("subscriptionHasBeenDeleted(%s)" % subscription)
        self.app.frame.setSideBarHTML()

    def publisherHasBeenDeleted(self, publisher):
        # print("publisherHasBeenDeleted(%s)" % publisher)
        if client.get("currentPublisher"):
            if not client.publishers():
                client.set("currentPublisher", "")
                # print("currentPublisher reset")
        self.app.frame.setSideBarHTML()

    def subscriptionHasBeenAdded(self, subscription):
        if not client.get("currentPublisher"):
            self.app.frame.setPublisherHTML(
                self.app.frame.b64encode(subscription.parent.canonicalURL)
            )

    def subscriptionWillUpdate(self, subscription):
        b64publisherID = self.app.frame.b64encode(subscription.parent.canonicalURL)
        b64subscriptionID = self.app.frame.b64encode(
            subscription.protocol.unsecretURL()
        )

        # Publisher
        self.app.frame.javaScript(
            "$('#sidebar #%s.publisher .reloadAnimation').show();" % b64publisherID
        )
        self.app.frame.javaScript(
            "$('#sidebar #%s.publisher .badges').hide();" % b64publisherID
        )

        # Subscription
        self.app.frame.javaScript(
            "$('#sidebar #%s.subscription .reloadAnimation').show();"
            % b64subscriptionID
        )
        self.app.frame.javaScript(
            "$('#sidebar #%s.subscription .badges').hide();" % b64subscriptionID
        )

    def subscriptionHasBeenUpdated(self, subscription, success, message, changes):
        b64publisherID = self.app.frame.b64encode(subscription.parent.canonicalURL)
        b64subscriptionID = self.app.frame.b64encode(
            subscription.protocol.unsecretURL()
        )

        if success:
            if client.get("currentPublisher") == subscription.parent.canonicalURL:
                self.app.frame.setPublisherHTML(
                    self.app.frame.b64encode(subscription.parent.canonicalURL)
                )
            self.app.frame.setSideBarHTML()

            # Hide alert
            self.app.frame.javaScript(
                "$('#sidebar #%s .alert').hide();" % b64publisherID
            )
            self.app.frame.javaScript(
                "$('#sidebar #%s .alert').hide();" % b64subscriptionID
            )

        else:
            # Show alert
            # 				if subscription.updatingProblem():
            self.app.frame.javaScript(
                "$('#sidebar #%s .alert').show();" % b64publisherID
            )
            self.app.frame.javaScript(
                "$('#sidebar #%s .alert ').show();" % b64subscriptionID
            )

        # Subscription
        self.app.frame.javaScript(
            f"""
            $('#sidebar #{b64subscriptionID}.subscription .reloadAnimation').hide();
            $('#sidebar #{b64subscriptionID}.subscription .badges').show();
            """
        )

        if subscription.parent.stillUpdating() == False:
            # Publisher
            self.app.frame.javaScript(
                f"""
                $('#sidebar #{b64publisherID}.publisher .reloadAnimation').hide();
                $('#sidebar #{b64publisherID}.publisher .badges').show();
                """
            )

        if client.allSubscriptionsUpdated():
            client.set("reloadSubscriptionsLastPerformed", int(time.time()))
            client.log("Reset reloadSubscriptionsLastPerformed")

        agent("amountOutdatedFonts %s" % client.amountOutdatedFonts())

    def clientPreferenceChanged(self, key, value):
        if key == "appUpdateProfile":
            self.app.frame.setAppCastURL()


delegate = ClientDelegate()
client = None  # set in startApp()


###########################################################################################################################################################################################################
###########################################################################################################################################################################################################
###########################################################################################################################################################################################################


class FoundryStyling(object):
    def __init__(self, foundry, theme):
        self.foundry = foundry
        self.theme = theme

        assert self.theme in ("light", "dark")

        # Apply default colors
        colors = typeworld.api.StylingDataType().exampleData()[self.theme]
        for key in colors:
            if "Color" in key:
                setattr(self, key, Color(hex=colors[key]))

        # Apply custom colors
        if self.foundry.styling:
            if self.theme in self.foundry.styling:
                colors = self.foundry.styling[self.theme]
                for key in colors:
                    if "Color" in key:
                        setattr(self, key, Color(hex=colors[key]))

        self.logoURL = None

        # Additionally calculated colors
        self.hoverColor = None
        self.hoverButtonColor = None
        self.hoverButtonTextColor = None
        self.selectionHoverColor = None
        self.selectionButtonColor = None
        self.selectionButtonTextColor = None
        self.selectionInactiveTextColor = None
        self.inactiveButtonColor = None
        self.inactiveButtonTextColor = None
        self.informationViewInactiveButtonColor = None
        self.informationViewInactiveButtonTextColor = None
        self.sectionTitleColor = None

        # Automatic adjustments

        # Hover Color
        if self.backgroundColor.darkHalf():
            self.hoverColor = self.backgroundColor.lighten(0.05)
            self.hoverButtonColor = self.hoverColor.lighten(0.1)
            self.hoverButtonTextColor = self.hoverColor.lighten(0.8)
            self.sectionTitleColor = self.backgroundColor.lighten(0.4)
        else:
            self.hoverColor = self.backgroundColor.darken(0.05)
            self.hoverButtonColor = self.hoverColor.darken(0.1)
            self.hoverButtonTextColor = self.hoverColor.darken(0.8)
            self.sectionTitleColor = self.backgroundColor.darken(0.4)

        # Selection Hover Color
        if self.selectionColor.darkHalf():
            self.selectionHoverColor = self.selectionColor.lighten(0.1)
            self.selectionInactiveTextColor = self.selectionColor.lighten(0.3)
        else:
            self.selectionHoverColor = self.selectionColor.darken(0.1)
            self.selectionInactiveTextColor = self.selectionColor.darken(0.3)

        # Selection Button Color
        if self.selectionColor.darkHalf():
            self.selectionButtonColor = self.selectionHoverColor.lighten(0.1)
            self.selectionButtonTextColor = self.selectionButtonColor.lighten(0.8)
        else:
            self.selectionButtonColor = self.selectionHoverColor.darken(0.1)
            self.selectionButtonTextColor = self.selectionButtonColor.darken(0.8)

        # Inactive Button Color
        if self.backgroundColor.darkHalf():
            self.inactiveButtonColor = self.backgroundColor.lighten(0.15)
            self.inactiveButtonTextColor = self.inactiveButtonColor.lighten(0.2)
        else:
            self.inactiveButtonColor = self.backgroundColor.darken(0.15)
            self.inactiveButtonTextColor = self.inactiveButtonColor.darken(0.2)

        # Information View Inactive Button Color
        if self.informationViewBackgroundColor.darkHalf():
            self.informationViewInactiveButtonColor = (
                self.informationViewBackgroundColor.lighten(0.15)
            )
            self.informationViewInactiveButtonTextColor = (
                self.informationViewInactiveButtonColor.lighten(0.2)
            )
        else:
            self.informationViewInactiveButtonColor = (
                self.informationViewBackgroundColor.darken(0.15)
            )
            self.informationViewInactiveButtonTextColor = (
                self.informationViewInactiveButtonColor.darken(0.2)
            )

        if self.informationViewLinkColor.darkHalf():
            self.informationViewLinkColor_Darker = (
                self.informationViewLinkColor.lighten(0.15)
            )
        else:
            self.informationViewLinkColor_Darker = self.informationViewLinkColor.darken(
                0.15
            )

    def logo(self):

        if self.foundry.styling:
            if self.theme in self.foundry.styling:
                if "logoURL" in self.foundry.styling[self.theme]:
                    self.logoURL = self.foundry.styling[self.theme]["logoURL"]

            # Fallback, take any
            if not self.logoURL:
                for themeName in self.foundry.styling:
                    if "logoURL" in self.foundry.styling[themeName]:
                        self.logoURL = self.foundry.styling[themeName]["logoURL"]

            return self.logoURL

    def foundryView(self, ID):

        tpl = Template(
            """<style>

#$ID.foundry .head {
background-color: #$headerColor;
color: #$headerTextColor;
}

#$ID.foundry .head a {
color: #$headerLinkColor;
}

#$ID.foundry {
background-color: #$backgroundColor;
color: #$textColor;
}

#$ID.foundry a {
color: #$linkColor;
}

#$ID.foundry .font.selected {
background-color: #$selectionColor;
color: #$selectionTextColor;
}

#$ID.foundry .font .inactive {
color: #$sectionTitleColor;
}

#$ID.foundry .font.selected .inactive {
color: #$selectionInactiveTextColor;
}

#$ID.foundry .font.selected a.button, #$ID.foundry .font.selected.hover a.button {
background-color: #$selectionButtonColor;
color: #$selectionButtonTextColor;
}

#$ID.foundry a.button {
background-color: #$buttonColor;
color: #$buttonTextColor;
}

#$ID.foundry a.button.inactive {
background-color: #$inactiveButtonColor;
color: #$inactiveButtonTextColor;
}

#$ID.foundry .font.hover, #$ID.foundry .section.hover {
background-color: #$hoverColor;
}

#$ID.foundry .section .title .name {
color: #$sectionTitleColor;
}

#$ID.foundry .font.hover.selected {
background-color: #$selectionHoverColor;
}

#$ID.foundry .font.hover a.button {
background-color: #$hoverButtonColor;
color: #$hoverButtonTextColor;
}

                </style>"""
        )

        r = {"ID": ID}
        for key in self.__dict__:
            if "Color" in key:
                r[key] = getattr(self, key).hex

        css = tpl.safe_substitute(r)
        return css

    def informationView(self):

        tpl = Template(
            """<style>

#metadataWrapper {
background-color: #$informationViewBackgroundColor;
color: #$informationViewTextColor;
}

#metadataWrapper a {
color: #$informationViewLinkColor;
}

#metadataWrapper a.button {
background-color: #$informationViewButtonColor;
color: #$informationViewButtonTextColor !important;
}

#metadataWrapper a.button.inactive {
background-color: #$informationViewInactiveButtonColor;
color: #$informationViewInactiveButtonTextColor;
}



</style>"""
        )

        # #metadataWrapper svg path {
        # 	fill: #$informationViewLinkColor;
        # }

        r = {}
        for key in self.__dict__:
            if "Color" in key:
                r[key] = getattr(self, key).hex

        css = tpl.safe_substitute(r)
        return css


# ''' + str(self.selectionHoverColor.hex) + '''


def agent(command):
    try:

        if agentIsRunning():
            try:
                address = ("localhost", 65501)
                myConn = Client(address)
                myConn.send(command)
                response = myConn.recv()
                myConn.close()

                return response
            except:
                pass

    except:
        client.handleTraceback(sourceMethod=globals()[sys._getframe().f_code.co_name])


def agentIsRunning():

    try:
        if MAC:
            from AppKit import NSRunningApplication

            # Kill running app
            ID = "world.type.agent"
            # App is running, so activate it
            apps = list(
                NSRunningApplication.runningApplicationsWithBundleIdentifier_(ID)
            )
            if apps:
                mainApp = apps[0]
                return True

        if WIN:
            return PID("TypeWorld Taskbar Agent.exe") is not None

    except:
        client.handleTraceback(sourceMethod=globals()[sys._getframe().f_code.co_name])


def waitToLaunchAgent():

    try:
        time.sleep(2)

        if MAC:
            agentPath = os.path.expanduser(
                "~/Library/Application Support/Type.World/Type.World Agent.app"
            )
            os.system(
                '"%s" &'
                % os.path.join(agentPath, "Contents", "MacOS", "Type.World Agent")
            )

            unlock()

            # import subprocess
            # subprocess.Popen(['"%s"' % os.path.join(agentPath, 'Contents', 'MacOS', 'Type.World Agent')])
    #
    except:
        client.handleTraceback(sourceMethod=globals()[sys._getframe().f_code.co_name])


def restartAgentWorker(wait):
    try:
        if wait:
            time.sleep(wait)
        uninstallAgent()
        installAgent()

        client.log("Agent restarted")
    except:
        client.handleTraceback(sourceMethod=globals()[sys._getframe().f_code.co_name])


def restartAgent(wait=0):
    try:
        restartAgentThread = Thread(target=restartAgentWorker, args=(wait,))
        restartAgentThread.start()
    except:
        client.handleTraceback(sourceMethod=globals()[sys._getframe().f_code.co_name])


def installAgent():
    try:
        # 	uninstallAgent()

        if RUNTIME:

            try:
                if MAC:

                    if not appIsRunning("world.type.agent"):

                        lock()
                        client.log("lock() from within installAgent()")

                        from AppKit import NSBundle

                        zipPath = NSBundle.mainBundle().pathForResource_ofType_(
                            "agent", "tar.bz2"
                        )
                        plistPath = os.path.expanduser(
                            "~/Library/LaunchAgents/world.type.agent.plist"
                        )
                        agentPath = os.path.expanduser(
                            "~/Library/Application Support/Type.World/Type.World Agent.app"
                        )
                        plist = (
                            """<?xml version="1.0" encoding="UTF-8"?>
                <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
                <plist version="1.0">
                <dict>
                <key>Debug</key>
                <true/>
                <key>Disabled</key>
                <false/>
                <key>KeepAlive</key>
                <true/>
                <key>Label</key>
                <string>world.type.agent</string>
                <key>MachServices</key>
                <dict>
                    <key>world.type.agent</key>
                    <true/>
                </dict>
                <key>OnDemand</key>
                <false/>
                <key>Program</key>
                <string>"""
                            + agentPath
                            + """/Contents/MacOS/Type.World Agent</string>
                <key>RunAtLoad</key>
                <true/>
                </dict>
                </plist>"""
                        )

                        # Extract app
                        folder = os.path.dirname(agentPath)
                        if not os.path.exists(folder):
                            os.makedirs(folder)
                        os.system('tar -zxf "%s" -C "%s"' % (zipPath, folder))

                        # Write Launch Agent
                        if not os.path.exists(os.path.dirname(plistPath)):
                            os.makedirs(os.path.dirname(plistPath))
                        f = open(plistPath, "w")
                        f.write(plist)
                        f.close()

                        # Run App
                        # 		if platform.mac_ver()[0].split('.') < '10.14.0'.split('.'):
                        # import subprocess
                        # subprocess.Popen(['"%s"' % os.path.join(agentPath, 'Contents', 'MacOS', 'Type.World Agent')])
                        # 		os.system('"%s" &' % os.path.join(agentPath, 'Contents', 'MacOS', 'Type.World Agent'))

                        launchAgentThread = Thread(target=waitToLaunchAgent)
                        launchAgentThread.start()

                if WIN:

                    if not appIsRunning("TypeWorld Taskbar Agent.exe"):

                        lock()
                        client.log("lock() from within installAgent()")

                        # 			file_path = os.path.join(os.path.dirname(__file__), r'TypeWorld Taskbar Agent.exe')
                        file_path = os.path.join(
                            os.path.dirname(__file__), r"TypeWorld Taskbar Agent.exe"
                        )
                        file_path = file_path.replace(r"\\Mac\Home", "Z:")
                        client.log(file_path)

                        import getpass

                        USER_NAME = getpass.getuser()

                        bat_path = (
                            r"C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
                            % USER_NAME
                        )
                        bat_command = 'start "" "%s"' % file_path

                        from pathlib import Path

                        client.log(Path(file_path).exists())
                        client.log(os.path.exists(file_path))

                        if not os.path.exists(os.path.dirname(bat_path)):
                            os.makedirs(os.path.dirname(bat_path))
                        with open(bat_path + "\\" + "TypeWorld.bat", "w+") as bat_file:
                            bat_file.write(bat_command)

                        import subprocess

                        os.chdir(os.path.dirname(file_path))
                        subprocess.Popen([file_path], executable=file_path)

                client.set("menuBarIcon", True)

                client.log("installAgent() done")

            except:
                client.log(traceback.format_exc())

                unlock()
                client.log("unlock() from within installAgent() after traceback")

    except:
        client.handleTraceback(sourceMethod=globals()[sys._getframe().f_code.co_name])


def uninstallAgent():
    try:

        lock()
        client.log("lock() from within uninstallAgent()")
        if MAC:

            plistPath = os.path.expanduser(
                "~/Library/LaunchAgents/world.type.agent.plist"
            )
            agentPath = os.path.expanduser(
                "~/Library/Application Support/Type.World/Type.World Agent.app"
            )

            # Kill running app
            ID = "world.type.agent"
            # App is running, so activate it
            apps = list(
                NSRunningApplication.runningApplicationsWithBundleIdentifier_(ID)
            )
            if apps:
                mainApp = apps[0]
                mainApp.terminate()

            # delete app bundle
            if os.path.exists(agentPath):
                os.system('rm -r "%s"' % agentPath)

            # delete plist
            if os.path.exists(plistPath):
                os.system('rm "%s"' % plistPath)

        if WIN:

            agent("quit")

            import getpass

            USER_NAME = getpass.getuser()

            bat_path = (
                r"C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\TypeWorld.bat"
                % USER_NAME
            )
            if os.path.exists(bat_path):
                os.remove(bat_path)

        client.set("menuBarIcon", False)

        unlock()
        client.log("unlock() from within uninstallAgent()")
    except:
        client.handleTraceback(sourceMethod=globals()[sys._getframe().f_code.co_name])


def localizeString(string, html=False, replace={}):
    try:
        string = locales.localizeString(string, languages=client.locale(), html=html)
        if replace:
            for key in replace:
                string = string.replace("%" + key + "%", str(replace[key]))

        if html:
            # string = string.replace("\n", "")
            string = string.replace("<br /></p>", "</p>")
            string = string.replace("<p><br />", "<p>")
        return string

    except:
        client.handleTraceback(sourceMethod=globals()[sys._getframe().f_code.co_name])


# Sparkle Updating

if MAC and RUNTIME:
    # Path to Sparkle's "Sparkle.framework" inside your app bundle

    if ".app" in os.path.dirname(__file__):
        SPARKLE_PATH = os.path.join(
            os.path.dirname(__file__), "..", "Frameworks", "Sparkle.framework"
        )
    else:
        SPARKLE_PATH = "/Users/yanone/Code/Sparkle/Sparkle.framework"

    from objc import pathForFramework, loadBundle

    sparkle_path = pathForFramework(SPARKLE_PATH)
    objc_namespace = dict()
    loadBundle("Sparkle", objc_namespace, bundle_path=sparkle_path)

    sparkle = objc_namespace["SUUpdater"].sharedUpdater()

    def waitForUpdateToFinish(app, updater, delegate):

        client.log("Waiting for update loop to finish")

        while updater.updateInProgress():
            time.sleep(1)

        client.log("Update loop finished")

        if delegate.downloadStarted == False:
            delegate.destroyIfRemotelyCalled()

    from AppKit import NSObject

    class SparkleUpdateDelegate(NSObject):
        def destroyIfRemotelyCalled(self):
            client.log("Quitting because app was called remotely for an update")
            global app
            if app.startWithCommand:
                if app.startWithCommand == "checkForUpdateInformation":
                    app.frame.Destroy()
                    client.log("app.frame.Destroy()")

        def updater_didAbortWithError_(self, updater, error):
            client.log("sparkleUpdateDelegate.updater_didAbortWithError_()")
            client.log(error)
            self.destroyIfRemotelyCalled()

        def userDidCancelDownload_(self, updater):
            client.log("sparkleUpdateDelegate.userDidCancelDownload_()")
            self.destroyIfRemotelyCalled()

        def updater_didFindValidUpdate_(self, updater, appcastItem):

            self.updateFound = True
            self.downloadStarted = False

            global app
            waitForUpdateThread = Thread(
                target=waitForUpdateToFinish, args=(app, updater, self)
            )
            waitForUpdateThread.start()

            client.log("sparkleUpdateDelegate.updater_didFindValidUpdate_() finished")

        def updaterDidNotFindUpdate_(self, updater):
            client.log("sparkleUpdateDelegate.updaterDidNotFindUpdate_()")
            self.updateFound = False
            self.destroyIfRemotelyCalled()

        # Not so important
        def updater_didFinishLoadingAppcast_(self, updater, appcast):
            client.log("sparkleUpdateDelegate.updater_didFinishLoadingAppcast_()")

        def bestValidUpdateInAppcast_forUpdater_(self, appcast, updater):
            client.log("sparkleUpdateDelegate.bestValidUpdateInAppcast_forUpdater_()")

        def bestValidUpdateInAppcast_forUpdater_(self, appcast, updater):
            client.log("sparkleUpdateDelegate.bestValidUpdateInAppcast_forUpdater_()")

        def updater_willDownloadUpdate_withRequest_(self, updater, appcast, request):
            self.downloadStarted = True
            client.log(
                "sparkleUpdateDelegate.updater_willDownloadUpdate_withRequest_()"
            )

        def updater_didDownloadUpdate_(self, updater, item):
            client.log("sparkleUpdateDelegate.updater_didDownloadUpdate_()")

        def updater_failedToDownloadUpdate_error_(self, updater, item, error):
            client.log("sparkleUpdateDelegate.updater_failedToDownloadUpdate_error_()")

        def updater_willExtractUpdate_(self, updater, item):
            client.log("sparkleUpdateDelegate.updater_willExtractUpdate_()")

        def updater_didExtractUpdate_(self, updater, item):
            client.log("sparkleUpdateDelegate.updater_didExtractUpdate_()")

        def updater_willInstallUpdate_(self, updater, item):
            client.log("sparkleUpdateDelegate.updater_willInstallUpdate_()")

        def updaterWillRelaunchApplication_(self, updater):
            client.log("sparkleUpdateDelegate.updater_willInstallUpdate_()")

        def updaterWillShowModalAlert_(self, updater):
            client.log("sparkleUpdateDelegate.updaterWillShowModalAlert_()")

        def updaterDidShowModalAlert_(self, updater):
            client.log("sparkleUpdateDelegate.updaterDidShowModalAlert_()")

    sparkleDelegate = SparkleUpdateDelegate.alloc().init()
    sparkle.setDelegate_(sparkleDelegate)


if WIN:

    class SparkleUpdateDelegate(object):
        def __init__(self):
            self.updateInProgress = False

        def waitForUpdateToFinish(self):

            while self.updateInProgress:
                time.sleep(1)

            client.log("Update loop finished")

            self.destroyIfRemotelyCalled()

        def destroyIfRemotelyCalled(self):
            client.log("Quitting because app was called remotely for an update")

            # Do nothing here for Windows because we didn't create an app instance

        def pywinsparkle_no_update_found(self):
            """ when no update has been found, close the updater"""
            client.log("No update found")
            self.updateInProgress = False

        def pywinsparkle_found_update(self):
            """ log that an update was found """
            client.log("New Update Available")
            # self.updateInProgress = False

        def pywinsparkle_encountered_error(self):
            client.log("An error occurred")
            self.updateInProgress = False
            self.destroyIfRemotelyCalled()

        def pywinsparkle_update_cancelled(self):
            """ when the update was cancelled, close the updater"""
            client.log("Update was cancelled")
            self.updateInProgress = False

        def pywinsparkle_shutdown(self):
            """ The installer is being launched signal the updater to shutdown """
            # actually shutdown the app here
            client.log("Safe to shutdown before installing")
            self.updateInProgress = False

        def check_with_ui(self):
            client.log("check_with_ui()")
            self.updateInProgress = True

            # waitForUpdateThread = Thread(target=self.waitForUpdateToFinish)
            # waitForUpdateThread.start()

            pywinsparkle.win_sparkle_check_update_with_ui()

            self.waitForUpdateToFinish()

        def check_without_ui(self):
            client.log("check_without_ui()")
            self.updateInProgress = True

            # waitForUpdateThread = Thread(target=self.waitForUpdateToFinish)
            # waitForUpdateThread.start()

            pywinsparkle.win_sparkle_check_update_without_ui()

            self.waitForUpdateToFinish()

        def setup(self):

            # register callbacks
            pywinsparkle.win_sparkle_set_did_find_update_callback(
                self.pywinsparkle_found_update
            )
            pywinsparkle.win_sparkle_set_did_not_find_update_callback(
                self.pywinsparkle_no_update_found
            )
            pywinsparkle.win_sparkle_set_error_callback(
                self.pywinsparkle_encountered_error
            )
            pywinsparkle.win_sparkle_set_update_cancelled_callback(
                self.pywinsparkle_update_cancelled
            )
            pywinsparkle.win_sparkle_set_shutdown_request_callback(
                self.pywinsparkle_shutdown
            )

            # set application details
            update_url = f"https://api.type.world/appcast/world.type.guiapp/windows/normal/appcast.xml?t={int(time.time())}"
            pywinsparkle.win_sparkle_set_appcast_url(update_url)
            pywinsparkle.win_sparkle_set_app_details(
                "Type.World", "Type.World", APPVERSION
            )

            pywinsparkle.win_sparkle_set_dsa_pub_pem(
                """-----BEGIN PUBLIC KEY-----
MIIGRzCCBDkGByqGSM44BAEwggQsAoICAQCZxho4eTkP3Jtj5onRubyG6XqN7jux
TFpPVE6ey9mYilFqmXW+YZKkhiaVvakn7HMigxooxaP1VmmtzLCPC7NLWsPCEsRy
LAvWWy05hSzLWLhI1HTU12s1eP8CfIyxuLwQkBLq6PiUQzTXiM9zETrrI1AyC6kj
uwaFDi8/5c1o/oDOOdoXqW/8M2VRCFolHCK+8xRXgWxDniepodDwR2B1+S9bljj4
YviJkNA2uWjH9dRPfGCl+W/F5WNAxEGf8K3kMhUjmsdHo7zCKt5gRDkO4CAGEDrF
3HNhHG3hS3DPYptryb8Fky2NcWa6/M8C5tIAz4eJxghwVrSAPjNNWCGwJ2v+wm1H
8H4SFxNMKPI18h1a0TnbRadNOOdyfIZ4/he83jjJ1LcCw+Xi7RhAAP+qs7kbN2mv
jVxvNNZHGSwGp962MG84P5gXYu73LBmDbfs+T3CGkCXvzee1E/6yHaGJHhr5sah6
+4kg2ted8sTPH921cIhdWvJ5ETvq95cqBv77v1DF9tIBKpVYXf55nz4+kJh5JJTG
xgdm6a9T+7zUACz84cstRD7/7M6bkg5FwmU6I7GiaVcJYxxaHiYaF2TrGvALA6vA
J1CrQ3EQPf9Fpq5/uqlJYiGdyLG6aGLb9c6EMwV/CsBX70+Ct/4T3vzcZRaDTgcp
GO5WgJ5rjg2UhQIhAOlHdxXVUfPx1vcFamAkUaEHggXbV3JVCLypoA6qicsZAoIC
AFgMMmoip2UFdAgmd2e2NNbS6Fn8s5CxSoHER9SsZSV286FczbxOC3smzsPq2P8X
r13tpnx1myZFNLdxrf71dUCidcJ90qxOahdIc0Ixef/6PrAhWFVfi22VyrKEo/tP
sc24z5xF+RuXFny0UfXx5pGMnOZZRk1w9PHagPzhS8nKnCBUPVJI2G6OL9Pn1uN9
bbrF6nj1skGNm7N6Ab3cV8GCA9y+QssrOnek/sFk7qEc/gdl7MvRVajxChN+QLYh
BLdq2CJLj+necwP+x6WyqyA040MRI5STUhqQKBP315eKSeMDPZdW79I4rQojLeKr
vVI1R5JjxKEBmr6R/WltTpKrGKcVX5zvoCNtZ0wjJkjbQxEKVDmX5XuXWu0wkDwk
RSDMeYTSiBoxwYOM+ZMios9on4XA9C1T8aJSMyo8z3TVCOJhSE2Hcv0Zk+XV+dkI
1FtnuEkLIr8jqdunmV2qp3zSH06t6jrmMgk9WEvyYHThlfauX9I1fM7F0HlxAAzp
HghsMzK3LypcuRhTr2VKwTEAtbAHniuRdpxjt/qTF2iJktuJUmOE9bCYQUn6NzEs
pGJLXpKBtd9XxUETVWqtEUhliQ1NtSeYa2wA6lDDoTvhLQhpw+1LLMRKbqeCUJTe
EU4vMq7s7uMerXAew7AfkRSLNNFLaIWXvcQd36d6SiSWA4ICBgACggIBAIbws0m0
6Sf61wo8KJpLlGd6Lcu2NvM650L5EdiLxRuWpTU6KN55iKUos92F7P/KNJeAcEo4
yOJ+o2zYFAO9FZCKB182cJ9tZZilkm/sq4HgbGDK3K984CtvW+2i0fan9HqUUTzA
U0OQBwxAeqg7ABYay7IMvDfIvwtjVzX8QGtQZfYl1p9M+xZEJA15Vwe+Zj/lYVZD
Ux7pGoRZKRutupKBMybyrmGIf583r09R6zLC7NJjIGm2U2ZRP9eNyBfE9KHQhRUX
ejUSwL23nZv3/sK+M8w6UU5Msh/IeEEpSL2KbOEAfpo3rCS4I/17jGXRXihjCIsn
/v6uf/R+yt5N5LJ2HSCQ+sWRb8kRQh5V0nYMY3/NI7Ektjsq0Pj8wuJTW1M0Mezr
CeK8cVocDxwBRLPFfCd/cLDI79oeG4V3+H4ztF+GAlT3EKCKLTlDjTnrRa7CsufR
wPEvjee3dxyZ9cVpEmggKQ6eOxK97+62yuNTCdpoiqw7Bka7xvVslkWii1WZ8KLX
JpFX7dcX6THLOhqgsNbxMR49yX2AfvUt8kampXBaYHJ8Y3IgJOIYQLeBsbJR/G+X
6DZd/e33YAxUQsVOh/TReFO754+QaF4Ahr6zFmtkE4sssILXQTx3uEalvtBpEN9Z
ziwuJDBJ75bzmLBh1nhU9olZNEUNIqxAmAw6
-----END PUBLIC KEY-----
"""
            )

            # initialize
            pywinsparkle.win_sparkle_init()

            # # check for updates
            # pywinsparkle.win_sparkle_check_update_with_ui()

            # # alternatively you could check for updates in the
            # # background silently
            # pywinsparkle.win_sparkle_check_update_without_ui()


if WIN and RUNTIME:
    sys._MEIPASS = os.path.join(
        os.path.dirname(__file__), "lib", "pywinsparkle", "libs", "x64"
    )
    from pywinsparkle import pywinsparkle

    pywinsparkleDelegate = SparkleUpdateDelegate()
    pywinsparkleDelegate.setup()


class AppFrame(wx.Frame):
    def __init__(self):

        try:

            self.messages = []
            self.active = True
            self.online = False
            self.lastMinuteCheck = 0
            self.lastOnlineCheck = 0

            self.allowedToPullServerUpdates = True
            self.allowCheckForURLInFile = True

            self.delegate = delegate
            self.delegate.parent = self

            self.panelVisible = None

            # Version adjustments

            # TODO: Remove these for future versions
            if client.get("appVersion"):
                # 0.1.4
                if (
                    client.get("appVersion") != APPVERSION
                    and APPVERSION == "0.1.4-alpha"
                    and semver.compare("0.1.4-alpha", client.get("appVersion")) == 1
                ):

                    if client.publishers():
                        for publisher in client.publishers():
                            publisher.delete()

                        self.messages.append(
                            "Due to a change in the subscription security and login infrastructure, all subscriptions were removed. The API endpoints need to be adjusted and subscriptions re-added following the new guidelines. See https://type.world/app/ for the release notes."
                        )

            if not client.get("appVersion"):
                client.set("appVersion", APPVERSION)
            if not client.get("localizationType"):
                client.set("localizationType", "systemLocale")
            if not client.get("customLocaleChoice"):
                client.set("customLocaleChoice", client.systemLocale())
            if not client.get("reloadSubscriptionsInterval"):
                client.set("reloadSubscriptionsInterval", 1 * 24 * 60 * 60)  # one day
            if not client.get("seenDialogs"):
                client.set("seenDialogs", [])

            client.set("appVersion", APPVERSION)

            # This should be unnecessary, but let's keep it here. More resilience.
            if client.get(
                "currentPublisher"
            ) == "pendingInvitations" and not client.get("pendingInvitations"):
                client.set("currentPublisher", "")

            if client.get("currentPublisher") == "None":
                client.set("currentPublisher", "")

            if not client.get("currentPublisher") and len(client.publishers()) >= 1:
                client.set("currentPublisher", client.publishers()[0].canonicalURL)

            self.thread = threading.current_thread()

            self.justAddedPublisher = None
            self.fullyLoaded = False
            self.panelVisible = None

            # Window Size
            minSize = [1100, 700]
            if client.get("sizeMainWindow"):
                size = list(client.get("sizeMainWindow"))

                if MAC:
                    from AppKit import NSScreen

                    screenSize = NSScreen.mainScreen().frame().size
                    if size[0] > screenSize.width:
                        size[0] = screenSize.width - 50
                    if size[1] > screenSize.height:
                        size[1] = screenSize.height - 50
            else:
                size = [1000, 700]
            size[0] = max(size[0], minSize[0])
            size[1] = max(size[1], minSize[1])
            super(AppFrame, self).__init__(None, size=size)
            self.SetMinSize(minSize)

            self.Title = "%s %s" % (APPNAME, APPVERSION)

            self.html = wx.html2.WebView.New(self)
            self.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, self.onNavigating, self.html)
            self.Bind(wx.html2.EVT_WEBVIEW_NAVIGATED, self.onNavigated, self.html)
            self.Bind(wx.html2.EVT_WEBVIEW_ERROR, self.onError, self.html)
            self.Bind(wx.html2.EVT_WEBVIEW_LOADED, self.onLoad, self.html)
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.html, 1, wx.EXPAND)
            self.SetSizer(sizer)

            self.Bind(wx.EVT_CLOSE, self.onClose)
            self.Bind(wx.EVT_QUERY_END_SESSION, self.onQuit)
            self.Bind(wx.EVT_END_SESSION, self.onQuit)

            self.Bind(wx.EVT_LEFT_DOWN, self.onMouseDown)

            ### Menus
            self.setMenuBar()
            self.CentreOnScreen()

            # Restart agent after restart
            if client.get("menuBarIcon") and not agentIsRunning():
                installAgent()

            self.Bind(wx.EVT_SIZE, self.onResize, self)
            self.Bind(wx.EVT_ACTIVATE, self.onActivate, self)
            self.Bind(wx.EVT_KILL_FOCUS, self.onInactivate)

            import signal

            def exit_signal_handler(signal, frame):

                # template = zroya.Template(zroya.TemplateType.ImageAndText4)
                # template.setFirstLine('Quit Signal')
                # # template.setSecondLine(str(signal))
                # # template.setThirdLine(str(frame))
                # expiration = 24 * 60 * 60 * 1000 # one day
                # template.setExpiration(expiration) # One day
                # notificationID = zroya.show(template)

                client.log("Received SIGTERM or SIGINT")

                self.onQuit(None)

            # if MAC:
            # 	signal.signal(signal.SIGBREAK, exit_signal_handler)
            signal.signal(signal.SIGTERM, exit_signal_handler)
            signal.signal(signal.SIGINT, exit_signal_handler)

        # 			client.log('AppFrame.__init__() finished')

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def onMouseDown(self, event):
        # print(event)
        pass

    def setMenuBar(self):
        try:
            menuBar = wx.MenuBar()

            # Exit
            menu = wx.Menu()
            m_opensubscription = menu.Append(
                wx.ID_OPEN,
                "%s...%s" % (localizeString("#(Add Subscription)"), "\tCtrl+O"),
            )  # \tCtrl-O
            self.Bind(wx.EVT_MENU, self.showAddSubscription, m_opensubscription)
            #        m_opensubscription.SetAccel(wx.AcceleratorEntry(wx.ACCEL_CTRL,  ord('o')))

            m_CheckForUpdates = menu.Append(
                wx.NewIdRef(count=1),
                "%s..." % (localizeString("#(Check for App Updates)")),
            )
            self.Bind(wx.EVT_MENU, self.onCheckForUpdates, m_CheckForUpdates)
            if MAC:
                m_closewindow = menu.Append(
                    wx.ID_CLOSE, "%s\tCtrl+W" % (localizeString("#(Close Window)"))
                )
                self.Bind(wx.EVT_MENU, self.onClose, m_closewindow)
            m_exit = menu.Append(
                wx.ID_EXIT,
                "%s\t%s" % (localizeString("#(Exit)"), "Ctrl-Q" if MAC else "Alt-F4"),
            )
            self.Bind(wx.EVT_MENU, self.onQuit, m_exit)

            # m_InstallAgent = menu.Append(wx.NewIdRef(count=1), "Install Agent")
            # self.Bind(wx.EVT_MENU, self.installAgent, m_InstallAgent)
            # m_RemoveAgent = menu.Append(wx.NewIdRef(count=1), "Remove Agent")
            # self.Bind(wx.EVT_MENU, self.uninstallAgent, m_RemoveAgent)

            menuBar.Append(menu, "&%s" % (localizeString("#(File)")))

            # Edit
            # if 'wxMac' in wx.PlatformInfo and wx.VERSION >= (3,0):
            #   wx.ID_COPY = wx.NewIdRef(count=1)
            #   wx.ID_PASTE = wx.NewIdRef(count=1)
            editMenu = wx.Menu()
            editMenu.Append(wx.ID_UNDO, "%s\tCtrl-Z" % (localizeString("#(Undo)")))
            editMenu.AppendSeparator()
            editMenu.Append(
                wx.ID_SELECTALL, "%s\tCtrl-A" % (localizeString("#(Select All)"))
            )
            editMenu.Append(wx.ID_COPY, "%s\tCtrl-C" % (localizeString("#(Copy)")))
            editMenu.Append(wx.ID_CUT, "%s\tCtrl-X" % (localizeString("#(Cut)")))
            editMenu.Append(wx.ID_PASTE, "%s\tCtrl-V" % (localizeString("#(Paste)")))

            if WIN:

                editMenu.AppendSeparator()

                m_prefs = editMenu.Append(
                    wx.ID_PREFERENCES,
                    "&%s\tCtrl-I" % (localizeString("#(Preferences)")),
                )
                self.Bind(wx.EVT_MENU, self.onPreferences, m_prefs)

            menuBar.Append(editMenu, "&%s" % (localizeString("#(Edit)")))

            menu = wx.Menu()
            m_about = menu.Append(
                wx.ID_ABOUT, "&%s %s" % (localizeString("#(About)"), APPNAME)
            )
            self.Bind(wx.EVT_MENU, self.onAbout, m_about)

            if MAC:

                m_prefs = menu.Append(
                    wx.ID_PREFERENCES,
                    "&%s\tCtrl-," % (localizeString("#(Preferences)")),
                )
                self.Bind(wx.EVT_MENU, self.onPreferences, m_prefs)

            # menuBar.Append(menu, "Type.World")
            menuBar.Append(menu, "&%s" % (localizeString("#(Help)")))

            self.SetMenuBar(menuBar)

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def javaScript(self, code):
        try:
            startWorker(
                self.threadSafeJavaScript_consumer,
                self.threadSafeJavaScript_worker,
                wargs=(code,),
            )
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def threadSafeJavaScript_worker(self, code):
        try:
            return code

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def threadSafeJavaScript_consumer(self, delayedResult):
        try:
            code = delayedResult.get()
            self._javaScript(code)

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def _javaScript(self, script):
        try:
            if self.fullyLoaded:
                if threading.current_thread() == self.thread:
                    if script:
                        self.html.RunScript(script)
                    # pass
                else:
                    client.log(
                        "JavaScript called from another thread: %s" % script[:100]
                    )
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def publishersNames(self):
        try:
            # Build list, sort it
            publishers = []
            for i, key in enumerate(client.endpoints.keys()):
                endpoint = client.endpoints[key]
                name, language = endpoint.latestVersion().name.getTextAndLocale(
                    locale=client.locale()
                )
                publishers.append((i, name, language))
            return publishers
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def onCheckForUpdates(self, event):
        try:
            if MAC:
                sparkle.resetUpdateCycle()
                self.setAppCastURL()
                sparkle.checkForUpdates_(self)
            elif WIN and RUNTIME:
                pywinsparkleDelegate.check_with_ui()

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def onClose(self, event):
        try:
            if self.panelVisible:
                self.javaScript("hidePanel();")
            else:
                self.onQuit(event)
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def onQuit(self, event, withExitCode=None):
        try:

            expiringInstalledFonts = client.expiringInstalledFonts()

            if expiringInstalledFonts:

                dlg = wx.MessageDialog(
                    None,
                    localizeString(
                        "You have installed %s font(s) that are under active expiration. Quitting the app will remove these fonts. Do you want to continue?"
                        % len(expiringInstalledFonts)
                    ),
                    localizeString("Active expiration fonts"),
                    wx.YES_NO | wx.ICON_QUESTION,
                )
                dlg.SetYesNoLabels(
                    localizeString("#(Remove and Quit)"), localizeString("#(Cancel)")
                )
                result = dlg.ShowModal()
                if result == wx.ID_YES:

                    fontIDs = [x.uniqueID for x in expiringInstalledFonts]
                    (
                        success,
                        message,
                    ) = font.parent.parent.parent.parent.subscription.removeFonts(
                        fontIDs
                    )
                    if not success:
                        self.errorMessage(message, "Error deleting fonts")
                        return

                else:
                    return

            self.active = False
            client.quit()

            # client.log('onQuit()')

            while locked():
                client.log("Waiting for locks to disappear")
                time.sleep(0.5)

            try:
                client.log("send closeListener command to self")
                address = ("localhost", 65500)
                myConn = Client(address)
                myConn.send("closeListener")
                myConn.close()
                client.log("send closeListener command to self (finished)")
            except ConnectionRefusedError:
                pass

            if WIN and RUNTIME:
                pywinsparkle.win_sparkle_cleanup()

            if withExitCode != None:
                self.parent.exitCode = withExitCode

            self.Destroy()

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def pullServerUpdates(self, force=False):

        try:
            if (
                not client.get("lastServerSync")
                or client.get("lastServerSync") < time.time() - PULLSERVERUPDATEINTERVAL
                or force
            ):
                if self.allowedToPullServerUpdates:
                    startWorker(
                        self.pullServerUpdates_consumer,
                        self.pullServerUpdates_worker,
                    )
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def pullServerUpdates_worker(self):
        try:
            return client.downloadSubscriptions()
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def pullServerUpdates_consumer(self, delayedResult):

        try:
            success, message = delayedResult.get()

            # print(success, message)

            self.setSideBarHTML()
            if client.get("currentPublisher"):
                self.setPublisherHTML(
                    self.b64encode(
                        client.publisher(client.get("currentPublisher")).canonicalURL
                    )
                )
            self.setBadges()

            if success:
                subscriptionsUpdatedNotification(message)
                agent("amountOutdatedFonts %s" % client.amountOutdatedFonts())

                self.javaScript('$("#userWrapper .alert").hide();')
                self.javaScript('$("#userWrapper .noAlert").show();')

            else:

                self.javaScript('$("#userWrapper .alert").show();')
                self.javaScript('$("#userWrapper .noAlert").hide();')

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def onInactivate(self, event):
        try:
            if client.get("currentPublisher"):
                self.setPublisherHTML(self.b64encode(client.get("currentPublisher")))
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def onActivate(self, event):
        try:

            if self.active:

                resize = False

                # If Window is outside of main screen (like after screen unplugging)
                if self.GetPosition()[0] < 0:
                    self.SetPosition((0, self.GetPosition()[1]))
                minY = 0
                if MAC:
                    minY = NSScreen.mainScreen().visibleFrame().origin.y
                if self.GetPosition()[1] < minY:
                    self.SetPosition((self.GetPosition()[0], minY))

                if MAC:

                    size = list(self.GetSize())

                    screenSize = NSScreen.mainScreen().frame().size
                    if size[0] > screenSize.width:
                        size[0] = screenSize.width - 50
                        resize = True
                    if size[1] > screenSize.height:
                        size[1] = screenSize.height - 50
                        resize = True

                if resize:
                    self.SetSize(size)

                if client.get("currentPublisher"):
                    self.setPublisherHTML(
                        self.b64encode(client.get("currentPublisher"))
                    )

                if WIN and self.allowCheckForURLInFile:
                    self.checkForURLInFile()

                if MAC:
                    self.applyDarkMode()

                # # checkIfOnline() if not directly after app start
                # if self.lastOnlineCheck > 0 and time.time() - self.lastOnlineCheck > 40:
                #     checkOnlineThread = Thread(target=self.checkIfOnline)
                #     checkOnlineThread.start()

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def theme(self):
        try:
            if MAC:
                if (
                    NSUserDefaults.standardUserDefaults().objectForKey_(
                        "AppleInterfaceStyle"
                    )
                    == "Dark"
                ):
                    return "dark"
                else:
                    return "light"
            else:
                return "light"
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def applyDarkMode(self):
        try:
            if platform.mac_ver()[0].split(".") > "10.14.0".split("."):

                if client and client.get("currentPublisher"):
                    publisher = client.publisher(client.get("currentPublisher"))
                    self.setPublisherHTML(
                        self.b64encode(client.get("currentPublisher"))
                    )
                    if publisher.get("currentSubscription"):
                        subscription = publisher.subscription(
                            publisher.get("currentSubscription")
                        )
                        if subscription.get("currentFont"):
                            self.setMetadataHTML(
                                self.b64encode(subscription.get("currentFont"))
                            )

                self.javaScript("$('body').removeClass('light');")
                self.javaScript("$('body').removeClass('dark');")
                self.javaScript("$('body').addClass('%s');" % self.theme())
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def onResize(self, event):
        try:
            size = self.GetSize()

            # self.javaScript("$('.panel').css('height', '%spx');" % (size[1]))

            if MAC:
                if hasattr(self, "dragView"):
                    self.dragView.setFrameSize_(NSSize(self.GetSize()[0], 40))
            client.set("sizeMainWindow", (self.GetSize()[0], self.GetSize()[1]))
            event.Skip()
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def onAbout(self, event):
        try:
            html = []

            html.append('<p style="text-align: center; margin-bottom: 20px;">')
            html.append(
                '<img src="file://##htmlroot##/icon.svg" style="width: 150px; height: 150px;"><br />'
            )
            html.append("</p>")
            html.append("<p>")
            html.append("#(AboutText)")
            html.append("</p>")

            html.append('<p style="margin-bottom: 20px;">')
            html.append("#(We thank our Patrons):")
            html.append("<br />")
            patrons = json.loads(
                ReadFromFile(
                    os.path.join(os.path.dirname(__file__), "patrons", "patrons.json")
                )
            )
            html.append(
                "<b>"
                + "</b>, <b>".join([x.replace(" ", "&nbsp;") for x in patrons])
                + "</b>"
            )
            html.append("</p>")

            html.append('<p style="margin-bottom: 20px;">')
            html.append("#(Anonymous App ID): %s<br />" % client.anonymousAppID())
            html.append("#(Version) %s<br />" % APPVERSION)
            html.append(
                '#(Version History) #(on) <a href="https://type.world/app">type.world/app</a>'
            )
            html.append("</p>")
            # html.append(u'<p>')
            # html.append(u'<a class="button" onclick="python('self.sparkle.checkForUpdates_(None)');">#(Check for App Updates)</a>')
            # html.append(u'</p>')

            # Print HTML
            html = "".join(map(str, html))
            html = self.replaceHTML(html)
            html = localizeString(html, html=True)
            html = html.replace('"', "'")
            html = html.replace("\n", "")
            js = '$("#about .inner").html("' + html + '");'
            self.javaScript(js)

            self.javaScript("showAbout();")
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def resetDialogs(self):
        try:
            client.set("seenDialogs", [])
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def unlinkUserAccount(self):
        try:
            success, message = client.unlinkUser()

            if success:

                self.onPreferences(None, "userAccount")
                if client.get("currentPublisher"):
                    self.setPublisherHTML(
                        self.b64encode(client.get("currentPublisher"))
                    )

            else:

                self.errorMessage(message)

            self.setSideBarHTML()
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def createUserAccount(self, name, email, password1, password2):
        try:
            success, message = client.createUserAccount(
                name, email, password1, password2
            )
            if not success:
                self.errorMessage(message)
            else:
                self.message("#(VerifyEmailAfterUserAccountCreation)")
                self.onPreferences(None, "userAccount")

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def resendEmailVerification(self):
        success, message = client.resendEmailVerification()
        if not success:
            self.errorMessage(message)
        else:
            self.message("#(VerifyEmailAfterUserAccountCreation)")

    def logIn(self, email, password):
        try:
            success, message = client.logInUserAccount(email, password)
            if not success:
                self.errorMessage(message)
            else:
                self.onPreferences(None, "userAccount")

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def revokeAppInstance(self, anonymousAppID):

        try:

            dlg = wx.MessageDialog(
                self,
                localizeString("#(Are you sure)"),
                localizeString("#(Revoke App)"),
                wx.YES_NO | wx.ICON_QUESTION,
            )
            dlg.SetYesNoLabels(localizeString("#(Revoke)"), localizeString("#(Cancel)"))
            result = dlg.ShowModal() == wx.ID_YES
            dlg.Destroy()

            if result:

                success, response = client.revokeAppInstance(anonymousAppID)
                if success:
                    self.onPreferences(None, "linkedApps")

                else:
                    self.errorMessage(response, "#(Revoke App)")
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def reactivateAppInstance(self, anonymousAppID):

        try:
            dlg = wx.MessageDialog(
                self,
                localizeString("#(Are you sure)"),
                localizeString("#(Reactivate App)"),
                wx.YES_NO | wx.ICON_QUESTION,
            )
            dlg.SetYesNoLabels(
                localizeString("#(Reactivate)"), localizeString("#(Cancel)")
            )
            result = dlg.ShowModal() == wx.ID_YES
            dlg.Destroy()

            if result:

                success, response = client.reactivateAppInstance(anonymousAppID)
                if success:
                    self.onPreferences(None, "linkedApps")

                else:
                    self.errorMessage(response, "#(Reactivate App)")
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def onPreferences(self, event, section="generalPreferences"):

        try:

            html = []

            html.append('<div class="head">')

            html.append('<div class="tabs clear">')

            # Tabs
            for keyword, title, condition in (
                ("generalPreferences", localizeString("#(Preferences)"), True),
                ("userAccount", localizeString("#(User Account)"), True),
                ("linkedApps", localizeString("#(Linked Apps)"), client.user()),
            ):

                if condition:
                    html.append(
                        '<div class="tab %s %s">'
                        % (keyword, "active" if section == keyword else "")
                    )
                    if keyword != section:
                        html.append(
                            '<a href="x-python://self.onPreferences(None, ____%s____)">'
                            % keyword
                        )
                    html.append(title)
                    if keyword != section:
                        html.append("</a>")
                    html.append("</div>")  # .tab

            html.append("</div>")  # .tabs

            html.append("</div>")  # head

            html.append('<div class="body inner">')

            if section == "linkedApps":
                self.panelVisible = "preferences(linkedApps)"

                success, instances = client.linkedAppInstances()
                if not success:

                    if instances[0] == "#(response.appInstanceRevoked)":
                        html.append(
                            "This app instance is revoked an cannot access other app instance information."
                        )
                    else:
                        html.append(instances)

                else:
                    for instance in instances:
                        html.append(
                            '<div class="appInstance clear" style="margin-bottom: 20px;">'
                        )

                        # html.append(instance.anonymousAppID)
                        # html.append('</div>') # .appInstance

                        html.append(
                            '<div style="float: left; width: 100px; margin-left: 20px;">'
                        )

                        image = instance.image
                        if image:
                            html.append(
                                f'<img src="{os.path.join(os.path.dirname(__file__), "htmlfiles", "machineModels", image)}" style="width: 80px; margin-top: 10px;">'
                            )

                        html.append("</div>")
                        html.append('<div style="float: left; width: 350px;">')

                        html.append("<p>")

                        html.append("<b>")
                        html.append(
                            instance.machineNodeName
                            or instance.machineHumanReadableName
                            or instance.anonymousAppID
                        )
                        html.append("</b>")
                        if instance.anonymousAppID == client.anonymousAppID():
                            html.append(" <i>(#(This app))</i>")
                        html.append("<br />")

                        if (
                            instance.machineModelIdentifier
                            and instance.machineModelIdentifier.startswith("Parallels")
                            or instance.machineHumanReadableName
                            and instance.machineHumanReadableName.startswith(
                                "Parallels"
                            )
                        ):
                            html.append("Parallels Desktop Virtual Machine")
                            html.append("<br />")
                        else:
                            if instance.machineHumanReadableName:
                                html.append(instance.machineHumanReadableName)
                                html.append("<br />")
                        if instance.machineSpecsDescription:
                            html.append(instance.machineSpecsDescription)
                            html.append("<br />")
                        if instance.machineOSVersion:
                            if instance.machineOSVersion.startswith("mac"):
                                src = "other/apple.svg"
                            elif instance.machineOSVersion.startswith("Windows"):
                                src = "other/windows.svg"
                            else:
                                src = None
                            if src:
                                html.append(
                                    f'<img src="{os.path.join(os.path.dirname(__file__), "htmlfiles", "machineModels", src)}" style="width: 16px; position: relative; top: 3px; margin-right: 5px;">'
                                )
                            html.append(instance.machineOSVersion)

                        if instance.revoked:
                            html.append("<br />")
                            html.append("<div>")
                            html.append(
                                '<span class_="box" style="background-color: orange; padding: 3px;">'
                            )
                            html.append(
                                "#(Revoked): %s %s"
                                % (
                                    locales.formatDate(
                                        instance.revokedTime, client.locale()
                                    ),
                                    locales.formatTime(
                                        instance.revokedTime, client.locale()
                                    ),
                                )
                            )
                            html.append("</span>")
                            html.append("</div>")

                        else:
                            if instance.lastUsed:
                                if (
                                    not instance.anonymousAppID
                                    == client.anonymousAppID()
                                ):
                                    html.append("<br />")
                                    html.append('<span style="color: #888;">')
                                    html.append(
                                        "#(Last active): %s %s"
                                        % (
                                            locales.formatDate(
                                                instance.lastUsed, client.locale()
                                            ),
                                            locales.formatTime(
                                                instance.lastUsed, client.locale()
                                            ),
                                        )
                                    )

                                html.append("</span>")
                        html.append("</p>")

                        html.append("</div>")

                        # Revoke/Activate
                        html.append('<div style="float: left; margin-left: 50px;">')

                        if not instance.anonymousAppID == client.anonymousAppID():
                            if instance.revoked:
                                html.append(
                                    f'<a class="button" href="x-python://self.reactivateAppInstance(____{instance.anonymousAppID}____)">#(Reactivate App)</a>'
                                )
                            else:
                                html.append(
                                    f'<a class="button" href="x-python://self.revokeAppInstance(____{instance.anonymousAppID}____)">#(Revoke App)</a>'
                                )
                        html.append("</div>")  # Revoke/Activate

                        html.append("</div>")  # .appInstance

            if section == "userAccount":
                self.panelVisible = "preferences(userAccount)"

                # User
                html.append("<h2>#(Type.World User Account)</h2>")
                if client.user():
                    html.append("<p>")
                    html.append("#(Linked User Account): ")
                    if client.userName() and client.userEmail():
                        html.append(
                            "<b>%s</b> (%s)" % (client.userName(), client.userEmail())
                        )
                    elif client.userEmail():
                        html.append("<b>%s</b>" % (client.userEmail()))
                    html.append("</p>")
                    # html.append('<p>')
                    # html.append('#(Account Last Synchronized): %s' % (NaturalRelativeWeekdayTimeAndDate(client.get('lastServerSync'), locale = client.locale()[0]) if client.get('lastServerSync') else 'Never'))
                    # html.append('</p>')

                    html.append("<hr>")

                    html.append("<h2>#(Verified Email Address)</h2>")
                    html.append("<p>")
                    html.append("#(Your email address is) ")
                    if client.get("userAccountEmailIsVerified"):
                        html.append("#(verified)")
                    else:
                        html.append(
                            '<span class_="box" style="background-color: orange; padding: 3px;">'
                        )
                        html.append("#(unverified)")
                        html.append("</span>")
                        html.append("</p>")
                        html.append("<p>")
                        html.append(
                            '<a id="resendEmailVerificationButton" class="button">#(Resend verification email)</a>'
                        )

                    html.append("</p>")
                    html.append(
                        """<script>$("#preferences #resendEmailVerificationButton").click(function() {

                    python("self.resendEmailVerification()");
                     
                });</script>"""
                    )

                    html.append("<hr>")

                    html.append("<h2>#(Unlink User Account)</h2>")
                    html.append("<p>")
                    html.append("#(UnlinkUserAccountExplanation)")
                    html.append("</p>")
                    html.append("<p>")
                    html.append(
                        '<a id="unlinkAppButton" class="button">#(Unlink User Account)</a>'
                    )
                    html.append("</p>")
                else:

                    # 				html.append('#(NoUserAccountLinked)<br />#(PleaseCreateUserAccountExplanation)')

                    html.append('<div class="clear">')
                    html.append(
                        '<div style="float: left; width: 47%; margin-right: 6%;">'
                    )

                    html.append("<div>")
                    html.append("<h4>#(Create Account)</h4>")
                    html.append("#(Name)")
                    html.append("<br />")
                    html.append(
                        '<input type="text" name="createAccountUserName" id="createAccountUserName" placeholder="#(John Doe)">'
                    )
                    html.append("<br />")
                    html.append("#(Email Address)")
                    html.append("<br />")
                    html.append(
                        '<input type="text" name="createAccountUserEmail" id="createAccountUserEmail" placeholder="#(johndoe@gmail.com)">'
                    )
                    html.append("<br />")
                    html.append("#(Password)")
                    html.append("<br />")
                    html.append(
                        '<input type="password" name="createAccountUserPassword" id="createAccountUserPassword">'
                    )
                    html.append("<br />")
                    html.append("#(Repeat Password)")
                    html.append("<br />")
                    html.append(
                        '<input type="password" name="createAccountUserPassword2" id="createAccountUserPassword2">'
                    )
                    html.append("</div>")

                    html.append("<p>")
                    html.append(
                        '<a id="createAccountButton" class="button">#(Create Account)</a>'
                    )
                    html.append("</p>")
                    html.append(
                        """<script>$("#preferences #createAccountButton").click(function() {

                    python("self.createUserAccount(____" + $("#preferences #createAccountUserName").val() + "____, ____" + $("#preferences #createAccountUserEmail").val() + "____, ____" + $("#preferences #createAccountUserPassword").val() + "____, ____" + $("#preferences #createAccountUserPassword2").val() + "____)");
                     
                });</script>"""
                    )

                    html.append("</div>")  # .floatleft
                    html.append('<div style="float: left; width: 47%;">')

                    html.append("<div>")
                    html.append("<h4>#(Log In To Existing Account)</h4>")
                    html.append("#(Email Address)")
                    html.append("<br />")
                    html.append(
                        '<input type="text" name="loginUserEmail" id="loginUserEmail" placeholder="#(johndoe@gmail.com)">'
                    )
                    html.append("<br />")
                    html.append("#(Password)")
                    html.append("<br />")
                    html.append(
                        '<input type="password" name="loginUserPassword" id="loginUserPassword">'
                    )
                    html.append("</div>")

                    html.append("<p>")
                    html.append('<a id="loginButton" class="button">#(Log In)</a>')
                    html.append("</p>")

                    html.append("<p>")
                    html.append(
                        '<a href="https://type.world/resetpassword">#(I Forgot My Password) ↗</a>'
                    )
                    html.append("</p>")

                    html.append(
                        """<script>$("#preferences #loginButton").click(function() {

                    python("self.logIn(____" + $("#preferences #loginUserEmail").val() + "____, ____" + $("#preferences #loginUserPassword").val() + "____)");
                     
                });</script>"""
                    )

                    html.append("</div>")  # .floatleft
                    html.append("</div>")  # .clear

                html.append(
                    """<script>$("#preferences #unlinkAppButton").click(function() {

                    python("self.unlinkUserAccount()");
                     
                });</script>"""
                )

            if section == "generalPreferences":

                self.panelVisible = "preferences(generalPreferences)"

                # # Update Interval
                # html.append('<h2>#(Update Interval)</h2>')
                # html.append('<p>#(UpdateIntervalExplanation)</p>')
                # html.append('<p>')
                # html.append('<select id="updateIntervalChoice" style="">')
                # for code, name in (
                # 	(-1, '#(Manually)'),
                # 	(1 * 60, '#(Minutely)'),
                # 	(1 * 60 * 60, '#(Hourly)'),
                # 	(24 * 60 * 60, '#(Daily)'),
                # 	(7 * 24 * 60 * 60, '#(Weekly)'),
                # 	(30 * 24 * 60 * 60, '#(Monthly)'),
                # ):
                # 	html.append('<option value="%s" %s>%s</option>' % (code, 'selected' if str(code) == str(client.get('reloadSubscriptionsInterval')) else '', name))
                # html.append('</select>')
                # html.append('<script>$("#preferences #updateIntervalChoice").click(function() {setPreference("reloadSubscriptionsInterval", $("#preferences #updateIntervalChoice").val());});</script>')
                # html.append('</p>')
                # html.append('<p>')
                # html.append('#(Last Check): %s' % NaturalRelativeWeekdayTimeAndDate(client.get('reloadSubscriptionsLastPerformed'), locale = client.locale()[0]))
                # html.append('</p>')

                # html.append('<hr>')
                # html.append('<hr>')
                # html.append('<hr>')
                # html.append('<hr>')
                # html.append('<hr>')
                # html.append('<hr>')
                # html.append('<hr>')
                # html.append('<hr>')
                # html.append('<hr>')
                # html.append('<hr>')
                # html.append('<hr>')
                # html.append('<hr>')

                # # Agent
                # if WIN:
                # 	html.append('<h2>#(Icon in Menu Bar.Windows)</h2>')
                # if MAC:
                # 	html.append('<h2>#(Icon in Menu Bar.Mac)</h2>')
                # html.append('<p>')
                # label = '#(Show Icon in Menu Bar' + ('.Windows' if WIN else '.Mac') + ')'
                # html.append('<span><input id="menubar" type="checkbox" name="menubar" %s><label for="menubar">%s</label></span>' % ('checked' if agentIsRunning() else '', label))
                # html.append('<script>$("#preferences #menubar").click(function() { if($("#preferences #menubar").prop("checked")) { python("installAgent()"); } else { setCursor("wait", 2000); python("uninstallAgent()"); } });</script>')
                # html.append('</p>')
                # html.append('<p>')
                # html.append('#(IconInMenuBarExplanation)')
                # html.append('</p>')

                # html.append('<hr>')

                # Localization
                systemLocale = client.systemLocale()
                for code, name in locales.locales:
                    if code == systemLocale:
                        systemLocale = name
                        break
                html.append("<h2>App Language</h2>")
                html.append("<p>")
                html.append(
                    '<span><input id="systemLocale" value="systemLocale" type="radio" name="localizationType" %s><label for="systemLocale">Use System Language (%s)</label></span>'
                    % (
                        "checked"
                        if client.get("localizationType") == "systemLocale"
                        else "",
                        systemLocale,
                    )
                )
                html.append(
                    '<script>$("#preferences #systemLocale").click(function() {setPreference("localizationType", "systemLocale");});</script>'
                )
                html.append("</p>")
                html.append("<p>")
                html.append(
                    '<span><input id="customLocale" value="customLocale" type="radio" name="localizationType" %s><label for="customLocale">Use Custom Language (choose below). Requires app restart to take full effect.</label></span>'
                    % (
                        "checked"
                        if client.get("localizationType") == "customLocale"
                        else ""
                    )
                )
                html.append(
                    '<script>$("#preferences #customLocale").click(function() {setPreference("localizationType", "customLocale");});</script>'
                )
                html.append("</p>")
                html.append("<p>")
                html.append('<select id="customLocaleChoice" style="" onchange="">')
                for code, name in locales.supportedLocales():
                    html.append(
                        '<option value="%s" %s>%s</option>'
                        % (
                            code,
                            "selected"
                            if code == client.get("customLocaleChoice")
                            else "",
                            name,
                        )
                    )
                html.append("</select>")
                html.append(
                    """<script>$("#preferences #customLocaleChoice").click(function() {

                    setPreference("customLocaleChoice", $("#preferences #customLocaleChoice").val());
                     
                });</script>"""
                )
                html.append("</p>")

                html.append("<hr>")

                # App updates
                html.append("<h2>#(App Updates)</h2>")
                html.append("<p>")
                html.append(
                    f'<input type="checkbox" id="developerAppUpdates" name="developerAppUpdates" {"checked" if client.get("appUpdateProfile") == "developer" else ""}><label for="developerAppUpdates">#(Receive Developer App Versions)</label>'
                )
                html.append(
                    '<script>$("#preferences #developerAppUpdates").click(function() { if ($("#preferences #developerAppUpdates:checked").val()) { setPreference("appUpdateProfile", "developer"); } else { setPreference("appUpdateProfile", "normal"); } });</script>'
                )
                html.append("</p>")
                # python("self.setAppCastURL()");
                # if ($("#preferences #developerAppUpdates:checked").val()) { setPreference("appUpdateProfile", "developer"); } else { setPreference("appUpdateProfile", "normal"); }

                html.append("<hr>")

                # Reset Dialogs
                html.append("<h2>#(Reset Dialogs)</h2>")
                html.append("<p>")
                html.append(
                    '<a id="resetDialogButton" class="button">#(ResetDialogsButton)</a>'
                )
                html.append("</p>")
                html.append(
                    """<script>$("#preferences #resetDialogButton").click(function() {

                    python("self.resetDialogs()");
                     
                });</script>"""
                )

            html.append("</div>")  # .inner

            # Print HTML
            html = "".join(map(str, html))
            html = html.replace('"', "'")
            html = localizeString(html, html=True)
            html = html.replace("\n", "")
            # print(html)
            js = '$("#preferences .centerOuter").html("<div>' + html + '</div>");'
            self.javaScript(js)

            self.javaScript("showPreferences();")
            # print(self.panelVisible)

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def setSubscriptionPreference(self, url, key, value):
        try:

            for publisher in client.publishers():
                for subscription in publisher.subscriptions():
                    if (
                        subscription.exists
                        and subscription.protocol.unsecretURL() == url
                    ):

                        if value == "true":
                            value = True
                        if value == "false":
                            value = False

                        subscription.set(key, value)

                        self.setPublisherHTML(self.b64encode(publisher.canonicalURL))
                        self.setSideBarHTML()

                        break
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def showSubscriptionPreferences(self, event, b64ID):

        try:
            for publisher in client.publishers():
                for subscription in publisher.subscriptions():
                    if (
                        subscription.exists
                        and subscription.protocol.unsecretURL() == self.b64decode(b64ID)
                    ):

                        html = []

                        html.append("<h2>#(Subscription)</h2>")
                        html.append("<p>URL: <em>")
                        html.append(
                            subscription.protocol.unsecretURL()
                        )  # .replace('secretKey', '<span style="color: orange;">secretKey</span>')
                        html.append("</em></p>")

                        success, message = subscription.protocol.rootCommand()
                        if success:
                            rootCommand = message
                        else:
                            rootCommand = None

                        (
                            success,
                            message,
                        ) = subscription.protocol.installableFontsCommand()
                        if success:
                            command = message
                        else:
                            command = None

                        userName = command.userName.getText(client.locale())
                        userEmail = command.userEmail

                        html.append("<p>")
                        html.append("#(Provided by) ")
                        if rootCommand.websiteURL:
                            html.append(
                                '<a href="%s" title="%s">'
                                % (rootCommand.websiteURL, rootCommand.websiteURL)
                            )
                        html.append(
                            "<b>" + rootCommand.name.getText(client.locale()) + "</b>"
                        )
                        if rootCommand.websiteURL:
                            html.append("</a> ")
                        if userName or userEmail:
                            html.append("#(for) ")
                        if userName and userEmail:
                            html.append("<b>%s</b> (%s)" % (userName, userEmail))
                        elif userName:
                            html.append("<b>%s</b>" % (userName))
                        elif userEmail:
                            html.append("<b>%s</b>" % (userEmail))

                        html.append("</p>")

                        # Invitation

                        if client.user() and subscription.invitationAccepted():

                            html.append("<hr>")

                            html.append("<h2>#(Invitations)</h2>")
                            html.append("<p>")

                            for invitation in client.acceptedInvitations():
                                if (
                                    invitation.url
                                    == subscription.protocol.unsecretURL()
                                ):

                                    if (
                                        invitation.invitedByUserEmail
                                        or invitation.invitedByUserName
                                    ):
                                        html.append(
                                            '#(Invited by) <img src="file://##htmlroot##/userIcon.svg" style="width: 16px; height: 16px; position: relative; top: 3px; margin-top: -3px; margin-right: 2px;">'
                                        )
                                        if (
                                            invitation.invitedByUserEmail
                                            and invitation.invitedByUserName
                                        ):
                                            html.append(
                                                '<b>%s</b> (<a href="mailto:%s">%s</a>)'
                                                % (
                                                    invitation.invitedByUserName,
                                                    invitation.invitedByUserEmail,
                                                    invitation.invitedByUserEmail,
                                                )
                                            )
                                        else:
                                            html.append(
                                                "%s"
                                                % (
                                                    invitation.invitedByUserName
                                                    or invitation.invitedByUserEmail
                                                )
                                            )

                                    if invitation.time:
                                        html.append(
                                            "<br />%s"
                                            % (
                                                NaturalRelativeWeekdayTimeAndDate(
                                                    invitation.time,
                                                    locale=client.locale()[0],
                                                )
                                            )
                                        )

                            html.append("</p>")

                        # Reveal Identity
                        if subscription.parent.get("type") == "JSON":

                            html.append("<hr>")

                            html.append("<h2>#(Reveal Identity)</h2>")
                            html.append("<p>")
                            if client.user():
                                html.append(
                                    '<span><input id="revealidentity" type="checkbox" name="revealidentity" %s><label for="revealidentity">#(Reveal Your Identity For This Subscription)</label></span>'
                                    % (
                                        "checked"
                                        if subscription.get("revealIdentity")
                                        else ""
                                    )
                                )
                                html.append(
                                    """<script>
                                    $("#preferences #revealidentity").click(function() {
                                        setSubscriptionPreference("%s", "revealIdentity", $("#preferences #revealidentity").prop("checked"));
                                    });
                                </script>"""
                                    % (b64ID)
                                )
                                html.append("</p><p>")
                                html.append("#(RevealIdentityExplanation)")
                            else:
                                html.append(
                                    "#(RevealIdentityRequiresUserAccountExplanation)<br />#(PleaseCreateUserAccountExplanation)"
                                )
                            html.append("</p>")

                        # Print HTML
                        html = "".join(map(str, html))
                        html = html.replace('"', "'")
                        html = localizeString(html, html=True)
                        html = html.replace("\n", "")
                        html = self.replaceHTML(html)
                        js = (
                            '$("#preferences .centerOuter").html("<div class=\'inner\'>'
                            + html
                            + '</div>");'
                        )
                        self.javaScript(js)
                        self.javaScript("showPreferences();")

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def inviteUsers(self, b64ID, string):
        try:
            subscription = None
            for publisher in client.publishers():
                for s in publisher.subscriptions():
                    if s.exists and s.protocol.unsecretURL() == self.b64decode(b64ID):
                        subscription = s
                        break

            for email in [x.strip() for x in string.split(", ")]:

                success, message = subscription.inviteUser(email)

                if success:
                    client.downloadSubscriptions()
                    self.showSubscriptionInvitations(None, b64ID)

                else:
                    self.errorMessage(message)
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def revokeUsers(self, b64ID, string):
        try:
            subscription = None
            for publisher in client.publishers():
                for s in publisher.subscriptions():
                    if s.exists and s.protocol.unsecretURL() == self.b64decode(b64ID):
                        subscription = s
                        break

            if subscription and client.userEmail():

                dlg = wx.MessageDialog(
                    None,
                    localizeString("#(RevokeInvitationExplanationDialog)"),
                    localizeString("#(Revoke Invitation)"),
                    wx.YES_NO | wx.ICON_QUESTION,
                )
                dlg.SetYesNoLabels(
                    localizeString("#(Revoke)"), localizeString("#(Cancel)")
                )
                result = dlg.ShowModal()
                if result == wx.ID_YES:

                    for email in [x.strip() for x in string.split(", ")]:

                        success, message = subscription.revokeUser(email)

                        if success:
                            client.downloadSubscriptions()
                            self.showSubscriptionInvitations(None, b64ID)

                        else:
                            self.errorMessage(message)
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def showSubscriptionInvitations(self, event, b64ID, loadUpdates=False):
        try:
            if loadUpdates:
                client.downloadSubscriptions()

            # print('showSubscriptionInvitations()')

            url = self.b64decode(b64ID)

            for publisher in client.publishers():
                for subscription in publisher.subscriptions():
                    if (
                        subscription.exists
                        and subscription.protocol.unsecretURL() == self.b64decode(b64ID)
                    ):

                        html = []

                        html.append("<h2>#(Invitations)</h2>")
                        html.append("<p>URL: <em>")
                        html.append(
                            subscription.protocol.unsecretURL()
                        )  # .replace('secretKey', '<span style="color: orange;">secretKey</span>')
                        html.append("</em></p>")

                        success, message = subscription.protocol.rootCommand()
                        if success:
                            rootCommand = message
                        else:
                            rootCommand = None

                        (
                            success,
                            message,
                        ) = subscription.protocol.installableFontsCommand()
                        if success:
                            command = message
                        else:
                            command = None

                        userName = command.userName.getText(client.locale())
                        userEmail = command.userEmail

                        html.append("<p>")
                        html.append("#(Provided by) ")
                        if rootCommand.websiteURL:
                            html.append(
                                '<a href="%s" title="%s">'
                                % (rootCommand.websiteURL, rootCommand.websiteURL)
                            )
                        html.append(
                            "<b>" + rootCommand.name.getText(client.locale()) + "</b>"
                        )
                        if rootCommand.websiteURL:
                            html.append("</a> ")
                        if userName or userEmail:
                            html.append("#(for) ")
                        if userName and userEmail:
                            html.append("<b>%s</b> (%s)" % (userName, userEmail))
                        elif userName:
                            html.append("<b>%s</b>" % (userName))
                        elif userEmail:
                            html.append("<b>%s</b>" % (userEmail))
                        html.append("</p>")

                        html.append("<hr>")

                        html.append("<p>")
                        html.append("#(InviteUserByEmailAddressExplanation)")
                        html.append("</p>")
                        html.append("<p>")
                        html.append(
                            '<input type="text" id="inviteUserName" placeholder="#(JohnDoeEmailAddresses)"><br />'
                        )
                        html.append(
                            '<a id="inviteUsersButton" class="button">#(Invite Users)</a>'
                        )

                        html.append("</p>")

                        html.append(
                            """<script>

                            $("#inviteUsersButton").click(function() {
                                python("self.inviteUsers(____%s____, ____" + $("#inviteUserName").val() + "____)");
                            });

                        </script>"""
                            % (b64ID)
                        )

                        matchedInvitations = []

                        for invitation in client.sentInvitations():
                            if invitation.url == url:
                                matchedInvitations.append(invitation)

                        html.append("<hr>")

                        if matchedInvitations:
                            for invitation in matchedInvitations:
                                html.append(
                                    '<div class="clear" style="margin-bottom: 3px;">'
                                )
                                html.append('<div style="float: left; width: 300px;">')
                                html.append(
                                    '<img src="file://##htmlroot##/userIcon.svg" style="width: 16px; height: 16px; position: relative; top: 3px; margin-top: -3px; margin-right: 2px;">'
                                )
                                html.append(
                                    '<b>%s</b> (<a href="mailto:%s">%s</a>)'
                                    % (
                                        invitation.invitedUserName,
                                        invitation.invitedUserEmail,
                                        invitation.invitedUserEmail,
                                    )
                                )
                                html.append("</div>")

                                html.append('<div style="float: left; width: 100px;">')
                                if invitation.confirmed:
                                    html.append("✓ #(Accepted)")
                                else:
                                    html.append("<em>#(Pending)…</em>")
                                html.append("</div>")

                                html.append('<div style="float: right; width: 100px;">')
                                html.append(
                                    '<a class="revokeInvitationButton" b64ID="%s" email="%s">#(Revoke Invitation)</a>'
                                    % (b64ID, invitation.invitedUserEmail)
                                )
                                html.append("</div>")

                                html.append("</div>")  # .clear

                        else:
                            html.append("<p>#(CurrentlyNoSentInvitations)</p>")

                        html.append("<p>")
                        html.append(
                            '<a id="updateInvitations" class="button">#(UpdateInfinitive)</a>'
                        )
                        html.append("</p>")
                        html.append(
                            """<script>

                            $("#updateInvitations").click(function() {
                                python("self.showSubscriptionInvitations(None, ____%s____, loadUpdates = True)");
                            });

                            $(".revokeInvitationButton").click(function() {
                                python("self.revokeUsers(____" + $(this).attr("b64ID") + "____, ____" + $(this).attr("email") + "____)");
                            });

                        </script>"""
                            % (b64ID)
                        )

                        # Print HTML
                        html = "".join(map(str, html))
                        html = html.replace('"', "'")
                        html = localizeString(html, html=True)
                        html = html.replace("\n", "")
                        html = self.replaceHTML(html)
                        js = (
                            '$("#preferences .centerOuter").html("<div class=\'inner\'>'
                            + html
                            + '</div>");'
                        )
                        self.javaScript(js)
                        self.javaScript("showPreferences();")

                        # # Print HTML
                        # html = ''.join(map(str, html))
                        # html = html.replace('"', '\'')
                        # html = localizeString(html, html = True)
                        # html = html.replace('\n', '')
                        # html = self.replaceHTML(html)

                        # js = '$("#preferences .inner").html("' + html + '");'
                        # self.javaScript(js)

                        # self.javaScript('showPreferences();')

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def onNavigating(self, evt):
        try:
            uri = evt.GetURL()  # you may need to deal with unicode here
            if uri.startswith("x-python://"):
                code = uri.split("x-python://")[1]
                code = urllib.parse.unquote(code)
                if code.endswith("/"):
                    code = code[:-1]
                # code = code.replace('http//', 'http://')
                # code = code.replace('https//', 'https://')
                code = code.replace("____", "'")
                code = code.replace("'", "'")
                # client.log("Python code:", code)
                exec(code)
                evt.Veto()
            elif uri.startswith("http://") or uri.startswith("https://"):

                # 				server = 'https://type.world'
                # 				server = 'https://typeworld.appspot.com'
                server = client.mothership.replace("/v1", "/linkRedirect")
                webbrowser.open_new_tab(server + "?url=" + urllib.parse.quote_plus(uri))
                evt.Veto()

            elif uri.startswith("mailto:"):
                webbrowser.open(uri, new=1)

            # else:
            #   code = uri
            #   code = urllib.unquote(code)
            #   print code
            #   exec(code)
            #   evt.Veto()
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def onNavigated(self, evt):
        try:
            uri = evt.GetURL()  # you may need to deal with unicode here
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def onError(self, evt):
        try:
            client.log("Error received from WebView: %s" % evt.GetString())
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def showAddSubscription(self, evt):
        try:
            self.javaScript("showAddSubscription();")
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def handleURL(self, url, username=None, password=None):
        try:

            if url.startswith("typeworld://") or url.startswith("typeworld//"):

                for publisher in client.publishers():
                    for subscription in publisher.subscriptions():
                        if subscription.protocol.unsecretURL() == url:
                            self.setActiveSubscription(
                                self.b64encode(publisher.canonicalURL),
                                self.b64encode(subscription.protocol.unsecretURL()),
                            )
                            return

                self.javaScript(
                    "showCenterMessage('%s');"
                    % localizeString("#(Loading Subscription)")
                )
                startWorker(
                    self.addSubscription_consumer,
                    self.addSubscription_worker,
                    wargs=(url, username, password),
                )

            elif url.startswith("typeworldapp://") or url.startswith("typeworldapp//"):
                self.handleAppCommand(
                    url.replace("typeworldapp://", "").replace("typeworldapp//", "")
                )
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def handleAppCommand(self, url):
        try:

            client.log("handleAppCommand(%s)" % url)

            parts = url.split("/")

            if parts[0] == "linkTypeWorldUserAccount":

                assert len(parts) == 3 and bool(parts[1])

                # Different user
                if client.user() and client.user() != parts[1]:
                    self.errorMessage("#(AccountAlreadyLinkedExplanation)")

                # Same user, do nothing
                if client.user() and client.user() == parts[1]:
                    pass

                # New user
                else:
                    success, message = client.linkUser(parts[1], parts[2])

                    if not success:
                        self.errorMessage(message)

                    if success:
                        self.setSideBarHTML()
                        self.javaScript("hidePanel();")
                        self.message("#(JustLinkedUserAccount)")

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def addSubscriptionViaDialog(self, url, username=None, password=None):
        try:

            if url.startswith("typeworldapp://"):
                self.handleAppCommand(url.replace("typeworldapp://", ""))

            else:

                startWorker(
                    self.addSubscription_consumer,
                    self.addSubscription_worker,
                    wargs=(url, username, password),
                )
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def addSubscription_worker(self, url, username, password):
        try:

            for protocol in typeworld.api.PROTOCOLS:
                url = url.replace(protocol + "//", protocol + "://")
            # url = url.replace('http//', 'http://')
            # url = url.replace('https//', 'https://')

            # Check for known protocol
            known = False
            for protocol in typeworld.api.PROTOCOLS:
                if url.startswith(protocol):
                    known = True
                    break

            if not known:
                return (
                    False,
                    "Unknown protocol. Known are: %s" % (typeworld.api.PROTOCOLS),
                    None,
                    None,
                )

            success, message, publisher, subscription = client.addSubscription(
                url, username, password
            )

            return success, message, publisher, subscription
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def addSubscription_consumer(self, delayedResult):
        try:

            success, message, publisher, subscription = delayedResult.get()

            if success:

                # if subscription.latestVersion().response.getCommand().prefersRevealedUserIdentity:

                # 	dlg = wx.MessageDialog(self, localizeString('#(RevealUserIdentityRequest)'), localizeString('#(Reveal Identity)'), wx.YES_NO | wx.ICON_QUESTION)
                # 	dlg.SetYesNoLabels(localizeString('#(Okay)'), localizeString('#(Cancel)'))
                # 	result = dlg.ShowModal() == wx.ID_YES
                # 	dlg.Destroy()

                # 	if result:
                # 		subscription.set('revealIdentity', True)

                b64ID = self.b64encode(publisher.canonicalURL)

                self.setSideBarHTML()
                self.setPublisherHTML(b64ID)
                self.javaScript("hidePanel();")

            else:

                self.errorMessage(message)

            # Reset Form
            self.javaScript('$("#addSubscriptionFormSubmitButton").show();')
            self.javaScript('$("#addSubscriptionFormCancelButton").show();')
            self.javaScript('$("#addSubscriptionFormSubmitAnimation").hide();')

            self.javaScript("hideCenterMessage();")

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def acceptInvitation(self, url):
        try:

            self.javaScript("startLoadingAnimation();")

            startWorker(
                self.acceptInvitation_consumer,
                self.acceptInvitation_worker,
                wargs=(url,),
            )

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def acceptInvitation_worker(self, url):
        try:

            success, message = client.acceptInvitation(self.b64decode(url))
            return success, message, url
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def acceptInvitation_consumer(self, delayedResult):
        try:

            success, message, url = delayedResult.get()

            if success:

                self.javaScript('$("#%s.invitation").slideUp();' % url)

                for invitation in client.acceptedInvitations():
                    if invitation.url == self.b64decode(url):

                        publisherURL = URL(invitation.canonicalURL).HTTPURL()
                        client.set("currentPublisher", publisherURL)
                        publisher = client.publisher(publisherURL)
                        publisher.set("currentSubscription", invitation.url)
                        self.setSideBarHTML()
                        self.setPublisherHTML(self.b64encode(publisherURL))
                        self.setBadges()

            else:

                pass

            self.javaScript("stopLoadingAnimation();")
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def declineInvitation(self, url):
        try:
            invitation = None

            for invitation in client.acceptedInvitations():
                if invitation.url == self.b64decode(url):
                    for publisher in client.publishers():
                        for subscription in publisher.subscriptions():
                            if invitation.url == subscription.protocol.unsecretURL():

                                name = (
                                    publisher.name(locale=client.locale())[0]
                                    + " ("
                                    + subscription.name(locale=client.locale())
                                    + ")"
                                )

                                dlg = wx.MessageDialog(
                                    self,
                                    localizeString(
                                        "#(Are you sure)\n#(RemoveInvitationConfirmationExplanation)"
                                    ),
                                    localizeString("#(Remove X)").replace(
                                        "%name%", name
                                    ),
                                    wx.YES_NO | wx.ICON_QUESTION,
                                )
                                dlg.SetYesNoLabels(
                                    localizeString("#(Remove)"),
                                    localizeString("#(Cancel)"),
                                )
                                result = dlg.ShowModal() == wx.ID_YES
                                dlg.Destroy()

                                if result:
                                    self.javaScript("startLoadingAnimation();")
                                    startWorker(
                                        self.declineInvitation_consumer,
                                        self.declineInvitation_worker,
                                        wargs=(url,),
                                    )

            for invitation in client.pendingInvitations():
                if invitation.url == self.b64decode(url):
                    dlg = wx.MessageDialog(
                        self,
                        localizeString("#(Are you sure)"),
                        localizeString("#(Decline Invitation)"),
                        wx.YES_NO | wx.ICON_QUESTION,
                    )
                    dlg.SetYesNoLabels(
                        localizeString("#(Remove)"), localizeString("#(Cancel)")
                    )
                    result = dlg.ShowModal() == wx.ID_YES
                    dlg.Destroy()

                    if result:
                        self.javaScript("startLoadingAnimation();")
                        startWorker(
                            self.declineInvitation_consumer,
                            self.declineInvitation_worker,
                            wargs=(url,),
                        )
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def declineInvitation_worker(self, url):
        try:
            success, message = client.declineInvitation(self.b64decode(url))
            return success, message, url
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def declineInvitation_consumer(self, delayedResult):
        try:
            success, message, url = delayedResult.get()

            if success:

                self.javaScript('$("#%s.invitation").slideUp();' % url)

                if len(client.pendingInvitations()) == 0:
                    if client.publishers():
                        self.setPublisherHTML(
                            self.b64encode(client.publishers()[0].canonicalURL)
                        )
                    else:
                        client.set("currentPublisher", "")
                self.setSideBarHTML()
                self.setBadges()

            else:

                pass

            self.javaScript("stopLoadingAnimation();")

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def removePublisher(self, evt, b64ID):
        try:

            self.allowedToPullServerUpdates = False

            publisher = client.publisher(self.b64decode(b64ID))

            dlg = wx.MessageDialog(
                self,
                localizeString("#(Are you sure)"),
                localizeString("#(Remove X)").replace(
                    "%name%", localizeString(publisher.name(client.locale())[0])
                ),
                wx.YES_NO | wx.ICON_QUESTION,
            )
            dlg.SetYesNoLabels(localizeString("#(Remove)"), localizeString("#(Cancel)"))
            result = dlg.ShowModal() == wx.ID_YES
            dlg.Destroy()

            if result:

                publisher.delete()
                client.set("currentPublisher", "")
                self.setSideBarHTML()
                self.javaScript("hideMain();")
                self.javaScript("hideMetadata();")

            self.allowedToPullServerUpdates = True
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def removeSubscription(self, evt, b64ID):
        try:

            self.allowedToPullServerUpdates = False

            for publisher in client.publishers():
                for subscription in publisher.subscriptions():
                    if subscription.protocol.unsecretURL() == self.b64decode(b64ID):

                        dlg = wx.MessageDialog(
                            self,
                            localizeString("#(Are you sure)"),
                            localizeString("#(Remove X)").replace(
                                "%name%",
                                localizeString(subscription.name(client.locale())),
                            ),
                            wx.YES_NO | wx.ICON_QUESTION,
                        )
                        dlg.SetYesNoLabels(
                            localizeString("#(Remove)"), localizeString("#(Cancel)")
                        )
                        result = dlg.ShowModal() == wx.ID_YES
                        dlg.Destroy()

                        if result:
                            subscription.delete()

                            if publisher.subscriptions():
                                publisher.set(
                                    "currentSubscription",
                                    publisher.subscriptions()[0].protocol.unsecretURL(),
                                )
                                self.setPublisherHTML(
                                    self.b64encode(publisher.canonicalURL)
                                )
                            else:
                                self.javaScript("hideMain();")
                                self.javaScript("hideMetadata();")

            self.setSideBarHTML()

            self.allowedToPullServerUpdates = True
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def publisherPreferences(self, i):
        try:
            client.log(("publisherPreferences", i))
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def installAllFonts(
        self,
        b64publisherID,
        b64subscriptionID,
        b64familyID,
        b64packageKeyword,
        formatName,
    ):
        try:
            fonts = []

            publisherID = self.b64decode(b64publisherID)
            subscriptionID = self.b64decode(b64subscriptionID)
            familyID = self.b64decode(b64familyID)
            packageKeyword = self.b64decode(b64packageKeyword)
            publisher = client.publisher(publisherID)
            subscription = publisher.subscription(subscriptionID)
            family = subscription.familyByID(familyID)

            for font in family.fonts:
                if (
                    packageKeyword in font.getPackageKeywords()
                    and font.format == formatName
                ):
                    if not subscription.installedFontVersion(font.uniqueID):
                        fonts.append(
                            [
                                b64publisherID,
                                b64subscriptionID,
                                self.b64encode(font.uniqueID),
                                font.getVersions()[-1].number,
                            ]
                        )

            self.installFonts(fonts)
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def removeAllFonts(
        self,
        b64publisherID,
        b64subscriptionID,
        b64familyID,
        b64packageKeyword,
        formatName,
    ):
        try:
            fonts = []

            publisherID = self.b64decode(b64publisherID)
            subscriptionID = self.b64decode(b64subscriptionID)
            familyID = self.b64decode(b64familyID)
            packageKeyword = self.b64decode(b64packageKeyword)
            publisher = client.publisher(publisherID)
            subscription = publisher.subscription(subscriptionID)
            family = subscription.familyByID(familyID)

            for font in family.fonts:
                if (
                    packageKeyword in font.getPackageKeywords()
                    and font.format == formatName
                ):
                    if subscription.installedFontVersion(font.uniqueID):
                        fonts.append(
                            [
                                b64publisherID,
                                b64subscriptionID,
                                self.b64encode(font.uniqueID),
                            ]
                        )

            self.removeFonts(fonts)
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def installFontFromMenu(
        self, event, b64publisherURL, b64subscriptionURL, b64fontID, version
    ):
        try:
            client.log("installFontFromMenu()")

            self.installFont(b64publisherURL, b64subscriptionURL, b64fontID, version)
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def installFont(self, b64publisherURL, b64subscriptionURL, b64fontID, version):
        try:
            self.selectFont(b64fontID)
            self.javaScript('$(".font.%s").addClass("loading");' % b64fontID)
            self.javaScript('$("#metadata .seatsInstalled").fadeTo(500, .1);')
            startWorker(
                self.installFonts_consumer,
                self.installFonts_worker,
                wargs=([[[b64publisherURL, b64subscriptionURL, b64fontID, version]]]),
            )
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def installFonts(self, fonts):

        try:
            for b64publisherURL, b64subscriptionURL, b64fontID, version in fonts:

                self.javaScript('$(".font.%s").addClass("loading");' % b64fontID)
                # self.javaScript('$("#%s.font").find("a.installButton").hide();' % b64fontID)
                # self.javaScript('$("#%s.font").find("a.removeButton").hide();' % b64fontID)
                # self.javaScript('$("#%s.font").find("a.status").show();' % b64fontID)
                # self.javaScript('$("#%s.font").find("a.more").hide();' % b64fontID)

            startWorker(
                self.installFonts_consumer, self.installFonts_worker, wargs=([fonts])
            )
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def installFonts_worker(self, fonts):

        try:

            fontsBySubscription = {}

            for b64publisherURL, b64subscriptionURL, b64fontID, version in fonts:

                publisherURL = self.b64decode(b64publisherURL)
                subscriptionURL = self.b64decode(b64subscriptionURL)
                fontID = self.b64decode(b64fontID)

                publisher = client.publisher(publisherURL)
                subscription = publisher.subscription(subscriptionURL)

                if subscription.fontByID(fontID):

                    if not subscription in fontsBySubscription:
                        fontsBySubscription[subscription] = []

                    fontsBySubscription[subscription].append([fontID, version])

                # Remove other installed versions
                installedVersion = subscription.installedFontVersion(fontID)
                if installedVersion and installedVersion != version:
                    success, message = subscription.removeFonts([fontID])
                    if success == False:
                        return success, message, b64publisherURL, subscription, fonts

            for subscription in fontsBySubscription:

                # Install new font
                success, message = subscription.installFonts(
                    fontsBySubscription[subscription]
                )

                if success == False:
                    return success, message, b64publisherURL, subscription, fonts

            # TODO: differentiate between b64publisherURLs here, as fonts could be from different publishers. Works for now, until fonts can be mixed in collections
            return True, None, b64publisherURL, subscription, fonts
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def installFonts_consumer(self, delayedResult):
        try:
            success, message, b64publisherURL, subscription, fonts = delayedResult.get()

            self.setFontStatuses(fonts)

            if success:

                pass

            else:

                for b64publisherURL, b64subscriptionURL, b64fontID, version in fonts:
                    self.javaScript('$(".font.%s").removeClass("loading");' % b64fontID)
                self.errorMessage(message, subscription=subscription)

            self.setSideBarHTML()
            self.setBadges()
            self.setPublisherHTML(b64publisherURL)
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def removeFont(self, b64publisherURL, b64subscriptionURL, b64fontID):
        try:
            self.selectFont(b64fontID)
            self.javaScript('$(".font.%s").addClass("loading");' % b64fontID)
            self.javaScript('$("#metadata .seatsInstalled").fadeTo(500, .1);')
            startWorker(
                self.removeFonts_consumer,
                self.removeFonts_worker,
                wargs=([[[b64publisherURL, b64subscriptionURL, b64fontID]]]),
            )
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def removeFonts(self, fonts):
        try:
            for b64publisherURL, b64subscriptionURL, b64fontID in fonts:

                self.javaScript('$(".font.%s").addClass("loading");' % b64fontID)
                # self.javaScript('$("#%s.font").find("a.installButton").hide();' % b64fontID)
                # self.javaScript('$("#%s.font").find("a.removeButton").hide();' % b64fontID)
                # self.javaScript('$("#%s.font").find("a.status").show();' % b64fontID)
                # self.javaScript('$("#%s.font").find("a.more").hide();' % b64fontID)

            startWorker(
                self.removeFonts_consumer, self.removeFonts_worker, wargs=([fonts])
            )
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def removeFonts_worker(self, fonts):
        try:
            fontsBySubscription = {}

            for b64publisherURL, b64subscriptionURL, b64fontID in fonts:

                publisherURL = self.b64decode(b64publisherURL)
                subscriptionURL = self.b64decode(b64subscriptionURL)
                fontID = self.b64decode(b64fontID)

                publisher = client.publisher(publisherURL)
                subscription = publisher.subscription(subscriptionURL)

                if subscription.fontByID(fontID):

                    if not subscription in fontsBySubscription:
                        fontsBySubscription[subscription] = []

                    fontsBySubscription[subscription].append(fontID)

            for subscription in fontsBySubscription:

                # Install new font
                success, message = subscription.removeFonts(
                    fontsBySubscription[subscription]
                )

                if success == False:
                    return success, message, b64publisherURL, subscription, fonts

            # TODO: differentiate between b64publisherURLs here, as fonts could be from different publishers. Works for now, until fonts can be mixed in collections
            return True, None, b64publisherURL, subscription, fonts
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def removeFonts_consumer(self, delayedResult):
        try:
            success, message, b64publisherURL, subscription, fonts = delayedResult.get()

            self.setFontStatuses(fonts)

            if success:

                pass

            else:

                if type(message) == str:
                    self.errorMessage(message)
                else:
                    self.errorMessage("Server: %s" % message.getText(client.locale()))

            self.setSideBarHTML()
            self.setBadges()
            self.setPublisherHTML(b64publisherURL)
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def updateAllFonts(self, evt, publisherB64ID, subscriptionB64ID):
        try:
            fonts = []

            if publisherB64ID:
                publisher = client.publisher(self.b64decode(publisherB64ID))
                for subscription in publisher.subscriptions():
                    subscriptionB64ID = self.b64encode(
                        subscription.protocol.unsecretURL()
                    )

                    success, message = subscription.protocol.installableFontsCommand()
                    if success:
                        command = message
                    else:
                        command = None

                    for foundry in command.foundries:
                        for family in foundry.families:
                            for font in family.fonts:
                                installedFontVersion = (
                                    subscription.installedFontVersion(font=font)
                                )
                                if (
                                    installedFontVersion
                                    and subscription.installedFontVersion(font=font)
                                    != font.getVersions()[-1].number
                                ):
                                    fonts.append(
                                        [
                                            publisherB64ID,
                                            subscriptionB64ID,
                                            self.b64encode(font.uniqueID),
                                            font.getVersions()[-1].number,
                                        ]
                                    )

            elif subscriptionB64ID:

                for publisher in client.publishers():
                    for subscription in publisher.subscriptions():
                        if subscription.protocol.unsecretURL() == self.b64decode(
                            subscriptionB64ID
                        ):
                            publisherB64ID = self.b64encode(publisher.canonicalURL)
                            break

                success, message = subscription.protocol.installableFontsCommand()
                if success:
                    command = message
                else:
                    command = None

                for foundry in command.foundries:
                    for family in foundry.families:
                        for font in family.fonts:
                            installedFontVersion = subscription.installedFontVersion(
                                font=font
                            )
                            if (
                                installedFontVersion
                                and subscription.installedFontVersion(font=font)
                                != font.getVersions()[-1].number
                            ):
                                fonts.append(
                                    [
                                        publisherB64ID,
                                        subscriptionB64ID,
                                        self.b64encode(font.uniqueID),
                                        font.getVersions()[-1].number,
                                    ]
                                )

            self.installFonts(fonts)

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def threadSafeExec(self, code):
        try:
            # print("threadSafeExec:", code)
            startWorker(
                self.threadSafeExec_consumer, self.threadSafeExec_worker, wargs=(code,)
            )
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def threadSafeExec_worker(self, code):
        try:
            return code

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def threadSafeExec_consumer(self, delayedResult):
        try:
            code = delayedResult.get()
            exec(code)

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def setFontStatuses(self, fonts):
        try:

            for line in fonts:

                b64publisherURL = line[0]
                b64subscriptionURL = line[1]
                b64fontID = line[2]

                subscription = client.publisher(
                    self.b64decode(b64publisherURL)
                ).subscription(self.b64decode(b64subscriptionURL))
                font = subscription.fontByID(self.b64decode(b64fontID))
                installedVersion = subscription.installedFontVersion(font=font)

                self.javaScript('$(".font.%s").removeClass("loading");' % b64fontID)
                self.javaScript('$(".font.%s").removeClass("installed");' % b64fontID)
                self.javaScript('$(".font.%s").removeClass("installed");' % b64fontID)
                self.javaScript(
                    '$(".font.%s").removeClass("notInstalled");' % b64fontID
                )
                self.javaScript(
                    '$(".font.%s").removeClass("notInstalled");' % b64fontID
                )
                if installedVersion:
                    self.javaScript('$(".font.%s").addClass("installed");' % b64fontID)
                else:
                    self.javaScript(
                        '$(".font.%s").addClass("notInstalled");' % b64fontID
                    )

                # metadata bar
                self.javaScript(
                    '$(".font.%s .version .status.install").show();' % b64fontID
                )
                self.javaScript(
                    '$(".font.%s .version .status.remove").hide();' % b64fontID
                )
                self.javaScript(
                    '$(".font.%s .version .label.installedVersion").hide();' % b64fontID
                )

                if installedVersion:
                    self.javaScript(
                        '$(".font.%s .version.%s .status.install").hide();'
                        % (b64fontID, self.versionEncode(installedVersion))
                    )
                    self.javaScript(
                        '$(".font.%s .version.%s .status.remove").show();'
                        % (b64fontID, self.versionEncode(installedVersion))
                    )
                    self.javaScript(
                        '$(".font.%s .version.%s .label.installedVersion").show();'
                        % (b64fontID, self.versionEncode(installedVersion))
                    )

                html = self.fontInstalledText(font)
                html = html.replace('"', "'")
                html = html.replace("\n", "")
                html = localizeString(html, html=True)
                html = self.replaceHTML(html)
                self.javaScript(
                    '$(".font.%s .installedText").html("%s");' % (b64fontID, html)
                )
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def checkFontExpirations(self):
        try:
            fonts = []

            for publisher in client.publishers():
                for subscription in publisher.subscriptions():
                    for font in subscription.installedFonts():
                        if font.expiry and time.time() > font.expiry:

                            fonts.append(
                                [
                                    self.b64encode(publisher.canonicalURL),
                                    self.b64encode(subscription.protocol.unsecretURL()),
                                    self.b64encode(font.uniqueID),
                                ]
                            )

            if fonts:
                self.removeFonts(fonts)
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def onContextMenu(self, x, y, target, b64ID):

        try:
            #       print x, y, target, b64ID, self.b64decode(b64ID)

            x = max(0, int(x) - 70)

            if "contextmenu publisher" in target:

                for publisher in client.publishers():
                    if publisher.canonicalURL == self.b64decode(b64ID):
                        break

                menu = wx.Menu()

                if len(publisher.subscriptions()) > 1:
                    item = wx.MenuItem(
                        menu,
                        wx.NewIdRef(count=1),
                        localizeString("#(Update All Subscriptions)"),
                    )
                    menu.Append(item)
                    menu.Bind(
                        wx.EVT_MENU, partial(self.reloadPublisher, b64ID=b64ID), item
                    )
                else:
                    item = wx.MenuItem(
                        menu,
                        wx.NewIdRef(count=1),
                        localizeString("#(Update Subscription)"),
                    )
                    menu.Append(item)
                    menu.Bind(
                        wx.EVT_MENU,
                        partial(
                            self.reloadSubscription,
                            b64ID=self.b64encode(
                                publisher.subscriptions()[0].protocol.unsecretURL()
                            ),
                            subscription=None,
                        ),
                        item,
                    )

                if publisher.amountOutdatedFonts():
                    item = wx.MenuItem(
                        menu,
                        wx.NewIdRef(count=1),
                        localizeString("#(Update All Fonts)"),
                    )
                    menu.Append(item)
                    menu.Bind(
                        wx.EVT_MENU,
                        partial(
                            self.updateAllFonts,
                            publisherB64ID=b64ID,
                            subscriptionB64ID=None,
                        ),
                        item,
                    )

                if publisher.get("type") == "GitHub":
                    item = wx.MenuItem(
                        menu,
                        wx.NewIdRef(count=1),
                        localizeString("#(Publisher Preferences)"),
                    )
                    menu.Append(item)
                    menu.Bind(
                        wx.EVT_MENU,
                        partial(self.showPublisherPreferences, b64ID=b64ID),
                        item,
                    )

                if len(publisher.subscriptions()) == 1:
                    item = wx.MenuItem(
                        menu,
                        wx.NewIdRef(count=1),
                        localizeString("#(Subscription Preferences)"),
                    )
                    menu.Append(item)
                    menu.Bind(
                        wx.EVT_MENU,
                        partial(
                            self.showSubscriptionPreferences,
                            b64ID=self.b64encode(
                                publisher.subscriptions()[0].protocol.unsecretURL()
                            ),
                        ),
                        item,
                    )

                    item = wx.MenuItem(
                        menu, wx.NewIdRef(count=1), localizeString("#(Invite Users)")
                    )
                    menu.Append(item)
                    menu.Bind(
                        wx.EVT_MENU,
                        partial(
                            self.showSubscriptionInvitations,
                            b64ID=self.b64encode(
                                publisher.subscriptions()[0].protocol.unsecretURL()
                            ),
                        ),
                        item,
                    )

                item = wx.MenuItem(
                    menu, wx.NewIdRef(count=1), localizeString("#(Show in Finder)")
                )
                menu.Append(item)
                menu.Bind(
                    wx.EVT_MENU, partial(self.showPublisherInFinder, b64ID=b64ID), item
                )

                menu.AppendSeparator()

                item = wx.MenuItem(
                    menu, wx.NewIdRef(count=1), localizeString("#(Remove)")
                )
                menu.Append(item)
                menu.Bind(wx.EVT_MENU, partial(self.removePublisher, b64ID=b64ID), item)

                self.PopupMenu(menu, wx.Point(int(x), int(y)))
                menu.Destroy()

            elif "contextmenu subscription" in target:
                menu = wx.Menu()

                item = wx.MenuItem(
                    menu, wx.NewIdRef(count=1), localizeString("#(Update Subscription)")
                )
                menu.Append(item)
                menu.Bind(
                    wx.EVT_MENU,
                    partial(self.reloadSubscription, b64ID=b64ID, subscription=None),
                    item,
                )

                for publisher in client.publishers():
                    for subscription in publisher.subscriptions():
                        if subscription.protocol.unsecretURL() == self.b64decode(b64ID):
                            if publisher.amountOutdatedFonts():
                                item = wx.MenuItem(
                                    menu,
                                    wx.NewIdRef(count=1),
                                    localizeString("#(Update All Fonts)"),
                                )
                                menu.Append(item)
                                menu.Bind(
                                    wx.EVT_MENU,
                                    partial(
                                        self.updateAllFonts,
                                        publisherB64ID=None,
                                        subscriptionB64ID=b64ID,
                                    ),
                                    item,
                                )
                            break

                item = wx.MenuItem(
                    menu,
                    wx.NewIdRef(count=1),
                    localizeString("#(Subscription Preferences)"),
                )
                menu.Append(item)
                menu.Bind(
                    wx.EVT_MENU,
                    partial(self.showSubscriptionPreferences, b64ID=b64ID),
                    item,
                )

                item = wx.MenuItem(
                    menu, wx.NewIdRef(count=1), localizeString("#(Invite Users)")
                )
                menu.Append(item)
                menu.Bind(
                    wx.EVT_MENU,
                    partial(self.showSubscriptionInvitations, b64ID=b64ID),
                    item,
                )

                menu.AppendSeparator()

                item = wx.MenuItem(
                    menu, wx.NewIdRef(count=1), localizeString("#(Remove)")
                )
                menu.Append(item)
                menu.Bind(
                    wx.EVT_MENU, partial(self.removeSubscription, b64ID=b64ID), item
                )

                self.PopupMenu(menu, wx.Point(int(x), int(y)))
                menu.Destroy()

            elif "contextmenu font" in target:
                menu = wx.Menu()

                fontID = self.b64decode(b64ID)

                for publisher in client.publishers():
                    for subscription in publisher.subscriptions():

                        (
                            success,
                            message,
                        ) = subscription.protocol.installableFontsCommand()
                        if success:
                            command = message
                        else:
                            command = None

                        for foundry in command.foundries:
                            for family in foundry.families:
                                for font in family.fonts:
                                    if font.uniqueID == fontID:

                                        if subscription.installedFontVersion(
                                            font.uniqueID
                                        ):
                                            item = wx.MenuItem(
                                                menu,
                                                wx.NewIdRef(count=1),
                                                localizeString("#(Show in Finder)"),
                                            )
                                            menu.Bind(
                                                wx.EVT_MENU,
                                                partial(
                                                    self.showFontInFinder,
                                                    subscription=subscription,
                                                    fontID=fontID,
                                                ),
                                                item,
                                            )
                                            menu.Append(item)

                                        # create a submenu
                                        subMenu = wx.Menu()
                                        menu.AppendMenu(
                                            wx.NewIdRef(count=1),
                                            localizeString("#(Install Version)"),
                                            subMenu,
                                        )

                                        for version in font.getVersions():

                                            if (
                                                subscription.installedFontVersion(
                                                    font.uniqueID
                                                )
                                                == version.number
                                            ):
                                                item = wx.MenuItem(
                                                    subMenu,
                                                    wx.NewIdRef(count=1),
                                                    str(version.number),
                                                    "",
                                                    wx.ITEM_RADIO,
                                                )

                                            else:
                                                item = wx.MenuItem(
                                                    subMenu,
                                                    wx.NewIdRef(count=1),
                                                    str(version.number),
                                                )

                                            if WIN:
                                                installHere = menu
                                            else:
                                                installHere = subMenu
                                            installHere.Bind(
                                                wx.EVT_MENU,
                                                partial(
                                                    self.installFontFromMenu,
                                                    b64publisherURL=self.b64encode(
                                                        publisher.canonicalURL
                                                    ),
                                                    b64subscriptionURL=self.b64encode(
                                                        subscription.protocol.unsecretURL()
                                                    ),
                                                    b64fontID=b64ID,
                                                    version=version.number,
                                                ),
                                                item,
                                            )
                                            subMenu.Append(item)

                                        #    def installFontFromMenu(self, event, b64publisherURL, b64subscriptionURL, b64fontID, version):

                                        self.PopupMenu(menu, wx.Point(int(x), int(y)))
                                        menu.Destroy()

                                        break

            else:

                menu = wx.Menu()

                item = wx.MenuItem(
                    menu, wx.NewIdRef(count=1), localizeString("#(Preferences)")
                )
                menu.Append(item)
                menu.Bind(wx.EVT_MENU, self.onPreferences, item)

                self.PopupMenu(menu, wx.Point(int(x), int(y)))
                menu.Destroy()
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def showPublisherPreferences(self, event, b64ID):
        try:

            for publisher in client.publishers():
                if publisher.exists and publisher.canonicalURL == self.b64decode(b64ID):

                    html = []

                    html.append(
                        "<h2>%s (%s)</h2>"
                        % (publisher.name(client.locale())[0], publisher.get("type"))
                    )
                    # if publisher.get('type') == 'GitHub':

                    # 	# Rate limits
                    # 	limits, responses = publisher.readGitHubResponse('https://api.github.com/rate_limit')
                    # 	limits = json.loads(limits)

                    # 	html.append('<p>')
                    # 	html.append('#(Username)<br />')
                    # 	html.append('<input type="text" id="username" value="%s">' % (publisher.get('username') or ''))
                    # 	html.append('#(Password)<br />')
                    # 	html.append('<input type="password" id="password" value="%s">' % (publisher.getPassword(publisher.get('username')) if publisher.get('username') else ''))
                    # 	html.append('</p>')
                    # 	html.append('<p>')
                    # 	html.append('#(GitHubRequestLimitExplanation)<br />')
                    # 	html.append(localizeString('#(GitHubRequestLimitRemainderExplanation)').replace('%requests%', str(limits['rate']['remaining'])).replace('%time%', datetime.datetime.fromtimestamp(limits['rate']['reset']).strftime('%Y-%m-%d %H:%M:%S')))
                    # 	html.append('</p>')
                    # 	html.append('<script>$("#publisherPreferences #username").blur(function() { setPublisherPreference("%s", "username", $("#publisherPreferences #username").val());});</script>' % (b64ID))
                    # 	html.append('<script>$("#publisherPreferences #password").blur(function() { if ($("#publisherPreferences #username").val()) { setPublisherPassword("%s", $("#publisherPreferences #username").val(), $("#publisherPreferences #password").val()); }});</script>' % (b64ID))

                    # Print HTML
                    html = "".join(map(str, html))
                    html = html.replace('"', "'")
                    html = html.replace("\n", "")
                    html = localizeString(html)
                    #       print html
                    js = '$("#publisherPreferences .inner").html("' + html + '");'
                    self.javaScript(js)

                    self.javaScript("showPublisherPreferences();")

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def showPublisherInFinder(self, evt, b64ID):
        try:

            publisher = client.publisher(self.b64decode(b64ID))
            path = publisher.folder()

            if not os.path.exists(path):
                os.makedirs(path)

            import subprocess

            subprocess.call(["open", path])
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def showFontInFinder(self, evt, subscription, fontID):
        try:

            font = subscription.fontByID(fontID)
            version = subscription.installedFontVersion(fontID)
            folder = subscription.parent.folder()
            font, path = subscription.fontPath(folder, fontID)

            import subprocess

            subprocess.call(["open", "-R", path])

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def wentOnline(self):
        print("wentOnline()")
        client.wentOnline()
        self.pullServerUpdates(force=True)

    def wentOffline(self):
        client.wentOffline()

    def checkIfOnline(self):
        isOnline = client.online()
        if (
            not self.online
            and isOnline
            or self.online
            and isOnline
            and time.time() - self.lastOnlineCheck > 40  # after sleep
        ):
            self.wentOnline()
            self.online = True
        elif self.online and not isOnline:
            self.wentOffline()
            self.online = False

        self.lastOnlineCheck = time.time()

    def minutely(self):
        try:

            if WIN:
                path = os.path.expanduser(
                    "~/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Type.World.lnk"
                )
                if os.path.exists(path):
                    os.remove(path)

            self.checkIfOnline()

            self.lastMinuteCheck = time.time()

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def reloadPublisher(self, evt, b64ID):
        try:
            client.prepareUpdate()

            publisher = client.publisher(self.b64decode(b64ID))
            for subscription in publisher.subscriptions():
                if subscription.exists:
                    self.reloadSubscription(None, None, subscription)

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def reloadSubscription(self, evt, b64ID=None, subscription=None):
        try:

            if subscription:
                pass
            else:
                ID = self.b64decode(b64ID)

                for publisher in client.publishers():
                    subscription = publisher.subscription(ID)
                    if subscription and subscription.exists:
                        break

            startWorker(
                self.reloadSubscription_consumer,
                self.reloadSubscription_worker,
                wargs=(subscription,),
            )

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def reloadSubscription_worker(self, subscription):
        try:

            success, message, changes = subscription.update()
            return success, message, changes, subscription
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def reloadSubscription_consumer(self, delayedResult):
        success, message, changes, subscription = delayedResult.get()
        pass

    def displaySyncProblems(self):
        try:
            self.errorMessage("\n\n".join(client.syncProblems()))
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def displayPublisherSidebarAlert(self, b64publisherID):
        try:
            publisher = client.publisher(self.b64decode(b64publisherID))

            for message in publisher.updatingProblem():
                self.errorMessage(message)
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def displaySubscriptionSidebarAlert(self, b64subscriptionID):
        try:

            for publisher in client.publishers():
                for subscription in publisher.subscriptions():
                    if subscription.protocol.unsecretURL() == self.b64decode(
                        b64subscriptionID
                    ):
                        message = subscription.updatingProblem()
                        if subscription.updatingProblem():
                            self.errorMessage(message)
                        else:
                            self.errorMessage("No error message defined :/")

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def errorMessage(self, message, title="", subscription=None):
        try:

            if type(message) in (list, tuple):
                assert len(message) == 2
                string, title = message

            elif type(message) == typeworld.api.MultiLanguageText:
                string = message.getText(locale=client.locale())

            else:
                string = message

            keepString = string
            string = localizeString(string)
            title = localizeString(title)

            dlg = wx.MessageDialog(
                self, string or "No message defined", title, wx.ICON_ERROR
            )
            result = dlg.ShowModal()
            dlg.Destroy()

            if (
                keepString == "#(response.loginRequired)"
                and subscription
                and subscription.protocol.rootCommand()[1].loginURL
            ):
                url = subscription.protocol.rootCommand()[1].loginURL
                url = addAttributeToURL(
                    url,
                    "subscriptionID=%s"
                    % typeworld.client.URL(subscription.url).subscriptionID,
                )
                webbrowser.open(url, new=1)
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def message(self, message, title=""):
        try:

            if type(message) in (list, tuple):
                assert len(message) == 2
                message, title = message

            elif type(message) == typeworld.api.MultiLanguageText:
                message = message.getText(locale=client.locale())

            client.log(message)

            message = localizeString(message)
            title = localizeString(title)

            dlg = wx.MessageDialog(self, message or "No message defined", title)
            result = dlg.ShowModal()
            dlg.Destroy()
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def fontHTML(self, font):
        try:

            subscription = font.parent.parent.parent

            html = []

            # Print HTML
            html = "".join(map(str, html))
            html = html.replace('"', "'")
            html = html.replace("\n", "")
            html = localizeString(html)
            html = self.replaceHTML(html)

            return html
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def setActiveSubscription(self, publisherB64ID, subscriptionB64ID):
        try:

            publisherID = self.b64decode(publisherB64ID)
            subscriptionID = self.b64decode(subscriptionB64ID)

            publisher = client.publisher(publisherID)
            subscription = publisher.subscription(subscriptionID)
            publisher.set("currentSubscription", subscription.protocol.unsecretURL())
            self.setPublisherHTML(publisherB64ID)
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def selectFont(self, b64ID):
        try:

            fontID = self.b64decode(b64ID)
            publisher = client.publisher(client.get("currentPublisher"))
            subscription = publisher.subscription(publisher.get("currentSubscription"))
            subscription.set("currentFont", fontID)
            font = subscription.fontByID(fontID)

            self.setMetadataHTML(b64ID)
            self.javaScript("showMetadata();")
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def showMetadataCategory(self, categoryName):
        try:
            client.set("metadataCategory", categoryName)

            publisher = client.publisher(client.get("currentPublisher"))
            subscription = publisher.subscription(publisher.get("currentSubscription"))
            font = subscription.fontByID(subscription.get("currentFont"))

            self.setMetadataHTML(self.b64encode(font.uniqueID))
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def setFontImage(self, index):
        try:

            index = int(index)
            publisher = client.publisher(client.get("currentPublisher"))
            subscription = publisher.subscription(publisher.get("currentSubscription"))
            font = subscription.fontByID(subscription.get("currentFont"))
            success, billboard, mimeType = client.resourceByURL(
                font.parent.billboardURLs[index], binary=True
            )
            if success:
                data = "data:%s;base64,%s" % (mimeType, billboard)
            else:
                data = font.parent.billboardURLs[index]

            self.javaScript('$("#fontBillboard").attr("src","%s");' % (data))
            self.javaScript('$(".fontBillboardLinks").removeClass("selected");')
            self.javaScript('$("#fontBillboardLink_%s").addClass("selected");' % index)
            font.parent.parent.parent.parent.set("currentFontImage", int(index))

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def setMetadataHTML(self, b64ID):
        try:

            if b64ID:

                fontID = self.b64decode(b64ID)
                publisher = client.publisher(client.get("currentPublisher"))
                subscription = publisher.subscription(
                    publisher.get("currentSubscription")
                )
                subscription.set("currentFont", fontID)
                font = subscription.fontByID(fontID)

                html = []

                if font:
                    foundry = font.parent.parent
                    subscription = font.parent.parent.parent.parent.subscription
                    installedVersion = subscription.installedFontVersion(font.uniqueID)

                    # metadata

                    theme = self.theme()
                    styling = FoundryStyling(foundry, theme)
                    html.append(styling.informationView())

                    if font.parent.billboardURLs:

                        index = (
                            font.parent.parent.parent.parent.get("currentFontImage")
                            or 0
                        )
                        if index > len(font.parent.billboardURLs) - 1:
                            index = 0
                            font.parent.parent.parent.parent.set(
                                "currentFontImage", int(index)
                            )

                        html.append('<div style="max-height: 400px; height: 300px;">')

                        success, billboard, mimeType = client.resourceByURL(
                            font.parent.billboardURLs[index], binary=True
                        )
                        if success:
                            html.append(
                                '<img id="fontBillboard" src="data:%s;base64,%s" style="width: 300px;">'
                                % (mimeType, billboard)
                            )
                        else:
                            html.append(
                                '<img id="fontBillboard" src="%s" style="width: 300px;">'
                                % (font.parent.billboardURLs[index])
                            )

                        html.append("</div>")
                        if len(font.parent.billboardURLs) > 1:
                            html.append(
                                '<div style="padding: 5px; text-align: center;">'
                            )
                            for i, billboard in enumerate(font.parent.billboardURLs):
                                html.append(
                                    '<span id="fontBillboardLink_%s" class="fontBillboardLinks %s"><a href="x-python://self.setFontImage(____%s____)" style="color: inherit;">•</a></span>'
                                    % (i, "selected" if i == index else "", i)
                                )
                            html.append("</div>")

                    html.append(
                        '<div class="font %s">' % (self.b64encode(font.uniqueID))
                    )
                    html.append(
                        '<div class="name">%s %s</div>'
                        % (
                            font.parent.name.getText(client.locale()),
                            font.name.getText(client.locale()),
                        )
                    )
                    html.append('<div class="categories">')

                    for keyword, name, condition in (
                        ("license", "#(License)", True),
                        ("information", "#(Information)", font.parent.description),
                        ("versions", "#(Versions)", True),
                        # 				('billboardURLs', '#(Images)', font.parent.billboardURLs),
                    ):

                        if condition:
                            html.append(
                                '<div class="category %s %s">'
                                % (
                                    "selected"
                                    if client.get("metadataCategory") == keyword
                                    else "",
                                    keyword,
                                )
                            )
                            if client.get("metadataCategory") != keyword:
                                html.append(
                                    '<a href="x-python://self.showMetadataCategory(____%s____)">'
                                    % keyword
                                )
                            html.append("%s&thinsp;→" % name)
                            if client.get("metadataCategory") != keyword:
                                html.append("</a>")
                            html.append("</div>")

                    html.append("</div>")

                    html.append(
                        '<div class="categoryBody %s">'
                        % (client.get("metadataCategory"))
                    )

                    if client.get("metadataCategory") == "license":
                        for usedLicense in font.usedLicenses:

                            # if usedLicense.upgradeURL:
                            # html.append('<div style="width: 90%; text-align: center; margin-top: 25px; margin-bottom: 35px; margin-right: 30px;">')
                            # html.append(f'<div style="display: inline-block; width: 50px;"><a href="{usedLicense.upgradeURL}">')
                            # html.append('<img src="file://##htmlroot##/seatallowance.svg" style="width: 100px;">')
                            # html.append('</div>')
                            # html.append('<p>')
                            # html.append('#(Upgrade License)&thinsp;↗︎')
                            # html.append('</p></a>')
                            # html.append('</div>')

                            # html.append('<div style="width: 90%; text-align: center; margin-top: 25px; margin-bottom: 35px; margin-right: 30px;">')
                            # html.append(f'<div style="display: inline-block; width: 50px;"><a href="{usedLicense.upgradeURL}">')
                            # html.append(open(os.path.join(os.path.dirname(__file__), 'htmlfiles', 'upgradeicon.svg')).read())
                            # html.append('</div>')
                            # html.append('<p>')
                            # html.append('#(Upgrade License)&thinsp;↗︎')
                            # html.append('</p></a>')
                            # html.append('</div>')

                            if usedLicense.seatsAllowed or usedLicense.seatsInstalled:
                                licenseLink = usedLicense.upgradeURL is not None
                                # 							licenseLink = False

                                if licenseLink:
                                    html.append(f'<a href="{usedLicense.upgradeURL}">')
                                html.append(
                                    '<div class="clear" style="width: 90%; margin-bottom: -20px;">'
                                )
                                html.append(
                                    '<div style="float: left; width: %s; min-width: 110px; text-align: center;">'
                                    % ("30%" if licenseLink else "100%")
                                )

                                html.append(
                                    '<div style="display: inline-block; width: 100px; ">'
                                )
                                html.append(
                                    '<img src="file://##htmlroot##/seatallowance.svg" style="width: 100px;">'
                                )

                                html.append(
                                    '<div style="width: 100px; position: relative; top: -%spx; left; 0px; margin-left: -4px; margin-bottom: -35px;  ">'
                                    % (80 if MAC else 82)
                                )
                                html.append(
                                    '<div class="seatsInstalled" style="position: relative; width: 30px; left: 21px; top: 2px; text-align: right; color: black !important;">'
                                )
                                html.append(usedLicense.seatsInstalled or 0)
                                html.append("</div>")
                                html.append(
                                    '<div style="position: relative; width: 30px; left: 57px; top: 2px; text-align: left; color: black !important;">'
                                )
                                html.append(usedLicense.seatsAllowed or 0)
                                html.append("</div>")
                                html.append("</div>")

                                html.append("</div>")

                                html.append("</div>")  # .float left # image

                                if licenseLink:
                                    html.append(
                                        '<div style="float: left; width: 140px; height: 100px; text-align: left; display: table;">'
                                    )
                                    html.append(
                                        '<div style="display: table-cell; vertical-align: middle; ">'
                                    )
                                    html.append("#(Upgrade License)&thinsp;↗︎")
                                    html.append("</div>")
                                    html.append("</div>")  # .float left
                                html.append("</div>")  # .clear

                                if licenseLink:
                                    html.append("</a>")

                            elif usedLicense.upgradeURL:
                                html.append(
                                    f'<a class="button" href="{usedLicense.upgradeURL}">'
                                )
                                html.append("#(Upgrade License)&thinsp;↗︎")
                                html.append("</a>")

                            license = usedLicense.getLicense()
                            html.append("<div>")
                            html.append(
                                "<p>%s<br />" % license.name.getText(client.locale())
                            )
                            html.append(
                                '<a href="%s">%s&thinsp;↗︎</a></p>'
                                % (license.URL, license.URL)
                            )
                            if (
                                usedLicense.seatsAllowed != None
                                and usedLicense.seatsInstalled != None
                            ):
                                html.append("<p>")
                                html.append(
                                    "#(Seats Installed): <b>"
                                    + localizeString(
                                        "#(%x% out of %y%)",
                                        replace={
                                            "x": f'<span class="seatsInstalled">{usedLicense.seatsInstalled}</span>',
                                            "y": usedLicense.seatsAllowed,
                                        },
                                    )
                                    + "</b>"
                                )
                                html.append("</p>")
                            html.append("</div>")

                    if (
                        client.get("metadataCategory") == "information"
                        and font.parent.description
                    ):
                        text, locale = font.parent.description.getTextAndLocale()
                        html.append("%s" % text)

                    if client.get("metadataCategory") == "versions":
                        html.append("<div>")
                        for version in reversed(font.getVersions()):
                            html.append(
                                '<div class="version %s">'
                                % self.versionEncode(version.number)
                            )
                            html.append(
                                '<p><b>#(Version) %s</b> <span class="label installedVersion %s" style="display: %s;">#(Installed)</span><br />'
                                % (
                                    version.number,
                                    "latestVersion"
                                    if version.number == font.getVersions()[-1].number
                                    else "olderVersion",
                                    "inline"
                                    if version.number == installedVersion
                                    else "none",
                                )
                            )
                            if version.description:
                                html.append(
                                    "%s" % version.description.getText(client.locale())
                                )
                            if version.releaseDate:
                                html.append(
                                    '<br /><span style="color: gray;">#(Published): %s</span>'
                                    % locales.formatDate(
                                        time.mktime(
                                            datetime.date.fromisoformat(
                                                version.releaseDate
                                            ).timetuple()
                                        ),
                                        client.locale(),
                                    )
                                )

                            html.append(
                                '<div class="installButton status install" style="display: %s; margin-top: -3px;">'
                                % (
                                    "block"
                                    if version.number != installedVersion
                                    else "none"
                                )
                            )
                            html.append(
                                '<a href="x-python://self.installFont(____%s____, ____%s____, ____%s____, ____%s____)" class="installButton button">'
                                % (
                                    self.b64encode(subscription.parent.canonicalURL),
                                    self.b64encode(subscription.protocol.unsecretURL()),
                                    self.b64encode(font.uniqueID),
                                    version.number,
                                )
                            )
                            html.append("✓ #(Install)")
                            html.append("</a>")
                            html.append("</div>")  # installButton
                            html.append(
                                '<div class="installButton status remove" style="display: %s; margin-top: -3px;">'
                                % (
                                    "none"
                                    if version.number != installedVersion
                                    else "block"
                                )
                            )
                            html.append(
                                '<a href="x-python://self.removeFont(____%s____, ____%s____, ____%s____)" class="removeButton button">'
                                % (
                                    self.b64encode(subscription.parent.canonicalURL),
                                    self.b64encode(subscription.protocol.unsecretURL()),
                                    self.b64encode(font.uniqueID),
                                )
                            )
                            html.append("✕ #(Remove)")
                            html.append("</a>")
                            html.append("</div>")  # installButton
                            html.append("</p>")
                            html.append("</div>")  # .version

                        html.append("</div>")

                    html.append("</div>")  # .categories
                    html.append("</div>")  # .font

                html = "".join(map(str, html))
                html = html.replace('"', "'")
                html = html.replace("\n", "")
                html = localizeString(html)
                html = self.replaceHTML(html)
                js = '$("#metadata .content").html("' + html + '");'
                self.javaScript(js)
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def setPublisherHTML(self, b64ID=None):
        try:

            # import cProfile
            # profile = cProfile.Profile()
            # profile.enable()

            if self.b64decode(b64ID) == "pendingInvitations":

                client.set("currentPublisher", "pendingInvitations")

                html = []

                pendingInvitations = client.pendingInvitations()
                if pendingInvitations:
                    for invitation in pendingInvitations:

                        html.append(
                            '<div class="publisher invitation" id="%s">' % invitation.ID
                        )

                        html.append('<div class="foundry">')
                        html.append(
                            '<div class="head clear" style="background-color: %s;">'
                            % (
                                "#"
                                + Color(hex=invitation.backgroundColor or "DDDDDD")
                                .desaturate(0 if self.IsActive() else 1)
                                .hex
                                if invitation.backgroundColor
                                else "none"
                            )
                        )

                        if invitation.logoURL:
                            success, logo, mimeType = client.resourceByURL(
                                invitation.logoURL, binary=True
                            )
                            if success:
                                html.append('<div class="logo">')
                                html.append(
                                    '<img src="data:%s;base64,%s" style="width: 100px; height: 100px;" />'
                                    % (mimeType, logo)
                                )
                                html.append("</div>")  # publisher
                            else:
                                html.append('<div class="logo">')
                                html.append(
                                    '<img src="%s" style="width: 100px; height: 100px;" />'
                                    % (invitation.logoURL)
                                )
                                html.append("</div>")  # publisher

                        html.append(
                            '<div class="names centerOuter"><div class="centerInner">'
                        )

                        html.append(
                            '<div class="vertCenterOuter" style="height: 100px;">'
                        )
                        html.append('<div class="vertCenterMiddle">')
                        html.append('<div class="vertCenterInner">')

                        name = typeworld.api.MultiLanguageText(
                            dict=invitation.publisherName
                        )
                        subscriptionName = typeworld.api.MultiLanguageText(
                            dict=invitation.subscriptionName
                        )
                        html.append(
                            '<div class="name">%s%s</div>'
                            % (
                                name.getText(client.locale()),
                                (
                                    " (%s)" % subscriptionName.getText(client.locale())
                                    if invitation.subscriptionName
                                    else ""
                                ),
                            )
                        )
                        if invitation.websiteURL:
                            html.append("<p>")
                            html.append(
                                '<div class="website"><a href="%s">%s</a></div>'
                                % (invitation.websiteURL, invitation.websiteURL)
                            )
                            html.append("</p>")

                        if (
                            invitation.foundries
                            or invitation.families
                            or invitation.fonts
                        ):
                            html.append("<p>")
                            html.append(
                                "%s #(Foundry/ies), %s #(Families/s), %s #(Font/s)"
                                % (
                                    invitation.foundries or 0,
                                    invitation.families or 0,
                                    invitation.fonts or 0,
                                )
                            )
                            html.append("</p>")

                        html.append("<p>")
                        if (
                            invitation.invitedByUserEmail
                            or invitation.invitedByUserName
                        ):
                            html.append(
                                '#(Invited by): <img src="file://##htmlroot##/userIcon.svg" style="width: 16px; height: 16px; position: relative; top: 3px; margin-top: -3px; margin-right: 2px;">'
                            )
                            if (
                                invitation.invitedByUserEmail
                                and invitation.invitedByUserName
                            ):
                                html.append(
                                    '<b>%s</b> (<a href="mailto:%s">%s</a>)'
                                    % (
                                        invitation.invitedByUserName,
                                        invitation.invitedByUserEmail,
                                        invitation.invitedByUserEmail,
                                    )
                                )
                            else:
                                html.append(
                                    "%s"
                                    % (
                                        invitation.invitedByUserName
                                        or invitation.invitedByUserEmail
                                    )
                                )

                        if invitation.time:
                            html.append(
                                ", %s"
                                % (
                                    NaturalRelativeWeekdayTimeAndDate(
                                        invitation.time, locale=client.locale()[0]
                                    )
                                )
                            )

                        html.append("</p>")

                        html.append('<div style="margin-top: 15px;">')

                        html.append(
                            '<a class="acceptInvitation" id="%s" href="x-python://self.acceptInvitation(____%s____)">'
                            % (
                                self.b64encode(invitation.url),
                                self.b64encode(invitation.url),
                            )
                        )
                        html.append('<div class="clear invitationButton accept">')
                        html.append('<div class="symbol">')
                        html.append("✓")
                        html.append("</div>")
                        html.append('<div class="text">')
                        html.append("#(Accept Invitation)")
                        html.append("</div>")
                        html.append("</div>")
                        html.append("</a>")

                        # 						html.append('&nbsp;&nbsp;')

                        html.append(
                            '<a class="declineInvitation" id="%s" href="x-python://self.declineInvitation(____%s____)">'
                            % (
                                self.b64encode(invitation.url),
                                self.b64encode(invitation.url),
                            )
                        )
                        html.append('<div class="clear invitationButton decline">')
                        html.append('<div class="symbol">')
                        html.append("✕")
                        html.append("</div>")
                        html.append('<div class="text">')
                        html.append("#(Decline Invitation)")
                        html.append("</div>")
                        html.append("</div>")
                        html.append("</a>")

                        html.append("</div>")  # buttons

                        html.append("</div>")  # .vertCenterInner
                        html.append("</div>")  # .vertCenterMiddle
                        html.append("</div>")  # .vertCenterOuter

                        html.append("</div></div>")  # .centerInner .centerOuter

                        html.append("</div>")  # .head
                        html.append("</div>")  # .foundry
                        html.append("</div>")  # .publisher

                # 			html.append('''<script>

                # $("#main .publisher a.acceptInvitation").click(function() {
                # 	python("self.acceptInvitation('" + $(this).attr('id') + "')");
                # });

                # $("#main .publisher a.declineInvitation").click(function() {
                # 	python("self.declineInvitation('" + $(this).attr("id") + "')");
                # });

                # 				</script>''')

                # Print HTML
                html = "".join(map(str, html))
                html = html.replace('"', "'")
                html = html.replace("\n", "")
                html = localizeString(html)
                html = self.replaceHTML(html)

                #       print html
                js = '$("#main").html("' + html + '");'
                self.javaScript(js)

                # Set Sidebar Focus
                self.javaScript('$("#sidebar div.subscriptions").slideUp();')

                self.javaScript("$('#sidebar .publisher').removeClass('selected');")
                self.javaScript("$('#sidebar .subscription').removeClass('selected');")
                self.javaScript(
                    "$('#sidebar .pendingInvitations').addClass('selected');"
                )
                self.javaScript("showMain();")

            else:

                #       print b64ID

                ID = self.b64decode(b64ID)

                client.set("currentPublisher", ID)

                html = []

                publisher = client.publisher(ID)
                if publisher.subscriptions() and not publisher.get(
                    "currentSubscription"
                ):
                    publisher.set(
                        "currentSubscription",
                        publisher.subscriptions()[0].protocol.unsecretURL(),
                    )

                if publisher.get("currentSubscription"):
                    subscription = publisher.subscription(
                        publisher.get("currentSubscription")
                    )
                else:
                    subscription = None

                if subscription and subscription.exists:

                    success, message = subscription.protocol.rootCommand()
                    if success:
                        rootCommand = message
                    else:
                        rootCommand = None

                    html.append('<div class="publisher" id="%s">' % (b64ID))

                    success, message = subscription.protocol.installableFontsCommand()
                    if success:
                        command = message
                    else:
                        command = None

                    if (
                        command.prefersRevealedUserIdentity
                        and subscription.get("revealIdentity") != True
                    ):

                        html.append('<div class="foundry" id="acceptRevealIdentity">')
                        html.append('<div class="head clear">')
                        html.append('<div class="inner">')

                        html.append('<div class="clear">')

                        html.append(
                            '<div class="one" style="float: left; width: 500px;">'
                        )
                        html.append("<p>")
                        html.append("<b>#(Reveal Identity)</b>")
                        html.append("</p>")
                        html.append("<p>")
                        html.append("#(RevealUserIdentityRequest)")
                        html.append("</p>")
                        html.append("</div>")  # .one

                        html.append('<div class="two" style="float: right;">')

                        # # BUTTON
                        html.append('<div style="margin-top: 18px;">')
                        html.append(
                            '<a class="acceptInvitation" id="acceptRevealIdentityButton">'
                        )
                        html.append('<div class="clear invitationButton agree">')
                        html.append('<div class="symbol">')
                        html.append("✓")
                        html.append("</div>")
                        html.append('<div class="text">')
                        html.append("#(Agree)")
                        html.append("</div>")
                        html.append("</div>")
                        html.append("</a>")
                        html.append("</div>")  # buttons

                        html.append("</div>")  # .two
                        html.append("</div>")  # .clear

                        html.append("</div>")  # .inner
                        html.append("</div>")  # .head
                        html.append("</div>")  # .foundry

                        html.append(
                            """<script>


            $("#acceptRevealIdentityButton").click(function() {
                $("#acceptRevealIdentity").slideUp(function(){ 
                    setSubscriptionPreference("%s", "revealIdentity", "true");
                });
            });

                            </script>"""
                            % self.b64encode(subscription.protocol.unsecretURL())
                        )

                    if subscription.get("acceptedTermsOfService") != True:

                        html.append('<div class="foundry" id="acceptTermsOfService">')
                        html.append('<div class="head clear">')
                        html.append('<div class="inner">')

                        html.append('<div class="clear">')

                        html.append(
                            '<div class="one" style="float: left; width: 500px;">'
                        )
                        html.append("<p>")
                        html.append("<b>#(Terms of Service)</b>")
                        html.append("</p>")
                        html.append("<p>")
                        html.append("#(AcceptTermsOfServiceExplanation)")
                        html.append("</p>")
                        html.append("<p>")
                        html.append(
                            '<a href="%s">→ %s</a>'
                            % (
                                addAttributeToURL(
                                    rootCommand.termsOfServiceURL,
                                    "locales="
                                    + ",".join(client.locale())
                                    + "&canonicalURL="
                                    + urllib.parse.quote(rootCommand.canonicalURL)
                                    + "&subscriptionID="
                                    + urllib.parse.quote(
                                        subscription.protocol.url.subscriptionID
                                    ),
                                ),
                                localizeString(
                                    "#(Read X)",
                                    replace={
                                        "content": localizeString("#(Terms of Service)")
                                    },
                                ),
                            )
                        )
                        html.append("</p>")

                        html.append('<p style="height: 5px;">&nbsp;</p>')

                        html.append("<p>")
                        html.append("<b>#(Privacy Policy)</b>")
                        html.append("</p>")
                        html.append("<p>")
                        html.append("#(AcceptPrivacyPolicyExplanation)")
                        html.append("</p>")
                        html.append("<p>")
                        html.append(
                            '<a href="%s">→ %s</a>'
                            % (
                                addAttributeToURL(
                                    rootCommand.privacyPolicyURL,
                                    "locales="
                                    + ",".join(client.locale())
                                    + "&canonicalURL="
                                    + urllib.parse.quote(rootCommand.canonicalURL)
                                    + "&subscriptionID="
                                    + urllib.parse.quote(
                                        subscription.protocol.url.subscriptionID
                                    ),
                                ),
                                localizeString(
                                    "#(Read X)",
                                    replace={
                                        "content": localizeString("#(Privacy Policy)")
                                    },
                                ),
                            )
                        )
                        html.append("</p>")

                        html.append("</div>")  # .one

                        html.append('<div class="two" style="float: right;">')

                        # # BUTTON
                        html.append('<div style="margin-top: 18px;">')
                        html.append(
                            '<a class="acceptInvitation" id="acceptTermsOfServiceButton">'
                        )
                        html.append('<div class="clear invitationButton agree">')
                        html.append('<div class="symbol">')
                        html.append("✓")
                        html.append("</div>")
                        html.append('<div class="text">')
                        html.append("#(Agree)")
                        html.append("</div>")
                        html.append("</div>")
                        html.append("</a>")
                        html.append("</div>")  # buttons

                        html.append("</div>")  # .two
                        html.append("</div>")  # .clear

                        html.append("</div>")  # .inner
                        html.append("</div>")  # .head
                        html.append("</div>")  # .foundry

                        html.append(
                            """<script>


            $("#acceptTermsOfServiceButton").click(function() {
                $("#acceptTermsOfService").slideUp(function(){ 
                    setSubscriptionPreference("%s", "acceptedTermsOfService", "true");
                });
            });

                            </script>"""
                            % self.b64encode(subscription.protocol.unsecretURL())
                        )

                    for foundry in command.foundries:

                        theme = self.theme()

                        ## STYLING
                        styling = FoundryStyling(foundry, theme)
                        logoURL = styling.logo()
                        html.append(
                            styling.foundryView(self.b64encode(foundry.uniqueID))
                        )

                        backgroundColorFoundryStyling = FoundryStyling(
                            foundry.parent.foundries[-1], theme
                        )
                        html.append(
                            """<style> #main { background-color: #%s; } </style>"""
                            % backgroundColorFoundryStyling.backgroundColor.hex
                        )

                        html.append(
                            '<div class="foundry" id="%s">'
                            % self.b64encode(foundry.uniqueID)
                        )
                        html.append('<div class="head clear">')

                        if logoURL:
                            success, logo, mimeType = subscription.resourceByURL(
                                logoURL, binary=True
                            )
                            if success:
                                html.append('<div class="logo">')
                                html.append(
                                    '<img src="data:%s;base64,%s" style="width: 100px; height: 100px;" />'
                                    % (mimeType, logo)
                                )
                                html.append("</div>")  # publisher

                        html.append(
                            '<div class="names centerOuter"><div class="centerInner">'
                        )

                        html.append(
                            '<div class="vertCenterOuter" style="height: 100px;">'
                        )
                        html.append('<div class="vertCenterMiddle">')
                        html.append('<div class="vertCenterInner">')

                        html.append(
                            '<div class="name">%s</div>'
                            % (foundry.name.getText(client.locale()))
                        )
                        if foundry.websiteURL:
                            html.append("<p>")
                            html.append(
                                '<div class="website"><a href="%s">%s</a></div>'
                                % (foundry.websiteURL, foundry.websiteURL)
                            )
                            html.append("</p>")

                        html.append("</div>")  # .vertCenterInner
                        html.append("</div>")  # .vertCenterMiddle
                        html.append("</div>")  # .vertCenterOuter

                        html.append("</div></div>")  # .centerInner .centerOuter

                        html.append("</div>")  # .head

                        html.append('<div class="families">')

                        for family in foundry.families:
                            html.append(
                                '<div class="contextmenu family" id="%s">'
                                % self.b64encode(family.uniqueID)
                            )

                            html.append('<div class="title">')
                            html.append('<div class="clear">')
                            html.append('<div class="left name">')
                            html.append(family.name.getText(client.locale()))
                            html.append("</div>")  # .left.name
                            html.append("</div>")  # .clear
                            html.append("</div>")  # .title

                            for package in family.getPackages():
                                for formatName in package.getFormats():

                                    amountInstalled = 0
                                    for font in package.fonts:
                                        if subscription.installedFontVersion(
                                            font.uniqueID
                                        ):
                                            amountInstalled += 1

                                    completeSetName = ""
                                    if package.keyword != typeworld.api.DEFAULT:
                                        completeSetName += (
                                            package.name.getText(client.locale()) + ", "
                                        )
                                    completeSetName += typeworld.api.FILEEXTENSIONNAMES[
                                        formatName
                                    ]

                                    html.append(
                                        '<div class="section %s" id="%s">'
                                        % (
                                            "multipleFonts"
                                            if len(package.fonts) > 1
                                            else "",
                                            completeSetName,
                                        )
                                    )

                                    html.append('<div class="title clear">')
                                    html.append(
                                        '<div class="name left">%s</div>'
                                        % completeSetName
                                    )

                                    if len(package.fonts) > 1:

                                        html.append(
                                            '<div class="more right" style="padding-top: 5px;">'
                                        )
                                        html.append(
                                            '<img src="file://##htmlroot##/more_darker.svg" style="height: 8px; position: relative; top: 0px;">'
                                        )
                                        html.append("</div>")

                                        html.append(
                                            '<div class="installButtons right" style="padding-top: 5px;">'
                                        )
                                        html.append('<div class="clear">')

                                        if amountInstalled < len(package.fonts):
                                            html.append(
                                                '<div class="install installButton right">'
                                            )
                                            html.append(
                                                '<a href="x-python://self.installAllFonts(____%s____, ____%s____, ____%s____, ____%s____, ____%s____)" class="installAllFonts installButton button">'
                                                % (
                                                    self.b64encode(ID),
                                                    self.b64encode(
                                                        subscription.protocol.unsecretURL()
                                                    ),
                                                    self.b64encode(family.uniqueID),
                                                    self.b64encode(package.keyword),
                                                    formatName,
                                                )
                                            )
                                            html.append("✓ #(Install All)")
                                            html.append("</a>")
                                            html.append("</div>")  # .installButton

                                        if amountInstalled > 0:
                                            html.append(
                                                '<div class="remove installButton right">'
                                            )
                                            html.append(
                                                '<a href="x-python://self.removeAllFonts(____%s____, ____%s____, ____%s____, ____%s____, ____%s____)" class="removeAllFonts removeButton button ">'
                                                % (
                                                    self.b64encode(ID),
                                                    self.b64encode(
                                                        subscription.protocol.unsecretURL()
                                                    ),
                                                    self.b64encode(family.uniqueID),
                                                    self.b64encode(package.keyword),
                                                    formatName,
                                                )
                                            )
                                            html.append("✕ #(Remove All)")
                                            html.append("</a>")
                                            html.append("</div>")  # .installButton

                                        html.append("</div>")  # .clear
                                        html.append("</div>")  # .installButtons

                                    html.append("</div>")  # .title

                                    for font in package.fonts:
                                        installedVersion = (
                                            subscription.installedFontVersion(
                                                font.uniqueID
                                            )
                                        )

                                        html.append(
                                            '<div class="contextmenu font %s %s %s" id="%s">'
                                            % (
                                                self.b64encode(font.uniqueID),
                                                "installed"
                                                if installedVersion
                                                else "notInstalled",
                                                "selected"
                                                if subscription.get("currentFont")
                                                == font.uniqueID
                                                else "",
                                                self.b64encode(font.uniqueID),
                                            )
                                        )
                                        html.append('<div class="clear">')

                                        html.append(
                                            '<div class="left" style="width: 50%;">'
                                        )
                                        html.append(font.name.getText(client.locale()))
                                        if font.free:
                                            html.append(
                                                '<span class="label free">free</span>'
                                            )
                                        if font.status != "stable":
                                            html.append(
                                                '<span class="label pre">%s</span>'
                                                % font.status
                                            )
                                        if font.variableFont:
                                            html.append(
                                                '<span class="label var">OTVar</span>'
                                            )
                                        html.append("</div>")  # .left

                                        html.append('<div class="left installedText">')
                                        html.append(self.fontInstalledText(font))
                                        html.append("</div>")  # .left

                                        expiry = ""
                                        if font.expiryDuration:
                                            expiry = "%s'" % font.expiryDuration
                                        if expiry:
                                            html.append('<div class="left expiryText">')
                                            html.append(
                                                '⏲<span class="countdownMinutes" timestamp="%s">%s</span>'
                                                % (font.expiry, expiry)
                                            )
                                            html.append("</div>")  # .left

                                        if font.purpose == "desktop":

                                            html.append(
                                                '<div class="installButtons right">'
                                            )
                                            html.append(
                                                '<div class="installButton status install">'
                                            )
                                            html.append(
                                                '<a href="x-python://self.installFont(____%s____, ____%s____, ____%s____, ____%s____)" class="installButton button">'
                                                % (
                                                    self.b64encode(
                                                        subscription.parent.canonicalURL
                                                    ),
                                                    self.b64encode(
                                                        subscription.protocol.unsecretURL()
                                                    ),
                                                    self.b64encode(font.uniqueID),
                                                    font.getVersions()[-1].number
                                                    if font.getVersions()
                                                    else "",
                                                )
                                            )
                                            html.append("✓ #(Install)")
                                            html.append("</a>")
                                            html.append("</div>")  # installButton
                                            html.append(
                                                '<div class="installButton status remove">'
                                            )
                                            html.append(
                                                '<a href="x-python://self.removeFont(____%s____, ____%s____, ____%s____)" class="removeButton button">'
                                                % (
                                                    self.b64encode(
                                                        subscription.parent.canonicalURL
                                                    ),
                                                    self.b64encode(
                                                        subscription.protocol.unsecretURL()
                                                    ),
                                                    self.b64encode(font.uniqueID),
                                                )
                                            )
                                            html.append("✕ #(Remove)")
                                            html.append("</a>")
                                            html.append("</div>")  # installButton
                                            html.append("</div>")  # .installButtons

                                            html.append(
                                                '<div class="status loading right">'
                                            )
                                            html.append('<a class="status">')
                                            html.append(
                                                """<img src="file://##htmlroot##/loading.gif" style="width: 50px; height: 13px; position: relative; top: 2px;">"""
                                            )
                                            html.append("</a>")
                                            html.append("</div>")  # .right

                                            html.append('<div class="more right">')
                                            html.append('<a class="more">')
                                            html.append(
                                                """<img src="file://##htmlroot##/more_lighter.svg" style="height: 8px; position: relative; top: 0px;">"""
                                            )
                                            html.append("</a>")
                                            html.append("</div>")  # .right

                                        html.append("</div>")  # .clear
                                        html.append("</div>")  # .font

                                    html.append("</div>")  # .section

                            html.append("</div>")  # .family

                        html.append("</div>")  # .families

                        html.append("</div>")  # .foundry

                    html.append("</div>")  # .publisher

                    html.append(
                        """<script>     


                $("#main .section .title").hover(function() {
                    $( this ).closest(".section").addClass( "hover" );
                    $( this ).closest(".section").children(".font").addClass("hover");

                  }, function() {
                    $( this ).closest(".section").removeClass( "hover" );
                    $( this ).closest(".section").children(".font").removeClass("hover");
                  }
                );

                $("#main .font").hover(function() {
                    $( this ).addClass( "hover" );
                    $( this ).addClass( "hoverOverFont" );
                  }, function() {
                    $( this ).removeClass( "hover" );
                    $( this ).removeClass( "hoverOverFont" );
                  }
                );

                $("#main .publisher a.reloadPublisherButton").click(function() {
                    $("#sidebar #%s .badges").hide();
                    $("#sidebar #%s .reloadAnimation").show();
                    python("self.reloadPublisher(None, ____%s____)");
                });


                $("#main .font").click(function() {
                    $("#main .font").removeClass('selected');
                    $(this).addClass('selected');
                    python("self.selectFont(____' + $(this).attr('id') + '____)");
                });

            </script>"""
                        % (b64ID, b64ID, b64ID)
                    )

                    # Unused:
                    """
                $("#main .font, #main .family .title").click(function() {
                    $("#main .font, #main .family .title").removeClass('selected');
                    $( this ).addClass( "selected" );
                  });
            """

                # Print HTML
                html = "".join(map(str, html))
                html = html.replace('"', "'")
                html = html.replace("\n", "")
                html = localizeString(html, html=True)
                html = self.replaceHTML(html)
                # print(html)
                js = '$("#main").html("' + html + '");'
                self.javaScript(js)

                # Set Sidebar Focus
                self.javaScript("$('#sidebar .publisher').removeClass('selected');")
                self.javaScript("$('#sidebar .subscription').removeClass('selected');")
                self.javaScript(
                    "$('#sidebar #%s.publisher').addClass('selected');" % b64ID
                )
                self.javaScript("recalcMinutesCountdown();")

                if subscription:
                    self.javaScript(
                        "$('#sidebar #%s.subscription').addClass('selected');"
                        % self.b64encode(subscription.protocol.unsecretURL())
                    )

                self.setBadges()
                agent("amountOutdatedFonts %s" % client.amountOutdatedFonts())

                if subscription and subscription.get("currentFont"):
                    self.selectFont(self.b64encode(subscription.get("currentFont")))

            self.javaScript("showMain();")

            # profile.disable()
            # profile.print_stats(sort='time')
            self.setSideBarHTML()

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def fontInstalledText(self, font):
        try:

            html = []

            subscription = font.parent.parent.parent.parent.subscription
            installedVersion = subscription.installedFontVersion(font=font)

            if installedVersion:
                html.append(
                    '#(Installed): <span class="label installedVersion %s">%s</a>'
                    % (
                        "latestVersion"
                        if installedVersion == font.getVersions()[-1].number
                        else "olderVersion",
                        installedVersion,
                    )
                )
            else:
                html.append(
                    '<span class="inactive notInstalled">#(Not Installed)</span>'
                )
            return "".join(html)
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def versionEncode(self, version):
        try:
            return version.replace(".", "_")
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def b64encode(self, string):
        try:
            b = str(string).encode()
            b64 = base64.b32encode(b)
            s = b64.decode()

            return s.replace("=", "-")
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def b64decode(self, string):
        try:
            b = str(string).replace("-", "=").encode()
            b64 = base64.b32decode(b)
            s = b64.decode()

            return s
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def hidePanel(self):
        try:
            self.panelVisible = None

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def setSideBarHTML(self):
        try:
            # Set publishers

            if not client.get("currentPublisher"):
                self.javaScript("hideMain();")

            if client.get(
                "currentPublisher"
            ) == "pendingInvitations" and not client.get("pendingInvitations"):
                client.set("currentPublisher", "")

            if not client.get("currentPublisher"):
                self.javaScript("hideMain();")

            else:
                if not client.get("currentPublisher") and client.publishers():
                    client.set("currentPublisher", client.publishers()[0].canonicalURL)
                    self.setActiveSubscription(
                        self.b64encode(client.publishers()[0].canonicalURL),
                        self.b64encode(
                            client.publishers()[0]
                            .subscriptions()[0]
                            .protocol.unsecretURL()
                        ),
                    )

            html = []

            # Sort
            # pass

            if client.publishers():
                html.append('<div class="headline">#(My Subscriptions)</div>')
                html.append('<div id="publishers">')

                # Create HTML
                for publisher in client.publishers():

                    b64ID = self.b64encode(publisher.canonicalURL)

                    if publisher.subscriptions():
                        name, language = publisher.name(locale=client.locale())

                        if language in ("ar", "he"):
                            direction = "rtl"
                            if language in ("ar"):
                                name = kashidaSentence(name, 20)
                        else:
                            direction = "ltr"

                        installedFonts = publisher.amountInstalledFonts()
                        outdatedFonts = publisher.amountOutdatedFonts()
                        selected = (
                            client.get("currentPublisher") == publisher.canonicalURL
                        )

                        _type = (
                            "multiple"
                            if len(publisher.subscriptions()) > 1
                            else "single"
                        )

                        html.append('<div class="publisherWrapper">')
                        #                html.append('<a class="publisher" href="x-python://self.setPublisherHTML(____%s____)">' % b64ID)
                        html.append(
                            '<div id="%s" class="contextmenu publisher line clear %s %s %s" lang="%s" dir="%s">'
                            % (
                                b64ID,
                                _type,
                                "selected" if selected else "",
                                "expanded"
                                if len(publisher.subscriptions()) > 1
                                else "",
                                language,
                                direction,
                            )
                        )
                        html.append('<div class="name">')
                        html.append(
                            "%s %s"
                            % (
                                name,
                                '<img src="file://##htmlroot##/github.svg" style="position:relative; top: 3px; width:16px; height:16px;">'
                                if publisher.get("type") == "GitHub"
                                else "",
                            )
                        )
                        html.append("</div>")
                        html.append(
                            '<div class="reloadAnimation" style="display: %s;">'
                            % ("block" if publisher.stillUpdating() else "none")
                        )
                        html.append(
                            '<img src="file://##htmlroot##/reload.gif" style="position:relative; top: 2px; width:20px; height:20px;">'
                        )
                        html.append("</div>")
                        html.append('<div class="badges clear">')
                        html.append(
                            '<div class="badge numbers outdated" style="display: %s;">'
                            % ("block" if outdatedFonts else "none")
                        )
                        html.append("%s" % (outdatedFonts or ""))
                        html.append("</div>")
                        html.append(
                            '<div class="badge numbers installed" style="display: %s;">'
                            % ("block" if installedFonts else "none")
                        )
                        html.append("%s" % (installedFonts or ""))
                        html.append("</div>")
                        html.append("</div>")  # .badges

                        # Identity Revealed Icon
                        if len(publisher.subscriptions()) == 1:

                            badges = []

                            subscription = publisher.subscriptions()[0]
                            if client.user() and subscription.get("revealIdentity"):
                                badges.append(
                                    '<div class="badge revealIdentity" style="display: block;" title="'
                                    + localizeString(
                                        "#(YourIdentityWillBeRevealedTooltip)"
                                    )
                                    + '"><img src="file://##htmlroot##/userIcon_Outline.svg" style="width: 16px; height: 16px; position: relative; top: 3px; margin-top: -3px;"></div>'
                                )

                            if client.user() and subscription.invitationAccepted():
                                badges.append(
                                    '<div class="badge revealIdentity" style="display: block;" title="'
                                    + localizeString("#(IsInvitationExplanation)")
                                    + '"><img src="file://##htmlroot##/invitation.svg" style="width: 16px; height: 16px; position: relative; top: 3px; margin-top: -3px;"></div>'
                                )

                            if badges:
                                html.append('<div class="badges clear">')
                                html.append("".join(badges))
                                html.append("</div>")  # .badges

                        html.append(
                            '<div class="alert noclick" style="display: %s;">'
                            % ("block" if publisher.updatingProblem() else "none")
                        )
                        html.append(
                            '<a href="x-python://self.displayPublisherSidebarAlert(____%s____)">'
                            % b64ID
                        )
                        html.append("⚠️")
                        html.append("</a>")
                        html.append("</div>")  # .alert
                        html.append("</div>")  # publisher
                        #                html.append('</a>')

                        html.append(
                            '<div class="subscriptions" style="display: %s;">'
                            % ("block" if selected else "none")
                        )
                        if len(publisher.subscriptions()) > 1:
                            for i, subscription in enumerate(publisher.subscriptions()):

                                amountInstalledFonts = (
                                    subscription.amountInstalledFonts()
                                )
                                amountOutdatedFonts = subscription.amountOutdatedFonts()
                                if publisher.get("currentSubscription"):
                                    selected = (
                                        subscription.protocol.unsecretURL()
                                        == publisher.subscription(
                                            publisher.get("currentSubscription")
                                        ).protocol.unsecretURL()
                                    )
                                else:
                                    selected = False

                                html.append("<div>")
                                html.append(
                                    '<div class="contextmenu subscription line clear %s" lang="%s" dir="%s" id="%s" publisherID="%s">'
                                    % (
                                        "selected" if selected else "",
                                        "en",
                                        "ltr",
                                        self.b64encode(
                                            subscription.protocol.unsecretURL()
                                        ),
                                        b64ID,
                                    )
                                )
                                html.append('<div class="name">')
                                html.append(subscription.name(locale=client.locale()))
                                html.append("</div>")
                                html.append(
                                    '<div class="reloadAnimation" style="display: %s;">'
                                    % (
                                        "block"
                                        if subscription.stillUpdating()
                                        else "none"
                                    )
                                )
                                html.append(
                                    '<img src="file://##htmlroot##/reload.gif" style="position:relative; top: 2px; width:20px; height:20px;">'
                                )
                                html.append("</div>")
                                html.append('<div class="badges clear">')
                                html.append(
                                    '<div class="badge numbers outdated" style="display: %s;">'
                                    % ("block" if amountOutdatedFonts else "none")
                                )
                                html.append("%s" % amountOutdatedFonts)
                                html.append("</div>")
                                html.append(
                                    '<div class="badge numbers installed" style="display: %s;">'
                                    % ("block" if amountInstalledFonts else "none")
                                )
                                html.append("%s" % amountInstalledFonts)
                                html.append("</div>")
                                html.append("</div>")  # .badges

                                # Identity Revealed Icon
                                badges = []

                                if client.user() and subscription.get("revealIdentity"):
                                    badges.append(
                                        '<div class="badge revealIdentity" style="display: %s;" title="'
                                        + localizeString(
                                            "#(YourIdentityWillBeRevealedTooltip)"
                                        )
                                        + '"><img src="file://##htmlroot##/userIcon_Outline.svg" style="width: 16px; height: 16px; position: relative; top: 3px; margin-top: -3px;"></div>'
                                    )

                                if client.user() and subscription.invitationAccepted():
                                    badges.append(
                                        '<div class="badge revealIdentity" style="display: block;" title="'
                                        + localizeString("#(IsInvitationExplanation)")
                                        + '"><img src="file://##htmlroot##/invitation.svg" style="width: 16px; height: 16px; position: relative; top: 3px; margin-top: -3px;"></div>'
                                    )

                                if badges:
                                    html.append('<div class="badges clear">')
                                    html.append("".join(badges))
                                    html.append("</div>")  # .badges

                                html.append(
                                    '<div class="alert" style="display: %s;">'
                                    % (
                                        "block"
                                        if subscription.updatingProblem()
                                        else "none"
                                    )
                                )
                                html.append(
                                    '<a href="x-python://self.displaySubscriptionSidebarAlert(____%s____)">'
                                    % self.b64encode(
                                        subscription.protocol.unsecretURL()
                                    )
                                )
                                html.append("⚠️")
                                html.append("</a>")
                                html.append("</div>")  # .alert
                                html.append("</div>")  # subscription
                                #                        html.append('</a>')
                                html.append("</div>")
                                if i == 0:
                                    html.append('<div class="margin top"></div>')
                            html.append('<div class="margin bottom"></div>')
                        html.append("</div>")

                        html.append("</div>")  # .publisherWrapper

            if client.get("pendingInvitations"):
                html.append('<div class="headline">#(Invitations)</div>')

                selected = client.get("currentPublisher") == "pendingInvitations"

                html.append('<div class="publisherWrapper">')
                html.append(
                    '<div id="%s" class="contextmenu publisher pendingInvitations line clear %s %s" lang="en" dir="ltr">'
                    % ("", "", "selected" if selected else "")
                )
                html.append('<div class="name">')
                html.append("#(Pending Invitations)…")
                html.append("</div>")
                html.append('<div class="badges clear">')
                html.append(
                    '<div class="badge numbers outdated" style="display: %s;">'
                    % ("block")
                )
                html.append("%s" % (len(client.get("pendingInvitations"))))
                html.append("</div>")
                # html.append('<div class="badge installed" style="display: %s;">' % ('block' if installedFonts else 'none'))
                # html.append('%s' % (installedFonts or ''))
                # html.append('</div>')
                html.append("</div>")  # .badges
                html.append("</div>")

            # // :not(.selected)
            html.append(
                """<script>


    $( document ).ready(function() {

        $("#sidebar div.publisher").click(function() {

            console.log("publisher click");

            if ($(this).hasClass('pendingInvitations')) {
                python('self.setPublisherHTML(____"""
                + self.b64encode("pendingInvitations")
                + """____)');
            }

                if ($(this).hasClass('selected')) {

                }
                else {
                    $("#sidebar div.subscriptions").slideUp();
                    $(this).parent().children(".subscriptions").slideDown();
                }
                $("#sidebar div.publisher").removeClass('selected');
                $(this).parent().children(".publisher").addClass('selected');

                python('self.setPublisherHTML(____' + $(this).attr('id') + '____)');
            }
        );

        $("#sidebar div.subscription").click(function() {

            debug("subscription click");

            python('self.setActiveSubscription(____' + $(this).attr('publisherID') + '____, ____' + $(this).attr('id') + '____)');

        });


        $("#sidebar div.publisher .alert").click(function() {
        });

        $("#sidebar .publisher").hover(function() {
            $( this ).addClass( "hover" );
          }, function() {
            $( this ).removeClass( "hover" );
          }
        );

        $("#sidebar .subscription").hover(function() {
            $( this ).addClass( "hover" );
          }, function() {
            $( this ).removeClass( "hover" );
          }
        );

    });



    </script>"""
            )

            html.append("</div>")  # publishers

            # Print HTML
            html = "".join(map(str, html))
            html = html.replace('"', "'")
            html = localizeString(html, html=True)
            html = html.replace("\n", "")
            html = self.replaceHTML(html)
            #        client.log(html)
            js = '$("#sidebar").html("' + html + '");'

            self.javaScript(js)

            if client.user():
                self.javaScript(
                    '$("#userBadge #userName").html("%s");'
                    % (client.userEmail() or "no email found")
                )  # (client.user()[:20] + '...')
                self.javaScript('$("#userBadge").show();')
            else:
                self.javaScript('$("#userBadge").hide();')

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def onLoad(self, event):
        try:

            self.fullyLoaded = True

            if MAC:
                self.javaScript("$('.sidebar').css('padding-top', '32px');")
                # self.javaScript("$('.panel').css('padding-left', '50px');")
                # self.javaScript("$('.panel').css('padding-top', '90px');")
                # self.javaScript("$('.panel').css('padding-bottom', '90px');")

                self.SetTitle("")

                # self.darkModeDetection = DarkModeDetection.alloc().initWithFrame_(NSMakeRect(0, 0, 40, 40))
                # self.darkModeDetection.app = self
                # print('darkModeDetection created', self.darkModeDetection)

            if WIN:
                self.javaScript(
                    "$('#atomButton .centerInner').css('padding-top', '72px');"
                )

            self.setSideBarHTML()

            # Open drawer for newly added publisher
            if self.justAddedPublisher:
                self.handleURL(self.justAddedPublisher)
                self.justAddedPublisher = None

            if client.get("currentPublisher"):
                self.javaScript('$("#welcome").hide();')
                self.setPublisherHTML(self.b64encode(client.get("currentPublisher")))
            self.setBadges()

            if WIN and self.allowCheckForURLInFile:
                self.checkForURLInFile()

            if MAC:

                delegate = DarkModeDelegate.alloc().init()
                delegate.app = self
                NSDistributedNotificationCenter.defaultCenter().addObserver_selector_name_object_(
                    delegate,
                    delegate.darkModeChanged_,
                    "AppleInterfaceThemeChangedNotification",
                    None,
                )

                self.applyDarkMode()

            startWorker(self.onLoadDetached_consumer, self.onLoadDetached_worker)

            if self.parent.startWithCommand:
                commands = self.parent.startWithCommand.split(" ")
                if commands[0] == "javaScript":
                    code = base64.b64decode(commands[1].encode()).decode()
                    self.javaScript(code)

            if self.parent.startWithCommand == "selftest":
                self.parent.startWithCommand = None
                self.selftest()

            self.setAppCastURL()

            if WIN:

                # Restart API
                from ctypes import windll

                windll.kernel32.RegisterApplicationRestart(None, 0)

                if RUNTIME:
                    pywinsparkle.win_sparkle_check_update_without_ui()

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def selftest_worker(self, pythonCode=None, javaScriptCode=None):

        try:
            return pythonCode, javaScriptCode

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def selftest_consumer(self, delayedResult):

        try:
            pythonCode, javaScriptCode = delayedResult.get()

            if pythonCode != None:
                exec(pythonCode, globals(), locals())

            elif javaScriptCode != None:
                self.javaScript(javaScriptCode)

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def selftest_python(self, code):
        startWorker(self.selftest_consumer, self.selftest_worker, wargs=(code, None))

    def selftest_javascript(self, code):
        startWorker(
            self.selftest_consumer, self.selftest_worker, wargs=(None, code)
        ).join()

    def sleep(self, seconds):
        return startWorker(self.sleep_consumer, self.sleep_worker, wargs=(seconds,))

    def sleep_worker(self, seconds):
        time.sleep(seconds)
        return seconds

    def sleep_consumer(self, delayedResult):
        seconds = delayedResult.get()

    def quitSelftest(self, message, exitCode):
        print("selftest failed with:", message)
        self.onQuit(None, withExitCode=exitCode)

    def selftest(self):

        try:

            # Set secret key so that new users are verified instantly
            if CI:
                SECRETKEY = os.getenv("REVOKEAPPINSTANCEAUTHKEY")
                client.secretServerAuthKey = SECRETKEY

            # Keyring
            keyring = client.keyring()
            assert keyring != None
            keyring.set_password("https://type.world", "testuser", "testpassword")
            assert (
                keyring.get_password("https://type.world", "testuser") == "testpassword"
            )

            # Badge label
            if MAC:
                self.setBadgeLabel(3)

            # Sparkle Update
            if MAC and CI:
                sparkle.resetUpdateCycle()
                self.setAppCastURL()
                sparkle.checkForUpdates_(self)
            elif WIN and RUNTIME:
                pywinsparkleDelegate.check_without_ui()

            # Actual subscriptions

            flatFreeSubscription = "typeworld://json+https//typeworldserver.com/flatapi/q8JZfYn9olyUvcCOiqHq/"

            # Delete User Account
            success, message = client.deleteUserAccount("test1@type.world", "12345678")
            condition = success == True
            if not condition:
                if message != [
                    "#(response.userUnknown)",
                    "#(response.userUnknown.headline)",
                ]:
                    return self.quitSelftest(message, 9)

            # Create User Account
            success, message = client.createUserAccount(
                "Test User", "test1@type.world", "12345678", "12345678"
            )

            condition = success == True
            if not condition:
                return self.quitSelftest(message, 10)

            # Add subscription
            success, message, publisher, subscription = client.addSubscription(
                flatFreeSubscription
            )
            condition = success == True
            if not condition:
                return self.quitSelftest(message, 20)

            font = (
                subscription.protocol.installableFontsCommand()[1]
                .foundries[0]
                .families[0]
                .fonts[0]
            )

            # Install font
            success, message = subscription.installFonts(
                [[font.uniqueID, font.getVersions()[-1].number]]
            )
            condition = success == False
            if not condition:
                return self.quitSelftest(message, 30)

            # Terms of Service
            subscription.set("acceptedTermsOfService", True)
            success, message = subscription.installFonts(
                [[font.uniqueID, font.getVersions()[-1].number]]
            )
            condition = success == True
            if not condition:
                return self.quitSelftest(message, 35)
            condition = subscription.amountInstalledFonts() == 1
            if not condition:
                return self.quitSelftest(
                    f"subscription.amountInstalledFonts() = {subscription.amountInstalledFonts()}",
                    40,
                )

            # Uninstall font
            success, message = subscription.removeFonts([font.uniqueID])
            condition = success == True
            if not condition:
                return self.quitSelftest(message, 50)
            condition = subscription.amountInstalledFonts() == 0
            if not condition:
                return self.quitSelftest(
                    f"subscription.amountInstalledFonts() = {subscription.amountInstalledFonts()}",
                    60,
                )

            # Update
            success, message, changed = subscription.update()
            condition = success == True
            if not condition:
                return self.quitSelftest(message, 70)

            # Delete User Account
            success, message = client.deleteUserAccount("test1@type.world", "12345678")
            condition = success == True
            if not condition:
                return self.quitSelftest(message, 80)

            notification("Test Notification Title", "Test Notification Text")

            self.onQuit(None, withExitCode=0)

        except:
            print(traceback.format_exc())
            return self.quitSelftest(traceback.format_exc(), 666)

    def onLoadDetached_worker(self):

        try:

            for message in self.messages:
                self.message(message)

            seenDialogs = client.get("seenDialogs") or []

            # # Ask to install agent
            # if not 'installMenubarIcon' in seenDialogs:

            # 	# Menu Bar is actually running, so don't do anything
            # 	if not client.get('menuBarIcon'):
            # 		dlg = wx.MessageDialog(None, localizeString("#(InstallMenubarIconQuestion)"), localizeString("#(ShowMenuBarIcon)"),wx.YES_NO | wx.ICON_QUESTION)
            # 		dlg.SetYesNoLabels(localizeString('#(Yes)'), localizeString('#(No)'))
            # 		result = dlg.ShowModal()
            # 		if result == wx.ID_YES:
            # 			installAgent()

            # 	seenDialogs.append('installMenubarIcon')
            # 	client.set('seenDialogs', seenDialogs)

            # Reinstall agent if outdated
            if agentIsRunning():
                agentVersion = agent("version")
                if semver.compare(APPVERSION, agentVersion) == 1:
                    client.log("Agent is outdated (%s), needs restart." % agentVersion)
                    restartAgent(2)

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def onLoadDetached_consumer(self, delayedResult):

        try:
            pass
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def checkForURLInFile(self):

        try:

            self.allowCheckForURLInFile = False

            from appdirs import user_data_dir

            openURLFilePath = os.path.join(
                user_data_dir("Type.World", "Type.World"), "url.txt"
            )

            if os.path.exists(openURLFilePath):
                urlFile = open(openURLFilePath, "r")
                url = urlFile.read().strip()
                urlFile.close()

                if self.fullyLoaded:
                    self.handleURL(url)
                else:

                    self.justAddedPublisher = url

                os.remove(openURLFilePath)
                time.sleep(0.5)

            self.allowCheckForURLInFile = True

            return True

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def setBadgeLabel(self, label):
        try:
            """\
            Set dock icon badge
            """
            if MAC:
                app = NSApp()
                dockTile = app.dockTile()

                label = str(label)
                dockTile.display()
                dockTile.setBadgeLabel_(label)

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def replaceHTML(self, html):
        try:
            global __file__
            path = os.path.join(os.path.dirname(__file__), "htmlfiles")
            if WIN:
                path = path.replace("\\", "/")
                if path.startswith("//"):
                    path = path[2:]
                # path = path.replace('Mac/', 'mac/')

            html = html.replace("##htmlroot##", path)
            return html
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def setBadges(self):
        try:
            amount = client.amountOutdatedFonts()
            if client.get("pendingInvitations"):
                amount += len(client.get("pendingInvitations"))
            if amount > 0:
                self.setBadgeLabel(str(amount))
            else:
                self.setBadgeLabel("")

        # def setPublisherInstalledFontBadge(self, b64ID, string):
        #   if string:
        #       self.javaScript('$("#sidebar #%s .badge.installed").show(); $("#sidebar #%s .badge.installed").html("%s");' % (b64ID, b64ID, string))
        #   else:
        #       self.javaScript('$("#sidebar #%s .badge.installed").hide();' % b64ID)

        # def setPublisherOutdatedFontBadge(self, b64ID, string):
        #   if string:
        #       self.javaScript('$("#sidebar #%s .badge.outdated").show(); $("#sidebar #%s .badge.outdated").html("%s");' % (b64ID, b64ID, string))
        #   else:
        #       self.javaScript('$("#sidebar #%s .badge.outdated").hide();' % b64ID)
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def debug(self, string):
        try:
            # print(string)
            client.log(string)
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def setAppCastURL(self):
        try:

            profile = client.get("appUpdateProfile") or "normal"

            if MAC and RUNTIME:
                update_url = f"https://api.type.world/appcast/world.type.guiapp/mac/{profile}/appcast.xml?t={int(time.time())}"
                sparkle.setFeedURL_(NSURL.alloc().initWithString_(update_url))

            if WIN and RUNTIME:
                update_url = f"https://api.type.world/appcast/world.type.guiapp/windows/{profile}/appcast.xml?t={int(time.time())}"
                pywinsparkle.win_sparkle_set_appcast_url(update_url)

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )


class DebugWindow(wx.Frame):
    def __init__(self, parent, ID, title):
        try:
            wx.Frame.__init__(
                self, parent, ID, title, wx.DefaultPosition, wx.Size(500, 300)
            )

            # ------ Area for the text output of pressing button
            textarea = wx.TextCtrl(self, -1, size=(500, 300))
            self.text = textarea
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )


class UpdateFrame(wx.Frame):
    def __init__(self, parent):
        try:

            super(UpdateFrame, self).__init__(parent)

            self.Bind(wx.EVT_CLOSE, self.onClose)

            if MAC:
                sparkle.checkForUpdatesInBackground()

            client.log("sparkle.checkForUpdateInformation() finished")
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def onClose(self, event=None):
        try:

            client.log("UpdateFrame.onCLose()")

            self.Destroy()
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )


if MAC:

    class NSAppDelegate(NSObject):
        def applicationWillFinishLaunching_(self, notification):
            try:
                client.log("applicationWillFinishLaunching_()")

                try:

                    app = wx.GetApp()

                    # 	app.CustomOnInit()
                    # 	app.frame.setMenuBar()

                    if app.startWithCommand == "checkForUpdateInformation":

                        from AppKit import NSApplicationActivationPolicyAccessory

                        NSApp().setActivationPolicy_(
                            NSApplicationActivationPolicyAccessory
                        )

                except:
                    client.log(traceback.format_exc())
            except Exception as e:
                client.handleTraceback(
                    sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
                )

        def applicationDidFinishLaunching_(self, notification):
            try:

                client.log("applicationDidFinishLaunching_()")

            except Exception as e:
                client.handleTraceback(
                    sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
                )


class MyApp(wx.App):
    def __init__(
        self, redirect=False, filename=None, useBestVisual=False, clearSigInt=True
    ):
        try:

            # # Hi-DPI support on Windows, see https://discuss.wxpython.org/t/support-for-high-dpi-on-windows-10/32925/2
            # try:
            #     import ctypes

            #     ctypes.windll.shcore.SetProcessDpiAwareness(True)

            #     # from ctypes import OleDLL

            #     # # Turn on high-DPI awareness to make sure rendering is sharp on big
            #     # # monitors with font scaling enabled.
            #     # OleDLL("shcore").SetProcessDpiAwareness(1)

            # except AttributeError:
            #     # We're on a non-Windows box.
            #     pass

            # except OSError:
            #     # exc.winerror is often E_ACCESSDENIED (-2147024891/0x80070005).
            #     # This occurs after the first run, when the parameter is reset in the
            #     # executable's manifest and then subsequent calls raise this exception
            #     # See last paragraph of Remarks at
            #     # [https://msdn.microsoft.com/en-us/library/dn302122(v=vs.85).aspx](https://msdn.microsoft.com/en-us/library/dn302122(v=vs.85).aspx)
            #     pass

            # Abuse unused "filename" as "startWithCommand"
            self.startWithCommand = filename
            self.exitCode = 0
            super().__init__(redirect, None, useBestVisual, clearSigInt)

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def OnPreInit(self):

        try:
            if MAC:
                if (
                    self.startWithCommand == "checkForUpdateInformation"
                ):  # Otherwise MacOpenURL() wont work
                    NSApplication.sharedApplication().setDelegate_(
                        NSAppDelegate.alloc().init()
                    )
                    client.log("set NSAppDelegate")
        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def MacOpenURL(self, url):
        try:
            client.log("MyApp.MacOpenURL(%s)" % url)

            if self.frame.fullyLoaded:
                self.frame.handleURL(url)
            else:
                self.frame.justAddedPublisher = url

            self.frame.Show()

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )

    def OnInit(self):

        try:

            client.log("self.startWithCommand: %s" % self.startWithCommand)

            if self.startWithCommand == "checkForUpdateInformation":

                if MAC:
                    self.frame = UpdateFrame(None)

            else:

                if WIN:
                    import winreg as wreg

                    current_file = __file__
                    key = wreg.CreateKey(
                        wreg.HKEY_CURRENT_USER,
                        "Software\\Microsoft\\Internet Explorer\\Main\\FeatureControl\\FEATURE_BROWSER_EMULATION",
                    )
                    wreg.SetValueEx(key, current_file, 0, wreg.REG_DWORD, 11001)

                frame = AppFrame()
                self.frame = frame
                self.frame.parent = self
                self.frame.Show()

                # Window Styling
                if MAC:
                    w = NSApp().mainWindow()
                    w.setMovable_(False)

                    from AppKit import (
                        NSLeftMouseDraggedMask,
                        NSLeftMouseUpMask,
                        NSScreen,
                        NSLeftMouseUp,
                    )

                    class MyView(NSView):
                        # def mouseDragged_(self, event):
                        # 	event.window().setFrameOrigin_(NSPoint(event.window().frame().origin.x + event.deltaX(), event.window().frame().origin.y - event.deltaY()))

                        def mouseDown_(self, event):

                            _initialLocation = event.locationInWindow()

                            while True:

                                theEvent = w.nextEventMatchingMask_(
                                    NSLeftMouseDraggedMask | NSLeftMouseUpMask
                                )
                                point = theEvent.locationInWindow()
                                screenVisibleFrame = (
                                    NSScreen.mainScreen().visibleFrame()
                                )
                                windowFrame = w.frame()
                                newOrigin = windowFrame.origin

                                # Get the mouse location in window coordinates.
                                currentLocation = point

                                # Update the origin with the difference between the new mouse location and the old mouse location.
                                newOrigin.x += currentLocation.x - _initialLocation.x
                                newOrigin.y += currentLocation.y - _initialLocation.y

                                # Don't let window get dragged up under the menu bar
                                if (newOrigin.y + windowFrame.size.height) > (
                                    screenVisibleFrame.origin.y
                                    + screenVisibleFrame.size.height
                                ):
                                    newOrigin.y = screenVisibleFrame.origin.y + (
                                        screenVisibleFrame.size.height
                                        - windowFrame.size.height
                                    )

                                # Move the window to the new location
                                w.setFrameOrigin_(newOrigin)

                                if theEvent.type() == NSLeftMouseUp:
                                    break

                            event.window().setFrameOrigin_(
                                NSPoint(
                                    event.window().frame().origin.x + event.deltaX(),
                                    event.window().frame().origin.y - event.deltaY(),
                                )
                            )

                        # def drawRect_(self, rect):
                        # 	NSColor.yellowColor().set()
                        # 	NSRectFill(rect)

                    self.frame.dragView = MyView.alloc().initWithFrame_(
                        NSMakeRect(0, 0, self.frame.GetSize()[0], 40)
                    )
                    w.contentView().addSubview_(self.frame.dragView)

                    self.frame.javaScript("$('.sidebar').css('padding-top', '32px');")
                    self.frame.SetTitle("")

                    w.setStyleMask_(1 << 0 | 1 << 1 | 1 << 2 | 1 << 3 | 1 << 15)
                    w.setTitlebarAppearsTransparent_(1)

                    w.setTitleVisibility_(1)
                    toolbar = NSToolbar.alloc().init()
                    toolbar.setShowsBaselineSeparator_(0)
                    w.setToolbar_(toolbar)

                client.log("MyApp.OnInit()")

                html = ReadFromFile(
                    os.path.join(
                        os.path.dirname(__file__), "htmlfiles", "main", "index.html"
                    )
                )

                #        html = html.replace('##jqueryuicss##', ReadFromFile(os.path.join(os.path.dirname(__file__), 'htmlfiles', 'main', 'css', 'jquery-ui.css')))
                html = html.replace("APPVERSION", APPVERSION)

                html = localizeString(html, html=True)
                html = frame.replaceHTML(html)

                # memoryfs = wx.MemoryFSHandler()
                # wx.FileSystem.AddHandler(memoryfs)
                # wx.MemoryFSHandler.AddFileWithMimeType("index.htm", html, 'text/html')
                # frame.html.RegisterHandler(wx.html2.WebViewFSHandler("memory"))

                #        frame.html.SetPage(html, os.path.join(os.path.dirname(__file__), 'htmlfiles', 'main'))
                # frame.html.SetPage(html, '')
                # frame.html.Reload()

                filename = os.path.join(prefDir, "world.type.guiapp.app.html")
                WriteToFile(filename, html)
                # print(filename)
                frame.html.LoadURL("file://%s" % filename)

                # TODO: Remove later, old implementation
                filename = os.path.join(os.path.dirname(__file__), "app.html")
                if os.path.exists(filename):
                    os.remove(filename)

                # if os.path.exists(openURLFilePath):
                #     urlFile = open(openURLFilePath, 'r')
                #     URL = urlFile.read().strip()
                #     urlFile.close()
                #     frame.justAddedPublisher = URL

                frame.Show()
                frame.CentreOnScreen()

            return True

        except Exception as e:
            client.handleTraceback(
                sourceMethod=getattr(self, sys._getframe().f_code.co_name), e=e
            )


# class MyNSApp(NSApp):


intercomCommands = [
    "amountOutdatedFonts",
    "startListener",
    "killAgent",
    "restartAgent",
    "uninstallAgent",
    "searchAppUpdate",
    "daemonStart",
    "pullServerUpdate",
    "javaScript",
]


def listenerFunction():

    try:
        from multiprocessing.connection import Listener

        address = ("localhost", 65500)
        listener = Listener(address)

        while True:
            conn = listener.accept()
            command = conn.recv()
            commands = command.split(" ")

            if command == "closeListener":
                conn.close()
                listener.close()
                break

            if commands[0] in intercomCommands:
                conn.send(intercom(commands))

            conn.close()

        listener.close()

        client.log("Closed listener loop")

    except:
        client.handleTraceback(sourceMethod=globals()[sys._getframe().f_code.co_name])


def intercom(commands):

    try:

        lock()
        client.log("lock() from within intercom()")
        returnObject = None
        client.mode = "headless"

        if not commands[0] in intercomCommands:
            client.log("Intercom: Command %s not registered" % (commands[0]))

        else:
            client.log("Intercom called with commands: %s" % commands)

            # if commands[0] == 'pullServerUpdate':

            # 	# Sync subscriptions
            # 	if not client.get('lastServerSync') or client.get('lastServerSync') < time.time() - PULLSERVERUPDATEINTERVAL:
            # 		success, message = client.downloadSubscriptions()
            # 		if success:
            # 			subscriptionsUpdatedNotification(message)

            if commands[0] == "javaScript":

                app = wx.GetApp()

                if app:
                    code = base64.b64decode(commands[1].encode()).decode()
                    log(f"Calling javaScript({code})")
                    app.frame.javaScript(code)

                else:
                    app = MyApp(redirect=False, filename=" ".join(commands))
                    app.MainLoop()

            if commands[0] == "amountOutdatedFonts":

                totalSuccess = False

                force = len(commands) > 1 and commands[1] == "force"

                # Preference is set to check automatically
                if (
                    client.get("reloadSubscriptionsInterval")
                    and int(client.get("reloadSubscriptionsInterval")) != -1
                ) or force:

                    # Has never been checked, set to long time ago
                    if not client.get("reloadSubscriptionsLastPerformed"):
                        client.set(
                            "reloadSubscriptionsLastPerformed",
                            int(time.time())
                            - int(client.get("reloadSubscriptionsInterval"))
                            - 10,
                        )

                    # See if we should check now
                    if (
                        int(client.get("reloadSubscriptionsLastPerformed"))
                        < int(time.time())
                        - int(client.get("reloadSubscriptionsInterval"))
                        or force
                    ):

                        client.log("now checking")

                        client.prepareUpdate()

                        for publisher in client.publishers():
                            for subscription in publisher.subscriptions():

                                startTime = time.time()
                                success, message, changes = subscription.update()

                                totalSuccess = totalSuccess and success

                                if not success:
                                    client.log(message)

                                client.log(
                                    "updated %s (%1.2fs)"
                                    % (subscription, time.time() - startTime)
                                )

                        # Reset
                        if client.allSubscriptionsUpdated():
                            client.log("resetting timing")
                            client.set(
                                "reloadSubscriptionsLastPerformed", int(time.time())
                            )

                client.log(
                    "client.amountOutdatedFonts() %s" % (client.amountOutdatedFonts())
                )

                returnObject = client.amountOutdatedFonts()

            if commands[0] == "startListener":

                client.log("about to start listener thread")

                listenerThread = Thread(target=listenerFunction)
                listenerThread.start()

                client.log("listener thread started")

            if commands[0] == "killAgent":

                agent("quit")

            if commands[0] == "uninstallAgent":

                uninstallAgent()

            if commands[0] == "restartAgent":

                agent("quit")

                # Restart after restart
                if client.get("menuBarIcon") and not agentIsRunning():

                    file_path = os.path.join(
                        os.path.dirname(__file__), r"TypeWorld Taskbar Agent.exe"
                    )
                    file_path = file_path.replace(r"\\Mac\Home", r"Z:")
                    import subprocess

                    os.chdir(os.path.dirname(file_path))
                    subprocess.Popen([file_path], executable=file_path)

            if commands[0] == "searchAppUpdate":

                client.log("Started checkForUpdateInformation()")

                if MAC:
                    app = MyApp(redirect=False, filename="checkForUpdateInformation")
                    app.MainLoop()

                if WIN:
                    pywinsparkleDelegate.check_without_ui()

                client.log("Finished checkForUpdateInformation()")

            if commands[0] == "daemonStart":

                agent("amountOutdatedFonts %s" % client.amountOutdatedFonts())

                unlock()
                client.log("unlock() from within intercom()")

        unlock()
        client.log("unlock() from within intercom()")
        client.log("about to return reply: %s" % returnObject)
        return returnObject

    except:
        client.handleTraceback(sourceMethod=globals()[sys._getframe().f_code.co_name])


def createClient(startWithCommand=None, externallyControlled=True):

    if startWithCommand == "selftest":
        if WIN:
            prefFile = os.path.join(
                prefDir, f"preferences.selftest.{int(time.time())}.json"
            )
            prefs = JSON(prefFile)
        elif MAC:
            prefs = AppKitNSUserDefaults(f"world.type.selftest.{int(time.time())}")
    else:
        if WIN:
            prefFile = os.path.join(prefDir, "preferences.json")
            prefs = JSON(prefFile)
        elif MAC:
            prefs = AppKitNSUserDefaults("world.type.clientapp" if DESIGNTIME else None)

    customMothership = None
    for arg in sys.argv:
        if arg.startswith("mothership="):
            customMothership = arg.split("=")[-1]

    global client
    client = APIClient(
        preferences=prefs,
        delegate=delegate,
        mode="gui",
        zmqSubscriptions=True,
        mothership=customMothership,
        externallyControlled=externallyControlled,
    )


def startApp(startWithCommand=None):

    # Prevent duplicate start
    if WIN:
        pid = PID("TypeWorld.exe")
        if pid:
            from pywinauto import Application

            try:
                app = Application().connect(process=pid)
                app.top_window().set_focus()
            except:
                pass
            sys.exit(1)

    # Start Intercom Server
    listenerThread = Thread(target=listenerFunction)
    listenerThread.start()

    # Start App
    app = MyApp(redirect=DEBUG and WIN, filename=startWithCommand)
    client.delegate.app = app

    # Last call, no more code after this point
    app.MainLoop()

    print("app.exitCode:", app.exitCode)
    sys.exit(app.exitCode)


# Main Loop
if __name__ == "__main__":

    # Decide what to do on startupp:

    # Just start intercom, no GUI
    if len(sys.argv) > 1 and sys.argv[1] in intercomCommands:
        createClient()
        client.log(intercom(sys.argv[1:]))

    # Self Test
    elif len(sys.argv) > 1 and sys.argv[1] == "selftest":
        createClient(startWithCommand="selftest", externallyControlled=False)
        startApp(startWithCommand="selftest")

    # Normal App Window
    else:
        createClient()
        startApp()
