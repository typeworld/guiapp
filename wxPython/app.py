#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import wx, os, webbrowser, urllib.request, urllib.parse, urllib.error, base64, plistlib, json, datetime, traceback
from threading import Thread
import threading
import wx.html2
import locales
import sys
import urllib.request, urllib.parse, urllib.error, time
from functools import partial

import platform
WIN = platform.system() == 'Windows'
MAC = platform.system() == 'Darwin'

from ynlib.files import ReadFromFile, WriteToFile
from ynlib.strings import kashidas, kashidaSentence
from ynlib.web import GetHTTP

from typeWorldClient import APIClient, JSON, AppKitNSUserDefaults
import typeWorld.api.base


try:
    __file__ = os.path.abspath(__file__)

except:
    __file__ = sys.executable


import ctypes, sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

APPNAME = 'Type.World'
APPVERSION = '0.1.3'
DEBUG = True



if not '.app/Contents' in os.path.dirname(__file__) or not 'app.py' in __file__:
    DESIGNTIME = True
    RUNTIME = False
else:
    DESIGNTIME = False
    RUNTIME = True

print('DESIGNTIME', DESIGNTIME)
print('RUNTIME', RUNTIME)



## Windows:
## Register Custom Protocol Handlers in the Registry. Later, this should be moved into the installer.

if WIN and RUNTIME:
    import winreg as wreg
    for handler in ['typeworldjson', 'typeworldgithub']:
        key = wreg.CreateKey(wreg.HKEY_CLASSES_ROOT, handler)
        wreg.SetValueEx(key, None, 0, wreg.REG_SZ, 'URL:%s' % handler)
        wreg.SetValueEx(key, 'URL Protocol', 0, wreg.REG_SZ, '')
        key = wreg.CreateKey(key, 'shell\\open\\command')
        wreg.SetValueEx(key, None, 0, wreg.REG_SZ, '"%s" "%%1"' % os.path.join(os.path.dirname(__file__), 'URL Opening Agent', 'TypeWorld Subscription Opener.exe'))

## Windows:
## Create lockfile to prevent second opening of the app


# if WIN:

    # try:
    #     import pywinauto
    #     app = pywinauto.Application().connect(path=__file__)
    #     app.top_window().set_focus()
    #     sys.exit()
    # except:
    #     pass


if WIN:

    # Write our own PID to the lockfile so the agent script can find it
    lockFilePath = os.path.join(os.path.dirname(__file__), 'pid.txt')
    lockFile = open(lockFilePath, 'w')
    lockFile.write(str(os.getpid()))
    lockFile.close()







# class AppBadge(NSDockTilePlugIn):

#   def setDockTile_(self, dockTile):

#       if dockTile:
#           dockTile.setBadgeLabel_('X')





if not DESIGNTIME:
    plist = plistlib.readPlist(os.path.join(os.path.dirname(__file__), '..', 'Info.plist'))
    APPVERSION = plist['CFBundleShortVersionString']


class AppFrame(wx.Frame):
    def __init__(self, parent):        

        if platform.system() == 'Windows':
            prefs = JSON(os.path.join(os.path.dirname(__file__), 'preferences.json'))
        else:
            prefs = AppKitNSUserDefaults('world.type.clientapp' if DESIGNTIME else None)


        self.client = APIClient(preferences = prefs)


        ### Preferences
        self.changePreferences()
        if not self.client.preferences.get('appVersion'):
            self.client.preferences.set('appVersion', APPVERSION)
        if not self.client.preferences.get('localizationType'):
            self.client.preferences.set('localizationType', 'systemLocale')
        if not self.client.preferences.get('customLocaleChoice'):
            self.client.preferences.set('customLocaleChoice', self.systemLocale())
        if not self.client.preferences.get('reloadSubscriptionsInterval'):
            self.client.preferences.set('reloadSubscriptionsInterval', 1 * 24 * 60 * 60) # one day



        self.thread = threading.current_thread()



        self.justAddedPublisher = None
        self.fullyLoaded = False
        self.panelVisible = False



        # Window Size
        minSize = [1000, 700]
        if self.client.preferences.get('sizeMainWindow'):
            size = list(self.client.preferences.get('sizeMainWindow'))

            if MAC:
                from AppKit import NSScreen
                screenSize = NSScreen.mainScreen().frame().size
                if size[0] > screenSize.width:
                    size[0] = screenSize.width - 50
                if size[1] > screenSize.height:
                    size[1] = screenSize.height - 50
        else:
            size=[1000,700]
        size[0] = max(size[0], minSize[0])
        size[1] = max(size[1], minSize[1])
        super(AppFrame, self).__init__(parent, size = size)
        self.SetMinSize(minSize)

        self.Title = '%s %s%s' % (APPNAME, APPVERSION, ' ADMIN' if is_admin else '')

        self.html = wx.html2.WebView.New(self)
        self.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, self.onNavigating, self.html)
        self.Bind(wx.html2.EVT_WEBVIEW_NAVIGATED, self.onNavigated, self.html)
        self.Bind(wx.html2.EVT_WEBVIEW_ERROR, self.onError, self.html)
        self.Bind(wx.html2.EVT_WEBVIEW_LOADED, self.onLoad, self.html)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.html, 1, wx.EXPAND)
        self.SetSizer(sizer)



        ### Menus
        menuBar = wx.MenuBar()

        # Exit
        menu = wx.Menu()
        m_opensubscription = menu.Append(wx.ID_OPEN, "%s\tCtrl-O" % (self.localize('Add Subscription')))
        self.Bind(wx.EVT_MENU, self.showAddPublisher, m_opensubscription)
        m_CheckForUpdates = menu.Append(wx.NewId(), "%s..." % (self.localize('Check for Updates')))
        self.Bind(wx.EVT_MENU, self.onCheckForUpdates, m_CheckForUpdates)
        m_closewindow = menu.Append(wx.ID_CLOSE, "%s\tCtrl-W" % (self.localize('Close Window')))
        self.Bind(wx.EVT_MENU, self.onClose, m_closewindow)
        m_exit = menu.Append(wx.ID_EXIT, "%s\tCtrl-X" % (self.localize('Exit')))
        self.Bind(wx.EVT_MENU, self.onQuit, m_exit)


        menuBar.Append(menu, "&%s" % (self.localize('File')))

        # Edit
        # if 'wxMac' in wx.PlatformInfo and wx.VERSION >= (3,0):
        #   wx.ID_COPY = wx.NewId()
        #   wx.ID_PASTE = wx.NewId()
        editMenu = wx.Menu()
        editMenu.Append(wx.ID_SELECTALL, "%s\tCTRL+A" % (self.localize('Select All')))
        editMenu.Append(wx.ID_COPY, "%s\tCTRL+C" % (self.localize('Copy')))
        editMenu.Append(wx.ID_CUT, "%s\tCTRL+X" % (self.localize('Cut')))
        editMenu.Append(wx.ID_PASTE, "%s\tCTRL+V" % (self.localize('Paste')))
        menuBar.Append(editMenu, "&%s" % (self.localize('Edit')))

        menu = wx.Menu()
        m_about = menu.Append(wx.ID_ABOUT, "&%s %s" % (self.localize('About'), APPNAME))
        self.Bind(wx.EVT_MENU, self.onAbout, m_about)
        m_prefs = menu.Append(wx.ID_PREFERENCES, "&%s\tCtrl-," % (self.localize('Preferences')))
        self.Bind(wx.EVT_MENU, self.onPreferences, m_prefs)        

        # menuBar.Append(menu, "Type.World")
        menuBar.Append(menu, "&%s" % (self.localize('Help')))

        self.SetMenuBar(menuBar)



        self.CentreOnScreen()
        self.Show()


        self.Bind(wx.EVT_SIZE, self.onResize, self)
        self.Bind(wx.EVT_ACTIVATE, self.onActivate, self)


        # self.Bind(wx.EVT_ACTIVATE, self.onActivate)

        # if wx.Platform == '__WXMAC__':
        #   w = self.nsapp.mainWindow()

        #   from AppKit import NSFullSizeContentViewWindowMask, NSWindowTitleHidden, NSBorderlessWindowMask, NSResizableWindowMask, NSTitledWindowMask, NSFullSizeContentViewWindowMask, NSWindowStyleMaskFullSizeContentView

#           w.setStyleMask_(NSFullSizeContentViewWindowMask)

            # 0: NSWindowStyleMaskTitled
            # 1: NSWindowStyleMaskClosable
            # 2: NSWindowStyleMaskMiniaturizable
            # 3: NSWindowStyleMaskResizable
            # 8: NSWindowStyleMaskTexturedBackground
            # 12: NSWindowStyleMaskUnifiedTitleAndToolbar
            # 14: NSWindowStyleMaskFullScreen
            # 15: NSWindowStyleMaskFullSizeContentView
            # 4: NSWindowStyleMaskUtilityWindow
            # 6: NSWindowStyleMaskDocModalWindow
            # 7: NSWindowStyleMaskNonactivatingPanel
            # 13: NSWindowStyleMaskHUDWindow


            # w.setStyleMask_(1 << 0 | 1 << 1 | 1 << 2 | 1 << 3)
            # w.setTitlebarAppearsTransparent_(True)
            # w.setTitleVisibility_(NSWindowTitleHidden)


#           w.setTitle_(' ')


#           w.setStyleMask_(NSBorderlessWindowMask)
            #w.setTitlebarAppearsTransparent_(1)
#           w.setIsMovable_(True)
            #w.setTitleVisibility_(0)
            #w.setMovableByWindowBackground_(True)
            # js = '$("#sidebar").css("padding-top", "18px");'
            # self.javaScript(js)


        if not DESIGNTIME:
            # Your Qt QApplication instance
            QT_APP = self
            # URL to Appcast.xml, eg. https://yourserver.com/Appcast.xml
            APPCAST_URL = 'https://type.world/downloads/guiapp/appcast.xml'
            # Path to Sparkle's "Sparkle.framework" inside your app bundle

            if '.app' in os.path.dirname(__file__):
                SPARKLE_PATH = os.path.join(os.path.dirname(__file__), '..', 'Frameworks', 'Sparkle.framework')
            else:
                SPARKLE_PATH = '/Users/yanone/Code/Sparkle/Sparkle.framework'

            from objc import pathForFramework, loadBundle
            sparkle_path = pathForFramework(SPARKLE_PATH)
            self.objc_namespace = dict()
            loadBundle('Sparkle', self.objc_namespace, bundle_path=sparkle_path)
            def about_to_quit():
                # See https://github.com/sparkle-project/Sparkle/issues/839
                self.objc_namespace['NSApplication'].sharedApplication().terminate_(None)

    #       QT_APP.aboutToQuit.connect(about_to_quit)
            self.sparkle = self.objc_namespace['SUUpdater'].sharedUpdater()
            self.sparkle.setAutomaticallyChecksForUpdates_(True)
    #       self.sparkle.setAutomaticallyDownloadsUpdates_(True)
            NSURL = self.objc_namespace['NSURL']
            self.sparkle.setFeedURL_(NSURL.URLWithString_(APPCAST_URL))
            self.sparkle.checkForUpdatesInBackground()


    def javaScript(self, script):
#        print()
        if self.fullyLoaded:
            if threading.current_thread() == self.thread:
#                print('JavaScript Executed:')
#                print(str(script.encode())[:100], '...')
                self.html.RunScript(script)
            else:
                pass
#                print('JavaScript called from another thread:')
#                print(str(script.encode())[:100], '...')



        else:
            pass
#            print('JavaScript Execution: Page not fully loaded:')
#            print(str(script.encode())[:100], '...')


    def changePreferences(self):

        # Has no version information
        if not self.client.preferences.get('appVersion'):

            self.log('Changing preferences from no version to version %s' % APPVERSION)

            # A few general keys
            for key in ['sizeMainWindow', 'anonymousAppID', 'currentPublisher', 'customLocaleChoice', 'localizationType', 'publishers']:
                if self.client.preferences.get(key) and type(self.client.preferences.get(key)) == str:
                    self.log('Translating content of "%s"' % key)
                    self.client.preferences.set(key, json.loads(self.client.preferences.get(key)))


            # Go through each publisher
            if self.client.preferences.get('publishers'):
                for publisherURL in self.client.preferences.get('publishers'):
                    publisher = json.loads(self.client.preferences.get(publisherURL))
                    publisher['type'] = 'JSON'
                    self.client.preferences.set('publisher(%s)' % publisherURL, publisher)
                    self.log('Translated "%s" to "publisher(%s)"' % (publisherURL, publisherURL))
                    self.client.preferences.remove(publisherURL)
                    self.log('Deleted "%s"' % (publisherURL))

                    # Go through subscriptions
                    if 'subscriptions' in self.client.preferences.get('publisher(%s)' % publisherURL):
                        for subscriptionURL in self.client.preferences.get('publisher(%s)' % publisherURL)['subscriptions']:

                            _json = json.loads(self.client.preferences.get(subscriptionURL))

                            self.client.preferences.set('subscription(%s)' % subscriptionURL, json.loads(self.client.preferences.get(subscriptionURL)))
                            self.log('Translated "%s" to "subscription(%s)"' % (subscriptionURL, subscriptionURL))
                            self.client.preferences.remove(subscriptionURL)
                            self.log('Deleted "%s"' % (subscriptionURL))

                            # Versions
                            subscription = self.client.preferences.get('subscription(%s)' % subscriptionURL)
                            _json['versions'] = [json.dumps(x) for x in _json['versions']]
                            subscription['versions'] = _json['versions']
                            self.client.preferences.set('subscription(%s)' % subscriptionURL, subscription)
                            self.log('Translated JSON back of "subscription(%s)[versions]"' % subscriptionURL)


            # Delete resources
            for key in list(self.client.preferences.dictionary().keys()):
                if key.startswith('resource('):
                    self.client.preferences.remove(key)
                    self.log('Deleted "%s"' % (key))


                




    def publishersNames(self):
        # Build list, sort it
        publishers = []
        for i, key in enumerate(self.client.endpoints.keys()):
            endpoint = self.client.endpoints[key]
            name, language = endpoint.latestVersion().name.getTextAndLocale(locale = self.locale())
            publishers.append((i, name, language))
        return publishers


    def onCheckForUpdates(self, event):
        self.sparkle.checkForUpdates_(None)

    def onClose(self, event):
        if self.panelVisible:
            self.javaScript('hidePanel();')
        else:
            self.Destroy()

    def onQuit(self, event):
        self.Destroy()

    def onActivate(self, event):

        resize = False

        self.SetTitle(str(sys.argv))


        if MAC:

            size = list(self.GetSize())

            from AppKit import NSScreen
            screenSize = NSScreen.mainScreen().frame().size
            if size[0] > screenSize.width:
                size[0] = screenSize.width - 50
                resize = True
            if size[1] > screenSize.height:
                size[1] = screenSize.height - 50
                resize = True

        if WIN:
            print('User is admin:', is_admin())

        if resize:
            self.SetSize(size)

        if self.client.preferences.get('currentPublisher'):
            self.setPublisherHTML(self.b64encode(self.client.preferences.get('currentPublisher')))

        if WIN:
            self.checkForURLInFile()


    def onResize(self, event):
        # Make title bar transparent
        # https://developer.apple.com/documentation/appkit/nswindowstylemask?language=objc
#       if False:
        # if wx.Platform == '__WXMAC__':
        #   w = self.nsapp.mainWindow()
            # w.setStyleMask_(1 << 0 | 1 << 1 | 1 << 2 | 1 << 3 | 1 << 15)
            # w.setTitlebarAppearsTransparent_(1)
#           w.setTitle_(' ')
#       print w.title(), w.titlebarAppearsTransparent(), w.styleMask()
        self.client.preferences.set('sizeMainWindow', (self.GetSize()[0], self.GetSize()[1]))
        event.Skip()
#       print event.Veto()
#       return


    def onAbout(self, event):

        try:

            html = []

            html.append('<p style="text-align: center; margin-bottom: 20px;">')
            html.append('<img src="file://##htmlroot##/biglogo.svg" style="width: 200px;"><br />')
            html.append('</p>')
            html.append('<p>')
            html.append('#(AboutText)')
            html.append('</p>')
            html.append('<p>')
            html.append('#(Anonymous App ID): %s<br />' % self.client.anonymousAppID())
            html.append('#(Version) %s<br />' % APPVERSION)
            html.append('#(Version History) #(on) <a href="https://type.world/app">type.world/app</a>')
            html.append('</p>')
            # html.append(u'<p>')
            # html.append(u'<a class="button" onclick="python('self.sparkle.checkForUpdates_(None)');">#(Check for Updates)</a>')
            # html.append(u'</p>')


            # Print HTML
            html = ''.join(html)
            html = self.replaceHTML(html)
            html = self.localizeString(html, html = True)
            html = html.replace('"', '\'')
            html = html.replace('\n', '')
#            print(html)
            js = '$("#about .inner").html("' + html + '");'
            self.javaScript(js)


            self.javaScript('showAbout();')

        except:
            self.log(traceback.format_exc())



    def onPreferences(self, event):


        html = []

        # Update Interval
        html.append('<h2>#(Update Interval)</h2>')
        html.append('<p>#(UpdateIntervalExplanation)</p>')
        html.append('<p>')
        html.append('<select id="updateIntervalChoice" style="">')
        for code, name in (
            (-1, '#(Manually)'),
            (1 * 60 * 60, '#(Hourly)'),
            (24 * 60 * 60, '#(Daily)'),
            (7 * 24 * 60 * 60, '#(Weekly)'),
            (30 * 24 * 60 * 60, '#(Monthly)'),
        ):
            html.append('<option value="%s" %s>%s</option>' % (code, 'selected' if str(code) == str(self.client.preferences.get('reloadSubscriptionsInterval')) else '', name))
        html.append('</select>')
        html.append('<script>$("#preferences #updateIntervalChoice").click(function() {setPreference("reloadSubscriptionsInterval", $("#preferences #updateIntervalChoice").val());});</script>')
        html.append('</p>')

        html.append('<p></p>')

        # Localoization
        systemLocale = self.systemLocale()
        for code, name in locales.locales:
            if code == systemLocale:
                systemLocale = name
                break
        html.append('<h2>App Localization</h2>')
        html.append('<p>')
        html.append('<span><input id="systemLocale" value="systemLocale" type="radio" name="localizationType" %s><label for="systemLocale">Use System Locale (%s)</label></span>' % ('checked' if self.client.preferences.get('localizationType') == 'systemLocale' else '', systemLocale))
        html.append('<script>$("#preferences #systemLocale").click(function() {setPreference("localizationType", "systemLocale");});</script>')
        html.append('<br />')
        html.append('<span><input id="customLocale" value="customLocale" type="radio" name="localizationType" %s><label for="customLocale">Use Custom Locale (choose below). Requires restart to take full effect.</label></span>' % ('checked' if self.client.preferences.get('localizationType') == 'customLocale' else ''))
        html.append('<script>$("#preferences #customLocale").click(function() {setPreference("localizationType", "customLocale");});</script>')
        html.append('<br />')
        html.append('<select id="customLocaleChoice" style="">')
        for code, name in locales.locales:
            html.append('<option value="%s" %s>%s</option>' % (code, 'selected' if code == self.client.preferences.get('customLocaleChoice') else '', name))
        html.append('</select>')
        html.append('<script>$("#preferences #customLocaleChoice").click(function() {setPreference("customLocaleChoice", $("#preferences #customLocaleChoice").val());});</script>')
        html.append('</p>')





        # Print HTML
        html = ''.join(html)
        html = html.replace('"', '\'')
        html = html.replace('\n', '')
        html = self.localizeString(html)
#       print html
        js = '$("#preferences .inner").html("' + html + '");'
        self.javaScript(js)

        self.javaScript('showPreferences();')


    def onNavigating(self, evt):
        uri = evt.GetURL() # you may need to deal with unicode here
        if uri.startswith('x-python://'):
            code = uri.split("x-python://")[1]
            code = urllib.parse.unquote(code)
            if code.endswith('/'):
                code = code[:-1]
            code = code.replace('http//', 'http://')
            code = code.replace('https//', 'https://')
            code = code.replace('____', '\'')
            print('Python code:', code)
            exec(code)
            evt.Veto()
        elif uri.startswith('http://') or uri.startswith('https://'):
            
            webbrowser.open_new_tab('https://type.world/linkRedirect/?url=' + urllib.parse.quote(uri))
            evt.Veto()
        # else:
        #   code = uri
        #   code = urllib.unquote(code)
        #   print code
        #   exec(code)
        #   evt.Veto()

    def onNavigated(self, evt):
        uri = evt.GetURL() # you may need to deal with unicode here
        print('Navigated: %s' % uri)


    def onError(self, evt):
        print()
        print('Error received from WebView:', evt.GetString())
#       raise Exception(evt.GetString())


    def showAddPublisher(self, evt):
        print('showAddPublisher()')
        self.javaScript('showAddPublisher();')

    def addPublisherJavaScript(self, url, username = None, password = None):

        self.log('addPublisherJavaScript(%s, %s, %s)' % (url, username, password))
        self.javaScript('addPublisher("%s", "%s", "%s", "%s");' % (url, username or '', password or '', self.localizeString('#(Loading Subscription)')))


    def addPublisher(self, url, username = None, password = None):

        for protocol in typeWorld.api.base.PROTOCOLS:
            url = url.replace(protocol + '//', protocol + '://')
        url = url.replace('http//', 'http://')
        url = url.replace('https//', 'https://')

        # Check for known protocol
        known = False
        for protocol in typeWorld.api.base.PROTOCOLS:
            if url.startswith(protocol):
                known = True
                break
        if not known:
            self.errorMessage('Unknown protocol. Known are: %s' % (typeWorld.api.base.PROTOCOLS))
            self.javaScript('$("#addSubscriptionFormSubmitButton").show();')
            self.javaScript('$("#addSubscriptionFormCancelButton").show();')
            self.javaScript('$("#addSubscriptionFormSubmitAnimation").hide();')

            self.javaScript('hideCenterMessage();')
            return

        # remove URI
        print(('addPublisher', url))

        success, message, publisher = self.client.addSubscription(url, username, password)

        if success:

            b64ID = self.b64encode(publisher.canonicalURL)

            self.setSideBarHTML()
            self.setPublisherHTML(b64ID)
            self.javaScript("hidePanel();")



        else:

            self.errorMessage(message)

        self.javaScript('$("#addSubscriptionFormSubmitButton").show();')
        self.javaScript('$("#addSubscriptionFormCancelButton").show();')
        self.javaScript('$("#addSubscriptionFormSubmitAnimation").hide();')

        self.javaScript('hideCenterMessage();')


    def removePublisher(self, evt, b64ID):

        publisher = self.client.publisher(self.b64decode(b64ID))

        dlg = wx.MessageDialog(self, self.localizeString('#(Are you sure)'), self.localizeString('#(Remove X)').replace('%name%', self.localizeString(publisher.name(self.locale())[0])), wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        
        if result:

            publisher.delete()
            self.setSideBarHTML()
            self.javaScript("hideMain();")

    def removeSubscription(self, evt, b64ID):


        for publisher in self.client.publishers():
            for subscription in publisher.subscriptions():
                if subscription.url == self.b64decode(b64ID):


                    dlg = wx.MessageDialog(self, self.localizeString('#(Are you sure)'), self.localizeString('#(Remove X)').replace('%name%', self.localizeString(subscription.name(self.locale()))), wx.YES_NO | wx.ICON_QUESTION)
                    result = dlg.ShowModal() == wx.ID_YES
                    dlg.Destroy()
                    
                    if result:

                        subscription.delete()

                        if publisher.subscription():
                            self.setPublisherHTML(self.b64encode(publisher.canonicalURL))
                        else:
                            self.javaScript("hideMain();")
        self.setSideBarHTML()


    def publisherPreferences(self, i):
        print(('publisherPreferences', i))


    def installAllFonts(self, b64publisherID, b64subscriptionID, b64familyID, b64setName, formatName):

        jsFonts = []

        publisherID = self.b64decode(b64publisherID)
        subscriptionID = self.b64decode(b64subscriptionID)
        familyID = self.b64decode(b64familyID)
        if b64setName:
            setName = self.b64decode(b64setName)
        else:
            setName = None
        publisher = self.client.publisher(publisherID)
        subscription = publisher.subscription(subscriptionID)
        family = subscription.familyByID(familyID)

        for font in family.fonts():
            if font.setName.getText(self.locale) == setName and font.format == formatName:
                if not font.installedVersion():
                    jsFonts.append("Array('%s', '%s', '%s', '%s')" % (b64publisherID, b64subscriptionID, self.b64encode(font.uniqueID), font.getVersions()[-1].number))

        call = 'installFonts(Array(' + ','.join(jsFonts) + '), true);'
        self.javaScript(call)


    def removeAllFonts(self, b64publisherID, b64subscriptionID, b64familyID, b64setName, formatName):

        jsFonts = []

        publisherID = self.b64decode(b64publisherID)
        subscriptionID = self.b64decode(b64subscriptionID)
        familyID = self.b64decode(b64familyID)
        if b64setName:
            setName = self.b64decode(b64setName)
        else:
            setName = None
        publisher = self.client.publisher(publisherID)
        subscription = publisher.subscription(subscriptionID)
        family = subscription.familyByID(familyID)

        for font in family.fonts():
            if font.setName.getText(self.locale) == setName and font.format == formatName:
                if font.installedVersion():
                    jsFonts.append("Array('%s', '%s', '%s', '%s')" % (b64publisherID, b64subscriptionID, self.b64encode(font.uniqueID), font.getVersions()[-1].number))

        call = 'removeFonts(Array(' + ','.join(jsFonts) + '), true);'
        self.javaScript(call)


    def installFonts(self, fonts):

        for b64publisherURL, b64subscriptionURL, b64fontID, version in fonts:

            publisherURL = self.b64decode(b64publisherURL)
            subscriptionURL = self.b64decode(b64subscriptionURL)
#           fontID = self.b64decode(b64fontID)

            publisher = self.client.publisher(publisherURL)
#           subscription = publisher.subscription(subscriptionURL)

            self.installFont(b64publisherURL, b64subscriptionURL, b64fontID, version)
            self.setSideBarHTML()
            self.setBadges()

        self.setPublisherHTML(b64publisherURL)


    def installFont(self, b64publisherURL, b64subscriptionURL, b64fontID, version):

        publisherURL = self.b64decode(b64publisherURL)
        subscriptionURL = self.b64decode(b64subscriptionURL)
        fontID = self.b64decode(b64fontID)

        publisher = self.client.publisher(publisherURL)
        subscription = publisher.subscription(subscriptionURL)
        api = subscription.latestVersion()

        success, message = subscription.installFont(fontID, version)

        if success:

            pass
            # self.setPublisherInstalledFontBadge(self.b64encode(subscription.parent.canonicalURL), subscription.parent.amountInstalledFonts())
            # self.setPublisherHTML(self.b64encode(subscription.parent.canonicalURL))

        else:

            if type(message) in (str, str):
                self.errorMessage(message)
            else:
                self.errorMessage('Server: %s' % message.getText(self.locale()))

            # self.javaScript("$('#%s .statusButton').hide();" % b64fontID)
            # self.javaScript("$('#%s .removeButton').show();" % b64fontID)


    def removeFonts(self, fonts):

        for b64publisherURL, b64subscriptionURL, b64fontID in fonts:

            publisherURL = self.b64decode(b64publisherURL)
            subscriptionURL = self.b64decode(b64subscriptionURL)
#           fontID = self.b64decode(b64fontID)

            publisher = self.client.publisher(publisherURL)
#           subscription = publisher.subscription(subscriptionURL)

            self.removeFont(b64publisherURL, b64subscriptionURL, b64fontID)
            self.setSideBarHTML()
            self.setBadges()

        self.setPublisherHTML(b64publisherURL)


    


        publisherURL = self.b64decode(b64publisherURL)
        subscriptionURL = self.b64decode(b64subscriptionURL)
        fontID = self.b64decode(b64fontID)

        # self.javaScript("$('#%s .installButton').hide();" % b64fontID)
        # self.javaScript("$('#%s .status').show();" % b64fontID)

        print(('installFont', publisherURL, subscriptionURL, fontID))

        publisher = self.client.publisher(publisherURL)
        subscription = publisher.subscription(subscriptionURL)
#       api = subscription.latestVersion()
#       b64ID = self.b64encode(publisherURL)

        # Check if font is already installed
        if subscription.installedFontVersion(fontID):
            print(('Removing old version %s' % version))
            success, message = subscription.removeFont(fontID)

            if not success:
                self.errorMessage(message)

            else:
                success, message = subscription.installFont(fontID, version)

        else:
            success, message = subscription.installFont(fontID, version)

        if success:

            pass
            
        else:

            if type(message) in (str, str):
                
                if message == 'seatAllowanceReached':
                    self.errorMessage('seatAllowanceReached')

                else:
                    self.errorMessage(message)
            else:
                self.errorMessage('Server: %s' % message.getText(self.locale()))

            # self.javaScript("$('#%s .statusButton').hide();" % b64fontID)
            # self.javaScript("$('#%s .installButton').show();" % b64fontID)


    def removeFont(self, b64publisherURL, b64subscriptionURL, b64fontID):

        publisherURL = self.b64decode(b64publisherURL)
        subscriptionURL = self.b64decode(b64subscriptionURL)
        fontID = self.b64decode(b64fontID)

        publisher = self.client.publisher(publisherURL)
        subscription = publisher.subscription(subscriptionURL)
        api = subscription.latestVersion()

        success, message = subscription.removeFont(fontID)

        if success:

            pass
            # self.setPublisherInstalledFontBadge(self.b64encode(subscription.parent.canonicalURL), subscription.parent.amountInstalledFonts())
            # self.setPublisherHTML(self.b64encode(subscription.parent.canonicalURL))

        else:

            if type(message) in (str, str):
                self.errorMessage(message)
            else:
                self.errorMessage('Server: %s' % message.getText(self.locale()))

            # self.javaScript("$('#%s .statusButton').hide();" % b64fontID)
            # self.javaScript("$('#%s .removeButton').show();" % b64fontID)




    def onContextMenu(self, x, y, target, b64ID):
#       print x, y, target, b64ID, self.b64decode(b64ID)

        x = max(0, int(x) - 70)

        if 'contextmenu publisher' in target:

            for publisher in self.client.publishers():
                if publisher.canonicalURL == self.b64decode(b64ID):
                    break

            menu = wx.Menu()

            item = wx.MenuItem(menu, wx.NewId(), self.localizeString('#(Update All Subscriptions)'))
            menu.Append(item)
            menu.Bind(wx.EVT_MENU, partial(self.reloadPublisherJavaScript, b64ID = b64ID), item)

            if publisher.amountOutdatedFonts():
                item = wx.MenuItem(menu, wx.NewId(), self.localizeString('#(Update All Fonts)'))
                menu.Append(item)
                menu.Bind(wx.EVT_MENU, partial(self.updateAllFonts, publisherB64ID = b64ID, subscriptionB64ID = None), item)


            item = wx.MenuItem(menu, wx.NewId(), self.localizeString('#(Show in Finder)'))
            menu.Append(item)
            menu.Bind(wx.EVT_MENU, partial(self.showPublisherInFinder, b64ID = b64ID), item)

            if publisher.get('type') == 'GitHub':
                item = wx.MenuItem(menu, wx.NewId(), self.localizeString('#(Preferences)'))
                menu.Append(item)
                menu.Bind(wx.EVT_MENU, partial(self.showPublisherPreferences, b64ID = b64ID), item)

            menu.AppendSeparator()

            item = wx.MenuItem(menu, wx.NewId(), self.localizeString('#(Remove)'))
            menu.Append(item)
            menu.Bind(wx.EVT_MENU, partial(self.removePublisher, b64ID = b64ID), item)

            self.PopupMenu(menu, wx.Point(int(x), int(y)))
            menu.Destroy()


        elif 'contextmenu subscription' in target:
            menu = wx.Menu()

            item = wx.MenuItem(menu, wx.NewId(), self.localizeString('#(Update Subscription)'))
            menu.Append(item)
            menu.Bind(wx.EVT_MENU, partial(self.reloadSubscriptionJavaScript, b64ID = b64ID), item)

            for publisher in self.client.publishers():
                for subscription in publisher.subscriptions():
                    if subscription.url == self.b64decode(b64ID):
                        if publisher.amountOutdatedFonts():
                            item = wx.MenuItem(menu, wx.NewId(), self.localizeString('#(Update All Fonts)'))
                            menu.Append(item)
                            menu.Bind(wx.EVT_MENU, partial(self.updateAllFonts, publisherB64ID = None, subscriptionB64ID = b64ID), item)
                        break

            menu.AppendSeparator()

            item = wx.MenuItem(menu, wx.NewId(), self.localizeString('#(Remove)'))
            menu.Append(item)
            menu.Bind(wx.EVT_MENU, partial(self.removeSubscription, b64ID = b64ID), item)


            self.PopupMenu(menu, wx.Point(int(x), int(y)))
            menu.Destroy()

        elif 'contextmenu font' in target:
            menu = wx.Menu()

            fontID = self.b64decode(b64ID)

            for publisher in self.client.publishers():
                for subscription in publisher.subscriptions():
                    for foundry in subscription.foundries():
                        for family in foundry.families():
                            for font in family.fonts():
                                if font.uniqueID == fontID:


                                    if font.installedVersion():
                                        item = wx.MenuItem(menu, wx.NewId(), self.localizeString('#(Show in Finder)'))
                                        menu.Append(item)
                                        menu.Bind(wx.EVT_MENU, partial(self.showFontInFinder, subscription = subscription, fontID = fontID), item)

                                    # create a submenu
                                    subMenu = wx.Menu()
                                    menu.AppendMenu(wx.NewId(), self.localizeString('#(Install Version)'), subMenu)

                                    for version in font.getVersions():

                                        if font.installedVersion() == version.number:
                                            installVersionsSubmenu = subMenu.Append(wx.NewId(), str(version.number), "", wx.ITEM_RADIO)
                                        else:
                                            installVersionsSubmenu = subMenu.Append(wx.NewId(), str(version.number))

                                        subMenu.Bind(wx.EVT_MENU, partial(self.installFontFromMenu, subscription = subscription, fontID = fontID, version = version.number), installVersionsSubmenu)

                                        # item = wx.MenuItem(subMenu, wx.NewId(), version.number)
                                        # subMenu.Append(item)
                                        #menu.Bind(wx.EVT_MENU, partial(self.reloadSubscriptionJavaScript, b64ID = b64ID), item)


                                    self.PopupMenu(menu, wx.Point(int(x), int(y)))
                                    menu.Destroy()

                                    break

        else:

            menu = wx.Menu()

            item = wx.MenuItem(menu, wx.NewId(), self.localizeString('#(Preferences)'))
            menu.Append(item)
            menu.Bind(wx.EVT_MENU, self.onPreferences, item)

            self.PopupMenu(menu, wx.Point(int(x), int(y)))
            menu.Destroy()


    def installFontFromMenu(self, event, subscription, fontID, version):
        self.javaScript("installFonts(Array(Array('%s', '%s', '%s', '%s')), true);" % (self.b64encode(subscription.parent.canonicalURL), self.b64encode(subscription.url), self.b64encode(fontID), version))

    def showPublisherPreferences(self, event, b64ID):

        for publisher in self.client.publishers():
            if publisher.exists and publisher.canonicalURL == self.b64decode(b64ID):


                html = []


                html.append('<h2>%s (%s)</h2>' % (publisher.name(self.locale())[0], publisher.get('type')))
                if publisher.get('type') == 'GitHub':

                    # Rate limits
                    limits, responses = publisher.readGitHubResponse('https://api.github.com/rate_limit')
                    limits = json.loads(limits)

                    html.append('<p>')
                    html.append('#(Username)<br />')
                    html.append('<input type="text" id="username" value="%s">' % (publisher.get('username') or ''))
                    html.append('#(Password)<br />')
                    html.append('<input type="password" id="password" value="%s">' % (publisher.getPassword(publisher.get('username')) if publisher.get('username') else ''))
                    html.append('</p>')
                    html.append('<p>')
                    html.append('#(GitHubRequestLimitExplanation)<br />')
                    html.append(self.localizeString('#(GitHubRequestLimitRemainderExplanation)').replace('%requests%', str(limits['rate']['remaining'])).replace('%time%', datetime.datetime.fromtimestamp(limits['rate']['reset']).strftime('%Y-%m-%d %H:%M:%S')))
                    html.append('</p>')
                    html.append('<script>$("#publisherPreferences #username").blur(function() { setPublisherPreference("%s", "username", $("#publisherPreferences #username").val());});</script>' % (b64ID))
                    html.append('<script>$("#publisherPreferences #password").blur(function() { if ($("#publisherPreferences #username").val()) { setPublisherPassword("%s", $("#publisherPreferences #username").val(), $("#publisherPreferences #password").val()); }});</script>' % (b64ID))



                # Print HTML
                html = ''.join(html)
                html = html.replace('"', '\'')
                html = html.replace('\n', '')
                html = self.localizeString(html)
        #       print html
                js = '$("#publisherPreferences .inner").html("' + html + '");'
                self.javaScript(js)

                self.javaScript('showPublisherPreferences();')

    def reloadSubscriptionJavaScript(self, evt, b64ID):
        print(('reloadSubscriptionJavaScript', b64ID))
        self.javaScript('showCenterMessage("%s", reloadSubscription("%s"));' % (self.localize('Reloading Subscription'), b64ID))

    def reloadPublisherJavaScript(self, evt, b64ID):
        print(('reloadPublisherJavaScript', b64ID))
        self.javaScript('showCenterMessage("%s", reloadPublisher("%s"));' % (self.localize('Reloading Publisher'), b64ID))

    def showPublisherInFinder(self, evt, b64ID):
        
        publisher = self.client.publisher(self.b64decode(b64ID))
        path = publisher.path()

        if not os.path.exists(path):
            os.makedirs(path)

        import subprocess
        subprocess.call(["open", "-R", path])

    def showFontInFinder(self, evt, subscription, fontID):
        font = subscription.fontByID(fontID)
        version = subscription.installedFontVersion(fontID)
        path = font.path(version, folder = None)

        import subprocess
        subprocess.call(["open", "-R", path])


    def updateAllFonts(self, evt, publisherB64ID, subscriptionB64ID):

        fonts = []

        if publisherB64ID:
            publisher = self.client.publisher(self.b64decode(publisherB64ID))
            for subscription in publisher.subscriptions():
                subscriptionB64ID = self.b64encode(subscription.url)
                for foundry in subscription.foundries():
                    for family in foundry.families():
                        for font in family.fonts():
                            if font.isOutdated():
                                fonts.append("Array('%s', '%s', '%s', '%s')" % (publisherB64ID, subscriptionB64ID, self.b64encode(font.uniqueID), font.getVersions()[-1].number))

        elif subscriptionB64ID:
            
            for publisher in self.client.publishers():
                for subscription in publisher.subscriptions():
                    if subscription.url == self.b64decode(subscriptionB64ID):
                        publisherB64ID = self.b64encode(publisher.canonicalURL)
                        break

            for foundry in subscription.foundries():
                for family in foundry.families():
                    for font in family.fonts():
                        if font.isOutdated():
                            fonts.append("Array('%s', '%s', '%s', '%s')" % (publisherB64ID, subscriptionB64ID, self.b64encode(font.uniqueID), font.getVersions()[-1].number))

        if fonts:
            call = 'removeFonts(Array(' + ','.join(fonts) + '), true);'
            self.javaScript(call)
            call = 'installFonts(Array(' + ','.join(fonts) + '), true);'
            self.javaScript(call)




    def reloadPublisher(self, evt, b64ID):

        # processThread = threading.Thread(target=self.reloadPublisherShowAnimation, args=(evt, b64ID));
        # processThread.start()


        print(('reloadPublisher', b64ID))


        ID = self.b64decode(b64ID)

        success, message = self.client.publisher(ID).update()

        if success:

            self.setPublisherHTML(b64ID)
            
        else:

            if type(message) in (str, str):
                
                self.errorMessage(message)
            else:
                self.errorMessage('Server: %s' % message.getText(self.locale()))


        self.javaScript('finishReloadPublisher("%s");' % (b64ID))
        self.javaScript('hideCenterMessage();')


        print('Done')

    def reloadSubscriptions(self):

        print('self.reloadSubscriptions()')

        # Preference is set to check automatically
        if int(self.client.preferences.get('reloadSubscriptionsInterval')) != -1:

            # Has never been checked, set to long time ago
            if not self.client.preferences.get('reloadSubscriptionsLastPerformed'):
                self.client.preferences.set('reloadSubscriptionsLastPerformed', int(time.time()) - int(self.client.preferences.get('reloadSubscriptionsInterval')) - 10)

            # See if we should check now
            if int(self.client.preferences.get('reloadSubscriptionsLastPerformed')) < int(time.time()) - int(self.client.preferences.get('reloadSubscriptionsInterval')):
                print('Automatically reloading subscriptions...')

                for publisher in self.client.publishers():
                    for subscription in publisher.subscriptions():
                        self.reloadSubscription(None, self.b64encode(subscription.url))

                self.log('Automatically reloaded subscriptions')

                # Set to now
                self.client.preferences.set('reloadSubscriptionsLastPerformed', int(time.time()))


    def reloadSubscription(self, evt, b64ID):

        print(('reloadSubscription', b64ID))

        success = False
        message = 'Couldnt find subscription.'

        ID = self.b64decode(b64ID)

        for publisher in self.client.publishers():

            if publisher.subscription(ID) and publisher.subscription(ID).exists:
                print((publisher, 'has subscription', publisher.subscription(ID)))
                success, message = publisher.subscription(ID).update()
                break



        if success:

            self.setPublisherHTML(self.b64encode(publisher.canonicalURL))
            
        else:

            if type(message) in (str, str):
                
                self.errorMessage(message)
            else:
                self.errorMessage('Server: %s' % message.getText(self.locale()))


        self.javaScript('finishReloadSubscription("%s");' % (b64ID))
        self.javaScript('hideCenterMessage();')


        print('Done')

    def errorMessage(self, message):
        dlg = wx.MessageDialog(self, message, '', wx.ICON_ERROR)
        result = dlg.ShowModal()
        dlg.Destroy()


    def fontHTML(self, font):

        subscription = font.parent.parent.parent

        html = []

        # Print HTML
        html = ''.join(html)
        html = html.replace('"', '\'')
        html = html.replace('\n', '')
        html = self.localizeString(html)
        html = self.replaceHTML(html)

        return html


    def setActiveSubscription(self, publisherB64ID, subscriptionB64ID):

        publisherID = self.b64decode(publisherB64ID)
        repositoryID = self.b64decode(subscriptionB64ID)

        publisher = self.client.publisher(publisherID)
        publisher.set('currentSubscription', repositoryID)
        self.setPublisherHTML(publisherB64ID)



    def setPublisherHTML(self, b64ID):

#       print b64ID

        ID = self.b64decode(b64ID)

        if self.client.preferences:
            self.client.preferences.set('currentPublisher', ID)

        html = []

        publisher = self.client.publisher(ID)
        subscription = publisher.currentSubscription()
#       api = subscription.latestVersion()
#       print api



        html.append('<div class="publisher" id="%s">' % (b64ID))

        for foundry in subscription.foundries():


            html.append('<div class="foundry">')
            html.append('<div class="head" style="height: %spx; background-color: %s;">' % (110 if foundry.logo else 70, '#' + foundry.backgroundColor if foundry.backgroundColor else 'none'))

            if foundry.logo:
                success, logo, mimeType = subscription.resourceByURL(foundry.logo, binary = True)
                if success:
                    html.append('<div class="logo">')
                    html.append('<img src="data:%s;base64,%s" style="width: 100px; height: 100px;" />' % (mimeType, logo))
                    html.append('</div>') # publisher

            html.append('<div class="names centerOuter"><div class="centerInner">')
            html.append('<div class="name">%s</div>' % (foundry.name.getText(self.locale())))
            if foundry.website:
                html.append('<div class="website"><a href="%s">%s</a></div>' % (foundry.website, foundry.website))

            html.append('</div></div>') # .centerInner .centerOuter



            html.append('</div>') # .head


            html.append('<div class="families">')

            for family in foundry.families():
                html.append('<div class="contextmenu family" id="%s">' % self.b64encode(family.uniqueID))

                html.append('<div class="title">')
                html.append('<div class="clear">')
                html.append('<div class="left name">')
                html.append(family.name.getText(self.locale()))
                html.append('</div>') # .left.name
                html.append('</div>') # .clear
                html.append('</div>') # .title


                for setName in family.setNames(self.locale()):
                    for formatName in family.formatsForSetName(setName, self.locale()):

                        fonts = []
                        amountInstalled = 0
                        for font in family.fonts():
                            if font.setName.getText(self.locale()) == setName and font.format == formatName:
                                fonts.append(font)
                                if font.installedVersion():
                                    amountInstalled += 1

                        completeSetName = ''
                        if setName:
                            completeSetName = setName + ', '
                        completeSetName += typeWorld.api.base.FILEEXTENSIONNAMES[formatName]

                        print(amountInstalled)

                        html.append('<div class="section" id="%s">' % completeSetName)

                        html.append('<div class="title clear">')
                        html.append('<div class="left">%s</div>' % completeSetName)

                        if len(fonts) > 1:

                            html.append('<div class="more right" style="padding-top: 5px;">')
                            html.append('<img src="file://##htmlroot##/more_darker.svg" style="height: 8px; position: relative; top: 0px;">')
                            html.append('</div>')

                            html.append('<div class="installButtons right" style="padding-top: 5px;">')
                            html.append('<div class="clear">')

                            if amountInstalled > 0:
                                html.append('<div class="remove installButton right">')
                                html.append('<a class="removeAllFonts removeButton button " publisherid="%s" subscriptionid="%s" familyid="%s" setname="%s" formatname="%s">' % (self.b64encode(ID), self.b64encode(subscription.url), self.b64encode(family.uniqueID), self.b64encode(setName) if setName else '', formatName))
                                html.append('✕ #(Remove All)')
                                html.append('</a>')
                                html.append('</div>') # .installButton

                            if amountInstalled < len(fonts):
                                html.append('<div class="install installButton right">')
                                html.append('<a class="installAllFonts installButton button" publisherid="%s" subscriptionid="%s" familyid="%s" setname="%s" formatname="%s">' % (self.b64encode(ID), self.b64encode(subscription.url), self.b64encode(family.uniqueID), self.b64encode(setName) if setName else '', formatName))
                                html.append('✓ #(Install All)')
                                html.append('</a>')
                                html.append('</div>') # .installButton
                            html.append('</div>') # .clear
                            html.append('</div>') # .installButtons
                        html.append('</div>') # .title

                        for font in fonts:
                            html.append('<div class="contextmenu font" id="%s">' % self.b64encode(font.uniqueID))
                            html.append('<div class="clear">')

                            html.append('<div class="left" style="width: 50%;">')
                            html.append(font.name.getText(self.locale()))
                            if font.free:
                                html.append('<span class="label free">free</span>')
                            if font.beta:
                                html.append('<span class="label beta">beta</span>')
                            if font.variableFont:
                                html.append('<span class="label var">OTVar</span>')
                            html.append('</div>') # .left
                            html.append('<div class="left">')
                            installedVersion = font.installedVersion()
                            if installedVersion:
                                html.append('#(Installed): <span class="label installedVersion %s">%s</a>' % ('latestVersion' if installedVersion == font.getVersions()[-1].number else 'olderVersion', installedVersion))
                            else:
                                html.append('<span class="notInstalled">#(Not Installed)</span>')
                            html.append('</div>') # .left

                            if font.purpose == 'desktop':
                                html.append('<div class="installButtons right">')
                                html.append('<div class="clear">')
                                html.append('<div class="installButton install right" style="display: %s;">' % ('none' if installedVersion else 'block'))
                                html.append('<a class="installButton button" publisherid="%s" subscriptionid="%s" fontid="%s" version="%s">' % (self.b64encode(subscription.parent.canonicalURL), self.b64encode(subscription.url), self.b64encode(font.uniqueID), font.getVersions()[-1].number if font.getVersions() else ''))
                                html.append('✓ #(Install)')
                                html.append('</a>')
                                html.append('</div>') # .right
                                html.append('<div class="installButton remove right" style="display: %s;">' % ('block' if installedVersion else 'none'))
                                html.append('<a class="removeButton button" publisherid="%s" subscriptionid="%s" fontid="%s">' % (self.b64encode(subscription.parent.canonicalURL), self.b64encode(subscription.url), self.b64encode(font.uniqueID)))
                                html.append('✕ #(Remove)')
                                html.append('</a>')
                                html.append('</div>') # .right
                                html.append('</div>') # .clear
                                html.append('</div>') # .installButtons
                                html.append('<div class="right">')
                                html.append('<a class="status">')
                                html.append('''<img src="file://##htmlroot##/loading.svg" style="height: 13px; position: relative; top: 2px;">''')
                                html.append('</a>')
                                html.append('<div>')
                                html.append('<a class="more">')
                                html.append('''<img src="file://##htmlroot##/more_lighter.svg" style="height: 8px; position: relative; top: 0px;">''')
                                html.append('</a>')
                                html.append('</div>')
                                html.append('</div>') # .right

                            html.append('</div>') # .clear
                            html.append('</div>') # .font

                        html.append('</div>') # .section

                html.append('</div>') # .family


            html.append('</div>') # .families




            html.append('</div>') # .foundry






        html.append('</div>') # .publisher



        html.append('''<script>     


    $(".font a.installButton").click(function() {
        installFonts(Array(Array($(this).attr('publisherid'), $(this).attr('subscriptionid'), $(this).attr('fontid'), $(this).attr('version'))));
    }); 
 
    $(".font a.removeButton").click(function() {
        removeFonts(Array(Array($(this).attr('publisherid'), $(this).attr('subscriptionid'), $(this).attr('fontid'))));
    }); 

    $(".family a.removeAllFonts").click(function() {
        removeAllFonts($(this).attr('publisherid'), $(this).attr('subscriptionid'), $(this).attr('familyid'), $(this).attr('setname'), $(this).attr('formatname')); 
    });

    $(".family a.installAllFonts").click(function() {
        installAllFonts($(this).attr('publisherid'), $(this).attr('subscriptionid'), $(this).attr('familyid'), $(this).attr('setname'), $(this).attr('formatname')); 
    });


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



</script>''' % (b64ID, b64ID, b64ID))


        # Unused:
        '''
    $("#main .font, #main .family .title").click(function() {
        $("#main .font, #main .family .title").removeClass('selected');
        $( this ).addClass( "selected" );
      });
'''



        # Print HTML
        html = ''.join(html)
        html = html.replace('"', '\'')
        html = html.replace('\n', '')
        html = self.localizeString(html)
        html = self.replaceHTML(html)
#       print html
        js = '$("#main").html("' + html + '");'
        self.javaScript(js)

        # Set Sidebar Focus
        self.javaScript("$('#sidebar .publisher').removeClass('selected');")
        self.javaScript("$('#sidebar #%s').addClass('selected');" % b64ID)
        self.javaScript("showMain();")

    def b64encode(self, string):

        b = str(string).encode()
        b64 = base64.b64encode(b)
        s = b64.decode()

        return s.replace('=', '-')

    def b64decode(self, string):

        b = str(string).replace('-', '=').encode()
        b64 = base64.b64decode(b)
        s = b64.decode()

        return s

    def setSideBarHTML(self):
        # Set publishers

        html = []

        # Sort
        # pass

        # Create HTML
        for publisher in self.client.publishers():

            b64ID = self.b64encode(publisher.canonicalURL)

            if publisher.subscriptions():
                name, language = publisher.name(locale = self.locale())


                if language in ('ar', 'he'):
                    direction = 'rtl'
                    if language in ('ar'):
                        name = kashidaSentence(name, 20)
                else:
                    direction = 'ltr'

                installedFonts = publisher.amountInstalledFonts()
                outdatedFonts = publisher.amountOutdatedFonts()

                _type = 'multiple' if len(publisher.subscriptions()) > 1 else 'single'
                print(_type)

                html.append('<div class="publisherWrapper">')
                html.append('<a class="publisher" href="x-python://self.setPublisherHTML(____%s____)">' % (b64ID))
                html.append('<div id="%s" class="contextmenu publisher line clear %s" lang="%s" dir="%s">' % (b64ID, _type, language, direction))
                html.append('<div class="name">')
                html.append('%s %s' % (name, '<img src="file://##htmlroot##/github.svg" style="position:relative; top: 3px; width:16px; height:16px;">' if publisher.get('type') == 'GitHub' else ''))
                html.append('</div>')
                html.append('<div class="reloadAnimation" style="display: none;">')
                html.append('↺')
                html.append('</div>')
                html.append('<div class="badges clear">')
                html.append('<div class="badge outdated" style="display: %s;">' % ('block' if outdatedFonts else 'none'))
                html.append('%s' % (outdatedFonts or ''))
                html.append('</div>')
                html.append('<div class="badge installed" style="display: %s;">' % ('block' if installedFonts else 'none'))
                html.append('%s' % (installedFonts or ''))
                html.append('</div>')
                html.append('</div>')
                html.append('</div>') # publisher
                html.append('</a>')

                html.append('<div class="subscriptions" style="display: %s;">' % ('block' if self.client.preferences.get('currentPublisher') == publisher.canonicalURL else 'none'))
                if len(publisher.subscriptions()) > 1:
                    html.append('<div class="margin top"></div>')
                    for subscription in publisher.subscriptions():

                        amountInstalledFonts = subscription.amountInstalledFonts()
                        amountOutdatedFonts = subscription.amountOutdatedFonts()
                        selected = subscription == publisher.currentSubscription()

                        html.append('<div>')
                        html.append('<a class="subscription" href="x-python://self.setActiveSubscription(____%s____, ____%s____)">' % (b64ID, self.b64encode(subscription.url)))
                        html.append('<div class="contextmenu subscription line clear %s" lang="%s" dir="%s" id="%s">' % ('selected' if selected else '', 'en', 'ltr', self.b64encode(subscription.url)))
                        html.append('<div class="name">')
                        html.append(subscription.name(locale=self.locale()))
                        html.append('</div>')
                        html.append('<div class="reloadAnimation" style="display: none;">')
                        html.append('↺')
                        html.append('</div>')
                        html.append('<div class="badges clear">')
                        html.append('<div class="badge outdated" style="display: %s;">' % ('block' if amountOutdatedFonts else 'none'))
                        html.append('%s' % amountOutdatedFonts)
                        html.append('</div>')
                        html.append('<div class="badge installed" style="display: %s;">' % ('block' if amountInstalledFonts else 'none'))
                        html.append('%s' % amountInstalledFonts)
                        html.append('</div>')
                        html.append('</div>')
                        html.append('</div>') # subscription
                        html.append('</a>')
                        html.append('</div>')
                    html.append('<div class="margin bottom"></div>')
                html.append('</div>')

                html.append('</div>') # .publisherWrapper



        html.append('''<script>


    $("#sidebar a.publisher:not([selected])").click(function() {

        $("#sidebar div.subscriptions").slideUp();
        $(this).parent().children("div.subscriptions").slideDown();

        $("#sidebar div.publisher.line").removeClass('selected');
        $(this).parent().children("div.line").addClass('selected');

    });

    $("#sidebar a.subscription").click(function() {
        $("#sidebar div.subscription.line").removeClass('selected');
        $(this).parent().find("div.line").addClass('selected');
        debug('div.subscription.line');

    });

$( document ).ready(function() {




    $("#sidebar .publisher").hover(function() {
        $( this ).addClass( "hover" );
      }, function() {
        $( this ).removeClass( "hover" );
      }
    );


});



</script>''')


        # Print HTML
        html = ''.join(html)
        html = html.replace('"', '\'')
        html = html.replace('\n', '')
        html = self.replaceHTML(html)
#       print html
        js = '$("#publishers").html("' + html + '");'
        self.javaScript(js)




    def onLoad(self, event):

        self.log('MyApp.frame.onLoad()')
        self.fullyLoaded = True

        self.setSideBarHTML()

        # Open drawer for newly added publisher
        if self.justAddedPublisher:
            self.addPublisherJavaScript(self.justAddedPublisher)
            self.justAddedPublisher = None


        if self.client.preferences.get('currentPublisher'):
            self.javaScript('$("#welcome").hide();')
            self.setPublisherHTML(self.b64encode(self.client.preferences.get('currentPublisher')))
        self.setBadges()


        if WIN:
            self.checkForURLInFile()

    def checkForURLInFile(self):

        openURLFilePath = os.path.join(os.path.dirname(__file__), 'url.txt')

        if os.path.exists(openURLFilePath):
            urlFile = open(openURLFilePath, 'r')
            URL = urlFile.read().strip()
            urlFile.close()


            self.addPublisherJavaScript(URL)

            os.remove(openURLFilePath)



    def log(self, message):
        if MAC:
            from AppKit import NSLog
            NSLog('Type.World App: %s' % message)

    def setBadgeLabel(self, label):
        '''\
        Set dock icon badge
        '''
        label = str(label)
        if MAC and self._dockTile:
            self._dockTile.display()
            self._dockTile.setBadgeLabel_(label)

    def localize(self, key, html = False):
        string = locales.localize(key, self.locale())
        if html:
            string = string.replace('\n', '<br />')
        return string

    def localizeString(self, string, html = False):
        string = locales.localizeString(string, languages = self.locale(), html = html)
        return string

    def replaceHTML(self, html):

        path = os.path.join(os.path.dirname(__file__), 'htmlfiles')
        if WIN:
            path = path.replace('\\', '/')
            if path.startswith('//'):
                path = path[2:]
            # path = path.replace('Mac/', 'mac/')

        print(path)

        html = html.replace('##htmlroot##', path)
        return html

    def systemLocale(self):
        if MAC:
            from AppKit import NSLocale
            return str(NSLocale.autoupdatingCurrentLocale().localeIdentifier().split('_')[0])
        else:
            return 'en'

    def locale(self):
        '''\
        Reads user locale from OS
        '''

        if not hasattr(self, '_locale'):

            if self.client.preferences.get('localizationType') == 'systemLocale':
                self._locale = [self.systemLocale(), 'en']
            elif self.client.preferences.get('localizationType') == 'customLocale':
                self._locale = [self.client.preferences.get('customLocaleChoice'), 'en']
            else:
                self._locale = [self.systemLocale(), 'en']
        return self._locale

    def setBadges(self):
        amount = 0
        for publisher in self.client.publishers():
            amount += publisher.amountOutdatedFonts()
        if amount > 0:
            self.setBadgeLabel(str(amount))
        else:
            self.setBadgeLabel('')

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

    def debug(self, string):
        print(string)



class DebugWindow(wx.Frame):
    def __init__(self, parent, ID, title):
        wx.Frame.__init__(self, parent, ID, title,wx.DefaultPosition,
                            wx.Size(500,300))
        
        # ------ Area for the text output of pressing button
        textarea = wx.TextCtrl(self, -1,
                                size=(500,300))
        self.text = textarea


class Logger(object):
    def __init__(self, window):
        self.terminal = sys.stdout
        self.window = window

    def write(self, message):

        message = message + '\r\n'
        self.terminal.write(message)
        self.window.text.AppendText(message)



class MyApp(wx.App):
    def MacOpenURL(self, url):
        
        self.frame.log('MyApp.MacOpenURL(%s)' % url)

        if self.frame.fullyLoaded:
            self.frame.addPublisherJavaScript(url)
        else:
            self.frame.justAddedPublisher = url

        self.frame.Show()


    def OnInit(self):



        frame = AppFrame(None)
        self.frame = frame

        self.frame.log('MyApp.OnInit()')
        
        if MAC:
            from AppKit import NSApp
            self.frame.nsapp = NSApp()
            self.frame._dockTile = self.frame.nsapp.dockTile()


        html = ReadFromFile(os.path.join(os.path.dirname(__file__), 'htmlfiles', 'main', 'index.html'))

        html = html.replace('##jquery##', ReadFromFile(os.path.join(os.path.dirname(__file__), 'htmlfiles', 'main', 'js', 'jquery-1.12.4.js')))
#        html = html.replace('##jqueryui##', ReadFromFile(os.path.join(os.path.dirname(__file__), 'htmlfiles', 'main', 'js', 'jquery-ui.js')))
        html = html.replace('##jqueryui##', '')

        html = html.replace('##js.js##', ReadFromFile(os.path.join(os.path.dirname(__file__), 'htmlfiles', 'main', 'js', 'js.js')))
        html = html.replace('##cubic.js##', ReadFromFile(os.path.join(os.path.dirname(__file__), 'htmlfiles', 'main', 'js', 'splitcubicatt.js')))
        html = html.replace('##atom.js##', ReadFromFile(os.path.join(os.path.dirname(__file__), 'htmlfiles', 'main', 'js', 'atom.js')))
        html = html.replace('##css##', ReadFromFile(os.path.join(os.path.dirname(__file__), 'htmlfiles', 'main', 'css', 'index.css')))
#        html = html.replace('##jqueryuicss##', ReadFromFile(os.path.join(os.path.dirname(__file__), 'htmlfiles', 'main', 'css', 'jquery-ui.css')))
        html = html.replace('APPVERSION', APPVERSION)

        html = frame.localizeString(html, html = True)
        html = frame.replaceHTML(html)

        if WIN:
            import winreg as wreg
            current_file = __file__
            key = wreg.CreateKey(wreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Internet Explorer\\Main\\FeatureControl\\FEATURE_BROWSER_EMULATION")
            wreg.SetValueEx(key, current_file, 0, wreg.REG_DWORD, 11001)

        # memoryfs = wx.MemoryFSHandler()
        # wx.FileSystem.AddHandler(memoryfs)
        # wx.MemoryFSHandler.AddFileWithMimeType("index.htm", html, 'text/html')
        # frame.html.RegisterHandler(wx.html2.WebViewFSHandler("memory"))

#        frame.html.SetPage(html, os.path.join(os.path.dirname(__file__), 'htmlfiles', 'main'))
        # frame.html.SetPage(html, '')
        # frame.html.Reload()

        filename = os.path.join(os.path.dirname(__file__), 'app.html')
        print('app.html:', filename)
        print('__file__:', __file__)
        WriteToFile(filename, html)
        frame.html.LoadURL("file://%s" % filename)



        frame.Show()
        frame.CentreOnScreen()


        # if WIN and DEBUG:

        #     self.debugWindow = DebugWindow(None, -1, "Debug")
        #     self.debugWindow.Show(True)

        #     sys.stdout = Logger(self.debugWindow)





        return True


app = MyApp(redirect = DEBUG and WIN, filename = None)
app.MainLoop()


