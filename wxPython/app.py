# -*- coding: utf-8 -*-

import wx, os, webbrowser, urllib
import wx.html2
from locales import *

from ynlib.files import ReadFromFile
from ynlib.strings import kashidas, kashidaSentence

from typeWorld.client import APIClient, AppKitNSUserDefaults

APPNAME = 'Type.World'
APPVERSION = 0.1


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
		menuBar.Append(menu, "&Help")
		# Preferences
		m_prefs = menu.Append(wx.ID_PREFERENCES, "&Preferences\tCtrl-,")
		self.Bind(wx.EVT_MENU, self.onPreferences, m_prefs)        

		self.SetMenuBar(menuBar)

		self.CentreOnScreen()


		from AppKit import NSApp
		self._NSApp = NSApp()
		self.Bind(wx.EVT_SIZE, self.onResize, self)



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


	def onClose(self, event):
		# dlg = wx.MessageDialog(self, 
		# 	"Do you really want to close this application?",
		# 	"Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
		# result = dlg.ShowModal()
		# dlg.Destroy()
		# if result == wx.ID_OK:
		# 	self.Destroy()
		self.Destroy()

	def onResize(self, event):
		# Make title bar transparent
		# https://developer.apple.com/documentation/appkit/nswindowstylemask?language=objc
#		if False:
		if wx.Platform == '__WXMAC__':
			w = self._NSApp.mainWindow()
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


		print 'addPublisher', url

		success, message = self.client.addRepository(url)

		if success:
			self.setSideBarHTML()
			self.html.RunScript("hideAddPublisher();")

		else:
			self.errorMessage(message)

	def removePublisher(self, i):
		publisher = self.orderedPublishers()[int(i.split('_')[1])]
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

			if success:

				# Get font
				for foundry in api.response.getCommand().foundries:
					for family in foundry.families:
						for font in family.fonts:
							if font.uniqueID == fontID:
								self.html.RunScript('$("#%s").html("%s");' % (fontID, self.fontHTML(api, font)))
								break

			else:

				if type(message) in (str, unicode):
					self.errorMessage(message)
				else:
					self.errorMessage('Server: %s' % message.getText(self.locale()))

		else:
			success = False
			self.errorMessage('The URL %s is unknown.' % (canonicalURL))




	def installFont(self, canonicalURL, fontID, version):
		self.html.RunScript("$('#%s .installButton').hide();" % fontID)
		self.html.RunScript("$('#%s .status').show();" % fontID)

		api = self.client.endpoints[canonicalURL].latestVersion()

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

	def setPublisherHTML(self, i):

		if self.client.preferences:
			self.client.preferences.set('currentPublisher', i)

		html = []

		api = self.orderedPublishers()[int(i.split('_')[1])].latestVersion()

		name, locale = api.name.getTextAndLocale(locale = self.locale())
		logo = False

		html.append('<div class="publisher">')
		html.append('<div class="head" style="height: 15px; background-color: white;">')
		# Preferences
		html.append('<div class="buttons clear">')
		html.append('<div class="left">#(Publisher): %s</div>' % (name))
		html.append('<div class="right"><a class="warningButton" href="x-python://self.removePublisher(____%s____)">#(Remove)</a></div>' % (i))
		html.append('<div class="right"><a href="x-python://self.publisherPreferences(____%s____)">#(Preferences)</a></div>' % i)
		html.append('<div class="right"><a href="x-python://self.publisherPreferences(____%s____)">#(Reload)</a></div>' % i)
		html.append('</div>') # .buttons
		html.append('</div>') # .head
		html.append('</div>') # .publisher

		html.append('<div class="publisher" id="%s">' % (i))

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


});

</script>''')


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
		self.html.RunScript("$('#sidebar #%s').addClass('selected');" % i)
		self.html.RunScript("showMain();")


	def setSideBarHTML(self):
		# Set publishers

		html = []


		# Sort
		# pass

		# Create HTML
		for key, name, language in self.publishersNames():

			if language in (u'ar', u'he'):
				direction = 'rtl'
				if language in (u'ar'):
					name = kashidaSentence(name, 20)
			else:
				direction = 'ltr'

			html.append(u'''
<a href="x-python://self.setPublisherHTML(____publisher_%s____)">
	<div id="publisher_%s" class="publisher clear" lang="%s" dir="%s">
		<div class="name">
		%s
		</div>
		<div class="new badge">
		</div>
	</div>
</a>''' % (key, key, language, direction, name))


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
		print html
		js = '$("#publishers").html("' + html + '");'
		self.html.RunScript(js)



	def onLoad(self, event):

		# Make title bar transparent
		# https://developer.apple.com/documentation/appkit/nswindowstylemask?language=objc
#		if False:
		if wx.Platform == '__WXMAC__':
			w = self._NSApp.mainWindow()
			# w.setStyleMask_(1 << 0 | 1 << 1 | 1 << 2 | 1 << 3 | 1 << 15)
			# w.setTitlebarAppearsTransparent_(1)
			# w.setTitle_(' ')
			# w.setTitleVisibility_(1)
			# w.setMovableByWindowBackground_(True)
			# js = '$("#sidebar").css("padding-top", "18px");'
			# self.html.RunScript(js)

		# DEV, REMOVE LATER
#		self.client.addRepository('http://192.168.56.102/type.world/api/wsqmRxRmY3C8vtrutfIr/?command=installableFonts&user=zFiZMRY3QHbq537RKL87')


		self.setSideBarHTML()
		if self.client.preferences and self.client.preferences.get('currentPublisher'):
			self.setPublisherHTML(self.client.preferences.get('currentPublisher'))


	def setBadgeLabel(self, label):
		u'''\
		Set dock icon badge
		'''
		self._dockTile = self._nsApp.dockTile()
		self._dockTile.setBadgeLabel_(label)

	def localize(self, key):
		return localize(key, self.locale())

	def localizeString(self, string):
		return localizeString(string, languages = self.locale())

	def locale(self):
		u'''\
		Reads user locale from OS
		'''
		if not hasattr(self, '_locale'):
			from AppKit import NSLocale
			self._locale = [str(NSLocale.autoupdatingCurrentLocale().localeIdentifier().split('_')[0]), 'en']
		return self._locale

	def setBadge(self, publisherKeyword, string):
		self.html.RunScript('$("#sidebar #%s .new").fadeOut();' % (publisherKeyword))
		self.html.RunScript('$("#sidebar #%s .new").fadeIn();' % (publisherKeyword))
		self.html.RunScript('$("#sidebar #%s .new").html("%s");' % (publisherKeyword, string))

	def debug(self, string):
		print string

if __name__ == '__main__':
	app = wx.App()

	frame = AppFrame(None)
#	frame.html.LoadURL(os.path.join('file://', os.path.dirname(__file__), 'html', 'main', 'index.html'))
	html = ReadFromFile(os.path.join(os.path.dirname(__file__), 'html', 'main', 'index.html'))
	frame.html.SetPage(frame.localizeString(html), os.path.join(os.path.dirname(__file__), 'html', 'main', 'index.html'))
	frame.Show()
	app.MainLoop()

