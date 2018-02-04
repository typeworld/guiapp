# -*- coding: utf-8 -*-

import wx, os, webbrowser, urllib, base64
from threading import Thread
import wx.html2
from locales import *
import sys
import urllib

from ynlib.files import ReadFromFile
from ynlib.strings import kashidas, kashidaSentence

from typeWorld.client import APIClient, AppKitNSUserDefaults

APPNAME = 'Type.World'
APPVERSION = 0.1

import AppKit
#from AppKit import NSDockTilePlugIn

class NSDockTilePlugIn(AppKit.NSObject):

	def setDockTile_(self, dockTile):
		dockTile.setBadgeLabel_(str(3))


class AboutWindow(wx.Dialog):
	def __init__(self, parent):

		self.parent = parent

		super(AboutWindow, self).__init__(self.parent, size=(500,200))


		self.Title = '%s %s' % (self.parent.localize('About'), APPNAME)

		self.html = wx.html2.WebView.New(self)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.html, 1, wx.EXPAND)
		self.SetSizer(sizer)

		self.CentreOnScreen()
		self.SetFocus()

class PreferencesWindow(wx.Dialog):
	def __init__(self, parent):

		self.parent = parent

		super(PreferencesWindow, self).__init__(self.parent, size=(500,200))

		self.Title = self.parent.localize('Preferences')

		self.html = wx.html2.WebView.New(self)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.html, 1, wx.EXPAND)
		self.SetSizer(sizer)

		self.CentreOnScreen()
		self.SetFocus()


class AppFrame(wx.Frame):
	def __init__(self, parent):        

		self.client = APIClient(preferences = AppKitNSUserDefaults('world.type.clientapp'))
		self.justAddedPublisher = None
		self.fullyLoaded = False

		if self.client.preferences.get('sizeMainWindow'):
			size = tuple(self.client.preferences.get('sizeMainWindow'))
		else:
			size=(1000,700)
		super(AppFrame, self).__init__(parent, size = size)

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
		m_exit = menu.Append(wx.ID_EXIT, "E&xit\tCtrl-X")
		self.Bind(wx.EVT_MENU, self.onClose, m_exit)
		menuBar.Append(menu, "&File")

		# Edit
		# if 'wxMac' in wx.PlatformInfo and wx.VERSION >= (3,0):
		# 	wx.ID_COPY = wx.NewId()
		# 	wx.ID_PASTE = wx.NewId()
		editMenu = wx.Menu()
		editMenu.Append(wx.ID_SELECTALL, "Select All\tCTRL+A")
		editMenu.Append(wx.ID_COPY, "Copy\tCTRL+C")
		editMenu.Append(wx.ID_CUT, "Cut\tCTRL+X")
		editMenu.Append(wx.ID_PASTE, "Paste\tCTRL+V")
		menuBar.Append(editMenu, "&Edit")

		# About
		menu = wx.Menu()
		m_about = menu.Append(wx.ID_ABOUT, "&About %s" % APPNAME)
		self.Bind(wx.EVT_MENU, self.onAbout, m_about)
		m_CheckForUpdates = menu.Append(1, "Check for updates...")
		self.Bind(wx.EVT_MENU, self.onCheckForUpdates, m_CheckForUpdates)
		menuBar.Append(menu, "&Help")
		# Preferences
		m_prefs = menu.Append(wx.ID_PREFERENCES, "&Preferences\tCtrl-,")
		self.Bind(wx.EVT_MENU, self.onPreferences, m_prefs)        

		self.SetMenuBar(menuBar)

		self.CentreOnScreen()
#		self.ShowWithEffect()
		self.Show()


		self.Bind(wx.EVT_SIZE, self.onResize, self)

		from AppKit import NSApp
		self.nsapp = NSApp()
		self._dockTile = self.nsapp.dockTile()


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



	def orderedPublishers(self):
		return [self.client.endpoints[x] for x in self.client.endpoints.keys()]


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

	def onActivate(self, event):
		self.errorMessage('Activated: %s' % sys.argv)

	def onClose(self, event):
		# dlg = wx.MessageDialog(self, 
		# 	"Do you really want to close this application?",
		# 	"Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
		# result = dlg.ShowModal()
		# dlg.Destroy()
		# if result == wx.ID_OK:
		# 	self.Destroy()

		# See https://github.com/sparkle-project/Sparkle/issues/839
#		self.objc_namespace['NSApplication'].sharedApplication().terminate_(None)

		self.Destroy()

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
		dlg = AboutWindow(self)
		html = ReadFromFile(os.path.join(os.path.dirname(__file__), 'html', 'about', 'index.html'))
		dlg.html.SetPage(localizeString(html, frame.locale()), os.path.join(os.path.dirname(__file__), 'html', 'about', 'index.html'))
		dlg.ShowModal()
		dlg.Destroy()  

	def onPreferences(self, event):
		dlg = PreferencesWindow(self)
		html = ReadFromFile(os.path.join(os.path.dirname(__file__), 'html', 'preferences', 'index.html'))
		dlg.html.SetPage(localizeString(html, frame.locale()), os.path.join(os.path.dirname(__file__), 'html', 'preferences', 'index.html'))
		dlg.ShowModal()
		dlg.Destroy()  

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
			webbrowser.open_new_tab(uri)
			evt.Veto()
		# else:
		# 	code = uri
		# 	code = urllib.unquote(code).decode('utf8')
		# 	print code
		# 	exec(code)
		# 	evt.Veto()

	def onError(self, evt):
		print evt.GetString()
		raise Exception(evt.GetString())


	def addPublisher(self, url):

		url = url.replace('http//', 'http://')
		url = url.replace('https//', 'https://')

		print 'addPublisher', url

		success, message, publisher = self.client.addRepository(url)

		if success:

			b64ID = base64.b64encode(publisher.latestVersion().canonicalURL).replace('=', '-')

			self.setSideBarHTML()
			self.setPublisherHTML(b64ID)

		else:
			self.errorMessage(message)

	def removePublisher(self, b64ID):

		ID = base64.b64decode(b64ID.replace('-', '='))
		publisher = self.client.endpoints[ID]
		publisher.remove()
		self.client.preferences.set('currentPublisher', None)
		self.setSideBarHTML()
		self.html.RunScript("hideMain();")

	def publisherPreferences(self, i):
		print 'publisherPreferences', i

	def removeFont(self, canonicalURL, fontID):

		api = self.client.endpoints[canonicalURL].latestVersion()

		if self.client.endpoints.has_key(canonicalURL):
			endpoint = self.client.endpoints[canonicalURL]
			success, message = endpoint.removeFont(fontID)
			b64ID = base64.b64encode(canonicalURL).replace("=", "-")

			if success:

				# Get font
				for foundry in api.response.getCommand().foundries:
					for family in foundry.families:
						for font in family.fonts:
							if font.uniqueID == fontID:
								self.html.RunScript('$("#%s").html("%s");' % (fontID, self.fontHTML(api, font)))
								break

				self.setPublisherBadge(b64ID, endpoint.amountInstalledFonts())

			else:

				if type(message) in (str, unicode):
					self.errorMessage(message)
				else:
					self.errorMessage('Server: %s' % message.getText(self.locale()))

		else:
			success = False
			self.errorMessage('The URL %s is unknown.' % (canonicalURL))

	def reloadPublisher(self, b64ID):

		print 'reloadPublisher', b64ID


		ID = base64.b64decode(b64ID.replace('-', '='))


		success, message = self.client.endpoints[ID].update()

		if success:

			self.setPublisherHTML(b64ID)
			
		else:

			if type(message) in (str, unicode):
				
				self.errorMessage(message)
			else:
				self.errorMessage('Server: %s' % message.getText(self.locale()))


		self.html.RunScript('$("#sidebar #%s .badges").show();' % b64ID)
		self.html.RunScript('$("#sidebar #%s .reloadAnimation").hide();' % b64ID)



	def installFont(self, canonicalURL, fontID, version):
		self.html.RunScript("$('#%s .installButton').hide();" % fontID)
		self.html.RunScript("$('#%s .status').show();" % fontID)


		publisher = self.client.endpoints[canonicalURL]
		api = publisher.latestVersion()
		b64ID = base64.b64encode(canonicalURL).replace("=", "-")

		if self.client.endpoints.has_key(canonicalURL):
			endpoint = self.client.endpoints[canonicalURL]
			success, message = endpoint.installFont(fontID, version)

			if success:

				# self.html.RunScript("$('#%s .status').hide();" % fontID)
				# self.html.RunScript("$('#%s .removeButton').show();" % fontID)
				


				# Get font
				for foundry in api.response.getCommand().foundries:
					for family in foundry.families:
						for font in family.fonts:
							if font.uniqueID == fontID:
								self.html.RunScript('$("#%s").html("%s");' % (fontID, self.fontHTML(api, font)))
								break

				self.setPublisherBadge(b64ID, publisher.amountInstalledFonts())
				

			else:

				if type(message) in (str, unicode):
					
					if message == 'seatAllowanceReached':
						self.errorMessage('seatAllowanceReached')

					else:
						self.errorMessage(message)
				else:
					self.errorMessage('Server: %s' % message.getText(self.locale()))

		else:
			success = False
			self.errorMessage('The URL %s is unknown.' % (canonicalURL))

		if not success:
			self.html.RunScript("$('#%s .installButton').show();" % fontID)
			self.html.RunScript("$('#%s .status').hide();" % fontID)


	def errorMessage(self, message):
		dlg = wx.MessageDialog(self, message, '', wx.ICON_ERROR)
		result = dlg.ShowModal()
		dlg.Destroy()


	def fontHTML(self, api, font):
		html = []
		html.append('<div class="clear">')
		html.append('<div class="left" style="width: 50%;">')
		html.append(font.name.getText(self.locale()))
		if font.free:
			html.append('<span class="fontLabel free">free</span>')
		if font.beta:
			html.append('<span class="fontLabel beta">beta</span>')
		if font.variableFont:
			html.append('<span class="fontLabel var">OTVar</span>')
		html.append('</div>') # .left
		html.append('<div class="left">')
		installedVersion = api.parent.parent.installedFontVersion(font.uniqueID)
		if installedVersion:
			html.append('#(Installed): %s' % installedVersion)
		else:
			html.append('#(Not Installed)')
		html.append('</div>') # .left
		html.append('<div class="right installButton" style="display: %s;">' % ('none' if installedVersion else 'block'))
		html.append('<a href="x-python://self.installFont(____%s____, ____%s____, ____%s____)">' % (api.canonicalURL, font.uniqueID, font.getSortedVersions()[-1].number))
		html.append('#(Install)')
		html.append('</a>')
		html.append('</div>') # .right
		html.append('<div class="right removeButton" style="display: %s;">' % ('block' if installedVersion else 'none'))
		html.append('<a href="x-python://self.removeFont(____%s____, ____%s____)">' % (api.canonicalURL, font.uniqueID))
		html.append('#(Remove)')
		html.append('</a>')
		html.append('</div>') # .right
		html.append('<div class="right status">')
		html.append('#(Installing)...')
		html.append('</div>') # .right
		html.append('</div>') # .clear

		# Print HTML
		html = ''.join(html)
		html = html.replace('"', '\'')
		html = html.replace('\n', '')
		html = self.localizeString(html)

		return html

	def setPublisherHTML(self, b64ID):

#		print b64ID

		ID = base64.b64decode(b64ID.replace('-', '='))

		if self.client.preferences:
			self.client.preferences.set('currentPublisher', b64ID)

		html = []

		api = self.client.endpoints[ID].latestVersion()

		name, locale = api.name.getTextAndLocale(locale = self.locale())
		logo = False

		html.append('<div class="publisher">')
		html.append('<div class="head" style="height: 15px; background-color: white;">')
		# Preferences
		html.append('<div class="buttons clear">')
		html.append('<div class="left">#(Publisher): %s</div>' % (name))
		html.append('<div class="right"><a class="warningButton" href="x-python://self.removePublisher(____%s____)">#(Remove)</a></div>' % (b64ID))
		html.append('<div class="right"><a href="x-python://self.publisherPreferences(____%s____)">#(Preferences)</a></div>' % b64ID)
		html.append('<div class="right"><a class="reloadPublisherButton">#(Reload)</a></div>')
		html.append('</div>') # .buttons
		html.append('</div>') # .head
		html.append('</div>') # .publisher

		html.append('<div class="publisher" id="%s">' % (b64ID))

		for foundry in api.response.getCommand().foundries:

			html.append('<div class="foundry">')
			html.append('<div class="head" style="height: %spx;">' % (110 if foundry.logo else 70))

			if logo:
				html.append('<div class="logo">')
				html.append('</div>') # publisher

			html.append('<div class="names centerOuter"><div class="centerInner">')
			html.append('<div class="name">%s</div>' % (foundry.name.getText(self.locale())))
			if foundry.website:
				html.append('<div class="website"><a href="%s">%s</a></div>' % (foundry.website, foundry.website))

			html.append('</div></div>') # .centerInner .centerOuter



			html.append('</div>') # .head


			html.append('<div class="families">')

			for family in foundry.families:
				html.append('<div class="family" id="%s">' % family.uniqueID)

				html.append('<div class="title">')
				html.append('<div class="clear">')
				html.append('<div class="left name">')
				html.append(family.name.getText(self.locale()))
				html.append('</div>') # .left.name
				html.append('<div class="right">')
				html.append('<a href="x-python://self.installAllFonts(____%s____)">' % family.uniqueID)
				html.append('#(Install All)')
				html.append('</a>')
				html.append('</div>') # .right
				html.append('</div>') # .clear
				html.append('</div>') # .head

				for font in family.fonts:
					html.append('<div class="font" id="%s">' % font.uniqueID)

					html.append(self.fontHTML(api, font))

					html.append('</div>') # .font

				html.append('</div>') # .family


			html.append('</div>') # .families







			html.append('</div>') # .foundry






		html.append('</div>') # .publisher





		html.append('''<script>

$( document ).ready(function() {

	$("#main .font, #main .family .title").hover(function() {
		$( this ).addClass( "hover" );
	  }, function() {
		$( this ).removeClass( "hover" );
	  }
	);

	$("#main .publisher a.reloadPublisherButton").click(function() {
		$("#sidebar #%s .badges").hide();
		$("#sidebar #%s .reloadAnimation").show();
		python("self.reloadPublisher(____%s____)");
	});


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
#		print html
		js = '$("#main").html("' + html + '");'
		self.html.RunScript(js)

		# Set Sidebar Focus
		self.html.RunScript("$('#sidebar .publisher').removeClass('selected');")
		self.html.RunScript("$('#sidebar #%s').addClass('selected');" % b64ID)
		self.html.RunScript("showMain();")



	def setSideBarHTML(self):
		# Set publishers

		html = []


		# Sort
		# pass

		# Create HTML
		for publisher in self.orderedPublishers():

			b64ID = base64.b64encode(publisher.canonicalURL).replace('=', '-')

			name, language = publisher.latestVersion().name.getTextAndLocale(locale = self.locale())

			if language in (u'ar', u'he'):
				direction = 'rtl'
				if language in (u'ar'):
					name = kashidaSentence(name, 20)
			else:
				direction = 'ltr'

			installedFonts = publisher.amountInstalledFonts()
			html.append(u'''
<a href="x-python://self.setPublisherHTML(____%s____)">
	<div id="%s" class="publisher clear" lang="%s" dir="%s">
		<div class="name">
		%s
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
</a>''' % (b64ID, b64ID, language, direction, name, 'block' if installedFonts else 'none', installedFonts or ''))


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

	def setBadgeLabel(self, label):
		u'''\
		Set dock icon badge
		'''
		label = str(label)
		self._dockTile.display()
		self._dockTile.setBadgeLabel_(label)

	def localize(self, key, html):
		string = localize(key, self.locale())
		if html:
			string = string.replace('\n', '<br />')
		print string

	def localizeString(self, string, html = False):
		string = localizeString(string, languages = self.locale(), html = html)
		return string

	def replaceHTML(self, html):
		html = html.replace('##htmlroot##', os.path.join(os.path.dirname(__file__), 'html'))
		return html

	def locale(self):
		u'''\
		Reads user locale from OS
		'''
		if not hasattr(self, '_locale'):
			from AppKit import NSLocale
			self._locale = [str(NSLocale.autoupdatingCurrentLocale().localeIdentifier().split('_')[0]), 'en']
		return self._locale

	def setPublisherBadge(self, b64ID, string):
		if string:
			self.html.RunScript('$("#sidebar #%s .badge.installed").fadeOut(200, function() { $("#sidebar #%s .badge.installed").html("%s"); $("#sidebar #%s .badge.installed").fadeIn(200); });' % (b64ID, b64ID, string, b64ID))
		else:
			self.html.RunScript('$("#sidebar #%s .badge.installed").fadeOut(200);' % b64ID)

	def debug(self, string):
		print string



class MyApp(wx.App):
	def MacOpenURL(self, url):
		if url.startswith('x-typeworldjson://'):
			url = url.replace('x-typeworldjson://', '')
			
			if self.frame.fullyLoaded:
				self.frame.addPublisher(url)
			else:
				self.frame.justAddedPublisher = url

	def OnInit(self):
		frame = AppFrame(None)
		self.frame = frame
		

		html = ReadFromFile(os.path.join(os.path.dirname(__file__), 'html', 'main', 'index.html'))

		html = html.replace('##jquery##', str(ReadFromFile(os.path.join(os.path.dirname(__file__), 'html', 'main', 'js', 'jquery-1.12.4.js'))))
		html = html.replace('##jqueryui##', str(ReadFromFile(os.path.join(os.path.dirname(__file__), 'html', 'main', 'js', 'jquery-ui.js'))))
		html = html.replace('##js.js##', str(ReadFromFile(os.path.join(os.path.dirname(__file__), 'html', 'main', 'js', 'js.js'))))
		html = html.replace('##css##', str(ReadFromFile(os.path.join(os.path.dirname(__file__), 'html', 'main', 'css', 'index.css'))))
		html = html.replace('##jqueryuicss##', str(ReadFromFile(os.path.join(os.path.dirname(__file__), 'html', 'main', 'css', 'jquery-ui.css'))))

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


