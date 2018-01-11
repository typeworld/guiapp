# -*- coding: utf-8 -*-

import wx, os, webbrowser, urllib
import wx.html2
from locales import *

from ynlib.files import ReadFromFile

APPNAME = 'Type World'
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
		super(AppFrame, self).__init__(parent, size=(800,500))

		# Set title to blank space to remove title bar but retain movability
		if wx.Platform == '__WXMAC__':
			self.Title = ' '
		else:
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
			w.setStyleMask_(1 << 0 | 1 << 1 | 1 << 2 | 1 << 3 | 1 << 15)
			w.setTitlebarAppearsTransparent_(1)
#			w.setTitle_(' ')
		print w.title(), w.titlebarAppearsTransparent(), w.styleMask()
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
#			code = code.replace('%5C\'', '\"')
			code = urllib.unquote(code).decode('utf8')
			print code
			exec(code)
			evt.Veto()
		elif uri.startswith('http://') or uri.startswith('https://'):
			webbrowser.open_new_tab(uri)
			evt.Veto()

	def onError(self, evt):
		print evt.GetString()
		raise Exception(evt.GetString())

	def onLoad(self, event):

		# Make title bar transparent
		# https://developer.apple.com/documentation/appkit/nswindowstylemask?language=objc
#		if False:
		if wx.Platform == '__WXMAC__':
			w = self._NSApp.mainWindow()
			w.setStyleMask_(1 << 0 | 1 << 1 | 1 << 2 | 1 << 3 | 1 << 15)
			w.setTitlebarAppearsTransparent_(1)
			w.setTitle_(' ')
	#		w.setTitleVisibility_(1)
	#		w.setMovableByWindowBackground_(True)
			js = '$("#sidebar").css("padding-top", "18px");'
			self.html.RunScript(js)


		# Set publishers

		from ynlib.strings import kashidas, kashidaSentence

		html = []
		for key, name, language in (
			(u'yanone', u'Yanone', u'en'),
			(u'abjd', u'مشروع ابجد', u'ar'),
			(u'abjad', u'ابجد', u'ar'),
			(u'n3m', u'نعم', u'ar'),
			):

			if language in (u'ar'):
				direction = 'rtl'
				name = kashidaSentence(name, 20)
			else:
				direction = 'ltr'

			html.append(u'''
	<div id="%s" class="publisher clear" lang="%s" dir="%s">
		<div class="name">
		%s
		</div>
		<div class="new badge">
		</div>
	</div>''' % (key, language, direction, name))

		js = '$("#publishers").html("' + ''.join(html).replace('"', '\'').replace('\n', '') + '");'
		self.html.RunScript(js)


	def setBadgeLabel(self, label):
		u'''\
		Set dock icon badge
		'''
		self._dockTile = self._nsApp.dockTile()
		self._dockTile.setBadgeLabel_(label)

	def localize(self, key):
		return localize(key, self.locale())

	def localizeString(self, string):
		return localizeString(string, self.locale())

	def locale(self):
		u'''\
		Reads user locale from OS
		'''
		if not hasattr(self, '_locale'):
			from AppKit import NSLocale
			self._locale = [NSLocale.autoupdatingCurrentLocale().localeIdentifier().split('_')[0]]
		return self._locale

	def setBadge(self, publisher, string):
		self.html.RunScript('$("#sidebar #%s .new").fadeOut();' % (publisher))
		self.html.RunScript('$("#sidebar #%s .new").fadeIn();' % (publisher))
		self.html.RunScript('$("#sidebar #%s .new").html("%s");' % (publisher, string))

if __name__ == '__main__':
	app = wx.App()

	frame = AppFrame(None)
#	frame.html.LoadURL(os.path.join('file://', os.path.dirname(__file__), 'html', 'main', 'index.html'))
	html = ReadFromFile(os.path.join(os.path.dirname(__file__), 'html', 'main', 'index.html'))
	frame.html.SetPage(frame.localizeString(html), os.path.join(os.path.dirname(__file__), 'html', 'main', 'index.html'))
	frame.Show()
	app.MainLoop()

