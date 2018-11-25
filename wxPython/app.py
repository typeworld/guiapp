#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os, sys

# Adjust __file__ for Windows executable
try:
	__file__ = os.path.abspath(__file__)

except:
	__file__ = sys.executable

sys.path.insert(0, os.path.dirname(__file__))


import wx, webbrowser, urllib.request, urllib.parse, urllib.error, base64, plistlib, json, datetime, traceback, ctypes, semver, platform, logging
from threading import Thread
import threading
import wx.html2
import locales
import urllib.request, urllib.parse, urllib.error, time
from functools import partial
from wx.lib.delayedresult import startWorker
from multiprocessing.connection import Client
from threading import Thread
from ynlib.system import Execute

import platform
WIN = platform.system() == 'Windows'
MAC = platform.system() == 'Darwin'

from ynlib.files import ReadFromFile, WriteToFile
from ynlib.strings import *
from ynlib.web import GetHTTP

from typeWorldClient import APIClient, JSON, AppKitNSUserDefaults
import typeWorld.api.base

# print ('__file__', __file__)
# print ('sys.executable ', sys.executable )

APPNAME = 'Type.World'
APPVERSION = 'n/a'
DEBUG = False
BUILDSTAGE = 'alpha'

# Mac executable
if 'app.py' in __file__ and '/Contents/MacOS/python' in sys.executable:
	DESIGNTIME = False
	RUNTIME = True

elif not 'app.py' in __file__:
	DESIGNTIME = False
	RUNTIME = True

else:
	DESIGNTIME = True
	RUNTIME = False

if WIN:
	sys._MEIPASS = os.path.join(os.path.dirname(__file__), 'lib', 'pywinsparkle', 'libs', 'x64')
	from pywinsparkle import pywinsparkle

## Windows:
## Register Custom Protocol Handlers in the Registry. Later, this should be moved into the installer.

if WIN and RUNTIME:
	try:
		import winreg as wreg
		for handler in ['typeworldjson', 'typeworldgithub']:
			key = wreg.CreateKey(wreg.HKEY_CLASSES_ROOT, handler)
			wreg.SetValueEx(key, None, 0, wreg.REG_SZ, 'URL:%s' % handler)
			wreg.SetValueEx(key, 'URL Protocol', 0, wreg.REG_SZ, '')
			key = wreg.CreateKey(key, 'shell\\open\\command')
			wreg.SetValueEx(key, None, 0, wreg.REG_SZ, '"%s" "%%1"' % os.path.join(os.path.dirname(__file__), 'TypeWorld Subscription Opener.exe'))
	except:
		pass


import sys, os, traceback, types


## Windows:
## Open other app instance if open

def PID(ID):
	import psutil
	PROCNAME = ID
	for proc in psutil.process_iter():
		if proc.name() == PROCNAME and proc.pid != os.getpid():
			return proc.pid



# Read app version number

def getFileProperties(fname):
	"""
	Read all properties of the given file return them as a dictionary.
	"""
	import win32api

	propNames = ('Comments', 'InternalName', 'ProductName',
		'CompanyName', 'LegalCopyright', 'ProductVersion',
		'FileDescription', 'LegalTrademarks', 'PrivateBuild',
		'FileVersion', 'OriginalFilename', 'SpecialBuild')

	props = {'FixedFileInfo': None, 'StringFileInfo': None, 'FileVersion': None}

	try:
		# backslash as parm returns dictionary of numeric info corresponding to VS_FIXEDFILEINFO struc
		fixedInfo = win32api.GetFileVersionInfo(fname, '\\')
		props['FixedFileInfo'] = fixedInfo
		props['FileVersion'] = "%d.%d.%d.%d" % (fixedInfo['FileVersionMS'] / 65536,
				fixedInfo['FileVersionMS'] % 65536, fixedInfo['FileVersionLS'] / 65536,
				fixedInfo['FileVersionLS'] % 65536)

		# \VarFileInfo\Translation returns list of available (language, codepage)
		# pairs that can be used to retreive string info. We are using only the first pair.
		lang, codepage = win32api.GetFileVersionInfo(fname, '\\VarFileInfo\\Translation')[0]

		# any other must be of the form \StringfileInfo\%04X%04X\parm_name, middle
		# two are language/codepage pair returned from above

		strInfo = {}
		for propName in propNames:
			strInfoPath = u'\\StringFileInfo\\%04X%04X\\%s' % (lang, codepage, propName)
			## print str_info
			strInfo[propName] = win32api.GetFileVersionInfo(fname, strInfoPath)

		props['StringFileInfo'] = strInfo
	except:
		pass

	return props

if DESIGNTIME:
	APPVERSION = open(os.path.join(os.path.dirname(__file__), '..', 'currentVersion.txt'), 'r').read().strip()

elif RUNTIME:

	if MAC:
		try:
			plist = plistlib.readPlist(os.path.join(os.path.dirname(__file__), '..', 'Info.plist'))
			APPVERSION = plist['CFBundleShortVersionString']
		except:
			pass

	elif WIN:
		APPVERSION = getFileProperties(__file__)['StringFileInfo']['ProductVersion'].strip()

		if len(APPVERSION.split('.')) == 4:
			APPVERSION = '.'.join(APPVERSION.split('.')[0:-1])

		APPVERSION += '-' + BUILDSTAGE

if WIN:
	from appdirs import user_data_dir
	prefDir = user_data_dir('Type.World', 'Type.World')
elif MAC:
	prefDir = os.path.expanduser('~/Library/Preferences/')


if WIN:
	prefFile = os.path.join(prefDir, 'preferences.json')
	prefs = JSON(prefFile)
	# print('Preferences at %s' % prefFile)
else:
	prefs = AppKitNSUserDefaults('world.type.clientapp' if DESIGNTIME else None)

client = APIClient(preferences = prefs)



def agent(command):
	
	if agentIsRunning():
		try:
			address = ('localhost', 65501)
			myConn = Client(address)
			myConn.send(command)
			response = myConn.recv()
			myConn.close()

			return response
		except:
			pass


def agentIsRunning():

	if MAC:
		from AppKit import NSRunningApplication

		# Kill running app
		ID = 'world.type.agent'
		# App is running, so activate it
		apps = list(NSRunningApplication.runningApplicationsWithBundleIdentifier_(ID))
		if apps:
			mainApp = apps[0]
			return True

	if WIN:
		return PID('TypeWorld Taskbar Agent.exe') is not None


def waitToLaunchAgent():

	time.sleep(2)

	if MAC:
		agentPath = os.path.expanduser('~/Library/Application Support/Type.World/Type.World Agent.app')
		os.system('"%s" &' % os.path.join(agentPath, 'Contents', 'MacOS', 'Type.World Agent'))

		# import subprocess
		# subprocess.Popen(['"%s"' % os.path.join(agentPath, 'Contents', 'MacOS', 'Type.World Agent')])
#

def installAgent():

#	uninstallAgent()

	if MAC:
		from AppKit import NSBundle
		zipPath = NSBundle.mainBundle().pathForResource_ofType_('agent', 'tar.bz2')
		plistPath = os.path.expanduser('~/Library/LaunchAgents/world.type.agent.plist')
		agentPath = os.path.expanduser('~/Library/Application Support/Type.World/Type.World Agent.app')
		plist = '''<?xml version="1.0" encoding="UTF-8"?>
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
<string>''' + agentPath + '''/Contents/MacOS/Type.World Agent</string>
<key>RunAtLoad</key>
<true/>
</dict>
</plist>'''


		# Extract app
		folder = os.path.dirname(agentPath)
		if not os.path.exists(folder):
			os.makedirs(folder)
		os.system('tar -zxf "%s" -C "%s"' % (zipPath, folder))

		# Write Launch Agent
		if not os.path.exists(os.path.dirname(plistPath)):
			os.makedirs(os.path.dirname(plistPath))
		f = open(plistPath, 'w')
		f.write(plist)
		f.close()

		# Run App
#		if platform.mac_ver()[0].split('.') < '10.14.0'.split('.'):
		# import subprocess
		# subprocess.Popen(['"%s"' % os.path.join(agentPath, 'Contents', 'MacOS', 'Type.World Agent')])
		os.system('"%s" &' % os.path.join(agentPath, 'Contents', 'MacOS', 'Type.World Agent'))

		launchAgentThread = Thread(target=waitToLaunchAgent)
		launchAgentThread.start()

		print('installAgent() done')

	if WIN:

#			file_path = os.path.join(os.path.dirname(__file__), r'TypeWorld Taskbar Agent.exe')
		file_path = os.path.join(os.path.dirname(__file__), r'TypeWorld Taskbar Agent.exe')
		file_path = file_path.replace(r'\\Mac\Home', r'Z:')
		print(file_path)

		import getpass
		USER_NAME = getpass.getuser()

		bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
		bat_command = 'start "" "%s"' % file_path

		from pathlib import Path
		print(Path(file_path).exists())

		if not os.path.exists(os.path.dirname(bat_path)):
			os.makedirs(os.path.dirname(bat_path))
		with open(bat_path + '\\' + "TypeWorld.bat", "w+") as bat_file:
			bat_file.write(bat_command)

		import subprocess
		os.chdir(os.path.dirname(file_path))
		subprocess.Popen([file_path], executable = file_path)

	client.preferences.set('menuBarIcon', True)




def uninstallAgent():

	if MAC:
		from AppKit import NSRunningApplication

		plistPath = os.path.expanduser('~/Library/LaunchAgents/world.type.agent.plist')
		agentPath = os.path.expanduser('~/Library/Application Support/Type.World/Type.World Agent.app')

		# Kill running app
		ID = 'world.type.agent'
		# App is running, so activate it
		apps = list(NSRunningApplication.runningApplicationsWithBundleIdentifier_(ID))
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

		agent('quit')	

		import getpass
		USER_NAME = getpass.getuser()

		bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\TypeWorld.bat' % USER_NAME
		if os.path.exists(bat_path):
			os.remove(bat_path)

	client.preferences.set('menuBarIcon', False)



class AppFrame(wx.Frame):
	def __init__(self, parent):        


		self.messages = []


		# Version adjustments

		# TODO: Remove these for future versions
		if client.preferences.get('appVersion'):
			# 0.1.4
			if client.preferences.get('appVersion') != APPVERSION and APPVERSION == '0.1.4-alpha' and semver.compare("0.1.4-alpha", client.preferences.get('appVersion')) == 1:

				if client.publishers():
					for publisher in client.publishers():
						publisher.delete()

					self.messages.append('Due to a change in the subscription security and login infrastructure, all subscriptions were removed. The API endpoints need to be adjusted and subscriptions re-added following the new guidelines. See https://type.world/app/ for the release notes.')


		if not client.preferences.get('appVersion'):
			client.preferences.set('appVersion', APPVERSION)
		if not client.preferences.get('localizationType'):
			client.preferences.set('localizationType', 'systemLocale')
		if not client.preferences.get('customLocaleChoice'):
			client.preferences.set('customLocaleChoice', client.systemLocale())
		if not client.preferences.get('reloadSubscriptionsInterval'):
			client.preferences.set('reloadSubscriptionsInterval', 1 * 24 * 60 * 60) # one day
		if not client.preferences.get('seenDialogs'):
			client.preferences.set('seenDialogs', [])

		client.preferences.set('appVersion', APPVERSION)



		self.thread = threading.current_thread()


		self.justAddedPublisher = None
		self.fullyLoaded = False
		self.panelVisible = False



		# Window Size
		minSize = [1000, 700]
		if client.preferences.get('sizeMainWindow'):
			size = list(client.preferences.get('sizeMainWindow'))

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

		self.Title = '%s %s' % (APPNAME, APPVERSION)

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


		### Menus
		menuBar = wx.MenuBar()

		# Exit
		menu = wx.Menu()
		m_opensubscription = menu.Append(wx.ID_OPEN, "%s...%s" % (self.localize('Add Subscription'), '\tCtrl+O' if MAC else ''))#\tCtrl-O
		self.Bind(wx.EVT_MENU, self.showAddSubscription, m_opensubscription)
#        m_opensubscription.SetAccel(wx.AcceleratorEntry(wx.ACCEL_CTRL,  ord('o')))


		m_CheckForUpdates = menu.Append(wx.NewId(), "%s..." % (self.localize('Check for App Updates')))
		self.Bind(wx.EVT_MENU, self.onCheckForUpdates, m_CheckForUpdates)
		if MAC:
			m_closewindow = menu.Append(wx.ID_CLOSE, "%s\tCtrl+W" % (self.localize('Close Window')))
			self.Bind(wx.EVT_MENU, self.onClose, m_closewindow)
		m_exit = menu.Append(wx.ID_EXIT, "%s\t%s" % (self.localize('Exit'), 'Ctrl-Q' if MAC else 'Alt-F4'))
		self.Bind(wx.EVT_MENU, self.onQuit, m_exit)

		# m_InstallAgent = menu.Append(wx.NewId(), "Install Agent")
		# self.Bind(wx.EVT_MENU, self.installAgent, m_InstallAgent)
		# m_RemoveAgent = menu.Append(wx.NewId(), "Remove Agent")
		# self.Bind(wx.EVT_MENU, self.uninstallAgent, m_RemoveAgent)


		menuBar.Append(menu, "&%s" % (self.localize('File')))

		# Edit
		# if 'wxMac' in wx.PlatformInfo and wx.VERSION >= (3,0):
		#   wx.ID_COPY = wx.NewId()
		#   wx.ID_PASTE = wx.NewId()
		editMenu = wx.Menu()
		editMenu.Append(wx.ID_UNDO, "%s\tCtrl-Z" % (self.localize('Undo')))
		editMenu.AppendSeparator()
		editMenu.Append(wx.ID_SELECTALL, "%s\tCtrl-A" % (self.localize('Select All')))
		editMenu.Append(wx.ID_COPY, "%s\tCtrl-C" % (self.localize('Copy')))
		editMenu.Append(wx.ID_CUT, "%s\tCtrl-X" % (self.localize('Cut')))
		editMenu.Append(wx.ID_PASTE, "%s\tCtrl-V" % (self.localize('Paste')))

		if WIN:
			editMenu.AppendSeparator()
			m_prefs = editMenu.Append(wx.ID_PREFERENCES, "&%s\tCtrl-I" % (self.localize('Preferences')))
			self.Bind(wx.EVT_MENU, self.onPreferences, m_prefs)



		menuBar.Append(editMenu, "&%s" % (self.localize('Edit')))

		menu = wx.Menu()
		m_about = menu.Append(wx.ID_ABOUT, "&%s %s" % (self.localize('About'), APPNAME))
		self.Bind(wx.EVT_MENU, self.onAbout, m_about)
		if MAC:
			m_prefs = menu.Append(wx.ID_PREFERENCES, "&%s\tCtrl-," % (self.localize('Preferences')))
			self.Bind(wx.EVT_MENU, self.onPreferences, m_prefs)        

		# menuBar.Append(menu, "Type.World")
		menuBar.Append(menu, "&%s" % (self.localize('Help')))

		self.SetMenuBar(menuBar)

		# Reinstall agent if outdated
		if agentIsRunning():
			agentVersion = agent('version')
			if semver.compare(APPVERSION, agentVersion) == 1:
				uninstallAgent()
				installAgent()


		self.CentreOnScreen()
		self.Show()


		# Restart agent after restart
		if client.preferences.get('menuBarIcon') and not agentIsRunning():
			installAgent()


		self.Bind(wx.EVT_SIZE, self.onResize, self)
		self.Bind(wx.EVT_ACTIVATE, self.onActivate, self)


		import signal

		def exit_signal_handler(signal, frame):

			# template = zroya.Template(zroya.TemplateType.ImageAndText4)
			# template.setFirstLine('Quit Signal')
			# # template.setSecondLine(str(signal))
			# # template.setThirdLine(str(frame))
			# expiration = 24 * 60 * 60 * 1000 # one day
			# template.setExpiration(expiration) # One day
			# notificationID = zroya.show(template)


			self.onQuit(None)

		# if MAC:
		# 	signal.signal(signal.SIGBREAK, exit_signal_handler)
		signal.signal(signal.SIGTERM, exit_signal_handler)
		signal.signal(signal.SIGINT, exit_signal_handler)




		if MAC and RUNTIME:
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

		if WIN:
			self.setup_pywinsparkle()

		# try:
		#     from ctypes import OleDLL
		#     # Turn on high-DPI awareness to make sure rendering is sharp on big
		#     # monitors with font scaling enabled.
		#     OleDLL('shcore').SetProcessDpiAwareness(1)
		# except AttributeError:
		#     # We're on a non-Windows box.
		#     pass
		# except OSError:
		#     # exc.winerror is often E_ACCESSDENIED (-2147024891/0x80070005).
		#     # This occurs after the first run, when the parameter is reset in the
		#     # executable's manifest and then subsequent calls raise this exception
		#     # See last paragraph of Remarks at
		#     # https://msdn.microsoft.com/en-us/library/dn302122(v=vs.85).aspx
		#     pass






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



				




	def publishersNames(self):
		# Build list, sort it
		publishers = []
		for i, key in enumerate(client.endpoints.keys()):
			endpoint = client.endpoints[key]
			name, language = endpoint.latestVersion().name.getTextAndLocale(locale = client.locale())
			publishers.append((i, name, language))
		return publishers


	def onCheckForUpdates(self, event):
		if MAC:
			self.sparkle.checkForUpdates_(None)
		elif WIN:
			pywinsparkle.win_sparkle_check_update_with_ui()

	def onClose(self, event):


		if self.panelVisible:
			self.javaScript('hidePanel();')
		else:

			self.onQuit(None)

	def onQuit(self, event):

		address = ('localhost', 65500)
		myConn = Client(address)
		myConn.send('closeListener')
		myConn.close()

		if WIN:
			pywinsparkle.win_sparkle_cleanup()

		self.Destroy()

	def onActivate(self, event):

		self.log('onActivate()')

		resize = False

		# self.SetTitle(str(sys.argv))


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

		if resize:
			self.SetSize(size)

		if client.preferences.get('currentPublisher'):
			self.setPublisherHTML(self.b64encode(client.preferences.get('currentPublisher')))

		if WIN:
			self.checkForURLInFile()

		# if MAC:
		# 	self.applyDarkMode()

	def applyDarkMode(self):

		if platform.mac_ver()[0].split('.') > '10.14.0'.split('.'):
			from AppKit import NSUserDefaults

			if NSUserDefaults.standardUserDefaults().objectForKey_('AppleInterfaceStyle') == 'Dark':
				self.javaScript('$("#main").css("background-color", "#000");')
				self.javaScript('$("#main").css("color", "#fff");')
				self.javaScript('$("#main .publisher .font.hover, #main .publisher .section.hover").css("background-color", "#070707");')

			else:
				self.javaScript('$("#main").css("background-color", "#fff");')
				self.javaScript('$("#main").css("color", "#000");')
				self.javaScript('$("#main .publisher .font.hover, #main .publisher .section.hover").css("background-color", "#F7F7F7");')




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
		client.preferences.set('sizeMainWindow', (self.GetSize()[0], self.GetSize()[1]))
		event.Skip()
#       print event.Veto()
#       return


	def onAbout(self, event):

		html = []

		html.append('<p style="text-align: center; margin-bottom: 20px;">')
		html.append('<img src="file://##htmlroot##/biglogo.svg" style="width: 200px;"><br />')
		html.append('</p>')
		html.append('<p>')
		html.append('#(AboutText)')
		html.append('</p>')
		html.append('<p>')
		html.append('#(Anonymous App ID): %s<br />' % client.anonymousAppID())
		html.append('#(Version) %s<br />' % APPVERSION)
		html.append('#(Version History) #(on) <a href="https://type.world/app">type.world/app</a>')
		html.append('</p>')
		# html.append(u'<p>')
		# html.append(u'<a class="button" onclick="python('self.sparkle.checkForUpdates_(None)');">#(Check for App Updates)</a>')
		# html.append(u'</p>')


		# Print HTML
		html = ''.join(html)
		html = self.replaceHTML(html)
		html = self.localizeString(html, html = True)
		html = html.replace('"', '\'')
		html = html.replace('\n', '')
		js = '$("#about .inner").html("' + html + '");'
		self.javaScript(js)

		self.javaScript('showAbout();')

	def resetDialogs(self):
		client.preferences.set('seenDialogs', [])


	def onPreferences(self, event):


		html = []

		# Update Interval
		html.append('<h2>#(Update Interval)</h2>')
		html.append('<p>#(UpdateIntervalExplanation)</p>')
		html.append('<p>')
		html.append('<select id="updateIntervalChoice" style="">')
		for code, name in (
			(-1, '#(Manually)'),
			(1 * 60, '#(Minutely)'),
			(1 * 60 * 60, '#(Hourly)'),
			(24 * 60 * 60, '#(Daily)'),
			(7 * 24 * 60 * 60, '#(Weekly)'),
			(30 * 24 * 60 * 60, '#(Monthly)'),
		):
			html.append('<option value="%s" %s>%s</option>' % (code, 'selected' if str(code) == str(client.preferences.get('reloadSubscriptionsInterval')) else '', name))
		html.append('</select>')
		html.append('<script>$("#preferences #updateIntervalChoice").click(function() {setPreference("reloadSubscriptionsInterval", $("#preferences #updateIntervalChoice").val());});</script>')
		html.append('<br />#(Last Check): %s' % NaturalRelativeWeekdayTimeAndDate(client.preferences.get('reloadSubscriptionsLastPerformed'), locale = client.locale()[0]))
		html.append('</p>')

		html.append('<p></p>')


		# Agent
		html.append('<h2>#(Icon in Menu Bar)</h2>')
		html.append('<p>')
		html.append('<span><input id="menubar" type="checkbox" name="menubar" %s><label for="menubar">#(Show Icon in Menu Bar)</label></span>' % ('checked' if agentIsRunning() else ''))
		html.append('<script>$("#preferences #menubar").click(function() { if($("#preferences #menubar").prop("checked")) { python("installAgent()"); } else { setCursor("wait", 2000); python("uninstallAgent()"); } });</script>')
		html.append('<br />')
		html.append('#(Icon in Menu Bar Explanation)')
		html.append('</p>')

		html.append('<p></p>')


		# Localization
		systemLocale = client.systemLocale()
		for code, name in locales.locales:
			if code == systemLocale:
				systemLocale = name
				break
		html.append('<h2>App Language</h2>')
		html.append('<p>')
		html.append('<span><input id="systemLocale" value="systemLocale" type="radio" name="localizationType" %s><label for="systemLocale">Use System Language (%s)</label></span>' % ('checked' if client.preferences.get('localizationType') == 'systemLocale' else '', systemLocale))
		html.append('<script>$("#preferences #systemLocale").click(function() {setPreference("localizationType", "systemLocale");});</script>')
		html.append('<br />')
		html.append('<span><input id="customLocale" value="customLocale" type="radio" name="localizationType" %s><label for="customLocale">Use Custom Language (choose below). Requires app restart to take full effect.</label></span>' % ('checked' if client.preferences.get('localizationType') == 'customLocale' else ''))
		html.append('<script>$("#preferences #customLocale").click(function() {setPreference("localizationType", "customLocale");});</script>')
		html.append('<br />')
		html.append('<select id="customLocaleChoice" style="" onchange="">')
		for code, name in locales.locales:
			html.append('<option value="%s" %s>%s</option>' % (code, 'selected' if code == client.preferences.get('customLocaleChoice') else '', name))
		html.append('</select>')
		html.append('''<script>$("#preferences #customLocaleChoice").click(function() {

			setPreference("customLocaleChoice", $("#preferences #customLocaleChoice").val());
			 
		});</script>''')
		html.append('</p>')


		# Reset Dialogs
		html.append('<h2>#(Reset Dialogs)</h2>')
		html.append('<p>')
		html.append('<a id="resetDialogButton" class="button">#(ResetDialogsButton)</a>')
		html.append('</p>')
		html.append('''<script>$("#preferences #resetDialogButton").click(function() {

			python("self.resetDialogs()");
			 
		});</script>''')


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
			code = code.replace("'", '\'')
			# print('Python code:', code)
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
		# print('Navigated: %s' % uri)


	def onError(self, evt):
		print()
		print('Error received from WebView:', evt.GetString())
#       raise Exception(evt.GetString())


	def showAddSubscription(self, evt):
		self.javaScript('showAddSubscription();')


	def addSubscription(self, url, username = None, password = None):

		for publisher in client.publishers():
			for subscription in publisher.subscriptions():
				# print (subscription.url, url)
				if subscription.url == client.addAttributeToURL(url.replace('typeworldjson://', ''), 'command', 'installableFonts'):
					self.setActiveSubscription(self.b64encode(publisher.canonicalURL), self.b64encode(subscription.url))
					return

		self.javaScript("showCenterMessage('%s');" % self.localizeString('#(Loading Subscription)'))
		startWorker(self.addSubscription_consumer, self.addSubscription_worker, wargs=(url, username, password))


	def addSubscriptionViaDialog(self, url, username = None, password = None):

		self.log('addSubscription(%s, %s, %s)' % (url, username, password))
		startWorker(self.addSubscription_consumer, self.addSubscription_worker, wargs=(url, username, password))



	def addSubscription_worker(self, url, username, password):

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
			return False, 'Unknown protocol. Known are: %s' % (typeWorld.api.base.PROTOCOLS), None

		success, message, publisher = client.addSubscription(url, username, password)
		return success, message, publisher


	def addSubscription_consumer(self, delayedResult):

		success, message, publisher = delayedResult.get()

		if success:

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

		self.javaScript('hideCenterMessage();')


	def removePublisher(self, evt, b64ID):

		publisher = client.publisher(self.b64decode(b64ID))

		dlg = wx.MessageDialog(self, self.localizeString('#(Are you sure)'), self.localizeString('#(Remove X)').replace('%name%', self.localizeString(publisher.name(client.locale())[0])), wx.YES_NO | wx.ICON_QUESTION)
		result = dlg.ShowModal() == wx.ID_YES
		dlg.Destroy()
		
		if result:

			publisher.delete()
			self.setSideBarHTML()
			self.javaScript("hideMain();")

	def removeSubscription(self, evt, b64ID):


		for publisher in client.publishers():
			for subscription in publisher.subscriptions():
				if subscription.url == self.b64decode(b64ID):


					dlg = wx.MessageDialog(self, self.localizeString('#(Are you sure)'), self.localizeString('#(Remove X)').replace('%name%', self.localizeString(subscription.name(client.locale()))), wx.YES_NO | wx.ICON_QUESTION)
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
		pass


	def installAllFonts(self, b64publisherID, b64subscriptionID, b64familyID, b64setName, formatName):

		fonts = []

		publisherID = self.b64decode(b64publisherID)
		subscriptionID = self.b64decode(b64subscriptionID)
		familyID = self.b64decode(b64familyID)
		if b64setName:
			setName = self.b64decode(b64setName)
		else:
			setName = None
		publisher = client.publisher(publisherID)
		subscription = publisher.subscription(subscriptionID)
		family = subscription.familyByID(familyID)

		for font in family.fonts():
			if font.setName.getText(client.locale()) == setName and font.format == formatName:
				if not font.installedVersion():
					fonts.append([b64publisherID, b64subscriptionID, self.b64encode(font.uniqueID), font.getVersions()[-1].number])

		self.installFonts(fonts)


	def removeAllFonts(self, b64publisherID, b64subscriptionID, b64familyID, b64setName, formatName):

		fonts = []

		publisherID = self.b64decode(b64publisherID)
		subscriptionID = self.b64decode(b64subscriptionID)
		familyID = self.b64decode(b64familyID)
		if b64setName:
			setName = self.b64decode(b64setName)
		else:
			setName = None
		publisher = client.publisher(publisherID)
		subscription = publisher.subscription(subscriptionID)
		family = subscription.familyByID(familyID)

		for font in family.fonts():
			if font.setName.getText(client.locale()) == setName and font.format == formatName:
				if font.installedVersion():
					fonts.append([b64publisherID, b64subscriptionID, self.b64encode(font.uniqueID)])

		self.removeFonts(fonts)



	def installFontFromMenu(self, event, b64publisherURL, b64subscriptionURL, b64fontID, version):

		self.log('installFontFromMenu()')

		self.installFont(b64publisherURL, b64subscriptionURL, b64fontID, version)


	def installFont(self, b64publisherURL, b64subscriptionURL, b64fontID, version):

		self.javaScript('$("#%s.font").find("a.installButton").hide();' % b64fontID)
		self.javaScript('$("#%s.font").find("a.removeButton").hide();' % b64fontID)
		self.javaScript('$("#%s.font").find("a.status").show();' % b64fontID)
		self.javaScript('$("#%s.font").find("a.more").hide();' % b64fontID)

		startWorker(self.installFonts_consumer, self.installFonts_worker, wargs=([[[b64publisherURL, b64subscriptionURL, b64fontID, version]]]))


	def installFonts(self, fonts):

		for b64publisherURL, b64subscriptionURL, b64fontID, version in fonts:

			self.javaScript('$("#%s.font").find("a.installButton").hide();' % b64fontID)
			self.javaScript('$("#%s.font").find("a.removeButton").hide();' % b64fontID)
			self.javaScript('$("#%s.font").find("a.status").show();' % b64fontID)
			self.javaScript('$("#%s.font").find("a.more").hide();' % b64fontID)

		startWorker(self.installFonts_consumer, self.installFonts_worker, wargs=([fonts]))



	def installFonts_worker(self, fonts):

		self.log(fonts)

		for b64publisherURL, b64subscriptionURL, b64fontID, version in fonts:

			publisherURL = self.b64decode(b64publisherURL)
			subscriptionURL = self.b64decode(b64subscriptionURL)
			fontID = self.b64decode(b64fontID)

			publisher = client.publisher(publisherURL)
			subscription = publisher.subscription(subscriptionURL)
			api = subscription.latestVersion()

			# Remove other installed versions
			if subscription.installedFontVersion(fontID) != version:
				success, message = subscription.removeFont(fontID)
				if success == False:
					return success, message, b64publisherURL

			# Install new font
			success, message = subscription.installFont(fontID, version)

			if success == False:
				return success, message, b64publisherURL

		return True, None, b64publisherURL


	def installFonts_consumer(self, delayedResult):

		success, message, b64publisherURL = delayedResult.get()

		if success:

			pass

		else:

			if type(message) in (str, str):
				self.errorMessage(message)
			else:
				self.errorMessage('Server: %s' % message.getText(client.locale()))

		self.setSideBarHTML()
		self.setBadges()
		self.setPublisherHTML(b64publisherURL)


	def updateAllFonts(self, evt, publisherB64ID, subscriptionB64ID):

		fonts = []

		if publisherB64ID:
			publisher = client.publisher(self.b64decode(publisherB64ID))
			for subscription in publisher.subscriptions():
				subscriptionB64ID = self.b64encode(subscription.url)
				for foundry in subscription.foundries():
					for family in foundry.families():
						for font in family.fonts():
							if font.isOutdated():
								fonts.append([publisherB64ID, subscriptionB64ID, self.b64encode(font.uniqueID), font.getVersions()[-1].number])

		elif subscriptionB64ID:
			
			for publisher in client.publishers():
				for subscription in publisher.subscriptions():
					if subscription.url == self.b64decode(subscriptionB64ID):
						publisherB64ID = self.b64encode(publisher.canonicalURL)
						break

			for foundry in subscription.foundries():
				for family in foundry.families():
					for font in family.fonts():
						if font.isOutdated():
							fonts.append([publisherB64ID, subscriptionB64ID, self.b64encode(font.uniqueID), font.getVersions()[-1].number])

		self.installFonts(fonts)


	def removeFont(self, b64publisherURL, b64subscriptionURL, b64fontID):

		self.javaScript('$("#%s.font").find("a.installButton").hide();' % b64fontID)
		self.javaScript('$("#%s.font").find("a.removeButton").hide();' % b64fontID)
		self.javaScript('$("#%s.font").find("a.status").show();' % b64fontID)
		self.javaScript('$("#%s.font").find("a.more").hide();' % b64fontID)

		startWorker(self.removeFonts_consumer, self.removeFonts_worker, wargs=([[[b64publisherURL, b64subscriptionURL, b64fontID]]]))

	def removeFonts(self, fonts):

		for b64publisherURL, b64subscriptionURL, b64fontID in fonts:

			self.javaScript('$("#%s.font").find("a.installButton").hide();' % b64fontID)
			self.javaScript('$("#%s.font").find("a.removeButton").hide();' % b64fontID)
			self.javaScript('$("#%s.font").find("a.status").show();' % b64fontID)
			self.javaScript('$("#%s.font").find("a.more").hide();' % b64fontID)

		startWorker(self.removeFonts_consumer, self.removeFonts_worker, wargs=([fonts]))


	def removeFonts_worker(self, fonts):

		for b64publisherURL, b64subscriptionURL, b64fontID in fonts:

			publisherURL = self.b64decode(b64publisherURL)
			subscriptionURL = self.b64decode(b64subscriptionURL)
			fontID = self.b64decode(b64fontID)

			publisher = client.publisher(publisherURL)
			subscription = publisher.subscription(subscriptionURL)
			api = subscription.latestVersion()

			success, message = subscription.removeFont(fontID)

			if success == False:
				return success, message, b64publisherURL


		return True, None, b64publisherURL


	def removeFonts_consumer(self, delayedResult):

		success, message, b64publisherURL = delayedResult.get()

		if success:

			pass

		else:

			if type(message) in (str, str):
				self.errorMessage(message)
			else:
				self.errorMessage('Server: %s' % message.getText(client.locale()))

		self.setSideBarHTML()
		self.setBadges()
		self.setPublisherHTML(b64publisherURL)


	def onContextMenu(self, x, y, target, b64ID):
#       print x, y, target, b64ID, self.b64decode(b64ID)

		x = max(0, int(x) - 70)

		if 'contextmenu publisher' in target:

			for publisher in client.publishers():
				if publisher.canonicalURL == self.b64decode(b64ID):
					break

			menu = wx.Menu()

			item = wx.MenuItem(menu, wx.NewId(), self.localizeString('#(Update All Subscriptions)'))
			menu.Append(item)
			menu.Bind(wx.EVT_MENU, partial(self.reloadPublisher, b64ID = b64ID), item)

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
			menu.Bind(wx.EVT_MENU, partial(self.reloadSubscription, b64ID = b64ID, subscription = None), item)

			for publisher in client.publishers():
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

			for publisher in client.publishers():
				for subscription in publisher.subscriptions():
					for foundry in subscription.foundries():
						for family in foundry.families():
							for font in family.fonts():
								if font.uniqueID == fontID:

									if font.installedVersion():
										item = wx.MenuItem(menu, wx.NewId(), self.localizeString('#(Show in Finder)'))
										menu.Bind(wx.EVT_MENU, partial(self.showFontInFinder, subscription = subscription, fontID = fontID), item)
										menu.Append(item)

									# create a submenu
									subMenu = wx.Menu()
									menu.AppendMenu(wx.NewId(), self.localizeString('#(Install Version)'), subMenu)

									for version in font.getVersions():

										if font.installedVersion() == version.number:
											item = wx.MenuItem(subMenu, wx.NewId(), str(version.number), "", wx.ITEM_RADIO)

										else:
											item = wx.MenuItem(subMenu, wx.NewId(), str(version.number))

										if WIN:
											installHere = menu
										else:
											installHere = subMenu
										installHere.Bind(wx.EVT_MENU, partial(self.installFontFromMenu, b64publisherURL = self.b64encode(publisher.canonicalURL), b64subscriptionURL = self.b64encode(subscription.url), b64fontID = b64ID, version = version.number), item)
										subMenu.Append(item)


#    def installFontFromMenu(self, event, b64publisherURL, b64subscriptionURL, b64fontID, version):

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



	def showPublisherPreferences(self, event, b64ID):

		for publisher in client.publishers():
			if publisher.exists and publisher.canonicalURL == self.b64decode(b64ID):


				html = []


				html.append('<h2>%s (%s)</h2>' % (publisher.name(client.locale())[0], publisher.get('type')))
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


	def showPublisherInFinder(self, evt, b64ID):
		
		publisher = client.publisher(self.b64decode(b64ID))
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

		# print('reloadPublisher()')

		client.prepareUpdate()

		publisher = client.publisher(self.b64decode(b64ID))
		for subscription in publisher.subscriptions():
			if subscription.exists:
				self.reloadSubscription(None, None, subscription)


	def autoReloadSubscriptions(self):

		if WIN:
			path = os.path.expanduser('~/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Type.World.lnk')
			if os.path.exists(path):
				os.remove(path)

		# Preference is set to check automatically
		if int(client.preferences.get('reloadSubscriptionsInterval')) != -1:

			# Has never been checked, set to long time ago
			if not client.preferences.get('reloadSubscriptionsLastPerformed'):
				client.preferences.set('reloadSubscriptionsLastPerformed', int(time.time()) - int(client.preferences.get('reloadSubscriptionsInterval')) - 10)

			# See if we should check now
			if int(client.preferences.get('reloadSubscriptionsLastPerformed')) < int(time.time()) - int(client.preferences.get('reloadSubscriptionsInterval')):

				self.log('Automatically reloading subscriptions...')

				client.prepareUpdate()

				for publisher in client.publishers():
					for subscription in publisher.subscriptions():
						self.reloadSubscription(None, None, subscription)

		agent('amountOutdatedFonts %s' % client.amountOutdatedFonts())


	def reloadSubscription(self, evt, b64ID, subscription = None):



		if subscription:
			pass
		else:

			ID = self.b64decode(b64ID)

			for publisher in client.publishers():
				subscription = publisher.subscription(ID)
				if subscription and subscription.exists:
					break


		if subscription:

			b64publisherID = self.b64encode(subscription.parent.canonicalURL)
			b64subscriptionID = self.b64encode(subscription.url)

			self.log('reloadSubscription(%s, %s, %s)' % (subscription.parent.canonicalURL, subscription.url, subscription.name()))

#            self.javaScript("startAnimation();")

			# Publisher
			self.javaScript("$('#sidebar #%s.publisher .reloadAnimation').show();" % b64publisherID)
			self.javaScript("$('#sidebar #%s.publisher .badges').hide();" % b64publisherID)

			# Subscription
			self.javaScript("$('#sidebar #%s.subscription .reloadAnimation').show();" % b64subscriptionID)
			self.javaScript("$('#sidebar #%s.subscription .badges').hide();" % b64subscriptionID)

			startWorker(self.reloadSubscription_consumer, self.reloadSubscription_worker, wargs=(subscription, ))




	def reloadSubscription_worker(self, subscription):

		success, message = subscription.update()
		return success, message, subscription


	def reloadSubscription_consumer(self, delayedResult):
		success, message, subscription = delayedResult.get()
		b64publisherID = self.b64encode(subscription.parent.canonicalURL)

		if success:
			if client.preferences.get('currentPublisher') == subscription.parent.canonicalURL:
				self.setPublisherHTML(self.b64encode(subscription.parent.canonicalURL))
			self.setSideBarHTML()
			# self.javaScript("$('#sidebar #%s').addClass('selected');" % b64publisherID)
			# self.javaScript("$('#sidebar #%s').addClass('selected');" % self.b64encode(subscription.url))
			
		# Show alert
		if subscription.updatingProblem():
			self.javaScript("$('#sidebar #%s .alert').show();" % b64publisherID)
			self.javaScript("$('#sidebar #%s .alert ').show();" % self.b64encode(subscription.url))
		# Hide alert
		else:
			self.javaScript("$('#sidebar #%s .alert').hide();" % b64publisherID)
			self.javaScript("$('#sidebar #%s .alert').hide();" % self.b64encode(subscription.url))

		# Subscription
		self.javaScript("$('#sidebar #%s.subscription .reloadAnimation').hide();" % (self.b64encode(subscription.url)))
		self.javaScript("$('#sidebar #%s.subscription .badges').show();" % (self.b64encode(subscription.url)))

		if subscription.parent.stillUpdating() == False:
			# Publisher
			self.javaScript("$('#sidebar #%s.publisher .reloadAnimation').hide();" % b64publisherID)
			self.javaScript("$('#sidebar #%s.publisher .badges').show();" % b64publisherID)
#            self.javaScript("stopAnimation();")

		if client.allSubscriptionsUpdated():
			client.preferences.set('reloadSubscriptionsLastPerformed', int(time.time()))
			self.log('Reset reloadSubscriptionsLastPerformed')

		agent('amountOutdatedFonts %s' % client.amountOutdatedFonts())


	def displayPublisherSidebarAlert(self, b64publisherID):
		publisher = client.publisher(self.b64decode(b64publisherID))

		for message in publisher.updatingProblem():
			self.errorMessage(message)        

	def displaySubscriptionSidebarAlert(self, b64subscriptionID):
		subscription = client.publisher(self.b64decode(b64subscriptionID))
		self.errorMessage(subscription.updatingProblem())        

	def errorMessage(self, message):

		if type(message) == typeWorld.api.base.MultiLanguageText:
			message = message.getText(locale = client.locale())

		dlg = wx.MessageDialog(self, message or 'No message defined', '', wx.ICON_ERROR)
		result = dlg.ShowModal()
		dlg.Destroy()


	def message(self, message):

		if type(message) == typeWorld.api.base.MultiLanguageText:
			message = message.getText(locale = client.locale())

		dlg = wx.MessageDialog(self, message or 'No message defined', '')
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

		publisher = client.publisher(publisherID)
		publisher.set('currentSubscription', repositoryID)
		self.setPublisherHTML(publisherB64ID)



	def setPublisherHTML(self, b64ID):

#       print b64ID

		ID = self.b64decode(b64ID)

		if client.preferences:
			client.preferences.set('currentPublisher', ID)

		html = []

		publisher = client.publisher(ID)
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
			html.append('<div class="name">%s</div>' % (foundry.name.getText(client.locale())))
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
				html.append(family.name.getText(client.locale()))
				html.append('</div>') # .left.name
				html.append('</div>') # .clear
				html.append('</div>') # .title


				for setName in family.setNames(client.locale()):
					for formatName in family.formatsForSetName(setName, client.locale()):

						fonts = []
						amountInstalled = 0
						for font in family.fonts():
							if font.setName.getText(client.locale()) == setName and font.format == formatName:
								fonts.append(font)
								if font.installedVersion():
									amountInstalled += 1

						completeSetName = ''
						if setName:
							completeSetName = setName + ', '
						completeSetName += typeWorld.api.base.FILEEXTENSIONNAMES[formatName]

						html.append('<div class="section" id="%s">' % completeSetName)

						html.append('<div class="title clear">')
						html.append('<div class="left">%s</div>' % completeSetName)

						if len(fonts) > 1:

							html.append('<div class="more right" style="padding-top: 5px;">')
							html.append('<img src="file://##htmlroot##/more_darker.svg" style="height: 8px; position: relative; top: 0px;">')
							html.append('</div>')

							html.append('<div class="installButtons right" style="padding-top: 5px;">')
							html.append('<div class="clear">')

							if amountInstalled < len(fonts):
								html.append('<div class="install installButton right">')
								html.append('<a href="x-python://self.installAllFonts(____%s____, ____%s____, ____%s____, ____%s____, ____%s____)" class="installAllFonts installButton button">' % (self.b64encode(ID), self.b64encode(subscription.url), self.b64encode(family.uniqueID), self.b64encode(setName) if setName else '', formatName))
								html.append('✓ #(Install All)')
								html.append('</a>')
								html.append('</div>') # .installButton

							if amountInstalled > 0:
								html.append('<div class="remove installButton right">')
								html.append('<a href="x-python://self.removeAllFonts(____%s____, ____%s____, ____%s____, ____%s____, ____%s____)" class="removeAllFonts removeButton button ">' % (self.b64encode(ID), self.b64encode(subscription.url), self.b64encode(family.uniqueID), self.b64encode(setName) if setName else '', formatName))
								html.append('✕ #(Remove All)')
								html.append('</a>')
								html.append('</div>') # .installButton

							html.append('</div>') # .clear
							html.append('</div>') # .installButtons

						html.append('</div>') # .title

						for font in fonts:
							html.append('<div class="contextmenu font" id="%s">' % self.b64encode(font.uniqueID))
							html.append('<div class="clear">')

							html.append('<div class="left" style="width: 50%;">')
							html.append(font.name.getText(client.locale()))
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
								html.append('<a href="x-python://self.installFont(____%s____, ____%s____, ____%s____, ____%s____)" class="installButton button">' % (self.b64encode(subscription.parent.canonicalURL), self.b64encode(subscription.url), self.b64encode(font.uniqueID), font.getVersions()[-1].number if font.getVersions() else ''))
								html.append('✓ #(Install)')
								html.append('</a>')
								html.append('</div>') # .right
								html.append('<div class="installButton remove right" style="display: %s;">' % ('block' if installedVersion else 'none'))
								html.append('<a href="x-python://self.removeFont(____%s____, ____%s____, ____%s____)" class="removeButton button">' % (self.b64encode(subscription.parent.canonicalURL), self.b64encode(subscription.url), self.b64encode(font.uniqueID)))
								html.append('✕ #(Remove)')
								html.append('</a>')
								html.append('</div>') # .right
								html.append('</div>') # .clear
								html.append('</div>') # .installButtons
								html.append('<div class="right">')
								html.append('<a class="status">')
								html.append('''<img src="file://##htmlroot##/loading.gif" style="height: 13px; position: relative; top: 2px;">''')
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
		self.javaScript("$('#sidebar .subscription').removeClass('selected');")
		self.javaScript("$('#sidebar #%s.publisher').addClass('selected');" % b64ID)
		self.javaScript("$('#sidebar #%s.subscription').addClass('selected');" % self.b64encode(subscription.url))
		self.javaScript("showMain();")

		agent('amountOutdatedFonts %s' % client.amountOutdatedFonts())

	def b64encode(self, string):

		b = str(string).encode()
		b64 = base64.b32encode(b)
		s = b64.decode()

		return s.replace('=', '-')

	def b64decode(self, string):

		b = str(string).replace('-', '=').encode()
		b64 = base64.b32decode(b)
		s = b64.decode()

		return s

	def setSideBarHTML(self):
		# Set publishers

		html = []

		# Sort
		# pass

		# Create HTML
		for publisher in client.publishers():

			b64ID = self.b64encode(publisher.canonicalURL)

			if publisher.subscriptions():
				name, language = publisher.name(locale = client.locale())


				if language in ('ar', 'he'):
					direction = 'rtl'
					if language in ('ar'):
						name = kashidaSentence(name, 20)
				else:
					direction = 'ltr'

				installedFonts = publisher.amountInstalledFonts()
				outdatedFonts = publisher.amountOutdatedFonts()
				selected = client.preferences.get('currentPublisher') == publisher.canonicalURL

				_type = 'multiple' if len(publisher.subscriptions()) > 1 else 'single'

				html.append('<div class="publisherWrapper">')
#                html.append('<a class="publisher" href="x-python://self.setPublisherHTML(____%s____)">' % b64ID)
				html.append('<div id="%s" class="contextmenu publisher line clear %s %s" lang="%s" dir="%s">' % (b64ID, _type, 'selected' if selected else '', language, direction))
				html.append('<div class="name">')
				html.append('%s %s' % (name, '<img src="file://##htmlroot##/github.svg" style="position:relative; top: 3px; width:16px; height:16px;">' if publisher.get('type') == 'GitHub' else ''))
				html.append('</div>')
				html.append('<div class="reloadAnimation" style="display: none;">')
				html.append('<img src="file://##htmlroot##/reload.gif" style="position:relative; top: 2px; width:20px; height:20px;">')
				html.append('</div>')
				html.append('<div class="badges clear">')
				html.append('<div class="badge outdated" style="display: %s;">' % ('block' if outdatedFonts else 'none'))
				html.append('%s' % (outdatedFonts or ''))
				html.append('</div>')
				html.append('<div class="badge installed" style="display: %s;">' % ('block' if installedFonts else 'none'))
				html.append('%s' % (installedFonts or ''))
				html.append('</div>')
				html.append('</div>') # .badges
				html.append('<div class="alert" style="display: none;">')
				html.append('<a href="x-python://self.displayPublisherSidebarAlert(____%s____)">' % b64ID)
				html.append('⚠️')
				html.append('</a>')
				html.append('</div>') # .alert
				html.append('</div>') # publisher
#                html.append('</a>')

				html.append('<div class="subscriptions" style="display: %s;">' % ('block' if selected else 'none'))
				if len(publisher.subscriptions()) > 1:
					html.append('<div class="margin top"></div>')
					for subscription in publisher.subscriptions():

						amountInstalledFonts = subscription.amountInstalledFonts()
						amountOutdatedFonts = subscription.amountOutdatedFonts()
						selected = subscription.url == publisher.currentSubscription().url

						html.append('<div>')
#                        html.append('<a class="subscription" href="x-python://self.setActiveSubscription(____%s____, ____%s____)">' % (b64ID, self.b64encode(subscription.url)))
						html.append('<div class="contextmenu subscription line clear %s" lang="%s" dir="%s" id="%s" publisherID="%s">' % ('selected' if selected else '', 'en', 'ltr', self.b64encode(subscription.url), b64ID))
						html.append('<div class="name">')
						html.append(self.localizeString(subscription.name(locale=client.locale())))
						html.append('</div>')
						html.append('<div class="reloadAnimation" style="display: none;">')
						html.append('<img src="file://##htmlroot##/reload.gif" style="position:relative; top: 2px; width:20px; height:20px;">')
						html.append('</div>')
						html.append('<div class="badges clear">')
						html.append('<div class="badge outdated" style="display: %s;">' % ('block' if amountOutdatedFonts else 'none'))
						html.append('%s' % amountOutdatedFonts)
						html.append('</div>')
						html.append('<div class="badge installed" style="display: %s;">' % ('block' if amountInstalledFonts else 'none'))
						html.append('%s' % amountInstalledFonts)
						html.append('</div>')
						html.append('</div>') # .badges
						html.append('<div class="alert" style="display: none;">')
						html.append('<a href="x-python://self.displaySubscriptionSidebarAlert(____%s____)">' % self.b64encode(subscription.url))
						html.append('⚠️')
						html.append('</a>')
						html.append('</div>') # .alert
						html.append('</div>') # subscription
#                        html.append('</a>')
						html.append('</div>')
					html.append('<div class="margin bottom"></div>')
				html.append('</div>')

				html.append('</div>') # .publisherWrapper


#// :not(.selected)
		html.append('''<script>


	$("#sidebar div.publisher").click(function() {

		$("#sidebar div.subscriptions").slideUp();
		$(this).parent().children(".subscriptions").slideDown();

		$("#sidebar div.publisher").removeClass('selected');
		$(this).parent().children(".publisher").addClass('selected');

		python('self.setPublisherHTML(____' + $(this).attr('id') + '____)');

	});

	$("#sidebar div.subscription").click(function() {

		python('self.setActiveSubscription(____' + $(this).attr('publisherID') + '____, ____' + $(this).attr('id') + '____)');

	});


	$("#sidebar div.publisher .alert").click(function() {
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
#        self.log(html)
		js = '$("#publishers").html("' + html + '");'

		self.javaScript(js)


	def onLoad(self, event):


		self.log('MyApp.frame.onLoad()')
		self.fullyLoaded = True

		self.setSideBarHTML()


		# Open drawer for newly added publisher
		if self.justAddedPublisher:
			self.addSubscription(self.justAddedPublisher)
			self.justAddedPublisher = None


		if client.preferences.get('currentPublisher'):
			self.javaScript('$("#welcome").hide();')
			self.setPublisherHTML(self.b64encode(client.preferences.get('currentPublisher')))
		self.setBadges()

		if WIN:
			self.checkForURLInFile()

		for message in self.messages:
			self.message(message)

		# Ask to install agent
		seenDialogs = client.preferences.get('seenDialogs') or []
		if not 'installMenubarIcon' in seenDialogs:

			# Menu Bar is actually running, so don't do anything
			if not client.preferences.get('menuBarIcon'):
				dlg = wx.MessageDialog(None, self.localizeString("#(InstallMenubarIconQuestion)"), self.localizeString("#(ShowMenuBarIcon)"),wx.YES_NO | wx.ICON_QUESTION)
				result = dlg.ShowModal()
				if result == wx.ID_YES:
					installAgent()

			seenDialogs.append('installMenubarIcon')
			client.preferences.set('seenDialogs', seenDialogs)


	def checkForURLInFile(self):

		from appdirs import user_data_dir
		openURLFilePath = os.path.join(user_data_dir('Type.World', 'Type.World'), 'url.txt')

		if os.path.exists(openURLFilePath):
			urlFile = open(openURLFilePath, 'r')
			url = urlFile.read().strip()
			urlFile.close()


			if self.fullyLoaded:
				self.addSubscription(url)
			else:

				self.justAddedPublisher = url


			os.remove(openURLFilePath)


		return True



	def log(self, message):
		if MAC:
			from AppKit import NSLog
			NSLog('Type.World App: %s' % message)
		else:
			print(message)

	def setBadgeLabel(self, label):
		'''\
		Set dock icon badge
		'''
		label = str(label)
		if MAC and self._dockTile:
			self._dockTile.display()
			self._dockTile.setBadgeLabel_(label)

	def localize(self, key, html = False):
		string = locales.localize('world.type.guiapp', key, client.locale())
		if html:
			string = string.replace('\n', '<br />')
		return string

	def localizeString(self, string, html = False):
		string = locales.localizeString('world.type.guiapp', string, languages = client.locale(), html = html)
		return string

	def replaceHTML(self, html):

		path = os.path.join(os.path.dirname(__file__), 'htmlfiles')
		if WIN:
			path = path.replace('\\', '/')
			if path.startswith('//'):
				path = path[2:]
			# path = path.replace('Mac/', 'mac/')

		html = html.replace('##htmlroot##', path)
		return html

	def setBadges(self):
		amount = 0
		for publisher in client.publishers():
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
		self.log(string)




	def pywinsparkle_no_update_found(self):
		""" when no update has been found, close the updater"""
		print("No update found")
		print("Setting flag to shutdown PassagesUpdater")


	def pywinsparkle_found_update(self):
		""" log that an update was found """
		print("New Update Available")


	def pywinsparkle_encountered_error(self):
		print("An error occurred")


	def pywinsparkle_update_cancelled(self):
		""" when the update was cancelled, close the updater"""
		print("Update was cancelled")
		print("Setting flag to shutdown PassagesUpdater")


	def pywinsparkle_shutdown(self):
		""" The installer is being launched signal the updater to shutdown """

		# actually shutdown the app here
		print("Safe to shutdown before installing")

	def setup_pywinsparkle(self):

		# register callbacks
		pywinsparkle.win_sparkle_set_did_find_update_callback(self.pywinsparkle_found_update)
		pywinsparkle.win_sparkle_set_error_callback(self.pywinsparkle_encountered_error)
		pywinsparkle.win_sparkle_set_update_cancelled_callback(self.pywinsparkle_update_cancelled)
		pywinsparkle.win_sparkle_set_did_not_find_update_callback(self.pywinsparkle_no_update_found)
		pywinsparkle.win_sparkle_set_shutdown_request_callback(self.pywinsparkle_shutdown)

		# set application details
		update_url = "https://type.world/downloads/guiapp/appcast_windows.xml"
		pywinsparkle.win_sparkle_set_appcast_url(update_url)
		pywinsparkle.win_sparkle_set_app_details("Type.World", "Type.World", APPVERSION)

		# initialize
		pywinsparkle.win_sparkle_init()

		# # check for updates
		# pywinsparkle.win_sparkle_check_update_with_ui()

		# # alternatively you could check for updates in the
		# # background silently
		# pywinsparkle.win_sparkle_check_update_without_ui()





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
			self.frame.addSubscription(url)
		else:
			self.frame.justAddedPublisher = url

		self.frame.Show()


	def OnInit(self):


		if WIN:
			import winreg as wreg
			current_file = __file__
			key = wreg.CreateKey(wreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Internet Explorer\\Main\\FeatureControl\\FEATURE_BROWSER_EMULATION")
			wreg.SetValueEx(key, current_file, 0, wreg.REG_DWORD, 11001)


		frame = AppFrame(None)
		self.frame = frame

		self.frame.log('MyApp.OnInit()')
		
		if MAC:
			from AppKit import NSApp
			self.frame.nsapp = NSApp()
			self.frame._dockTile = self.frame.nsapp.dockTile()


		html = ReadFromFile(os.path.join(os.path.dirname(__file__), 'htmlfiles', 'main', 'index.html'))

#        html = html.replace('##jqueryuicss##', ReadFromFile(os.path.join(os.path.dirname(__file__), 'htmlfiles', 'main', 'css', 'jquery-ui.css')))
		html = html.replace('APPVERSION', APPVERSION)

		html = frame.localizeString(html, html = True)
		html = frame.replaceHTML(html)


		# memoryfs = wx.MemoryFSHandler()
		# wx.FileSystem.AddHandler(memoryfs)
		# wx.MemoryFSHandler.AddFileWithMimeType("index.htm", html, 'text/html')
		# frame.html.RegisterHandler(wx.html2.WebViewFSHandler("memory"))

#        frame.html.SetPage(html, os.path.join(os.path.dirname(__file__), 'htmlfiles', 'main'))
		# frame.html.SetPage(html, '')
		# frame.html.Reload()

		filename = os.path.join(prefDir, 'world.type.guiapp.app.html')
		WriteToFile(filename, html)
		frame.html.LoadURL("file://%s" % filename)

		#TODO: Remove later, old implementation
		filename = os.path.join(os.path.dirname(__file__), 'app.html')
		if os.path.exists(filename):
			os.remove(filename)


		# if os.path.exists(openURLFilePath):
		#     urlFile = open(openURLFilePath, 'r')
		#     URL = urlFile.read().strip()
		#     urlFile.close()
		#     frame.justAddedPublisher = URL



		frame.Show()
		frame.CentreOnScreen()

		# if MAC:

		# 	from AppKit import NSObject, NSDistributedNotificationCenter
		# 	class darkModeDelegate(NSObject):
		# 		def darkModeChanged_(self, sender):
		# 			print('darkmodeChanged', sender)

		# 	delegate = darkModeDelegate.alloc().init()

		# 	NSDistributedNotificationCenter.defaultCenter().addObserver_selector_name_object_(delegate, delegate.darkModeChanged_, 'AppleInterfaceThemeChangedNotification', None)




		return True

#class MyNSApp(NSApp):


def listenerFunction():
	from multiprocessing.connection import Listener

	address = ('localhost', 65500)
	listener = Listener(address)

	while True:
		conn = listener.accept()
		command = conn.recv()
		commands = command.split(' ')

		if command == 'closeListener':
			conn.close()
			listener.close()
			break

		if commands[0] in intercomCommands:
			conn.send(intercom(commands))

		conn.close()

	listener.close()

	log('Closed listener loop')


intercomCommands = ['amountOutdatedFonts', 'startListener', 'killAgent', 'restartAgent', 'uninstallAgent']



def intercom(commands):

	log('intercom %s' % commands[0])

	if commands[0] == 'amountOutdatedFonts':

		totalSuccess = False

		force = (len(commands) > 1 and commands[1] == 'force')


		# Preference is set to check automatically
		if (client.preferences.get('reloadSubscriptionsInterval') and int(client.preferences.get('reloadSubscriptionsInterval')) != -1) or force:


			# Has never been checked, set to long time ago
			if not client.preferences.get('reloadSubscriptionsLastPerformed'):
				client.preferences.set('reloadSubscriptionsLastPerformed', int(time.time()) - int(client.preferences.get('reloadSubscriptionsInterval')) - 10)

			# See if we should check now
			if int(client.preferences.get('reloadSubscriptionsLastPerformed')) < int(time.time()) - int(client.preferences.get('reloadSubscriptionsInterval')) or force:

				log('now checking')

				client.prepareUpdate()

				for publisher in client.publishers():
					for subscription in publisher.subscriptions():

						startTime = time.time()
						success, message = subscription.update()

						totalSuccess = totalSuccess and success   

						if not success:
							log(message)

						log('updated %s (%1.2fs)' % (subscription, time.time() - startTime))

				# Reset
				if client.allSubscriptionsUpdated():
					log('resetting timing')
					client.preferences.set('reloadSubscriptionsLastPerformed', int(time.time()))


		log('client.amountOutdatedFonts() %s' % (client.amountOutdatedFonts()))
		return client.amountOutdatedFonts()


	if commands[0] == 'startListener':

		log('about to start listener thread')

		listenerThread = Thread(target=listenerFunction)
		listenerThread.start()

		log('listener thread started')

	if commands[0] == 'killAgent':

		agent('quit')

	if commands[0] == 'uninstallAgent':

		uninstallAgent()

	if commands[0] == 'restartAgent':

		agent('quit')

		# Restart after restart
		if client.preferences.get('menuBarIcon') and not agentIsRunning():

			file_path = os.path.join(os.path.dirname(__file__), r'TypeWorld Taskbar Agent.exe')
			file_path = file_path.replace(r'\\Mac\Home', r'Z:')
			import subprocess
			os.chdir(os.path.dirname(file_path))
			subprocess.Popen([file_path], executable = file_path)


# Set up logging
if WIN and DEBUG:
	filename = os.path.join(prefDir, os.path.basename(__file__) + '.txt')
	if os.path.exists(filename):
		os.remove(filename)
	logging.basicConfig(filename=filename,level=logging.DEBUG)

def log(message):
	if WIN and DEBUG:
		logging.debug(message)

log(sys.argv)

if len(sys.argv) > 1 and sys.argv[1] in intercomCommands:


	# Output to STDOUT
	print(intercom(sys.argv[1:]))

	sys.exit(0)

else:

	# Prevent second start

	if WIN:

		pid = PID('TypeWorld.exe')

		if pid:

			from pywinauto import Application
			try:
				app = Application().connect(process = pid)
				app.top_window().set_focus()

			except:
				pass

			sys.exit(1)

	listenerThread = Thread(target=listenerFunction)
	listenerThread.start()


	app = MyApp(redirect = DEBUG and WIN and RUNTIME, filename = None)
	app.MainLoop()
