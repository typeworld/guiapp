# -*- coding: utf-8 -*-


import wx, os, webbrowser, urllib, base64, plistlib, json, datetime
from threading import Thread
import threading
import wx.html2
import locales
import sys
import urllib, time
from functools import partial

from ynlib.files import ReadFromFile
from ynlib.strings import kashidas, kashidaSentence

from typeWorldClient import APIClient, AppKitNSUserDefaults
import typeWorld.api.base

from AppKit import NSScreen, NSLocale

APPNAME = 'Type.World'
APPVERSION = '0.1.3'


if not '.app/Contents' in os.path.dirname(__file__):
	DESIGNTIME = True
else:
	DESIGNTIME = False

if not DESIGNTIME:
	plist = plistlib.readPlist(os.path.join(os.path.dirname(__file__), '..', 'Info.plist'))
	APPVERSION = plist['CFBundleShortVersionString']


class AppFrame(wx.Frame):
	def __init__(self, parent):        


		self.client = APIClient(preferences = AppKitNSUserDefaults('world.type.clientapp' if DESIGNTIME else None))


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







		self.justAddedPublisher = None
		self.fullyLoaded = False
		self.panelVisible = False

		# Window Size
		minSize = [1000, 700]
		if self.client.preferences.get('sizeMainWindow'):
			size = list(self.client.preferences.get('sizeMainWindow'))
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

		self.Title = '%s %s' % (APPNAME, APPVERSION)

		self.html = wx.html2.WebView.New(self)
		self.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, self.onNavigate, self.html)
		self.Bind(wx.html2.EVT_WEBVIEW_ERROR, self.onError, self.html)
		self.Bind(wx.html2.EVT_WEBVIEW_LOADED, self.onLoad, self.html)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.html, 1, wx.EXPAND)
		self.SetSizer(sizer)



		### Menus
		menuBar = wx.MenuBar()

		# Exit
		menu = wx.Menu()
		m_exit = menu.Append(wx.ID_EXIT, "%s\tCtrl-X" % (self.localize('Exit')))
		self.Bind(wx.EVT_MENU, self.onQuit, m_exit)
		m_opensubscription = menu.Append(wx.ID_OPEN, "%s\tCtrl-O" % (self.localize('Add Subscription')))
		self.Bind(wx.EVT_MENU, self.showAddPublisher, m_opensubscription)
		m_CheckForUpdates = menu.Append(wx.NewId(), "%s..." % (self.localize('Check for Updates')))
		self.Bind(wx.EVT_MENU, self.onCheckForUpdates, m_CheckForUpdates)
		m_closewindow = menu.Append(wx.ID_CLOSE, "%s\tCtrl-W" % (self.localize('Close Window')))
		self.Bind(wx.EVT_MENU, self.onClose, m_closewindow)


		menuBar.Append(menu, "&%s" % (self.localize('File')))

		# Edit
		# if 'wxMac' in wx.PlatformInfo and wx.VERSION >= (3,0):
		# 	wx.ID_COPY = wx.NewId()
		# 	wx.ID_PASTE = wx.NewId()
		editMenu = wx.Menu()
		editMenu.Append(wx.ID_SELECTALL, "%s\tCTRL+A" % (self.localize('Select All')))
		editMenu.Append(wx.ID_COPY, "%s\tCTRL+C" % (self.localize('Copy')))
		editMenu.Append(wx.ID_CUT, "%s\tCTRL+X" % (self.localize('Cut')))
		editMenu.Append(wx.ID_PASTE, "%s\tCTRL+V" % (self.localize('Paste')))
		menuBar.Append(editMenu, "&%s" % (self.localize('Edit')))

		# About
		menu = wx.Menu()
		m_about = menu.Append(wx.ID_ABOUT, "&%s %s" % (self.localize('About'), APPNAME))
		self.Bind(wx.EVT_MENU, self.onAbout, m_about)
		menuBar.Append(menu, "&%s" % (self.localize('Help')))
		# Preferences
		m_prefs = menu.Append(wx.ID_PREFERENCES, "&%s\tCtrl-," % (self.localize('Preferences')))
		self.Bind(wx.EVT_MENU, self.onPreferences, m_prefs)        

		self.SetMenuBar(menuBar)

		self.CentreOnScreen()
		self.Show()


		self.Bind(wx.EVT_SIZE, self.onResize, self)
		self.Bind(wx.EVT_ACTIVATE, self.onActivate, self)


		# self.Bind(wx.EVT_ACTIVATE, self.onActivate)

		# if wx.Platform == '__WXMAC__':
		# 	w = self.nsapp.mainWindow()

		# 	from AppKit import NSFullSizeContentViewWindowMask, NSWindowTitleHidden, NSBorderlessWindowMask, NSResizableWindowMask, NSTitledWindowMask, NSFullSizeContentViewWindowMask, NSWindowStyleMaskFullSizeContentView

#			w.setStyleMask_(NSFullSizeContentViewWindowMask)

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


#			w.setTitle_(' ')


#			w.setStyleMask_(NSBorderlessWindowMask)
			#w.setTitlebarAppearsTransparent_(1)
#			w.setIsMovable_(True)
			#w.setTitleVisibility_(0)
			#w.setMovableByWindowBackground_(True)
			# js = '$("#sidebar").css("padding-top", "18px");'
			# self.html.RunScript(js)


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

	#		QT_APP.aboutToQuit.connect(about_to_quit)
			self.sparkle = self.objc_namespace['SUUpdater'].sharedUpdater()
			self.sparkle.setAutomaticallyChecksForUpdates_(True)
	#		self.sparkle.setAutomaticallyDownloadsUpdates_(True)
			NSURL = self.objc_namespace['NSURL']
			self.sparkle.setFeedURL_(NSURL.URLWithString_(APPCAST_URL))
			self.sparkle.checkForUpdatesInBackground()


	def changePreferences(self):

		# Has no version information
		if not self.client.preferences.get('appVersion'):

			self.log('Changing preferences from no version to version %s' % APPVERSION)

			# A few general keys
			for key in ['sizeMainWindow', 'anonymousAppID', 'currentPublisher', 'customLocaleChoice', 'localizationType', 'publishers']:
				if self.client.preferences.get(key) and type(self.client.preferences.get(key)) == unicode:
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
					if self.client.preferences.get('publisher(%s)' % publisherURL).has_key('subscriptions'):
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
			for key in self.client.preferences.dictionary().keys():
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
			self.html.RunScript('hidePanel();')
		else:
			self.Destroy()

	def onQuit(self, event):
		self.Destroy()

	def onActivate(self, event):

		size = list(self.GetSize())

		resize = False
		screenSize = NSScreen.mainScreen().frame().size
		if size[0] > screenSize.width:
			size[0] = screenSize.width - 50
			resize = True
		if size[1] > screenSize.height:
			size[1] = screenSize.height - 50
			resize = True

		if resize:
			self.SetSize(size)

		if self.client.preferences.get('currentPublisher'):
			self.setPublisherHTML(self.b64encode(self.client.preferences.get('currentPublisher')))


	def onResize(self, event):
		# Make title bar transparent
		# https://developer.apple.com/documentation/appkit/nswindowstylemask?language=objc
#		if False:
		# if wx.Platform == '__WXMAC__':
		# 	w = self.nsapp.mainWindow()
			# w.setStyleMask_(1 << 0 | 1 << 1 | 1 << 2 | 1 << 3 | 1 << 15)
			# w.setTitlebarAppearsTransparent_(1)
#			w.setTitle_(' ')
#		print w.title(), w.titlebarAppearsTransparent(), w.styleMask()
		self.client.preferences.set('sizeMainWindow', (self.GetSize()[0], self.GetSize()[1]))
		event.Skip()
#		print event.Veto()
#		return


	def onAbout(self, event):
		self.html.RunScript('showAbout();')

	def onPreferences(self, event):


		html = []

		# Update Interval
		html.append(u'<h2>#(Update Interval)</h2>')
		html.append(u'<p>#(UpdateIntervalExplanation)</p>')
		html.append(u'<p>')
		html.append(u'<select id="updateIntervalChoice" style="">')
		for code, name in (
			(-1, '#(Manually)'),
			(1 * 60 * 60, '#(Hourly)'),
			(24 * 60 * 60, '#(Daily)'),
			(7 * 24 * 60 * 60, '#(Weekly)'),
			(30 * 24 * 60 * 60, '#(Monthly)'),
		):
			html.append(u'<option value="%s" %s>%s</option>' % (code, 'selected' if str(code) == str(self.client.preferences.get('reloadSubscriptionsInterval')) else '', name))
		html.append(u'</select>')
		html.append(u'<script>$("#preferences #updateIntervalChoice").click(function() {setPreference("reloadSubscriptionsInterval", $("#preferences #updateIntervalChoice").val());});</script>')
		html.append(u'</p>')

		html.append(u'<p></p>')

		# Localoization
		systemLocale = self.systemLocale()
		for code, name in locales.locales:
			if code == systemLocale:
				systemLocale = name
				break
		html.append(u'<h2>App Localization</h2>')
		html.append(u'<p>')
		html.append(u'<span><input id="systemLocale" value="systemLocale" type="radio" name="localizationType" %s><label for="systemLocale">Use System Locale (%s)</label></span>' % ('checked' if self.client.preferences.get('localizationType') == 'systemLocale' else '', systemLocale))
		html.append(u'<script>$("#preferences #systemLocale").click(function() {setPreference("localizationType", "systemLocale");});</script>')
		html.append(u'<br />')
		html.append(u'<span><input id="customLocale" value="customLocale" type="radio" name="localizationType" %s><label for="customLocale">Use Custom Locale (choose below). Requires restart to take full effect.</label></span>' % ('checked' if self.client.preferences.get('localizationType') == 'customLocale' else ''))
		html.append(u'<script>$("#preferences #customLocale").click(function() {setPreference("localizationType", "customLocale");});</script>')
		html.append(u'<br />')
		html.append(u'<select id="customLocaleChoice" style="">')
		for code, name in locales.locales:
			html.append(u'<option value="%s" %s>%s</option>' % (code, u'selected' if code == self.client.preferences.get('customLocaleChoice') else u'', name.decode('utf-8')))
		html.append(u'</select>')
		html.append(u'<script>$("#preferences #customLocaleChoice").click(function() {setPreference("customLocaleChoice", $("#preferences #customLocaleChoice").val());});</script>')
		html.append(u'</p>')





		# Print HTML
		html = u''.join(html)
		html = html.replace('"', '\'')
		html = html.replace('\n', '')
		html = self.localizeString(html)
#		print html
		js = '$("#preferences .inner").html("' + html + '");'
		self.html.RunScript(js)

		self.html.RunScript('showPreferences();')


	def onNavigate(self, evt):
		uri = evt.GetURL() # you may need to deal with unicode here
		if uri.startswith('x-python://'):
			code = uri.split("x-python://")[1]
			code = urllib.unquote(code).decode('utf8')
			code = code.replace('http//', 'http://')
			code = code.replace('https//', 'https://')
			code = code.replace('____', '\'')
			exec(code)
			evt.Veto()
		elif uri.startswith('http://') or uri.startswith('https://'):
			
			webbrowser.open_new_tab('https://type.world/linkRedirect/?url=' + urllib.quote(uri))
			evt.Veto()
		# else:
		# 	code = uri
		# 	code = urllib.unquote(code).decode('utf8')
		# 	print code
		# 	exec(code)
		# 	evt.Veto()

	def onError(self, evt):
		print evt.GetString()
#		raise Exception(evt.GetString())


	def showAddPublisher(self, evt):
		self.html.RunScript('showAddPublisher();')
		

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
			self.html.RunScript('$("#addSubscriptionFormSubmitButton").show();')
			self.html.RunScript('$("#addSubscriptionFormCancelButton").show();')
			self.html.RunScript('$("#addSubscriptionFormSubmitAnimation").hide();')
			return

		# remove URI
		print 'addPublisher', url

		success, message, publisher = self.client.addSubscription(url, username, password)

		if success:

			b64ID = self.b64encode(publisher.canonicalURL)

			self.setSideBarHTML()
			self.setPublisherHTML(b64ID)
			self.html.RunScript("hidePanel();")

		else:

			self.errorMessage(message)

		self.html.RunScript('$("#addSubscriptionFormSubmitButton").show();')
		self.html.RunScript('$("#addSubscriptionFormCancelButton").show();')
		self.html.RunScript('$("#addSubscriptionFormSubmitAnimation").hide();')


	def removePublisher(self, evt, b64ID):

		publisher = self.client.publisher(self.b64decode(b64ID))

		dlg = wx.MessageDialog(self, 'Are you sure?', 'Remove publisher %s' % (publisher.name(self.locale())[0]), wx.YES_NO | wx.ICON_QUESTION)
		result = dlg.ShowModal() == wx.ID_YES
		dlg.Destroy()
		
		if result:

			publisher.delete()
			self.setSideBarHTML()
			self.html.RunScript("hideMain();")

	def removeSubscription(self, evt, b64ID):

		
			for publisher in self.client.publishers():
				for subscription in publisher.subscriptions():
					if subscription.url == self.b64decode(b64ID):


						dlg = wx.MessageDialog(self, 'Are you sure?', 'Remove subscription %s' % (subscription.name(self.locale())), wx.YES_NO | wx.ICON_QUESTION)
						result = dlg.ShowModal() == wx.ID_YES
						dlg.Destroy()
						
						if result:


							subscription.delete()

							if publisher.get('subscriptions'):
								self.setPublisherHTML(self.b64encode(publisher.canonicalURL))
							else:
								self.html.RunScript("hideMain();")
								self.setSideBarHTML()


	def publisherPreferences(self, i):
		print 'publisherPreferences', i


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
				if not subscription.installedFontVersion(font.uniqueID):
					jsFonts.append("Array('%s', '%s', '%s', '%s')" % (b64publisherID, b64subscriptionID, self.b64encode(font.uniqueID), font.getSortedVersions()[-1].number))

		call = 'installFonts(Array(' + ','.join(jsFonts) + '), true);'
		self.html.RunScript(call)


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
				if subscription.installedFontVersion(font.uniqueID):
					jsFonts.append("Array('%s', '%s', '%s', '%s')" % (b64publisherID, b64subscriptionID, self.b64encode(font.uniqueID), font.getSortedVersions()[-1].number))

		call = 'removeFonts(Array(' + ','.join(jsFonts) + '), true);'
		self.html.RunScript(call)


	def installFonts(self, fonts):

		for b64publisherURL, b64subscriptionURL, b64fontID, version in fonts:

			publisherURL = self.b64decode(b64publisherURL)
			subscriptionURL = self.b64decode(b64subscriptionURL)
			fontID = self.b64decode(b64fontID)

			publisher = self.client.publisher(publisherURL)
			subscription = publisher.subscription(subscriptionURL)

			self.installFont(b64publisherURL, b64subscriptionURL, b64fontID, version)
			self.setPublisherBadge(b64publisherURL, subscription.parent.amountInstalledFonts())

		self.setPublisherHTML(b64publisherURL)

	def removeFonts(self, fonts):

		for b64publisherURL, b64subscriptionURL, b64fontID in fonts:

			publisherURL = self.b64decode(b64publisherURL)
			subscriptionURL = self.b64decode(b64subscriptionURL)
			fontID = self.b64decode(b64fontID)

			publisher = self.client.publisher(publisherURL)
			subscription = publisher.subscription(subscriptionURL)

			self.removeFont(b64publisherURL, b64subscriptionURL, b64fontID)
			self.setPublisherBadge(b64publisherURL, subscription.parent.amountInstalledFonts())

		self.setPublisherHTML(b64publisherURL)


	def installFont(self, b64publisherURL, b64subscriptionURL, b64fontID, version):


		publisherURL = self.b64decode(b64publisherURL)
		subscriptionURL = self.b64decode(b64subscriptionURL)
		fontID = self.b64decode(b64fontID)

		# self.html.RunScript("$('#%s .installButton').hide();" % b64fontID)
		# self.html.RunScript("$('#%s .status').show();" % b64fontID)

		print 'installFont', publisherURL, subscriptionURL, fontID

		publisher = self.client.publisher(publisherURL)
		subscription = publisher.subscription(subscriptionURL)
		api = subscription.latestVersion()
		b64ID = self.b64encode(publisherURL)

		# Check if font is already installed
		if subscription.installedFontVersion(fontID):
			print 'Removing old version %s' % version
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

			if type(message) in (str, unicode):
				
				if message == 'seatAllowanceReached':
					self.errorMessage('seatAllowanceReached')

				else:
					self.errorMessage(message)
			else:
				self.errorMessage('Server: %s' % message.getText(self.locale()))

			# self.html.RunScript("$('#%s .statusButton').hide();" % b64fontID)
			# self.html.RunScript("$('#%s .installButton').show();" % b64fontID)


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
			# self.setPublisherBadge(self.b64encode(subscription.parent.canonicalURL), subscription.parent.amountInstalledFonts())
			# self.setPublisherHTML(self.b64encode(subscription.parent.canonicalURL))

		else:

			if type(message) in (str, unicode):
				self.errorMessage(message)
			else:
				self.errorMessage('Server: %s' % message.getText(self.locale()))

			# self.html.RunScript("$('#%s .statusButton').hide();" % b64fontID)
			# self.html.RunScript("$('#%s .removeButton').show();" % b64fontID)


	def onContextMenu(self, x, y, target, b64ID):
#		print x, y, target, b64ID, self.b64decode(b64ID)

		x = max(0, int(x) - 70)

		if 'contextmenu publisher' in target:

			menu = wx.Menu()

			item = wx.MenuItem(menu, wx.NewId(), self.localizeString('#(Reload)'))
			menu.Append(item)
			menu.Bind(wx.EVT_MENU, partial(self.reloadPublisherJavaScript, b64ID = b64ID), item)

			item = wx.MenuItem(menu, wx.NewId(), self.localizeString('#(Show in Finder)'))
			menu.Append(item)
			menu.Bind(wx.EVT_MENU, partial(self.showPublisherInFinder, b64ID = b64ID), item)

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

			item = wx.MenuItem(menu, wx.NewId(), self.localizeString('#(Reload)'))
			menu.Append(item)
			menu.Bind(wx.EVT_MENU, partial(self.reloadSubscriptionJavaScript, b64ID = b64ID), item)

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


									if subscription.installedFontVersion(fontID):
										item = wx.MenuItem(menu, wx.NewId(), self.localizeString('#(Show in Finder)'))
										menu.Append(item)
										menu.Bind(wx.EVT_MENU, partial(self.showFontInFinder, subscription = subscription, fontID = fontID), item)

									# create a submenu
									subMenu = wx.Menu()
									menu.AppendMenu(wx.NewId(), self.localizeString('#(Install Version)'), subMenu)

									for version in font.getSortedVersions():

										if subscription.installedFontVersion(fontID) == version.number:
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
		self.html.RunScript("installFonts(Array(Array('%s', '%s', '%s', '%s')), true);" % (self.b64encode(subscription.parent.canonicalURL), self.b64encode(subscription.url), self.b64encode(fontID), version))

	def showPublisherPreferences(self, event, b64ID):

		for publisher in self.client.publishers():
			if publisher.exists and publisher.canonicalURL == self.b64decode(b64ID):


				html = []

				# Rate limits
				limits, responses = publisher.readGitHubResponse('https://api.github.com/rate_limit')
				limits = json.loads(limits)

				html.append('<h2>%s (%s)</h2>' % (publisher.name(self.locale())[0], publisher.get('type')))
				if publisher.get('type') == 'GitHub':
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
		#		print html
				js = '$("#publisherPreferences .inner").html("' + html + '");'
				self.html.RunScript(js)

				self.html.RunScript('showPublisherPreferences();')

	def reloadSubscriptionJavaScript(self, evt, b64ID):
		print 'reloadSubscriptionJavaScript', b64ID
		self.html.RunScript('reloadSubscription("%s");' % (b64ID))

	def reloadPublisherJavaScript(self, evt, b64ID):
		print 'reloadPublisherJavaScript', b64ID
		self.html.RunScript('reloadPublisher("%s");' % (b64ID))

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


	def reloadPublisher(self, evt, b64ID):

		# processThread = threading.Thread(target=self.reloadPublisherShowAnimation, args=(evt, b64ID));
		# processThread.start()


		print 'reloadPublisher', b64ID


		ID = base64.b64decode(b64ID.replace('-', '='))

		success, message = self.client.publisher(ID).update()

		if success:

			self.setSubscriptionsHTML(b64ID)
			self.setPublisherHTML(b64ID)
			
		else:

			if type(message) in (str, unicode):
				
				self.errorMessage(message)
			else:
				self.errorMessage('Server: %s' % message.getText(self.locale()))


		self.html.RunScript('finishReloadPublisher("%s");' % (b64ID))


		print 'Done'

	def reloadSubscriptions(self):

		print 'self.reloadSubscriptions()'

		# Preference is set to check automatically
		if int(self.client.preferences.get('reloadSubscriptionsInterval')) != -1:

			# Has never been checked, set to long time ago
			if not self.client.preferences.get('reloadSubscriptionsLastPerformed'):
				self.client.preferences.set('reloadSubscriptionsLastPerformed', int(time.time()) - int(self.client.preferences.get('reloadSubscriptionsInterval')) - 10)

			# See if we should check now
			if int(self.client.preferences.get('reloadSubscriptionsLastPerformed')) < int(time.time()) - int(self.client.preferences.get('reloadSubscriptionsInterval')):
				print 'Automatically reloading subscriptions...'

				for publisher in self.client.publishers():
					for subscription in publisher.subscriptions():
						self.reloadSubscription(None, self.b64encode(subscription.url))

				self.log('Automatically reloaded subscriptions')

				# Set to now
				self.client.preferences.set('reloadSubscriptionsLastPerformed', int(time.time()))


	def reloadSubscription(self, evt, b64ID):

		print 'reloadSubscription', b64ID

		success = False
		message = 'Couldnt find subscription.'

		ID = self.b64decode(b64ID)

		for publisher in self.client.publishers():

			if publisher.subscription(ID) and publisher.subscription(ID).exists:
				print publisher, 'has subscription', publisher.subscription(ID)
				success, message = publisher.subscription(ID).update()
				break



		if success:

			self.setSubscriptionsHTML(self.b64encode(publisher.canonicalURL))
			self.setPublisherHTML(self.b64encode(publisher.canonicalURL))
			
		else:

			if type(message) in (str, unicode):
				
				self.errorMessage(message)
			else:
				self.errorMessage('Server: %s' % message.getText(self.locale()))


		self.html.RunScript('finishReloadSubscription("%s");' % (b64ID))


		print 'Done'

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


	def getSubscriptionsHTML(self, b64ID):
		ID = self.b64decode(b64ID)

#		print 'setSubscriptionsHTML', ID

		html = []
		repos = []
		publisher = self.client.publisher(ID)
		for subscription in publisher.subscriptions():

			amountInstalledFonts = subscription.amountInstalledFonts()
			selected = subscription == publisher.currentSubscription()

			string = []
			string.append('<a href="x-python://self.setActiveSubscription(____%s____, ____%s____)">' % (b64ID, self.b64encode(subscription.url)))
			string.append('<div class="contextmenu subscription publisher clear %s" lang="%s" dir="%s" id="%s">' % ('selected' if selected else '', 'en', 'ltr', self.b64encode(subscription.url)))
			string.append('<div class="name">')
			string.append(subscription.name(locale=self.locale()))
			string.append('</div>')

			string.append('<div class="badges">')
			string.append('<div class="badge installed" style="display: %s;">' % ('block' if amountInstalledFonts else 'none'))
			string.append('%s' % amountInstalledFonts)
			string.append('</div>')
			string.append('</div>')
			string.append('</div>')
			string.append('</a>')

			html.append(''.join(string))


			html.append('''<script>

$( document ).ready(function() {

	$("#subscriptions .publisher").hover(function() {
		$( this ).addClass( "hover" );
	  }, function() {
		$( this ).removeClass( "hover" );
	  }
	);


});


</script>''')


		html.append(', '.join(repos))


		# Print HTML
		html = ''.join(html)
		html = html.replace('"', '\'')
		html = html.replace('\n', '')
		html = self.localizeString(html)

		return html

	def setSubscriptionsHTML(self, b64ID):

		html = self.getSubscriptionsHTML(b64ID)

		js = '$("#subscriptions #content").html("' + html + '");'
		self.html.RunScript(js)


	def setPublisherHTML(self, b64ID):

#		print b64ID

		ID = self.b64decode(b64ID)

		if self.client.preferences:
			self.client.preferences.set('currentPublisher', ID)

		html = []

		publisher = self.client.publisher(ID)
		subscription = publisher.currentSubscription()
		api = subscription.latestVersion()
#		print api



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
								if subscription.installedFontVersion(font.uniqueID):
									amountInstalled += 1

						completeSetName = ''
						if setName:
							completeSetName = setName + ', '
						completeSetName += typeWorld.api.base.FILEEXTENSIONNAMES[formatName]

						print amountInstalled

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
								html.append(u'✕ #(Remove All)')
								html.append('</a>')
								html.append('</div>') # .installButton

							if amountInstalled < len(fonts):
								html.append('<div class="install installButton right">')
								html.append('<a class="installAllFonts installButton button" publisherid="%s" subscriptionid="%s" familyid="%s" setname="%s" formatname="%s">' % (self.b64encode(ID), self.b64encode(subscription.url), self.b64encode(family.uniqueID), self.b64encode(setName) if setName else '', formatName))
								html.append(u'✓ #(Install All)')
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
							installedVersion = subscription.installedFontVersion(font.uniqueID)
							if installedVersion:
								html.append('#(Installed): <span class="label installedVersion %s">%s</a>' % ('latestVersion' if installedVersion == font.getSortedVersions()[-1].number else 'olderVersion', installedVersion))
							else:
								html.append('<span class="notInstalled">#(Not Installed)</span>')
							html.append('</div>') # .left

							if font.purpose == 'desktop':
								html.append('<div class="installButtons right">')
								html.append('<div class="clear">')
								html.append('<div class="installButton install right" style="display: %s;">' % ('none' if installedVersion else 'block'))
								html.append('<a class="installButton button" publisherid="%s" subscriptionid="%s" fontid="%s" version="%s">' % (self.b64encode(subscription.parent.canonicalURL), self.b64encode(subscription.url), self.b64encode(font.uniqueID), font.getSortedVersions()[-1].number if font.getSortedVersions() else ''))
								html.append(u'✓ #(Install)')
								html.append('</a>')
								html.append('</div>') # .right
								html.append('<div class="installButton remove right" style="display: %s;">' % ('block' if installedVersion else 'none'))
								html.append('<a class="removeButton button" publisherid="%s" subscriptionid="%s" fontid="%s">' % (self.b64encode(subscription.parent.canonicalURL), self.b64encode(subscription.url), self.b64encode(font.uniqueID)))
								html.append(u'✕ #(Remove)')
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
#		print html
		js = '$("#main").html("' + html + '");'
		self.html.RunScript(js)

		# Set Sidebar Focus
		self.html.RunScript("$('#sidebar .publisher').removeClass('selected');")
		self.html.RunScript("$('#sidebar #%s').addClass('selected');" % b64ID)
		self.setSubscriptionsHTML(b64ID)
		self.html.RunScript("showMain();")


	def b64encode(self, string):
		return base64.b64encode(string.encode('utf-8')).replace('=', '-')

	def b64decode(self, string):
		return base64.b64decode(string.replace('-', '=')) # .decode('utf-8')

	def setSideBarHTML(self):
		# Set publishers

		html = []


		# Sort
		# pass

		# Create HTML
		for publisher in self.client.publishers():

			b64ID = base64.b64encode(publisher.canonicalURL).replace('=', '-')

			if publisher.subscriptions():
				name, language = publisher.name(locale = self.locale())


				if language in (u'ar', u'he'):
					direction = 'rtl'
					if language in (u'ar'):
						name = kashidaSentence(name, 20)
				else:
					direction = 'ltr'

				installedFonts = publisher.amountInstalledFonts()
				html.append(u'''
<a href="x-python://self.setPublisherHTML(____%s____)">
	<div id="%s" class="contextmenu publisher clear" lang="%s" dir="%s">
		<div class="name">
		%s %s
		</div>
		<div class="reloadAnimation" style="display: none;">
		↺
		</div>
		<div class="badges">
			<div class="badge installed" style="display: %s;">
			%s
			</div>
		</div>
	</div>
</a>''' % (b64ID, b64ID, language, direction, name, '<img src="file://##htmlroot##/github.svg" style="position:relative; top: 3px; width:16px; height:16px;">' if publisher.get('type') == 'GitHub' else '', 'block' if installedFonts else 'none', installedFonts or ''))


		html.append('''<script>

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
#		print html
		js = '$("#publishers").html("' + html + '");'
		self.html.RunScript(js)




	def onLoad(self, event):

		self.setSideBarHTML()

		# Open drawer for newly added publisher
		if self.justAddedPublisher:
			self.addPublisher(self.justAddedPublisher)
			self.justAddedPublisher = None

		self.fullyLoaded = True

		if self.client.preferences.get('currentPublisher'):
			self.html.RunScript('$("#welcome").hide();')
			self.setPublisherHTML(self.b64encode(self.client.preferences.get('currentPublisher')))

#		self.reloadSubscriptions()


	def log(self, message):

		from AppKit import NSLog
		NSLog('Type.World App: %s' % message)

	def setBadgeLabel(self, label):
		u'''\
		Set dock icon badge
		'''
		label = str(label)
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
		html = html.replace('##htmlroot##', os.path.join(os.path.dirname(__file__), 'html'))
		return html

	def systemLocale(self):
		return str(NSLocale.autoupdatingCurrentLocale().localeIdentifier().split('_')[0])

	def locale(self):
		u'''\
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

	def setPublisherBadge(self, b64ID, string):
		if string:
			self.html.RunScript('$("#sidebar #%s .badge.installed").show(); $("#sidebar #%s .badge.installed").html("%s");' % (b64ID, b64ID, string))
		else:
			self.html.RunScript('$("#sidebar #%s .badge.installed").hide();' % b64ID)
		# if string:
		# 	self.html.RunScript('$("#sidebar #%s .badge.installed").fadeOut(200, function() { $("#sidebar #%s .badge.installed").html("%s"); $("#sidebar #%s .badge.installed").fadeIn(200); });' % (b64ID, b64ID, string, b64ID))
		# else:
		# 	self.html.RunScript('$("#sidebar #%s .badge.installed").fadeOut(200);' % b64ID)

	def debug(self, string):
		print string



class MyApp(wx.App):
	def MacOpenURL(self, url):
		
		if self.frame.fullyLoaded:
			self.frame.addPublisher(url)
		else:
			self.frame.justAddedPublisher = url

		self.frame.Show()


	def OnInit(self):
		frame = AppFrame(None)
		self.frame = frame
		
		from AppKit import NSApp
		self.frame.nsapp = NSApp()
		self.frame._dockTile = self.frame.nsapp.dockTile()


		html = ReadFromFile(os.path.join(os.path.dirname(__file__), 'html', 'main', 'index.html'))

		html = html.replace('##jquery##', str(ReadFromFile(os.path.join(os.path.dirname(__file__), 'html', 'main', 'js', 'jquery-1.12.4.js'))))
		html = html.replace('##jqueryui##', str(ReadFromFile(os.path.join(os.path.dirname(__file__), 'html', 'main', 'js', 'jquery-ui.js'))))
		html = html.replace('##js.js##', str(ReadFromFile(os.path.join(os.path.dirname(__file__), 'html', 'main', 'js', 'js.js'))))
		html = html.replace('##cubic.js##', str(ReadFromFile(os.path.join(os.path.dirname(__file__), 'html', 'main', 'js', 'splitcubicatt.js'))))
		html = html.replace('##atom.js##', str(ReadFromFile(os.path.join(os.path.dirname(__file__), 'html', 'main', 'js', 'atom.js'))))
		html = html.replace('##css##', str(ReadFromFile(os.path.join(os.path.dirname(__file__), 'html', 'main', 'css', 'index.css'))))
		html = html.replace('##jqueryuicss##', str(ReadFromFile(os.path.join(os.path.dirname(__file__), 'html', 'main', 'css', 'jquery-ui.css'))))
		html = html.replace('APPVERSION', APPVERSION)

		html = frame.localizeString(html, html = True)
		html = frame.replaceHTML(html)

		# import cgi
		# html = cgi.escape(html)
	#	html = html.decode('windows-1252')

		frame.html.SetPage(html, os.path.join(os.path.dirname(__file__), 'html', 'main'))
		frame.Show()

		return True


if __name__ == '__main__':
	app = MyApp()


	app.MainLoop()


