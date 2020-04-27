#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os, sys

# Adjust __file__ for Windows executable
try:
	__file__ = os.path.abspath(__file__)

except:
	__file__ = sys.executable

sys.path.insert(0, os.path.dirname(__file__))

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

import wx, webbrowser, urllib.request, urllib.parse, urllib.error, base64, plistlib, json, datetime, traceback, semver, platform, logging
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
from string import Template

WIN = platform.system() == 'Windows'
MAC = platform.system() == 'Darwin'

from ynlib.files import ReadFromFile, WriteToFile
from ynlib.strings import *
from ynlib.web import GetHTTP
from ynlib.colors import Color

from typeWorld.client import APIClient, JSON, AppKitNSUserDefaults, TypeWorldClientDelegate
import typeWorld.api

APPNAME = 'Type.World'
APPVERSION = 'n/a'
DEBUG = True
BUILDSTAGE = 'alpha'
PULLSERVERUPDATEINTERVAL = 60

global app
app = None





if MAC:
	import objc
	from AppKit import NSString, NSUTF8StringEncoding, NSApplication, NSApp, NSObject, NSUserNotification, NSUserNotificationCenter, NSDistributedNotificationCenter, NSNotification
	from AppKit import NSView, NSRect, NSPoint, NSSize, NSMakeRect, NSColor, NSRectFill, NSToolbar
	from AppKit import NSRunningApplication
	from AppKit import NSScreen
	from AppKit import NSUserDefaults

	NSUserNotificationCenterDelegate = objc.protocolNamed('NSUserNotificationCenterDelegate')
	class NotificationDelegate(NSObject, protocols=[NSUserNotificationCenterDelegate]):

		def userNotificationCenter_didActivateNotification_(self, center, aNotification):
			pass

	userNotificationCenter = NSUserNotificationCenter.defaultUserNotificationCenter()
	userNotificationCenterDelegate = NotificationDelegate.alloc().init()
	userNotificationCenter.setDelegate_(userNotificationCenterDelegate)

	# Dark Mode
	class DarkModeDelegate(NSObject):
		def darkModeChanged_(self, sender):
			self.app.applyDarkMode()


if WIN:
	from appdirs import user_data_dir
	prefDir = user_data_dir('Type.World', 'Type.World')
elif MAC:
	prefDir = os.path.expanduser('~/Library/Preferences/')


# Set up logging
if WIN and DEBUG:
	filename = os.path.join(prefDir, os.path.basename(__file__) + '.txt')
	if os.path.exists(filename):
		os.remove(filename)
	logging.basicConfig(filename=filename,level=logging.DEBUG)


def log(message):
	# print('log(): %s' % message)
	if DEBUG:
		if WIN:
			logging.debug(message)
		if MAC:
			from AppKit import NSLog
			NSLog(f'Type.World App: {message}')



# print ('__file__', __file__)
# print ('sys.executable ', sys.executable )

try:

	## Windows:
	## Register Custom Protocol Handlers in the Registry. TODO: Later, this should be moved into the installer.

	if WIN and RUNTIME:
		try:
			import winreg as wreg
			for handler in ['typeworld', 'typeworldapp']:
				key = wreg.CreateKey(wreg.HKEY_CLASSES_ROOT, handler)
				wreg.SetValueEx(key, None, 0, wreg.REG_SZ, 'URL:%s' % handler)
				wreg.SetValueEx(key, 'URL Protocol', 0, wreg.REG_SZ, '')
				key = wreg.CreateKey(key, 'shell\\open\\command')
				wreg.SetValueEx(key, None, 0, wreg.REG_SZ, '"%s" "%%1"' % os.path.join(os.path.dirname(__file__), 'TypeWorld Subscription Opener.exe'))
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
			notificationCenter.deliverNotification_(notification)

		if WIN:

			import zroya
			zroya.init("Type.World", "Type.World", "Type.World", "guiapp", "Version")
			template = zroya.Template(zroya.TemplateType.ImageAndText4)
			template.setFirstLine(title)
			template.setSecondLine(text)
			expiration = 24 * 60 * 60 * 1000 # one day
			template.setExpiration(expiration) # One day
			notificationID = zroya.show(template) # , on_action=onAction

	def subscriptionsUpdatedNotification(message):
		if type(message) == int:
			if message > 0:
				notification(localizeString('#(Subscriptions added)'), localizeString('#(SubscriptionAddedLongText)', replace = {'number': abs(message)}))
			if message < 0:
				notification(localizeString('#(Subscriptions removed)'), localizeString('#(SubscriptionRemovedLongText)', replace = {'number': abs(message)}))


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
				with open(os.path.join(os.path.dirname(__file__), '..', 'Info.plist'), 'rb') as f:
					plist = plistlib.load(f)
					APPVERSION = plist['CFBundleShortVersionString']
			except:
				pass

		elif WIN:
			APPVERSION = getFileProperties(__file__)['StringFileInfo']['ProductVersion'].strip()

			if len(APPVERSION.split('.')) == 4:
				APPVERSION = '.'.join(APPVERSION.split('.')[0:-1])

			APPVERSION += '-' + BUILDSTAGE


	if WIN:
		prefFile = os.path.join(prefDir, 'preferences.json')
		prefs = JSON(prefFile)
		# log('Preferences at %s' % prefFile)
	else:
		prefs = AppKitNSUserDefaults('world.type.clientapp' if DESIGNTIME else None)

	class ClientDelegate(TypeWorldClientDelegate):
		def fontWillInstall(self, font):
			# print('fontWillInstall', font)
			assert type(font) == typeWorld.api.Font

		def fontHasInstalled(self, success, message, font):
			# print('fontHasInstalled', success, message, font)
			assert type(font) == typeWorld.api.Font

		def fontWillUninstall(self, font):
			# print('fontWillUninstall', font)
			assert type(font) == typeWorld.api.Font

		def fontHasUninstalled(self, success, message, font):
			# print('fontHasUninstalled', success, message, font)
			assert type(font) == typeWorld.api.Font

		def subscriptionUpdateNotificationHasBeenReceived(self, subscription):
#			print('PULLED FROM SERVER: subscriptionHasUpdated(%s)' % subscription)
			assert type(subscription) == typeWorld.client.APISubscription
			self.app.frame.reloadSubscriptionFromClient(subscription)

		def userAccountUpdateNotificationHasBeenReceived(self):
			# print('userAccountUpdateNotificationHasBeenReceived()')
			self.app.frame.pullServerUpdates(force = True)

		def subscriptionWasDeleted(self, subscription):
			print('subscriptionWasDeleted(%s)' % subscription)
			self.app.frame.setSideBarHTML()

		def publisherWasDeleted(self, publisher):
			print('publisherWasDeleted(%s)' % publisher)
			if client.preferences.get('currentPublisher'):
				if not client.publishers():
					client.preferences.set('currentPublisher', '')
					print('currentPublisher reset')
			self.app.frame.setSideBarHTML()

		def subscriptionWasAdded(self, publisher, subscription):
			if not client.preferences.get('currentPublisher'):
				self.app.frame.setPublisherHTML(self.app.frame.b64encode(publisher.canonicalURL))

		def subscriptionWasUpdated(self, publisher, subscription):
			print('subscriptionWasUpdated', publisher, subscription)
			if client.preferences.get('currentPublisher') == publisher.canonicalURL and publisher.get('currentSubscription') == subscription.url:
				self.app.frame.setPublisherHTML(self.app.frame.b64encode(publisher.canonicalURL))

	delegate = ClientDelegate()
	client = APIClient(preferences = prefs, delegate = delegate, mode = 'gui', pubSubSubscriptions = True)


	class FoundryStyling(object):
		def __init__(self, foundry, theme):
			self.foundry = foundry
			self.theme = theme

			assert self.theme in ('light', 'dark')

			# Apply default colors
			colors = typeWorld.api.StylingDataType().exampleData()[self.theme]
			for key in colors:
				if 'Color' in key:
					setattr(self, key, Color(hex=colors[key]))

			# Apply custom colors
			if self.foundry.styling:
				if self.theme in self.foundry.styling:
					colors = self.foundry.styling[self.theme]
					for key in colors:
						if 'Color' in key:
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
				self.hoverColor = self.backgroundColor.lighten(.05)
				self.hoverButtonColor = self.hoverColor.lighten(.1)
				self.hoverButtonTextColor = self.hoverColor.lighten(.8)
				self.sectionTitleColor = self.backgroundColor.lighten(.4)
			else:
				self.hoverColor = self.backgroundColor.darken(.05)
				self.hoverButtonColor = self.hoverColor.darken(.1)
				self.hoverButtonTextColor = self.hoverColor.darken(.8)
				self.sectionTitleColor = self.backgroundColor.darken(.4)

			# Selection Hover Color
			if self.selectionColor.darkHalf():
				self.selectionHoverColor = self.selectionColor.lighten(.1)
				self.selectionInactiveTextColor = self.selectionColor.lighten(.3)
			else:
				self.selectionHoverColor = self.selectionColor.darken(.1)
				self.selectionInactiveTextColor = self.selectionColor.darken(.3)

			# Selection Button Color
			if self.selectionColor.darkHalf():
				self.selectionButtonColor = self.selectionHoverColor.lighten(.1)
				self.selectionButtonTextColor = self.selectionButtonColor.lighten(.8)
			else:
				self.selectionButtonColor = self.selectionHoverColor.darken(.1)
				self.selectionButtonTextColor = self.selectionButtonColor.darken(.8)

			# Inactive Button Color
			if self.backgroundColor.darkHalf():
				self.inactiveButtonColor = self.backgroundColor.lighten(.15)
				self.inactiveButtonTextColor = self.inactiveButtonColor.lighten(.2)
			else:
				self.inactiveButtonColor = self.backgroundColor.darken(.15)
				self.inactiveButtonTextColor = self.inactiveButtonColor.darken(.2)

			# Information View Inactive Button Color
			if self.informationViewBackgroundColor.darkHalf():
				self.informationViewInactiveButtonColor = self.informationViewBackgroundColor.lighten(.15)
				self.informationViewInactiveButtonTextColor = self.informationViewInactiveButtonColor.lighten(.2)
			else:
				self.informationViewInactiveButtonColor = self.informationViewBackgroundColor.darken(.15)
				self.informationViewInactiveButtonTextColor = self.informationViewInactiveButtonColor.darken(.2)

			if self.informationViewLinkColor.darkHalf():
				self.informationViewLinkColor_Darker = self.informationViewLinkColor.lighten(.15)
			else:
				self.informationViewLinkColor_Darker = self.informationViewLinkColor.darken(.15)


		def logo(self):

			if self.foundry.styling:
				if self.theme in self.foundry.styling:
					if 'logo' in self.foundry.styling[self.theme]:
						self.logoURL = self.foundry.styling[self.theme]['logo']

				# Fallback, take any
				if not self.logoURL:
					for themeName in self.foundry.styling:
						if 'logo' in self.foundry.styling[themeName]:
							self.logoURL = self.foundry.styling[themeName]['logo']

				return self.logoURL

		def foundryView(self, ID):

			tpl = Template('''<style>

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

					</style>''')

			r = {'ID': ID}
			for key in self.__dict__:
				if 'Color' in key:
					r[key] = getattr(self, key).hex

			css = tpl.safe_substitute(r)
			return css



		def informationView(self):

			tpl = Template('''<style>

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



</style>''')

# #metadataWrapper svg path {
# 	fill: #$informationViewLinkColor;
# }


			r = {}
			for key in self.__dict__:
				if 'Color' in key:
					r[key] = getattr(self, key).hex

			css = tpl.safe_substitute(r)
			return css


# ''' + str(self.selectionHoverColor.hex) + '''

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

			unlock()

			# import subprocess
			# subprocess.Popen(['"%s"' % os.path.join(agentPath, 'Contents', 'MacOS', 'Type.World Agent')])
	#

	def restartAgentWorker(wait):

		if wait:
			time.sleep(wait)
		uninstallAgent()
		installAgent()

		log('Agent restarted')

	def restartAgent(wait = 0):
		restartAgentThread = Thread(target = restartAgentWorker, args=(wait, ))
		restartAgentThread.start()


	def installAgent():

	#	uninstallAgent()

		if RUNTIME:


			try:
				if MAC:

					if not appIsRunning('world.type.agent'):


						lock()
						log('lock() from within installAgent()')

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
				#		os.system('"%s" &' % os.path.join(agentPath, 'Contents', 'MacOS', 'Type.World Agent'))

						launchAgentThread = Thread(target=waitToLaunchAgent)
						launchAgentThread.start()


				if WIN:

					if not appIsRunning('TypeWorld Taskbar Agent.exe'):

						lock()
						log('lock() from within installAgent()')


				#			file_path = os.path.join(os.path.dirname(__file__), r'TypeWorld Taskbar Agent.exe')
						file_path = os.path.join(os.path.dirname(__file__), r'TypeWorld Taskbar Agent.exe')
						file_path = file_path.replace(r'\\Mac\Home', 'Z:')
						log(file_path)

						import getpass
						USER_NAME = getpass.getuser()

						bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
						bat_command = 'start "" "%s"' % file_path

						from pathlib import Path
						log(Path(file_path).exists())
						log(os.path.exists(file_path))

						if not os.path.exists(os.path.dirname(bat_path)):
							os.makedirs(os.path.dirname(bat_path))
						with open(bat_path + '\\' + "TypeWorld.bat", "w+") as bat_file:
							bat_file.write(bat_command)

						import subprocess
						os.chdir(os.path.dirname(file_path))
						subprocess.Popen([file_path], executable = file_path)

				client.preferences.set('menuBarIcon', True)

				log('installAgent() done')

			except:
				log(traceback.format_exc())

				unlock()
				log('unlock() from within installAgent() after traceback')



	def uninstallAgent():

		lock()
		log('lock() from within uninstallAgent()')
		try:
			if MAC:

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

		except:
			log(traceback.format_exc())
		unlock()
		log('unlock() from within uninstallAgent()')


	def localizeString(string, html = False, replace = {}):
		string = locales.localizeString(string, languages = client.locale(), html = html)
		if replace:
			for key in replace:
				string = string.replace('%' + key + '%', str(replace[key]))

		if html:
			string = string.replace('\n', '')
			string = string.replace('<br /></p>', '</p>')
			string = string.replace('<p><br />', '<p>')
		return string



	# Sparkle Updating

	if MAC and RUNTIME:
		# URL to Appcast.xml, eg. https://yourserver.com/Appcast.xml
		APPCAST_URL = 'https://type.world/downloads/guiapp/appcast.xml'
		# Path to Sparkle's "Sparkle.framework" inside your app bundle

		if '.app' in os.path.dirname(__file__):
			SPARKLE_PATH = os.path.join(os.path.dirname(__file__), '..', 'Frameworks', 'Sparkle.framework')
		else:
			SPARKLE_PATH = '/Users/yanone/Code/Sparkle/Sparkle.framework'

		from objc import pathForFramework, loadBundle
		sparkle_path = pathForFramework(SPARKLE_PATH)
		objc_namespace = dict()
		loadBundle('Sparkle', objc_namespace, bundle_path=sparkle_path)

		sparkle = objc_namespace['SUUpdater'].sharedUpdater()
	#       sparkle.setAutomaticallyDownloadsUpdates_(True)
		# NSURL = objc_namespace['NSURL']
		# sparkle.setFeedURL_(NSURL.URLWithString_(APPCAST_URL))


		def waitForUpdateToFinish(app, updater, delegate):

			log('Waiting for update loop to finish')

			while updater.updateInProgress():
				time.sleep(1)

			log('Update loop finished')

			if delegate.downloadStarted == False:
				delegate.destroyIfRemotelyCalled()


		from AppKit import NSObject
		class SparkleUpdateDelegate(NSObject):

			def destroyIfRemotelyCalled(self):
				log('Quitting because app was called remotely for an update')
				global app
				if app.startWithCommand:
					if app.startWithCommand == 'checkForUpdateInformation':
						app.frame.Destroy()
						log('app.frame.Destroy()')

			def updater_didAbortWithError_(self, updater, error):
				log('sparkleUpdateDelegate.updater_didAbortWithError_()')
				log(error)
				self.destroyIfRemotelyCalled()

			def userDidCancelDownload_(self, updater):
				log('sparkleUpdateDelegate.userDidCancelDownload_()')
				self.destroyIfRemotelyCalled()

			def updater_didFindValidUpdate_(self, updater, appcastItem):

				self.updateFound = True
				self.downloadStarted = False

				global app
				waitForUpdateThread = Thread(target=waitForUpdateToFinish, args=(app, updater, self))
				waitForUpdateThread.start()

				log('sparkleUpdateDelegate.updater_didFindValidUpdate_() finished')


			def updaterDidNotFindUpdate_(self, updater):
				log('sparkleUpdateDelegate.updaterDidNotFindUpdate_()')
				self.updateFound = False
				self.destroyIfRemotelyCalled()

			# Not so important
			def updater_didFinishLoadingAppcast_(self, updater, appcast):
				log('sparkleUpdateDelegate.updater_didFinishLoadingAppcast_()')

			def bestValidUpdateInAppcast_forUpdater_(self, appcast, updater):
				log('sparkleUpdateDelegate.bestValidUpdateInAppcast_forUpdater_()')

			def bestValidUpdateInAppcast_forUpdater_(self, appcast, updater):
				log('sparkleUpdateDelegate.bestValidUpdateInAppcast_forUpdater_()')

			def updater_willDownloadUpdate_withRequest_(self, updater, appcast, request):
				self.downloadStarted = True
				log('sparkleUpdateDelegate.updater_willDownloadUpdate_withRequest_()')

			def updater_didDownloadUpdate_(self, updater, item):
				log('sparkleUpdateDelegate.updater_didDownloadUpdate_()')

			def updater_failedToDownloadUpdate_error_(self, updater, item, error):
				log('sparkleUpdateDelegate.updater_failedToDownloadUpdate_error_()')

			def updater_willExtractUpdate_(self, updater, item):
				log('sparkleUpdateDelegate.updater_willExtractUpdate_()')

			def updater_didExtractUpdate_(self, updater, item):
				log('sparkleUpdateDelegate.updater_didExtractUpdate_()')

			def updater_willInstallUpdate_(self, updater, item):
				log('sparkleUpdateDelegate.updater_willInstallUpdate_()')

			def updaterWillRelaunchApplication_(self, updater):
				log('sparkleUpdateDelegate.updater_willInstallUpdate_()')

			def updaterWillShowModalAlert_(self, updater):
				log('sparkleUpdateDelegate.updaterWillShowModalAlert_()')

			def updaterDidShowModalAlert_(self, updater):
				log('sparkleUpdateDelegate.updaterDidShowModalAlert_()')

		sparkleDelegate = SparkleUpdateDelegate.alloc().init()
		sparkle.setDelegate_(sparkleDelegate)


	if WIN:
		class SparkleUpdateDelegate(object):

			def __init__(self):
				self.updateInProgress = False

			def waitForUpdateToFinish(self):

				while self.updateInProgress:
					time.sleep(1)

				log('Update loop finished')

				self.destroyIfRemotelyCalled()

			def destroyIfRemotelyCalled(self):
				log('Quitting because app was called remotely for an update')

				# Do nothing here for Windows because we didn't create an app instance

			def pywinsparkle_no_update_found(self):
				""" when no update has been found, close the updater"""
				log("No update found")
				self.updateInProgress = False


			def pywinsparkle_found_update(self):
				""" log that an update was found """
				log("New Update Available")
				# self.updateInProgress = False


			def pywinsparkle_encountered_error(self):
				log("An error occurred")
				self.updateInProgress = False
				self.destroyIfRemotelyCalled()


			def pywinsparkle_update_cancelled(self):
				""" when the update was cancelled, close the updater"""
				log("Update was cancelled")
				self.updateInProgress = False

			def pywinsparkle_shutdown(self):
				""" The installer is being launched signal the updater to shutdown """
				# actually shutdown the app here
				log("Safe to shutdown before installing")
				self.updateInProgress = False

			def check_with_ui(self):
				log("check_with_ui()")
				self.updateInProgress = True

				# waitForUpdateThread = Thread(target=self.waitForUpdateToFinish)
				# waitForUpdateThread.start()

				pywinsparkle.win_sparkle_check_update_with_ui()

				self.waitForUpdateToFinish()

			def check_without_ui(self):
				log("check_without_ui()")
				self.updateInProgress = True

				# waitForUpdateThread = Thread(target=self.waitForUpdateToFinish)
				# waitForUpdateThread.start()

				pywinsparkle.win_sparkle_check_update_without_ui()

				self.waitForUpdateToFinish()

			def setup(self):

				# register callbacks
				pywinsparkle.win_sparkle_set_did_find_update_callback(self.pywinsparkle_found_update)
				pywinsparkle.win_sparkle_set_did_not_find_update_callback(self.pywinsparkle_no_update_found)
				pywinsparkle.win_sparkle_set_error_callback(self.pywinsparkle_encountered_error)
				pywinsparkle.win_sparkle_set_update_cancelled_callback(self.pywinsparkle_update_cancelled)
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

	if WIN:
		sys._MEIPASS = os.path.join(os.path.dirname(__file__), 'lib', 'pywinsparkle', 'libs', 'x64')
		from pywinsparkle import pywinsparkle

		pywinsparkleDelegate = SparkleUpdateDelegate()
		pywinsparkleDelegate.setup()





	class AppFrame(wx.Frame):
		def __init__(self, parent):        



			self.messages = []
			self.active = True

			self.allowedToPullServerUpdates = True
			self.allowCheckForURLInFile = True

			self.delegate = delegate
			self.delegate.parent = self




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

			# This should be unnecessary, but let's keep it here. More resilience.
			if client.preferences.get('currentPublisher') == 'pendingInvitations' and not client.preferences.get('pendingInvitations'):
				client.preferences.set('currentPublisher', '')

			if client.preferences.get('currentPublisher') == 'None':
				client.preferences.set('currentPublisher', '')

			if not client.preferences.get('currentPublisher') and len(client.publishers()) >= 1:
				client.preferences.set('currentPublisher', client.publishers()[0].canonicalURL)



			self.thread = threading.current_thread()


			self.justAddedPublisher = None
			self.fullyLoaded = False
			self.panelVisible = False



			# Window Size
			minSize = [1100, 700]
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

			self.Bind(wx.EVT_LEFT_DOWN, self.onMouseDown)

			### Menus
			self.setMenuBar()
			self.CentreOnScreen()
			self.Show()


			# Restart agent after restart
			if client.preferences.get('menuBarIcon') and not agentIsRunning():
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

				self.log('Received SIGTERM or SIGINT')

				self.onQuit(None)

			# if MAC:
			# 	signal.signal(signal.SIGBREAK, exit_signal_handler)
			signal.signal(signal.SIGTERM, exit_signal_handler)
			signal.signal(signal.SIGINT, exit_signal_handler)



			log('AppFrame.__init__() finished')

		def onMouseDown(self, event):
			# print(event)
			pass


		def setMenuBar(self):
			menuBar = wx.MenuBar()

			# Exit
			menu = wx.Menu()
			m_opensubscription = menu.Append(wx.ID_OPEN, "%s...%s" % (localizeString('#(Add Subscription)'), '\tCtrl+O'))#\tCtrl-O
			self.Bind(wx.EVT_MENU, self.showAddSubscription, m_opensubscription)
	#        m_opensubscription.SetAccel(wx.AcceleratorEntry(wx.ACCEL_CTRL,  ord('o')))


			m_CheckForUpdates = menu.Append(wx.NewIdRef(count=1), "%s..." % (localizeString('#(Check for App Updates)')))
			self.Bind(wx.EVT_MENU, self.onCheckForUpdates, m_CheckForUpdates)
			if MAC:
				m_closewindow = menu.Append(wx.ID_CLOSE, "%s\tCtrl+W" % (localizeString('#(Close Window)')))
				self.Bind(wx.EVT_MENU, self.onClose, m_closewindow)
			m_exit = menu.Append(wx.ID_EXIT, "%s\t%s" % (localizeString('#(Exit)'), 'Ctrl-Q' if MAC else 'Alt-F4'))
			self.Bind(wx.EVT_MENU, self.onQuit, m_exit)

			# m_InstallAgent = menu.Append(wx.NewIdRef(count=1), "Install Agent")
			# self.Bind(wx.EVT_MENU, self.installAgent, m_InstallAgent)
			# m_RemoveAgent = menu.Append(wx.NewIdRef(count=1), "Remove Agent")
			# self.Bind(wx.EVT_MENU, self.uninstallAgent, m_RemoveAgent)

			menuBar.Append(menu, "&%s" % (localizeString('#(File)')))

			# Edit
			# if 'wxMac' in wx.PlatformInfo and wx.VERSION >= (3,0):
			#   wx.ID_COPY = wx.NewIdRef(count=1)
			#   wx.ID_PASTE = wx.NewIdRef(count=1)
			editMenu = wx.Menu()
			editMenu.Append(wx.ID_UNDO, "%s\tCtrl-Z" % (localizeString('#(Undo)')))
			editMenu.AppendSeparator()
			editMenu.Append(wx.ID_SELECTALL, "%s\tCtrl-A" % (localizeString('#(Select All)')))
			editMenu.Append(wx.ID_COPY, "%s\tCtrl-C" % (localizeString('#(Copy)')))
			editMenu.Append(wx.ID_CUT, "%s\tCtrl-X" % (localizeString('#(Cut)')))
			editMenu.Append(wx.ID_PASTE, "%s\tCtrl-V" % (localizeString('#(Paste)')))

			if WIN:

				editMenu.AppendSeparator()

				m_prefs = editMenu.Append(wx.ID_PREFERENCES, "&%s\tCtrl-I" % (localizeString('#(Preferences)')))
				self.Bind(wx.EVT_MENU, self.onPreferences, m_prefs)




			menuBar.Append(editMenu, "&%s" % (localizeString('#(Edit)')))

			menu = wx.Menu()
			m_about = menu.Append(wx.ID_ABOUT, "&%s %s" % (localizeString('#(About)'), APPNAME))
			self.Bind(wx.EVT_MENU, self.onAbout, m_about)

			if MAC:

				m_prefs = menu.Append(wx.ID_PREFERENCES, "&%s\tCtrl-," % (localizeString('#(Preferences)')))
				self.Bind(wx.EVT_MENU, self.onPreferences, m_prefs)        

			# menuBar.Append(menu, "Type.World")
			menuBar.Append(menu, "&%s" % (localizeString('#(Help)')))

			self.SetMenuBar(menuBar)



		def javaScript(self, script):
			if self.fullyLoaded:
				if threading.current_thread() == self.thread:
					# log('JavaScript Executed:')
					# log(str(script)[:100])
					self.html.RunScript(script)
				else:
					log('JavaScript called from another thread: %s' % script[:100])
#					log(str(script.encode())[:100], '...')



			else:
				pass
	#            log('JavaScript Execution: Page not fully loaded:')
	#            log(str(script.encode())[:100], '...')




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
				sparkle.checkForUpdates_(self)
				# sparkle.checkForUpdateInformation()
			elif WIN:
				pywinsparkleDelegate.check_with_ui()

		def onClose(self, event):

			# print('onClose()')

			if self.panelVisible:
				self.javaScript('hidePanel();')
			else:


				self.onQuit(event)


		def onQuit(self, event):


			expiringInstalledFonts = client.expiringInstalledFonts()

			if expiringInstalledFonts:

				dlg = wx.MessageDialog(None, localizeString("You have installed %s font(s) that are under active expiration. Quitting the app will remove these fonts. Do you want to continue?" % len(expiringInstalledFonts)), localizeString("Active expiration fonts"), wx.YES_NO | wx.ICON_QUESTION)
				dlg.SetYesNoLabels(localizeString('#(Remove and Quit)'), localizeString('#(Cancel)'))
				result = dlg.ShowModal()
				if result == wx.ID_YES:

					for font in expiringInstalledFonts:
						success, message = font.parent.parent.parent.parent.subscription.removeFont(font.uniqueID)
						if not success:
							self.errorMessage(message, 'Error deleting fonts')
							return

				else:
					return

			self.active = False

			# log('onQuit()')

			while locked():
				log('Waiting for locks to disappear')
				time.sleep(.5)

			try:
				log('send closeListener command to self')
				address = ('localhost', 65500)
				myConn = Client(address)
				myConn.send('closeListener')
				myConn.close()
				log('send closeListener command to self (finished)')
			except ConnectionRefusedError:
				pass

			if WIN:
				pywinsparkle.win_sparkle_cleanup()

			self.Destroy()


				


		def pullServerUpdates(self, force = False):


			if not client.preferences.get('lastServerSync') or client.preferences.get('lastServerSync') < time.time() - PULLSERVERUPDATEINTERVAL or force:
				if self.allowedToPullServerUpdates:
					startWorker(self.pullServerUpdates_consumer, self.pullServerUpdates_worker)


		def pullServerUpdates_worker(self):

			return client.downloadSubscriptions()


		def pullServerUpdates_consumer(self, delayedResult):

			success, message = delayedResult.get()

			# print(success, message)

			self.setSideBarHTML()
			if client.preferences.get('currentPublisher'):
				self.setPublisherHTML(self.b64encode(client.publisher(client.preferences.get('currentPublisher')).canonicalURL))
			self.setBadges()

			if success:
				subscriptionsUpdatedNotification(message)
				agent('amountOutdatedFonts %s' % client.amountOutdatedFonts())

				self.javaScript('$("#userWrapper .alert").hide();')
				self.javaScript('$("#userWrapper .noAlert").show();')

			else:

				self.javaScript('$("#userWrapper .alert").show();')
				self.javaScript('$("#userWrapper .noAlert").hide();')




		def onInactivate(self, event):

			if client.preferences.get('currentPublisher'):
				self.setPublisherHTML(self.b64encode(client.preferences.get('currentPublisher')))

		def onActivate(self, event):


			if self.active:
				self.log('onActivate()')

				# self.pullServerUpdates()

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

				if client.preferences.get('currentPublisher'):
					self.setPublisherHTML(self.b64encode(client.preferences.get('currentPublisher')))

				if WIN and self.allowCheckForURLInFile:
					self.checkForURLInFile()

				if MAC:

					self.applyDarkMode()

		def theme(self):
			if MAC:
				if NSUserDefaults.standardUserDefaults().objectForKey_('AppleInterfaceStyle') == 'Dark':
					return 'dark'
				else:
					return 'light'
			else:
				return 'light'


		def applyDarkMode(self):

			if platform.mac_ver()[0].split('.') > '10.14.0'.split('.'):
				
				if client.preferences.get('currentPublisher'):
					publisher = client.publisher(client.preferences.get('currentPublisher'))
					self.setPublisherHTML(self.b64encode(client.preferences.get('currentPublisher')))
					if publisher.get('currentSubscription'):
						subscription = publisher.subscription(publisher.get('currentSubscription'))
						if subscription.get('currentFont'):
							self.setMetadataHTML(self.b64encode(subscription.get('currentFont')))

				self.javaScript("$('body').removeClass('light');")
				self.javaScript("$('body').removeClass('dark');")
				self.javaScript("$('body').addClass('%s');" % self.theme())


		def onResize(self, event):

			size = self.GetSize()

			# self.javaScript("$('.panel').css('height', '%spx');" % (size[1]))

			if MAC:
				self.dragView.setFrameSize_(NSSize(self.GetSize()[0], 40))
			client.preferences.set('sizeMainWindow', (self.GetSize()[0], self.GetSize()[1]))
			event.Skip()


		def onAbout(self, event):

			html = []

			html.append('<p style="text-align: center; margin-bottom: 20px;">')
			html.append('<img src="file://##htmlroot##/icon.svg" style="width: 150px; height: 150px;"><br />')
			html.append('</p>')
			html.append('<p>')
			html.append('#(AboutText)')
			html.append('</p>')

			html.append('<p style="margin-bottom: 20px;">')
			html.append('#(We thank our Patrons):')
			html.append('<br />')
			patrons = json.loads(ReadFromFile(os.path.join(os.path.dirname(__file__), 'patrons', 'patrons.json')))
			html.append('<b>' + '</b>, <b>'.join([x.replace(' ', '&nbsp;') for x in patrons]) + '</b>')
			html.append('</p>')


			html.append('<p style="margin-bottom: 20px;">')
			html.append('#(Anonymous App ID): %s<br />' % client.anonymousAppID())
			html.append('#(Version) %s<br />' % APPVERSION)
			html.append('#(Version History) #(on) <a href="https://type.world/app">type.world/app</a>')
			html.append('</p>')
			# html.append(u'<p>')
			# html.append(u'<a class="button" onclick="python('self.sparkle.checkForUpdates_(None)');">#(Check for App Updates)</a>')
			# html.append(u'</p>')


			# Print HTML
			html = ''.join(map(str, html))
			html = self.replaceHTML(html)
			html = localizeString(html, html = True)
			html = html.replace('"', '\'')
			html = html.replace('\n', '')
			js = '$("#about .inner").html("' + html + '");'
			self.javaScript(js)

			self.javaScript('showAbout();')

		def resetDialogs(self):
			client.preferences.set('seenDialogs', [])


		def unlinkUserAccount(self):


			success, message = client.unlinkUser()

			if success:

				self.onPreferences(None, 'userAccount')
				if client.preferences.get('currentPublisher'):
					self.setPublisherHTML(self.b64encode(client.preferences.get('currentPublisher')))

			else:

				self.errorMessage(message)

			self.setSideBarHTML()


		def createUserAccount(self, name, email, password1, password2):

			success, message = client.createUserAccount(name, email, password1, password2)
			if not success:
				self.errorMessage(message)
			else:
				self.onPreferences(None, 'userAccount')


		def logIn(self, email, password):
			success, message = client.logInUserAccount(email, password)
			if not success:
				self.errorMessage(message)
			else:
				self.onPreferences(None, 'userAccount')


		def revokeAppInstance(self, anonymousAppID):

			dlg = wx.MessageDialog(self, localizeString('#(Are you sure)'), localizeString('#(Revoke App)'), wx.YES_NO | wx.ICON_QUESTION)
			dlg.SetYesNoLabels(localizeString('#(Revoke)'), localizeString('#(Cancel)'))
			result = dlg.ShowModal() == wx.ID_YES
			dlg.Destroy()
			
			if result:

				success, response = client.revokeAppInstance(anonymousAppID)
				if success:
					self.onPreferences(None, 'linkedApps')

				else:
					self.errorMessage(response, '#(Revoke App)')


		def reactivateAppInstance(self, anonymousAppID):

			dlg = wx.MessageDialog(self, localizeString('#(Are you sure)'), localizeString('#(Reactivate App)'), wx.YES_NO | wx.ICON_QUESTION)
			dlg.SetYesNoLabels(localizeString('#(Reactivate)'), localizeString('#(Cancel)'))
			result = dlg.ShowModal() == wx.ID_YES
			dlg.Destroy()
			
			if result:

				success, response = client.reactivateAppInstance(anonymousAppID)
				if success:
					self.onPreferences(None, 'linkedApps')

				else:
					self.errorMessage(response, '#(Reactivate App)')



		def onPreferences(self, event, section = 'generalPreferences'):


			html = []

			html.append('<div class="head">')


			html.append('<div class="tabs clear">')

			for keyword, title, condition in (
				('generalPreferences', localizeString('#(Preferences)'), True),
				('userAccount', localizeString('#(User Account)'), True),
				('linkedApps', localizeString('#(Linked Apps)'), client.user()),
				):

				if condition:
					html.append('<div class="tab %s">' % ('active' if section == keyword else ''))
					if keyword != section:
						html.append('<a href="x-python://self.onPreferences(None, ____%s____)">' % keyword)
					html.append(title)
					if keyword != section:
						html.append('</a>')
					html.append('</div>') # .tab

			html.append('</div>') # .tabs

			html.append('</div>')


			html.append('<div class="body inner">')


			if section == 'linkedApps':

				html.append('''<style>





					</style>''')

				
				success, instances = client.linkedAppInstances()
				if not success:
					html.append(instances)

				else:
					for instance in instances:
						html.append('<div class="appInstance clear" style="margin-bottom: 20px;">')

						# html.append(instance.anonymousAppID)
						# html.append('</div>') # .appInstance


						html.append('<div style="float: left; width: 100px; margin-left: 20px;">')

						image = instance.image
						if image:
							html.append(f'<img src="{os.path.join(os.path.dirname(__file__), "htmlfiles", "machineModels", image)}" style="width: 80px; margin-top: 10px;">')

						html.append('</div>')
						html.append('<div style="float: left; width: 350px;">') 

						html.append('<p>')

						html.append('<b>')
						html.append(instance.machineNodeName or instance.machineHumanReadableName or instance.anonymousAppID)
						html.append('</b>')
						if instance.anonymousAppID == client.anonymousAppID():
							html.append(' <i>(#(This app))</i>')
						html.append('<br />')

						if instance.machineModelIdentifier and instance.machineModelIdentifier.startswith('Parallels') or instance.machineHumanReadableName and instance.machineHumanReadableName.startswith('Parallels'):
							html.append('Parallels Desktop Virtual Machine')
							html.append('<br />')
						else:
							if instance.machineHumanReadableName:
								html.append(instance.machineHumanReadableName)
								html.append('<br />')
						if instance.machineSpecsDescription:
							html.append(instance.machineSpecsDescription)
							html.append('<br />')
						if instance.machineOSVersion:
							if instance.machineOSVersion.startswith('mac'):
								src = 'other/apple.svg'
							elif instance.machineOSVersion.startswith('Windows'):
								src = 'other/windows.svg'
							else:
								src = None
							if src:
								html.append(f'<img src="{os.path.join(os.path.dirname(__file__), "htmlfiles", "machineModels", src)}" style="width: 16px; position: relative; top: 3px; margin-right: 5px;">')
							html.append(instance.machineOSVersion)

						if instance.revoked:
							html.append('<br />')
							html.append('<div>')
							html.append('<span class_="box" style="background-color: orange; padding: 3px;">')
							html.append('#(Revoked): %s %s' % (locales.formatDate(instance.revokedTime, client.locale()), locales.formatTime(instance.revokedTime, client.locale())))
							html.append('</span>')
							html.append('</div>')

						else:
							if instance.lastUsed:
								if not instance.anonymousAppID == client.anonymousAppID():
									html.append('<br />')
									html.append('<span style="color: #888;">')
									html.append('#(Last active): %s %s' % (locales.formatDate(instance.lastUsed, client.locale()), locales.formatTime(instance.lastUsed, client.locale())))


								

								html.append('</span>')
						html.append('</p>')

						html.append('</div>')


						# Revoke/Activate
						html.append('<div style="float: left; margin-left: 50px;">')

						if not instance.anonymousAppID == client.anonymousAppID():
							if instance.revoked:
								html.append(f'<a class="button" href="x-python://self.reactivateAppInstance(____{instance.anonymousAppID}____)">#(Reactivate App)</a>')
							else:
								html.append(f'<a class="button" href="x-python://self.revokeAppInstance(____{instance.anonymousAppID}____)">#(Revoke App)</a>')
						html.append('</div>') # Revoke/Activate



						html.append('</div>') # .appInstance



			if section == 'userAccount':

				# User
				html.append('<h2>#(Type.World User Account)</h2>')
				if client.user():
					html.append('<p>')
					html.append('#(Linked User Account): ')
					if client.userName() and client.userEmail():
						html.append('<b>%s</b> (%s)' % (client.userName(), client.userEmail()))
					elif client.userEmail():
						html.append('<b>%s</b>' % (client.userEmail()))
					html.append('</p>')
					# html.append('<p>')
					# html.append('#(Account Last Synchronized): %s' % (NaturalRelativeWeekdayTimeAndDate(client.preferences.get('lastServerSync'), locale = client.locale()[0]) if client.preferences.get('lastServerSync') else 'Never'))
					# html.append('</p>')
					html.append('<h2>#(Unlink User Account)</h2>')
					html.append('<p>')
					html.append('#(UnlinkUserAccountExplanation)')
					html.append('</p>')
					html.append('<p>')
					html.append('<a id="unlinkAppButton" class="button">#(Unlink User Account)</a>')
					html.append('</p>')
				else:

	#				html.append('#(NoUserAccountLinked)<br />#(PleaseCreateUserAccountExplanation)')

					html.append('<div class="clear">')
					html.append('<div style="float: left; width: 47%; margin-right: 6%;">')

					html.append('<div>')
					html.append('<h4>#(Create Account)</h4>')
					html.append('#(Name)')
					html.append('<br />')
					html.append('<input type="text" name="createAccountUserName" id="createAccountUserName" placeholder="#(John Doe)">')
					html.append('<br />')
					html.append('#(Email Address)')
					html.append('<br />')
					html.append('<input type="text" name="createAccountUserEmail" id="createAccountUserEmail" placeholder="#(johndoe@gmail.com)">')
					html.append('<br />')
					html.append('#(Password)')
					html.append('<br />')
					html.append('<input type="password" name="createAccountUserPassword" id="createAccountUserPassword">')
					html.append('<br />')
					html.append('#(Repeat Password)')
					html.append('<br />')
					html.append('<input type="password" name="createAccountUserPassword2" id="createAccountUserPassword2">')
					html.append('</div>')

					html.append('<p>')
					html.append('<a id="createAccountButton" class="button">#(Create Account)</a>')
					html.append('</p>')
					html.append('''<script>$("#preferences #createAccountButton").click(function() {

					python("self.createUserAccount(____" + $("#preferences #createAccountUserName").val() + "____, ____" + $("#preferences #createAccountUserEmail").val() + "____, ____" + $("#preferences #createAccountUserPassword").val() + "____, ____" + $("#preferences #createAccountUserPassword2").val() + "____)");
					 
				});</script>''')

					html.append('</div>') # .floatleft
					html.append('<div style="float: left; width: 47%;">')

					html.append('<div>')
					html.append('<h4>#(Log In To Existing Account)</h4>')
					html.append('#(Email Address)')
					html.append('<br />')
					html.append('<input type="text" name="loginUserEmail" id="loginUserEmail" placeholder="#(johndoe@gmail.com)">')
					html.append('<br />')
					html.append('#(Password)')
					html.append('<br />')
					html.append('<input type="password" name="loginUserPassword" id="loginUserPassword">')
					html.append('</div>')

					html.append('<p>')
					html.append('<a id="loginButton" class="button">#(Log In)</a>')
					html.append('</p>')

					html.append('<p>')
					html.append('<a href="https://type.world/resetpassword">#(I Forgot My Password) ↗</a>')
					html.append('</p>')

					html.append('''<script>$("#preferences #loginButton").click(function() {

					python("self.logIn(____" + $("#preferences #loginUserEmail").val() + "____, ____" + $("#preferences #loginUserPassword").val() + "____)");
					 
				});</script>''')

					html.append('</div>') # .floatleft
					html.append('</div>') # .clear



				html.append('''<script>$("#preferences #unlinkAppButton").click(function() {

					python("self.unlinkUserAccount()");
					 
				});</script>''')






			if section == 'generalPreferences':

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
			# 	html.append('<option value="%s" %s>%s</option>' % (code, 'selected' if str(code) == str(client.preferences.get('reloadSubscriptionsInterval')) else '', name))
			# html.append('</select>')
			# html.append('<script>$("#preferences #updateIntervalChoice").click(function() {setPreference("reloadSubscriptionsInterval", $("#preferences #updateIntervalChoice").val());});</script>')
			# html.append('</p>')
			# html.append('<p>')
			# html.append('#(Last Check): %s' % NaturalRelativeWeekdayTimeAndDate(client.preferences.get('reloadSubscriptionsLastPerformed'), locale = client.locale()[0]))
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



				# html.append('<hr>')

				# Agent
				if WIN:
					html.append('<h2>#(Icon in Menu Bar.Windows)</h2>')
				if MAC:
					html.append('<h2>#(Icon in Menu Bar.Mac)</h2>')
				html.append('<p>')
				label = '#(Show Icon in Menu Bar' + ('.Windows' if WIN else '.Mac') + ')'
				html.append('<span><input id="menubar" type="checkbox" name="menubar" %s><label for="menubar">%s</label></span>' % ('checked' if agentIsRunning() else '', label))
				html.append('<script>$("#preferences #menubar").click(function() { if($("#preferences #menubar").prop("checked")) { python("installAgent()"); } else { setCursor("wait", 2000); python("uninstallAgent()"); } });</script>')
				html.append('</p>')
				html.append('<p>')
				html.append('#(IconInMenuBarExplanation)')
				html.append('</p>')

				html.append('<hr>')

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
				html.append('</p>')
				html.append('<p>')
				html.append('<span><input id="customLocale" value="customLocale" type="radio" name="localizationType" %s><label for="customLocale">Use Custom Language (choose below). Requires app restart to take full effect.</label></span>' % ('checked' if client.preferences.get('localizationType') == 'customLocale' else ''))
				html.append('<script>$("#preferences #customLocale").click(function() {setPreference("localizationType", "customLocale");});</script>')
				html.append('</p>')
				html.append('<p>')
				html.append('<select id="customLocaleChoice" style="" onchange="">')
				for code, name in locales.locales:
					html.append('<option value="%s" %s>%s</option>' % (code, 'selected' if code == client.preferences.get('customLocaleChoice') else '', name))
				html.append('</select>')
				html.append('''<script>$("#preferences #customLocaleChoice").click(function() {

					setPreference("customLocaleChoice", $("#preferences #customLocaleChoice").val());
					 
				});</script>''')
				html.append('</p>')

				html.append('<hr>')

				# Reset Dialogs
				html.append('<h2>#(Reset Dialogs)</h2>')
				html.append('<p>')
				html.append('<a id="resetDialogButton" class="button">#(ResetDialogsButton)</a>')
				html.append('</p>')
				html.append('''<script>$("#preferences #resetDialogButton").click(function() {

					python("self.resetDialogs()");
					 
				});</script>''')


			html.append('</div>') # .inner



			# Print HTML
			html = ''.join(map(str, html))
			html = html.replace('"', '\'')
			html = localizeString(html, html = True)
			html = html.replace('\n', '')
			# print(html)
			js = '$("#preferences .centerOuter").html("<div>' + html + '</div>");'
			self.javaScript(js)

			self.javaScript('showPreferences();')


		def setSubscriptionPreference(self, url, key, value):

			# print('setSubscriptionPreference()', url, key, value)

			for publisher in client.publishers():
				for subscription in publisher.subscriptions():
					if subscription.exists and subscription.protocol.unsecretURL() == url:

						if value == 'true':
							value = True
						if value == 'false':
							value = False

						subscription.set(key, value)

						self.setPublisherHTML(self.b64encode(publisher.canonicalURL))
						self.setSideBarHTML()

						break


		def showSubscriptionPreferences(self, event, b64ID):


			for publisher in client.publishers():
				for subscription in publisher.subscriptions():
					if subscription.exists and subscription.protocol.unsecretURL() == self.b64decode(b64ID):


						html = []

						html.append('<h2>#(Subscription)</h2>')
						html.append('<p>URL: <em>')
						html.append(subscription.protocol.unsecretURL()) # .replace('secretKey', '<span style="color: orange;">secretKey</span>')
						html.append('</em></p>')


						success, message = subscription.protocol.rootCommand()
						if success:
							rootCommand = message
						else:
							rootCommand = None


						success, message = subscription.protocol.installableFontsCommand()
						if success:
							command = message
						else:
							command = None

						userName = command.userName.getText(client.locale())
						userEmail = command.userEmail

						html.append('<p>')
						html.append('#(Provided by) ')
						if rootCommand.website:
							html.append('<a href="%s" title="%s">' % (rootCommand.website, rootCommand.website))
						html.append('<b>' + rootCommand.name.getText(client.locale()) + '</b>')
						if rootCommand.website:
							html.append('</a> ')
						if userName or userEmail:
							html.append('#(for) ')
						if userName and userEmail:
							html.append('<b>%s</b> (%s)' % (userName, userEmail))
						elif userName:
							html.append('<b>%s</b>' % (userName))
						elif userEmail:
							html.append('<b>%s</b>' % (userEmail))

						html.append('</p>')




						# Invitation

						if client.user() and subscription.invitationAccepted():

							html.append('<hr>')

							html.append('<h2>#(Invitations)</h2>')
							html.append('<p>')

							for invitation in client.acceptedInvitations():
								if invitation.url == subscription.protocol.unsecretURL():

									if invitation.invitedByUserEmail or invitation.invitedByUserName:
										html.append('#(Invited by) <img src="file://##htmlroot##/userIcon.svg" style="width: 16px; height: 16px; position: relative; top: 3px; margin-top: -3px; margin-right: 2px;">')
										if invitation.invitedByUserEmail and invitation.invitedByUserName:
											html.append('<b>%s</b> (<a href="mailto:%s">%s</a>)' % (invitation.invitedByUserName, invitation.invitedByUserEmail, invitation.invitedByUserEmail))
										else:
											html.append('%s' % (invitation.invitedByUserName or invitation.invitedByUserEmail))

									if invitation.time:
										html.append('<br />%s' % (NaturalRelativeWeekdayTimeAndDate(invitation.time, locale = client.locale()[0])))

							html.append('</p>')



						# Reveal Identity
						if subscription.parent.get('type') == 'JSON':

							html.append('<hr>')

							html.append('<h2>#(Reveal Identity)</h2>')
							html.append('<p>')
							if client.user():
								html.append('<span><input id="revealidentity" type="checkbox" name="revealidentity" %s><label for="revealidentity">#(Reveal Your Identity For This Subscription)</label></span>' % ('checked' if subscription.get('revealIdentity') else ''))
								html.append('''<script>
									$("#preferences #revealidentity").click(function() {
										setSubscriptionPreference("%s", "revealIdentity", $("#preferences #revealidentity").prop("checked"));
									});
								</script>''' % (b64ID))
								html.append('</p><p>')
								html.append('#(RevealIdentityExplanation)')
							else:
								html.append('#(RevealIdentityRequiresUserAccountExplanation)<br />#(PleaseCreateUserAccountExplanation)')
							html.append('</p>')


						# Print HTML
						html = ''.join(map(str, html))
						html = html.replace('"', '\'')
						html = localizeString(html, html = True)
						html = html.replace('\n', '')
						html = self.replaceHTML(html)


						js = '$("#preferences .inner").html("' + html + '");'
						self.javaScript(js)

						self.javaScript('showPreferences();')

		def showAppInstances(self, event):



			html = []




			# Print HTML
			html = ''.join(map(str, html))
			html = html.replace('"', '\'')
			html = localizeString(html, html = True)
			html = html.replace('\n', '')
			html = self.replaceHTML(html)

			js = '$("#preferences .inner").html("' + html + '");'
			self.javaScript(js)

			self.javaScript('showPreferences();')


		def inviteUsers(self, b64ID, string):
			
			subscription = None
			for publisher in client.publishers():
				for s in publisher.subscriptions():
					if s.exists and s.protocol.unsecretURL() == self.b64decode(b64ID):
						subscription = s
						break

			for email in [x.strip() for x in string.split(', ')]:

				success, message = subscription.inviteUser(email)

				if success:
					client.downloadSubscriptions()
					self.showSubscriptionInvitations(None, b64ID)

				else:
					self.errorMessage(message)



		def revokeUsers(self, b64ID, string):
			
			subscription = None
			for publisher in client.publishers():
				for s in publisher.subscriptions():
					if s.exists and s.protocol.unsecretURL() == self.b64decode(b64ID):
						subscription = s
						break

			if subscription and client.userEmail():

				dlg = wx.MessageDialog(None, localizeString("#(RevokeInvitationExplanationDialog)"), localizeString("#(Revoke Invitation)"), wx.YES_NO | wx.ICON_QUESTION)
				dlg.SetYesNoLabels(localizeString('#(Revoke)'), localizeString('#(Cancel)'))
				result = dlg.ShowModal()
				if result == wx.ID_YES:

					for email in [x.strip() for x in string.split(', ')]:

						success, message = subscription.revokeUser(email)

						if success:
							client.downloadSubscriptions()
							self.showSubscriptionInvitations(None, b64ID)

						else:
							self.errorMessage(message)


		def showSubscriptionInvitations(self, event, b64ID, loadUpdates = False):

			if loadUpdates:
				client.downloadSubscriptions()


			# print('showSubscriptionInvitations()')

			url = self.b64decode(b64ID)

			for publisher in client.publishers():
				for subscription in publisher.subscriptions():
					if subscription.exists and subscription.protocol.unsecretURL() == self.b64decode(b64ID):

						html = []

						html.append('<h2>#(Invitations)</h2>')
						html.append('<p>URL: <em>')
						html.append(subscription.protocol.unsecretURL()) # .replace('secretKey', '<span style="color: orange;">secretKey</span>')
						html.append('</em></p>')

						success, message = subscription.protocol.rootCommand()
						if success:
							rootCommand = message
						else:
							rootCommand = None


						success, message = subscription.protocol.installableFontsCommand()
						if success:
							command = message
						else:
							command = None

						userName = command.userName.getText(client.locale())
						userEmail = command.userEmail

						html.append('<p>')
						html.append('#(Provided by) ')
						if rootCommand.website:
							html.append('<a href="%s" title="%s">' % (rootCommand.website, rootCommand.website))
						html.append('<b>' + rootCommand.name.getText(client.locale()) + '</b>')
						if rootCommand.website:
							html.append('</a> ')
						if userName or userEmail:
							html.append('#(for) ')
						if userName and userEmail:
							html.append('<b>%s</b> (%s)' % (userName, userEmail))
						elif userName:
							html.append('<b>%s</b>' % (userName))
						elif userEmail:
							html.append('<b>%s</b>' % (userEmail))
						html.append('</p>')



						html.append('<hr>')


						html.append('<p>')
						html.append('#(InviteUserByEmailAddressExplanation)')
						html.append('</p>')
						html.append('<p>')
						html.append('<input type="text" id="inviteUserName" placeholder="#(JohnDoeEmailAddresses)"><br />')
						html.append('<a id="inviteUsersButton" class="button">#(Invite Users)</a>')


						html.append('</p>')


						html.append('''<script>

							$("#inviteUsersButton").click(function() {
								python("self.inviteUsers(____%s____, ____" + $("#inviteUserName").val() + "____)");
							});

						</script>''' % (b64ID))



						matchedInvitations = []

						for invitation in client.sentInvitations():
							if invitation.url == url:
								matchedInvitations.append(invitation)


						html.append('<hr>')


						if matchedInvitations:
							for invitation in matchedInvitations:
								html.append('<div class="clear" style="margin-bottom: 3px;">')
								html.append('<div style="float: left; width: 300px;">')
								html.append('<img src="file://##htmlroot##/userIcon.svg" style="width: 16px; height: 16px; position: relative; top: 3px; margin-top: -3px; margin-right: 2px;">')
								html.append('<b>%s</b> (<a href="mailto:%s">%s</a>)' % (invitation.invitedUserName, invitation.invitedUserEmail, invitation.invitedUserEmail))
								html.append('</div>')

								html.append('<div style="float: left; width: 100px;">')
								if invitation.confirmed:
									html.append('✓ #(Accepted)')
								else:
									html.append('<em>#(Pending)…</em>')
								html.append('</div>')

								html.append('<div style="float: right; width: 100px;">')
								html.append('<a class="revokeInvitationButton" b64ID="%s" email="%s">#(Revoke Invitation)</a>' % (b64ID, invitation.invitedUserEmail))
								html.append('</div>')

								html.append('</div>') # .clear


						else:
							html.append('<p>#(CurrentlyNoSentInvitations)</p>')

						html.append('<p>')
						html.append('<a id="updateInvitations" class="button">#(UpdateInfinitive)</a>')
						html.append('</p>')
						html.append('''<script>

							$("#updateInvitations").click(function() {
								python("self.showSubscriptionInvitations(None, ____%s____, loadUpdates = True)");
							});

							$(".revokeInvitationButton").click(function() {
								python("self.revokeUsers(____" + $(this).attr("b64ID") + "____, ____" + $(this).attr("email") + "____)");
							});

						</script>''' % (b64ID))


						# Print HTML
						html = ''.join(map(str, html))
						html = html.replace('"', '\'')
						html = localizeString(html, html = True)
						html = html.replace('\n', '')
						html = self.replaceHTML(html)


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
				# code = code.replace('http//', 'http://')
				# code = code.replace('https//', 'https://')
				code = code.replace('____', '\'')
				code = code.replace("'", '\'')
				# log('Python code:', code)
				exec(code)
				evt.Veto()
			elif uri.startswith('http://') or uri.startswith('https://'):
				
#				server = 'https://type.world'
#				server = 'https://typeworld.appspot.com'
				server = client.mothership.replace('/api', '/linkRedirect')
				webbrowser.open_new_tab(server + '?url=' + urllib.parse.quote_plus(uri))
				evt.Veto()

			elif uri.startswith('mailto:'):
				webbrowser.open(uri, new=1)

			# else:
			#   code = uri
			#   code = urllib.unquote(code)
			#   print code
			#   exec(code)
			#   evt.Veto()

		def onNavigated(self, evt):
			uri = evt.GetURL() # you may need to deal with unicode here


		def onError(self, evt):
			log('Error received from WebView: %s' % evt.GetString())
	#       raise Exception(evt.GetString())


		def showAddSubscription(self, evt):
			self.javaScript('showAddSubscription();')


		def handleURL(self, url, username = None, password = None):

			if url.startswith('typeworld://') or url.startswith('typeworld//'):

				for publisher in client.publishers():
					for subscription in publisher.subscriptions():
						if subscription.protocol.unsecretURL() == url:
							self.setActiveSubscription(self.b64encode(publisher.canonicalURL), self.b64encode(subscription.protocol.unsecretURL()))
							return

				self.javaScript("showCenterMessage('%s');" % localizeString('#(Loading Subscription)'))
				startWorker(self.addSubscription_consumer, self.addSubscription_worker, wargs=(url, username, password))

			elif url.startswith('typeworldapp://') or url.startswith('typeworldapp//'):
				self.handleAppCommand(url.replace('typeworldapp://', '').replace('typeworldapp//', ''))

		def handleAppCommand(self, url):

			log('handleAppCommand(%s)' % url)

			parts = url.split('/')

			if parts[0] == 'linkTypeWorldUserAccount':

				assert len(parts) == 3 and bool(parts[1])

				# Different user
				if client.user() and client.user() != parts[1]:
					self.errorMessage('#(AccountAlreadyLinkedExplanation)')

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
						self.javaScript('hidePanel();')
						self.message('#(JustLinkedUserAccount)')



		def addSubscriptionViaDialog(self, url, username = None, password = None):

			if url.startswith('typeworldapp://'):
				self.handleAppCommand(url.replace('typeworldapp://', ''))

			else:

				startWorker(self.addSubscription_consumer, self.addSubscription_worker, wargs=(url, username, password))


		def addSubscription_worker(self, url, username, password):

			for protocol in typeWorld.api.PROTOCOLS:
				url = url.replace(protocol + '//', protocol + '://')
			# url = url.replace('http//', 'http://')
			# url = url.replace('https//', 'https://')

			# Check for known protocol
			known = False
			for protocol in typeWorld.api.PROTOCOLS:
				if url.startswith(protocol):
					known = True
					break

			if not known:
				return False, 'Unknown protocol. Known are: %s' % (typeWorld.api.PROTOCOLS), None, None

			success, message, publisher, subscription = client.addSubscription(url, username, password)

			return success, message, publisher, subscription


		def addSubscription_consumer(self, delayedResult):

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

			self.javaScript('hideCenterMessage();')


		def acceptInvitation(self, ID):

			self.javaScript('startLoadingAnimation();')

			startWorker(self.acceptInvitation_consumer, self.acceptInvitation_worker, wargs=(ID, ))

		def acceptInvitation_worker(self, ID):

			success, message = client.acceptInvitation(ID)
			return success, message, ID


		def acceptInvitation_consumer(self, delayedResult):

			success, message, ID = delayedResult.get()

			if success:

				self.javaScript('$("#%s.invitation").slideUp();' % ID)

				for invitation in client.acceptedInvitations():
					if invitation.ID == ID:

						client.preferences.set('currentPublisher', invitation.canonicalURL)
						self.setSideBarHTML()
						self.setPublisherHTML(self.b64encode(client.publisher(client.preferences.get('currentPublisher')).canonicalURL))
						self.setBadges()

			else:

				pass

			self.javaScript('stopLoadingAnimation();')


		def declineInvitation(self, ID):

			invitation = None


			for invitation in client.acceptedInvitations():
				if invitation.ID == ID:
					url = invitation.url
					for publisher in client.publishers():
						for subscription in publisher.subscriptions():
							if url == subscription.protocol.unsecretURL():

								name = publisher.name(locale = client.locale())[0] + ' (' + subscription.name(locale=client.locale()) + ')'

								dlg = wx.MessageDialog(self, localizeString('#(Are you sure)\n#(RemoveInvitationConfirmationExplanation)'), localizeString('#(Remove X)').replace('%name%', name), wx.YES_NO | wx.ICON_QUESTION)
								dlg.SetYesNoLabels(localizeString('#(Remove)'), localizeString('#(Cancel)'))
								result = dlg.ShowModal() == wx.ID_YES
								dlg.Destroy()
					
								if result:
									self.javaScript('startLoadingAnimation();')
									startWorker(self.declineInvitation_consumer, self.declineInvitation_worker, wargs=(ID, ))


			for invitation in client.pendingInvitations():
				if invitation.ID == ID:
					dlg = wx.MessageDialog(self, localizeString('#(Are you sure)'), localizeString('#(Decline Invitation)'), wx.YES_NO | wx.ICON_QUESTION)
					dlg.SetYesNoLabels(localizeString('#(Remove)'), localizeString('#(Cancel)'))
					result = dlg.ShowModal() == wx.ID_YES
					dlg.Destroy()
		
					if result:
						self.javaScript('startLoadingAnimation();')
						startWorker(self.declineInvitation_consumer, self.declineInvitation_worker, wargs=(ID, ))

		def declineInvitation_worker(self, ID):

			success, message = client.declineInvitation(ID)
			return success, message, ID


		def declineInvitation_consumer(self, delayedResult):

			success, message, ID = delayedResult.get()

			if success:

				self.javaScript('$("#%s.invitation").slideUp();' % ID)

				if len(client.pendingInvitations()) == 0:
					if client.publishers():
						self.setPublisherHTML(self.b64encode(client.publishers()[0].canonicalURL))
					else:
						client.preferences.set('currentPublisher', '')
				self.setSideBarHTML()
				self.setBadges()


			else:

				pass

			self.javaScript('stopLoadingAnimation();')


				


		def removePublisher(self, evt, b64ID):

			self.allowedToPullServerUpdates = False

			publisher = client.publisher(self.b64decode(b64ID))

			dlg = wx.MessageDialog(self, localizeString('#(Are you sure)'), localizeString('#(Remove X)').replace('%name%', localizeString(publisher.name(client.locale())[0])), wx.YES_NO | wx.ICON_QUESTION)
			dlg.SetYesNoLabels(localizeString('#(Remove)'), localizeString('#(Cancel)'))
			result = dlg.ShowModal() == wx.ID_YES
			dlg.Destroy()
			
			if result:

				publisher.delete()
				client.preferences.set('currentPublisher', '')
				self.setSideBarHTML()
				self.javaScript("hideMain();")
				self.javaScript("hideMetadata();")

			self.allowedToPullServerUpdates = True

		def removeSubscription(self, evt, b64ID):

			self.allowedToPullServerUpdates = False

			for publisher in client.publishers():
				for subscription in publisher.subscriptions():
					if subscription.protocol.unsecretURL() == self.b64decode(b64ID):


						dlg = wx.MessageDialog(self, localizeString('#(Are you sure)'), localizeString('#(Remove X)').replace('%name%', localizeString(subscription.name(client.locale()))), wx.YES_NO | wx.ICON_QUESTION)
						dlg.SetYesNoLabels(localizeString('#(Remove)'), localizeString('#(Cancel)'))
						result = dlg.ShowModal() == wx.ID_YES
						dlg.Destroy()
						
						if result:
							subscription.delete()

							if publisher.subscriptions():
								publisher.set('currentSubscription', publisher.subscriptions()[0].protocol.unsecretURL())
								self.setPublisherHTML(self.b64encode(publisher.canonicalURL))
							else:
								self.javaScript("hideMain();")
								self.javaScript("hideMetadata();")

			self.setSideBarHTML()

			self.allowedToPullServerUpdates = True


		def publisherPreferences(self, i):
			log(('publisherPreferences', i))
			pass


		def installAllFonts(self, b64publisherID, b64subscriptionID, b64familyID, b64packageKeyword, formatName):

			fonts = []

			publisherID = self.b64decode(b64publisherID)
			subscriptionID = self.b64decode(b64subscriptionID)
			familyID = self.b64decode(b64familyID)
			packageKeyword = self.b64decode(b64packageKeyword)
			publisher = client.publisher(publisherID)
			subscription = publisher.subscription(subscriptionID)
			family = subscription.familyByID(familyID)

			for font in family.fonts:
				if packageKeyword in font.getPackageKeywords() and font.format == formatName:
					if not subscription.installedFontVersion(font.uniqueID):
						fonts.append([b64publisherID, b64subscriptionID, self.b64encode(font.uniqueID), font.getVersions()[-1].number])

			self.installFonts(fonts)


		def removeAllFonts(self, b64publisherID, b64subscriptionID, b64familyID, b64packageKeyword, formatName):

			fonts = []

			publisherID = self.b64decode(b64publisherID)
			subscriptionID = self.b64decode(b64subscriptionID)
			familyID = self.b64decode(b64familyID)
			packageKeyword = self.b64decode(b64packageKeyword)
			publisher = client.publisher(publisherID)
			subscription = publisher.subscription(subscriptionID)
			family = subscription.familyByID(familyID)

			for font in family.fonts:
				if packageKeyword in font.getPackageKeywords() and font.format == formatName:
					if subscription.installedFontVersion(font.uniqueID):
						fonts.append([b64publisherID, b64subscriptionID, self.b64encode(font.uniqueID)])

			self.removeFonts(fonts)



		def installFontFromMenu(self, event, b64publisherURL, b64subscriptionURL, b64fontID, version):

			self.log('installFontFromMenu()')

			self.installFont(b64publisherURL, b64subscriptionURL, b64fontID, version)


		def installFont(self, b64publisherURL, b64subscriptionURL, b64fontID, version):

			self.selectFont(b64fontID)
			self.javaScript('$(".font.%s").addClass("loading");' % b64fontID)
			self.javaScript('$("#metadata .seatsInstalled").fadeTo(500, .1);')
			startWorker(self.installFonts_consumer, self.installFonts_worker, wargs=([[[b64publisherURL, b64subscriptionURL, b64fontID, version]]]))


		def installFonts(self, fonts):


			for b64publisherURL, b64subscriptionURL, b64fontID, version in fonts:

				self.javaScript('$(".font.%s").addClass("loading");' % b64fontID)
				# self.javaScript('$("#%s.font").find("a.installButton").hide();' % b64fontID)
				# self.javaScript('$("#%s.font").find("a.removeButton").hide();' % b64fontID)
				# self.javaScript('$("#%s.font").find("a.status").show();' % b64fontID)
				# self.javaScript('$("#%s.font").find("a.more").hide();' % b64fontID)

			startWorker(self.installFonts_consumer, self.installFonts_worker, wargs=([fonts]))



		def installFonts_worker(self, fonts):

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
					success, message = subscription.removeFont(fontID)
					if success == False:
						return success, message, b64publisherURL, subscription, fonts

			for subscription in fontsBySubscription:

				# Install new font
				success, message = subscription.installFonts(fontsBySubscription[subscription])

				if success == False:
					return success, message, b64publisherURL, subscription, fonts

			# TODO: differentiate between b64publisherURLs here, as fonts could be from different publishers. Works for now, until fonts can be mixed in collections
			return True, None, b64publisherURL, subscription, fonts


		def installFonts_consumer(self, delayedResult):

			success, message, b64publisherURL, subscription, fonts = delayedResult.get()

			self.setFontStatuses(fonts)

			if success:

				pass

			else:

				for b64publisherURL, b64subscriptionURL, b64fontID, version in fonts:
					self.javaScript('$(".font.%s").removeClass("loading");' % b64fontID)
				self.errorMessage(message, subscription = subscription)

			self.setSideBarHTML()
			self.setBadges()
			self.setPublisherHTML(b64publisherURL)


		def removeFont(self, b64publisherURL, b64subscriptionURL, b64fontID):

			self.selectFont(b64fontID)
			self.javaScript('$(".font.%s").addClass("loading");' % b64fontID)
			self.javaScript('$("#metadata .seatsInstalled").fadeTo(500, .1);')
			startWorker(self.removeFonts_consumer, self.removeFonts_worker, wargs=([[[b64publisherURL, b64subscriptionURL, b64fontID]]]))

		def removeFonts(self, fonts):

			for b64publisherURL, b64subscriptionURL, b64fontID in fonts:

				self.javaScript('$(".font.%s").addClass("loading");' % b64fontID)
				# self.javaScript('$("#%s.font").find("a.installButton").hide();' % b64fontID)
				# self.javaScript('$("#%s.font").find("a.removeButton").hide();' % b64fontID)
				# self.javaScript('$("#%s.font").find("a.status").show();' % b64fontID)
				# self.javaScript('$("#%s.font").find("a.more").hide();' % b64fontID)

			startWorker(self.removeFonts_consumer, self.removeFonts_worker, wargs=([fonts]))


		def removeFonts_worker(self, fonts):

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
				success, message = subscription.removeFonts(fontsBySubscription[subscription])

				if success == False:
					return success, message, b64publisherURL, subscription, fonts

			# TODO: differentiate between b64publisherURLs here, as fonts could be from different publishers. Works for now, until fonts can be mixed in collections
			return True, None, b64publisherURL, subscription, fonts



		def removeFonts_consumer(self, delayedResult):

			success, message, b64publisherURL, subscription, fonts = delayedResult.get()

			self.setFontStatuses(fonts)

			if success:

				pass

			else:

				if type(message) == str:
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
					subscriptionB64ID = self.b64encode(subscription.protocol.unsecretURL())

					success, message = subscription.protocol.installableFontsCommand()
					if success:
						command = message
					else:
						command = None

					for foundry in command.foundries:
						for family in foundry.families:
							for font in family.fonts:
								installedFontVersion = subscription.installedFontVersion(font = font)
								if installedFontVersion and subscription.installedFontVersion(font = font) != font.getVersions()[-1].number:
									fonts.append([publisherB64ID, subscriptionB64ID, self.b64encode(font.uniqueID), font.getVersions()[-1].number])

			elif subscriptionB64ID:
				
				for publisher in client.publishers():
					for subscription in publisher.subscriptions():
						if subscription.protocol.unsecretURL() == self.b64decode(subscriptionB64ID):
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
							installedFontVersion = subscription.installedFontVersion(font = font)
							if installedFontVersion and subscription.installedFontVersion(font = font) != font.getVersions()[-1].number:
								fonts.append([publisherB64ID, subscriptionB64ID, self.b64encode(font.uniqueID), font.getVersions()[-1].number])

			self.installFonts(fonts)


		def setFontStatuses(self, fonts):

			for line in fonts:

				b64publisherURL = line[0]
				b64subscriptionURL = line[1]
				b64fontID = line[2]

				subscription = client.publisher(self.b64decode(b64publisherURL)).subscription(self.b64decode(b64subscriptionURL))
				font = subscription.fontByID(self.b64decode(b64fontID))
				installedVersion = subscription.installedFontVersion(font=font)

				self.javaScript('$(".font.%s").removeClass("loading");' % b64fontID)
				self.javaScript('$(".font.%s").removeClass("installed");' % b64fontID)
				self.javaScript('$(".font.%s").removeClass("installed");' % b64fontID)
				self.javaScript('$(".font.%s").removeClass("notInstalled");' % b64fontID)
				self.javaScript('$(".font.%s").removeClass("notInstalled");' % b64fontID)
				if installedVersion:
					self.javaScript('$(".font.%s").addClass("installed");' % b64fontID)
				else:
					self.javaScript('$(".font.%s").addClass("notInstalled");' % b64fontID)


				# metadata bar
				self.javaScript('$(".font.%s .version .status.install").show();' % b64fontID)
				self.javaScript('$(".font.%s .version .status.remove").hide();' % b64fontID)
				self.javaScript('$(".font.%s .version .label.installedVersion").hide();' % b64fontID)

				if installedVersion:
					self.javaScript('$(".font.%s .version.%s .status.install").hide();' % (b64fontID, self.versionEncode(installedVersion)))
					self.javaScript('$(".font.%s .version.%s .status.remove").show();' % (b64fontID, self.versionEncode(installedVersion)))
					self.javaScript('$(".font.%s .version.%s .label.installedVersion").show();' % (b64fontID, self.versionEncode(installedVersion)))


				html = self.fontInstalledText(font)
				html = html.replace('"', '\'')
				html = html.replace('\n', '')
				html = localizeString(html, html = True)
				html = self.replaceHTML(html)
				self.javaScript('$(".font.%s .installedText").html("%s");' % (b64fontID, html))


		def checkFontExpirations(self):

			fonts = []

			for publisher in client.publishers():
				for subscription in publisher.subscriptions():
					for font in subscription.installedFonts():
						if font.expiry and time.time() > font.expiry:

							fonts.append([self.b64encode(publisher.canonicalURL), self.b64encode(subscription.protocol.unsecretURL()), self.b64encode(font.uniqueID)])

			if fonts:
				self.removeFonts(fonts)




		def onContextMenu(self, x, y, target, b64ID):
	#       print x, y, target, b64ID, self.b64decode(b64ID)

			x = max(0, int(x) - 70)

			if 'contextmenu publisher' in target:

				for publisher in client.publishers():
					if publisher.canonicalURL == self.b64decode(b64ID):
						break

				menu = wx.Menu()

				if len(publisher.subscriptions()) > 1:
					item = wx.MenuItem(menu, wx.NewIdRef(count=1), localizeString('#(Update All Subscriptions)'))
					menu.Append(item)
					menu.Bind(wx.EVT_MENU, partial(self.reloadPublisher, b64ID = b64ID), item)
				else:
					item = wx.MenuItem(menu, wx.NewIdRef(count=1), localizeString('#(Update Subscription)'))
					menu.Append(item)
					menu.Bind(wx.EVT_MENU, partial(self.reloadSubscription, b64ID = self.b64encode(publisher.subscriptions()[0].protocol.unsecretURL()), subscription = None), item)

				if publisher.amountOutdatedFonts():
					item = wx.MenuItem(menu, wx.NewIdRef(count=1), localizeString('#(Update All Fonts)'))
					menu.Append(item)
					menu.Bind(wx.EVT_MENU, partial(self.updateAllFonts, publisherB64ID = b64ID, subscriptionB64ID = None), item)


				if publisher.get('type') == 'GitHub':
					item = wx.MenuItem(menu, wx.NewIdRef(count=1), localizeString('#(Publisher Preferences)'))
					menu.Append(item)
					menu.Bind(wx.EVT_MENU, partial(self.showPublisherPreferences, b64ID = b64ID), item)

				if len(publisher.subscriptions()) == 1:
					item = wx.MenuItem(menu, wx.NewIdRef(count=1), localizeString('#(Subscription Preferences)'))
					menu.Append(item)
					menu.Bind(wx.EVT_MENU, partial(self.showSubscriptionPreferences, b64ID = self.b64encode(publisher.subscriptions()[0].protocol.unsecretURL())), item)

					item = wx.MenuItem(menu, wx.NewIdRef(count=1), localizeString('#(Invite Users)'))
					menu.Append(item)
					menu.Bind(wx.EVT_MENU, partial(self.showSubscriptionInvitations, b64ID = self.b64encode(publisher.subscriptions()[0].protocol.unsecretURL())), item)

				item = wx.MenuItem(menu, wx.NewIdRef(count=1), localizeString('#(Show in Finder)'))
				menu.Append(item)
				menu.Bind(wx.EVT_MENU, partial(self.showPublisherInFinder, b64ID = b64ID), item)

				menu.AppendSeparator()

				item = wx.MenuItem(menu, wx.NewIdRef(count=1), localizeString('#(Remove)'))
				menu.Append(item)
				menu.Bind(wx.EVT_MENU, partial(self.removePublisher, b64ID = b64ID), item)

				self.PopupMenu(menu, wx.Point(int(x), int(y)))
				menu.Destroy()


			elif 'contextmenu subscription' in target:
				menu = wx.Menu()

				item = wx.MenuItem(menu, wx.NewIdRef(count=1), localizeString('#(Update Subscription)'))
				menu.Append(item)
				menu.Bind(wx.EVT_MENU, partial(self.reloadSubscription, b64ID = b64ID, subscription = None), item)

				for publisher in client.publishers():
					for subscription in publisher.subscriptions():
						if subscription.protocol.unsecretURL() == self.b64decode(b64ID):
							if publisher.amountOutdatedFonts():
								item = wx.MenuItem(menu, wx.NewIdRef(count=1), localizeString('#(Update All Fonts)'))
								menu.Append(item)
								menu.Bind(wx.EVT_MENU, partial(self.updateAllFonts, publisherB64ID = None, subscriptionB64ID = b64ID), item)
							break

				item = wx.MenuItem(menu, wx.NewIdRef(count=1), localizeString('#(Subscription Preferences)'))
				menu.Append(item)
				menu.Bind(wx.EVT_MENU, partial(self.showSubscriptionPreferences, b64ID = b64ID), item)

				item = wx.MenuItem(menu, wx.NewIdRef(count=1), localizeString('#(Invite Users)'))
				menu.Append(item)
				menu.Bind(wx.EVT_MENU, partial(self.showSubscriptionInvitations, b64ID = b64ID), item)

				menu.AppendSeparator()

				item = wx.MenuItem(menu, wx.NewIdRef(count=1), localizeString('#(Remove)'))
				menu.Append(item)
				menu.Bind(wx.EVT_MENU, partial(self.removeSubscription, b64ID = b64ID), item)


				self.PopupMenu(menu, wx.Point(int(x), int(y)))
				menu.Destroy()

			elif 'contextmenu font' in target:
				menu = wx.Menu()

				fontID = self.b64decode(b64ID)

				for publisher in client.publishers():
					for subscription in publisher.subscriptions():

						success, message = subscription.protocol.installableFontsCommand()
						if success:
							command = message
						else:
							command = None


						for foundry in command.foundries:
							for family in foundry.families:
								for font in family.fonts:
									if font.uniqueID == fontID:

										if subscription.installedFontVersion(font.uniqueID):
											item = wx.MenuItem(menu, wx.NewIdRef(count=1), localizeString('#(Show in Finder)'))
											menu.Bind(wx.EVT_MENU, partial(self.showFontInFinder, subscription = subscription, fontID = fontID), item)
											menu.Append(item)

										# create a submenu
										subMenu = wx.Menu()
										menu.AppendMenu(wx.NewIdRef(count=1), localizeString('#(Install Version)'), subMenu)

										for version in font.getVersions():

											if subscription.installedFontVersion(font.uniqueID) == version.number:
												item = wx.MenuItem(subMenu, wx.NewIdRef(count=1), str(version.number), "", wx.ITEM_RADIO)

											else:
												item = wx.MenuItem(subMenu, wx.NewIdRef(count=1), str(version.number))

											if WIN:
												installHere = menu
											else:
												installHere = subMenu
											installHere.Bind(wx.EVT_MENU, partial(self.installFontFromMenu, b64publisherURL = self.b64encode(publisher.canonicalURL), b64subscriptionURL = self.b64encode(subscription.protocol.unsecretURL()), b64fontID = b64ID, version = version.number), item)
											subMenu.Append(item)


	#    def installFontFromMenu(self, event, b64publisherURL, b64subscriptionURL, b64fontID, version):

										self.PopupMenu(menu, wx.Point(int(x), int(y)))
										menu.Destroy()

										break

			else:

				menu = wx.Menu()

				item = wx.MenuItem(menu, wx.NewIdRef(count=1), localizeString('#(Preferences)'))
				menu.Append(item)
				menu.Bind(wx.EVT_MENU, self.onPreferences, item)

				self.PopupMenu(menu, wx.Point(int(x), int(y)))
				menu.Destroy()



		def showPublisherPreferences(self, event, b64ID):

			for publisher in client.publishers():
				if publisher.exists and publisher.canonicalURL == self.b64decode(b64ID):


					html = []


					html.append('<h2>%s (%s)</h2>' % (publisher.name(client.locale())[0], publisher.get('type')))
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
					html = ''.join(map(str, html))
					html = html.replace('"', '\'')
					html = html.replace('\n', '')
					html = localizeString(html)
			#       print html
					js = '$("#publisherPreferences .inner").html("' + html + '");'
					self.javaScript(js)

					self.javaScript('showPublisherPreferences();')


		def showPublisherInFinder(self, evt, b64ID):
			
			log('showPublisherInFinder()')
			publisher = client.publisher(self.b64decode(b64ID))
			path = publisher.folder()

			if not os.path.exists(path):
				os.makedirs(path)

			import subprocess
			subprocess.call(["open", "-R", path])

		def showFontInFinder(self, evt, subscription, fontID):

			log('showFontInFinder()')
			font = subscription.fontByID(fontID)
			version = subscription.installedFontVersion(fontID)
			path = font.path(version, folder = None)

			import subprocess
			subprocess.call(["open", "-R", path])


		def reloadPublisher(self, evt, b64ID):

			# log('reloadPublisher()')

			client.prepareUpdate()

			publisher = client.publisher(self.b64decode(b64ID))
			for subscription in publisher.subscriptions():
				if subscription.exists:
					self.reloadSubscription(None, None, subscription)


		def autoReloadSubscriptions(self):

			client.pubSubSetup()
			for publisher in client.publishers():
				for subscription in publisher.subscriptions():
					subscription.pubSubSetup()


			if WIN:
				path = os.path.expanduser('~/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Type.World.lnk')
				if os.path.exists(path):
					os.remove(path)

			# # Preference is set to check automatically
			# if int(client.preferences.get('reloadSubscriptionsInterval')) != -1:

			# 	# Has never been checked, set to long time ago
			# 	if not client.preferences.get('reloadSubscriptionsLastPerformed'):
			# 		client.preferences.set('reloadSubscriptionsLastPerformed', int(time.time()) - int(client.preferences.get('reloadSubscriptionsInterval')) - 10)

			# 	# See if we should check now
			# 	if int(client.preferences.get('reloadSubscriptionsLastPerformed')) < int(time.time()) - int(client.preferences.get('reloadSubscriptionsInterval')):

			# 		self.log('Automatically reloading subscriptions...')

			# 		client.prepareUpdate()

			# 		for publisher in client.publishers():
			# 			for subscription in publisher.subscriptions():
			# 				self.reloadSubscription(None, None, subscription)




		def reloadSubscriptionFromClient(self, subscription):
			startWorker(self.reloadSubscriptionFromClient_consumer, self.reloadSubscriptionFromClient_worker, wargs=(subscription, ))

		def reloadSubscriptionFromClient_worker(self, subscription):
			return subscription

		def reloadSubscriptionFromClient_consumer(self, delayedResult):
			# self.log('PULLED FROM SERVER: %s' % (subscription))
			subscription = delayedResult.get()
			self.reloadSubscription(None, subscription = subscription)

		def reloadSubscription(self, evt, b64ID = None, subscription = None):

#			self.log('reloadSubscription(%s, %s)' % (b64ID, subscription))

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
				b64subscriptionID = self.b64encode(subscription.protocol.unsecretURL())


				# Publisher
				self.javaScript("$('#sidebar #%s.publisher .reloadAnimation').show();" % b64publisherID)
				self.javaScript("$('#sidebar #%s.publisher .badges').hide();" % b64publisherID)

				# Subscription
				self.javaScript("$('#sidebar #%s.subscription .reloadAnimation').show();" % b64subscriptionID)
				self.javaScript("$('#sidebar #%s.subscription .badges').hide();" % b64subscriptionID)

				startWorker(self.reloadSubscription_consumer, self.reloadSubscription_worker, wargs=(subscription, ))




		def reloadSubscription_worker(self, subscription):

			success, message, changes = subscription.update()
			return success, message, changes, subscription


		def reloadSubscription_consumer(self, delayedResult):
			success, message, changes, subscription = delayedResult.get()
			b64publisherID = self.b64encode(subscription.parent.canonicalURL)

			if success:
				if client.preferences.get('currentPublisher') == subscription.parent.canonicalURL:
					self.setPublisherHTML(self.b64encode(subscription.parent.canonicalURL))
				self.setSideBarHTML()

				# Hide alert
				self.javaScript("$('#sidebar #%s .alert').hide();" % b64publisherID)
				self.javaScript("$('#sidebar #%s .alert').hide();" % self.b64encode(subscription.protocol.unsecretURL()))
			
			else:	
				# Show alert
#				if subscription.updatingProblem():
				self.javaScript("$('#sidebar #%s .alert').show();" % b64publisherID)
				self.javaScript("$('#sidebar #%s .alert ').show();" % self.b64encode(subscription.protocol.unsecretURL()))

			# Subscription
			self.javaScript("$('#sidebar #%s.subscription .reloadAnimation').hide();" % (self.b64encode(subscription.protocol.unsecretURL())))
			self.javaScript("$('#sidebar #%s.subscription .badges').show();" % (self.b64encode(subscription.protocol.unsecretURL())))

			if subscription.parent.stillUpdating() == False:
				# Publisher
				self.javaScript("$('#sidebar #%s.publisher .reloadAnimation').hide();" % b64publisherID)
				self.javaScript("$('#sidebar #%s.publisher .badges').show();" % b64publisherID)
	#            self.javaScript("stopAnimation();")

			if client.allSubscriptionsUpdated():
				client.preferences.set('reloadSubscriptionsLastPerformed', int(time.time()))
				self.log('Reset reloadSubscriptionsLastPerformed')

			agent('amountOutdatedFonts %s' % client.amountOutdatedFonts())


		def displaySyncProblems(self):

			self.errorMessage('\n\n'.join(client.syncProblems()))


		def displayPublisherSidebarAlert(self, b64publisherID):
			publisher = client.publisher(self.b64decode(b64publisherID))

			for message in publisher.updatingProblem():
				self.errorMessage(message)

		def displaySubscriptionSidebarAlert(self, b64subscriptionID):

			for publisher in client.publishers():
				for subscription in publisher.subscriptions():
					if subscription.protocol.unsecretURL() == self.b64decode(b64subscriptionID):
						message = subscription.updatingProblem()
						if subscription.updatingProblem():
							self.errorMessage(message)
						else:
							self.errorMessage('No error message defined :/')


		def errorMessage(self, message, title = '', subscription = None):

			if type(message) in (list, tuple):
				assert len(message) == 2
				string, title = message

			elif type(message) == typeWorld.api.MultiLanguageText:
				string = message.getText(locale = client.locale())

			else:
				string = message

			keepString = string
			string = localizeString(string)
			title = localizeString(title)

			dlg = wx.MessageDialog(self, string or 'No message defined', title, wx.ICON_ERROR)
			result = dlg.ShowModal()
			dlg.Destroy()

			if keepString == '#(response.loginRequired)' and subscription and subscription.protocol.rootCommand()[1].loginURL:
				url = subscription.protocol.rootCommand()[1].loginURL
				url = addAttributeToURL(url, 'subscriptionID=%s' % typeWorld.client.URL(subscription.url).subscriptionID)
				print(url)
				webbrowser.open(url, new=1)


		def message(self, message, title = ''):

			if type(message) in (list, tuple):
				assert len(message) == 2
				message, title = message

			elif type(message) == typeWorld.api.MultiLanguageText:
				message = message.getText(locale = client.locale())

			log(message)

			message = localizeString(message)
			title = localizeString(title)

			dlg = wx.MessageDialog(self, message or 'No message defined', title)
			result = dlg.ShowModal()
			dlg.Destroy()

		def fontHTML(self, font):

			subscription = font.parent.parent.parent

			html = []

			# Print HTML
			html = ''.join(map(str, html))
			html = html.replace('"', '\'')
			html = html.replace('\n', '')
			html = localizeString(html)
			html = self.replaceHTML(html)

			return html


		def setActiveSubscription(self, publisherB64ID, subscriptionB64ID):

			publisherID = self.b64decode(publisherB64ID)
			subscriptionID = self.b64decode(subscriptionB64ID)

			publisher = client.publisher(publisherID)
			subscription = publisher.subscription(subscriptionID)
			publisher.set('currentSubscription', subscription.protocol.unsecretURL())
			self.setPublisherHTML(publisherB64ID)


		def selectFont(self, b64ID):

			fontID = self.b64decode(b64ID)
			publisher = client.publisher(client.preferences.get('currentPublisher'))
			subscription = publisher.subscription(publisher.get('currentSubscription'))
			subscription.set('currentFont', fontID)
			font = subscription.fontByID(fontID)

			self.setMetadataHTML(b64ID)
			self.javaScript("showMetadata();")


		def showMetadataCategory(self, categoryName):
			client.preferences.set('metadataCategory', categoryName)

			publisher = client.publisher(client.preferences.get('currentPublisher'))
			subscription = publisher.subscription(publisher.get('currentSubscription'))
			font = subscription.fontByID(subscription.get('currentFont'))

			self.setMetadataHTML(self.b64encode(font.uniqueID))

		def setFontImage(self, index):

			index = int(index)
			publisher = client.publisher(client.preferences.get('currentPublisher'))
			subscription = publisher.subscription(publisher.get('currentSubscription'))
			font = subscription.fontByID(subscription.get('currentFont'))
			success, billboard, mimeType = client.resourceByURL(font.parent.billboards[index], binary = True)
			if success:
				data = "data:%s;base64,%s" % (mimeType, billboard)
			else:
				data = font.parent.billboards[index]

			self.javaScript('$("#fontBillboard").attr("src","%s");' % (data))
			self.javaScript('$(".fontBillboardLinks").removeClass("selected");')
			self.javaScript('$("#fontBillboardLink_%s").addClass("selected");' % index)
			font.parent.parent.parent.parent.set('currentFontImage', int(index))

		def setMetadataHTML(self, b64ID):

			if b64ID:

				fontID = self.b64decode(b64ID)
				publisher = client.publisher(client.preferences.get('currentPublisher'))
				subscription = publisher.subscription(publisher.get('currentSubscription'))
				subscription.set('currentFont', fontID)
				font = subscription.fontByID(fontID)

				html = []

				if font:
					foundry = font.parent.parent
					subscription = font.parent.parent.parent.parent.subscription
					installedVersion = subscription.installedFontVersion(font.uniqueID)




					#metadata

					theme = self.theme()
					styling = FoundryStyling(foundry, theme)
					html.append(styling.informationView())


					if font.parent.billboards:

						index = font.parent.parent.parent.parent.get('currentFontImage') or 0
						if index > len(font.parent.billboards) - 1:
							index = 0
							font.parent.parent.parent.parent.set('currentFontImage', int(index))

						html.append('<div style="max-height: 400px; height: 300px;">')

						success, billboard, mimeType = client.resourceByURL(font.parent.billboards[index], binary = True)
						if success:
							html.append('<img id="fontBillboard" src="data:%s;base64,%s" style="width: 300px;">' % (mimeType, billboard))
						else:
							html.append('<img id="fontBillboard" src="%s" style="width: 300px;">' % (font.parent.billboards[index]))


						html.append('</div>')
						if len(font.parent.billboards) > 1:
							html.append('<div style="padding: 5px; text-align: center;">')
							for i, billboard in enumerate(font.parent.billboards):
								html.append('<span id="fontBillboardLink_%s" class="fontBillboardLinks %s"><a href="x-python://self.setFontImage(____%s____)" style="color: inherit;">•</a></span>' % (i, 'selected' if i == index else '', i))
							html.append('</div>')

					html.append('<div class="font %s">' % (self.b64encode(font.uniqueID)))
					html.append('<div class="name">%s %s</div>' % (font.parent.name.getText(client.locale()), font.name.getText(client.locale())))
					html.append('<div class="categories">')

					for keyword, name, condition in (
						('license', '#(License)', True),
						('information', '#(Information)', font.parent.description),
						('versions', '#(Versions)', True),
		#				('billboards', '#(Images)', font.parent.billboards),
						):

						if condition:
							html.append('<div class="category %s %s">' % ('selected' if client.preferences.get('metadataCategory') == keyword else '', keyword))
							if client.preferences.get('metadataCategory') != keyword:
								html.append('<a href="x-python://self.showMetadataCategory(____%s____)">' % keyword)
							html.append('%s&thinsp;→' % name)
							if client.preferences.get('metadataCategory') != keyword:
								html.append('</a>')
							html.append('</div>')

					html.append('</div>')

					html.append('<div class="categoryBody %s">' % (client.preferences.get('metadataCategory')))

					if client.preferences.get('metadataCategory') == 'license':
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

							if usedLicense.seatsAllowed != None and usedLicense.seatsInstalled != None:
								licenseLink = usedLicense.upgradeURL is not None
	#							licenseLink = False
								
								if licenseLink:
									html.append(f'<a href="{usedLicense.upgradeURL}">')
								html.append('<div class="clear" style="width: 90%; margin-bottom: -20px;">')
								html.append('<div style="float: left; width: %s; min-width: 110px; text-align: center;">' % ('30%' if licenseLink else '100%'))

								html.append('<div style="display: inline-block; width: 100px; ">')
								html.append('<img src="file://##htmlroot##/seatallowance.svg" style="width: 100px;">')

								html.append('<div style="width: 100px; position: relative; top: -%spx; left; 0px; margin-left: -4px; margin-bottom: -35px;  ">' % (80 if MAC else 82))
								html.append('<div class="seatsInstalled" style="position: relative; width: 30px; left: 21px; top: 2px; text-align: right; color: black !important;">')
								html.append(usedLicense.seatsInstalled)
								html.append('</div>')
								html.append('<div style="position: relative; width: 30px; left: 57px; top: 2px; text-align: left; color: black !important;">')
								html.append(usedLicense.seatsAllowed)
								html.append('</div>')
								html.append('</div>')

								html.append('</div>')

								html.append('</div>') # .float left # image

								if licenseLink:
									html.append('<div style="float: left; width: 140px; height: 100px; text-align: left; display: table;">')
									html.append('<div style="display: table-cell; vertical-align: middle; ">')
									html.append('#(Upgrade License)&thinsp;↗︎')
									html.append('</div>')
									html.append('</div>') # .float left
								html.append('</div>') # .clear

								if licenseLink:
									html.append('</a>')

							elif usedLicense.upgradeURL:
								html.append(f'<a class="button" href="{usedLicense.upgradeURL}">')
								html.append('#(Upgrade License)&thinsp;↗︎')
								html.append('</a>')



							license = usedLicense.getLicense()
							html.append('<div>')
							html.append('<p>%s<br />' % license.name.getText(client.locale()))
							html.append('<a href="%s">%s&thinsp;↗︎</a></p>' % (license.URL, license.URL))
							if usedLicense.seatsAllowed != None and usedLicense.seatsInstalled != None:
								html.append('<p>')
								html.append('#(Seats Installed): <b>' + localizeString('#(%x% out of %y%)', replace = {'x': f'<span class="seatsInstalled">{usedLicense.seatsInstalled}</span>', 'y': usedLicense.seatsAllowed}) + '</b>')
								html.append('</p>')
							html.append('</div>')

					if client.preferences.get('metadataCategory') == 'information' and font.parent.description:
						text, locale = font.parent.description.getTextAndLocale()
						html.append('%s' % text)

					if client.preferences.get('metadataCategory') == 'versions':
						html.append('<div>')
						for version in reversed(font.getVersions()):
							html.append('<div class="version %s">' % self.versionEncode(version.number))
							html.append('<p><b>#(Version) %s</b> <span class="label installedVersion %s" style="display: %s;">#(Installed)</span><br />' % (version.number, 'latestVersion' if version.number == font.getVersions()[-1].number else 'olderVersion', 'inline' if version.number == installedVersion else 'none'))
							if version.description:
								html.append('%s' % version.description.getText(client.locale()))
							if version.releaseDate:
								html.append('<br /><span style="color: gray;">#(Published): %s</span>' % locales.formatDate(time.mktime(datetime.date.fromisoformat(version.releaseDate).timetuple()), client.locale()))

							html.append('<div class="installButton status install" style="display: %s; margin-top: -3px;">' % ('block' if version.number != installedVersion else 'none'))
							html.append('<a href="x-python://self.installFont(____%s____, ____%s____, ____%s____, ____%s____)" class="installButton button">' % (self.b64encode(subscription.parent.canonicalURL), self.b64encode(subscription.protocol.unsecretURL()), self.b64encode(font.uniqueID), version.number))
							html.append('✓ #(Install)')
							html.append('</a>')
							html.append('</div>') # installButton
							html.append('<div class="installButton status remove" style="display: %s; margin-top: -3px;">' % ('none' if version.number != installedVersion else 'block'))
							html.append('<a href="x-python://self.removeFont(____%s____, ____%s____, ____%s____)" class="removeButton button">' % (self.b64encode(subscription.parent.canonicalURL), self.b64encode(subscription.protocol.unsecretURL()), self.b64encode(font.uniqueID)))
							html.append('✕ #(Remove)')
							html.append('</a>')
							html.append('</div>') # installButton
							html.append('</p>')
							html.append('</div>') # .version

						html.append('</div>')
					
					html.append('</div>') # .categories
					html.append('</div>') # .font

				html = ''.join(map(str, html))
				html = html.replace('"', '\'')
				html = html.replace('\n', '')
				html = localizeString(html)
				html = self.replaceHTML(html)
				js = '$("#metadata .content").html("' + html + '");'
				self.javaScript(js)


		def setPublisherHTML(self, b64ID = None):

			# import cProfile
			# profile = cProfile.Profile()
			# profile.enable()

			if self.b64decode(b64ID) == 'pendingInvitations':

				client.preferences.set('currentPublisher', 'pendingInvitations')

				html = []

				pendingInvitations = client.pendingInvitations()
				if pendingInvitations:
					for invitation in pendingInvitations:

						html.append('<div class="publisher invitation" id="%s">' % invitation.ID)

						html.append('<div class="foundry">')
						html.append('<div class="head clear" style="background-color: %s;">' % ('#' + Color(hex=invitation.backgroundColor or 'DDDDDD').desaturate(0 if self.IsActive() else 1).hex if invitation.backgroundColor else 'none'))


						if invitation.logoURL:
							success, logo, mimeType = client.resourceByURL(invitation.logoURL, binary = True)
							if success:
								html.append('<div class="logo">')
								html.append('<img src="data:%s;base64,%s" style="width: 100px; height: 100px;" />' % (mimeType, logo))
								html.append('</div>') # publisher
							else:
								html.append('<div class="logo">')
								html.append('<img src="%s" style="width: 100px; height: 100px;" />' % (invitation.logoURL))
								html.append('</div>') # publisher

						html.append('<div class="names centerOuter"><div class="centerInner">')

						html.append('<div class="vertCenterOuter" style="height: 100px;">')
						html.append('<div class="vertCenterMiddle">')
						html.append('<div class="vertCenterInner">')

						name = typeWorld.api.MultiLanguageText(dict = invitation.publisherName)
						subscriptionName = typeWorld.api.MultiLanguageText(dict = invitation.subscriptionName)
						html.append('<div class="name">%s%s</div>' % (name.getText(client.locale()), (' (%s)' % subscriptionName.getText(client.locale()) if invitation.subscriptionName else '')))
						if invitation.website:
							html.append('<p>')
							html.append('<div class="website"><a href="%s">%s</a></div>' % (invitation.website, invitation.website))
							html.append('</p>')

						if invitation.foundries or invitation.families or invitation.fonts:
							html.append('<p>')
							html.append('%s #(Foundry/ies), %s #(Families/s), %s #(Font/s)' % (invitation.foundries or 0, invitation.families or 0, invitation.fonts or 0))
							html.append('</p>')

						html.append('<p>')
						if invitation.invitedByUserEmail or invitation.invitedByUserName:
							html.append('#(Invited by): <img src="file://##htmlroot##/userIcon.svg" style="width: 16px; height: 16px; position: relative; top: 3px; margin-top: -3px; margin-right: 2px;">')
							if invitation.invitedByUserEmail and invitation.invitedByUserName:
								html.append('<b>%s</b> (<a href="mailto:%s">%s</a>)' % (invitation.invitedByUserName, invitation.invitedByUserEmail, invitation.invitedByUserEmail))
							else:
								html.append('%s' % (invitation.invitedByUserName or invitation.invitedByUserEmail))

						if invitation.time:
							html.append(', %s' % (NaturalRelativeWeekdayTimeAndDate(invitation.time, locale = client.locale()[0])))

						html.append('</p>')


						html.append('<div style="margin-top: 15px;">')

						html.append('<a class="acceptInvitation" id="%s" href="x-python://self.acceptInvitation(____%s____)">' % (invitation.ID, invitation.ID))
						html.append('<div class="clear invitationButton accept">')
						html.append('<div class="symbol">')
						html.append('✓')
						html.append('</div>')
						html.append('<div class="text">')
						html.append('#(Accept Invitation)')
						html.append('</div>')
						html.append('</div>')
						html.append('</a>')

#						html.append('&nbsp;&nbsp;')

						html.append('<a class="declineInvitation" id="%s" href="x-python://self.declineInvitation(____%s____)">' % (invitation.ID, invitation.ID))
						html.append('<div class="clear invitationButton decline">')
						html.append('<div class="symbol">')
						html.append('✕')
						html.append('</div>')
						html.append('<div class="text">')
						html.append('#(Decline Invitation)')
						html.append('</div>')
						html.append('</div>')
						html.append('</a>')

						html.append('</div>') # buttons


						html.append('</div>') # .vertCenterInner
						html.append('</div>') # .vertCenterMiddle
						html.append('</div>') # .vertCenterOuter


						html.append('</div></div>') # .centerInner .centerOuter





						html.append('</div>') # .head
						html.append('</div>') # .foundry
						html.append('</div>') # .publisher


			# 			html.append('''<script>


			# $("#main .publisher a.acceptInvitation").click(function() {
			# 	python("self.acceptInvitation('" + $(this).attr('id') + "')");
			# });

			# $("#main .publisher a.declineInvitation").click(function() {
			# 	python("self.declineInvitation('" + $(this).attr("id") + "')");
			# });


			# 				</script>''')


				# Print HTML
				html = ''.join(map(str, html))
				html = html.replace('"', '\'')
				html = html.replace('\n', '')
				html = localizeString(html)
				html = self.replaceHTML(html)


		#       print html
				js = '$("#main").html("' + html + '");'
				self.javaScript(js)

				# Set Sidebar Focus
				self.javaScript('$("#sidebar div.subscriptions").slideUp();')
				
				self.javaScript("$('#sidebar .publisher').removeClass('selected');")
				self.javaScript("$('#sidebar .subscription').removeClass('selected');")
				self.javaScript("$('#sidebar .pendingInvitations').addClass('selected');")
				self.javaScript("showMain();")

			else:


		#       print b64ID

				ID = self.b64decode(b64ID)

				client.preferences.set('currentPublisher', ID)

				html = []


				publisher = client.publisher(ID)
				if publisher.subscriptions() and not publisher.get('currentSubscription'):
					publisher.set('currentSubscription', publisher.subscriptions()[0].protocol.unsecretURL())

				if publisher.get('currentSubscription'):
					subscription = publisher.subscription(publisher.get('currentSubscription'))
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

					if command.prefersRevealedUserIdentity and subscription.get('revealIdentity') != True:

						html.append('<div class="foundry" id="acceptRevealIdentity">')
						html.append('<div class="head clear">')
						html.append('<div class="inner">')

						html.append('<div class="clear">')

						html.append('<div class="one" style="float: left; width: 500px;">')
						html.append('<p>')
						html.append('<b>#(Reveal Identity)</b>')
						html.append('</p>')
						html.append('<p>')
						html.append('#(RevealUserIdentityRequest)')
						html.append('</p>')
						html.append('</div>') # .one

						html.append('<div class="two" style="float: right;">')

						# # BUTTON
						html.append('<div style="margin-top: 18px;">')
						html.append('<a class="acceptInvitation" id="acceptRevealIdentityButton">')
						html.append('<div class="clear invitationButton agree">')
						html.append('<div class="symbol">')
						html.append('✓')
						html.append('</div>')
						html.append('<div class="text">')
						html.append('#(Agree)')
						html.append('</div>')
						html.append('</div>')
						html.append('</a>')
						html.append('</div>') # buttons

						html.append('</div>') # .two
						html.append('</div>') # .clear

						html.append('</div>') # .inner
						html.append('</div>') # .head
						html.append('</div>') # .foundry

						html.append('''<script>


			$("#acceptRevealIdentityButton").click(function() {
				$("#acceptRevealIdentity").slideUp(function(){ 
					setSubscriptionPreference("%s", "revealIdentity", "true");
				});
			});

							</script>''' % self.b64encode(subscription.protocol.unsecretURL()))



					if subscription.get('acceptedTermsOfService') != True:

						html.append('<div class="foundry" id="acceptTermsOfService">')
						html.append('<div class="head clear">')
						html.append('<div class="inner">')

						html.append('<div class="clear">')

						html.append('<div class="one" style="float: left; width: 500px;">')
						html.append('<p>')
						html.append('<b>#(Terms of Service)</b>')
						html.append('</p>')
						html.append('<p>')
						html.append('#(AcceptTermsOfServiceExplanation)')
						html.append('</p>')
						html.append('<p>')
						html.append('<a href="%s">→ %s</a>' % (addAttributeToURL(rootCommand.termsOfServiceAgreement, 'locales=' + ','.join(client.locale()) + '&canonicalURL=' + urllib.parse.quote(rootCommand.canonicalURL) + '&subscriptionID=' + urllib.parse.quote(subscription.protocol.url.subscriptionID)), localizeString('#(Read X)', replace = {'content': localizeString('#(Terms of Service)')})))
						html.append('</p>')

						html.append('<p style="height: 5px;">&nbsp;</p>')

						html.append('<p>')
						html.append('<b>#(Privacy Policy)</b>')
						html.append('</p>')
						html.append('<p>')
						html.append('#(AcceptPrivacyPolicyExplanation)')
						html.append('</p>')
						html.append('<p>')
						html.append('<a href="%s">→ %s</a>' % (addAttributeToURL(rootCommand.privacyPolicy, 'locales=' + ','.join(client.locale()) + '&canonicalURL=' + urllib.parse.quote(rootCommand.canonicalURL) + '&subscriptionID=' + urllib.parse.quote(subscription.protocol.url.subscriptionID)), localizeString('#(Read X)', replace = {'content': localizeString('#(Privacy Policy)')})))
						html.append('</p>')

						html.append('</div>') # .one

						html.append('<div class="two" style="float: right;">')

						# # BUTTON
						html.append('<div style="margin-top: 18px;">')
						html.append('<a class="acceptInvitation" id="acceptTermsOfServiceButton">')
						html.append('<div class="clear invitationButton agree">')
						html.append('<div class="symbol">')
						html.append('✓')
						html.append('</div>')
						html.append('<div class="text">')
						html.append('#(Agree)')
						html.append('</div>')
						html.append('</div>')
						html.append('</a>')
						html.append('</div>') # buttons

						html.append('</div>') # .two
						html.append('</div>') # .clear

						html.append('</div>') # .inner
						html.append('</div>') # .head
						html.append('</div>') # .foundry

						html.append('''<script>


			$("#acceptTermsOfServiceButton").click(function() {
				$("#acceptTermsOfService").slideUp(function(){ 
					setSubscriptionPreference("%s", "acceptedTermsOfService", "true");
				});
			});

							</script>''' % self.b64encode(subscription.protocol.unsecretURL()))



					for foundry in command.foundries:

						theme = self.theme()

						## STYLING
						styling = FoundryStyling(foundry, theme)
						logoURL = styling.logo()
						html.append(styling.foundryView(self.b64encode(foundry.uniqueID)))

						backgroundColorFoundryStyling = FoundryStyling(foundry.parent.foundries[-1], theme)
						html.append('''<style> #main { background-color: #%s; } </style>''' % backgroundColorFoundryStyling.backgroundColor.hex)

						html.append('<div class="foundry" id="%s">' % self.b64encode(foundry.uniqueID))
						html.append('<div class="head clear">')

						if logoURL:
							success, logo, mimeType = subscription.resourceByURL(logoURL, binary = True)
							if success:
								html.append('<div class="logo">')
								html.append('<img src="data:%s;base64,%s" style="width: 100px; height: 100px;" />' % (mimeType, logo))
								html.append('</div>') # publisher

						html.append('<div class="names centerOuter"><div class="centerInner">')

						html.append('<div class="vertCenterOuter" style="height: 100px;">')
						html.append('<div class="vertCenterMiddle">')
						html.append('<div class="vertCenterInner">')


						html.append('<div class="name">%s</div>' % (foundry.name.getText(client.locale())))
						if foundry.website:
							html.append('<p>')
							html.append('<div class="website"><a href="%s">%s</a></div>' % (foundry.website, foundry.website))
							html.append('</p>')

						html.append('</div>') # .vertCenterInner
						html.append('</div>') # .vertCenterMiddle
						html.append('</div>') # .vertCenterOuter

						html.append('</div></div>') # .centerInner .centerOuter





						html.append('</div>') # .head










						html.append('<div class="families">')

						for family in foundry.families:
							html.append('<div class="contextmenu family" id="%s">' % self.b64encode(family.uniqueID))

							html.append('<div class="title">')
							html.append('<div class="clear">')
							html.append('<div class="left name">')
							html.append(family.name.getText(client.locale()))
							html.append('</div>') # .left.name
							html.append('</div>') # .clear
							html.append('</div>') # .title


							for package in family.getPackages():
								for formatName in package.getFormats():

									amountInstalled = 0
									for font in package.fonts:
										if subscription.installedFontVersion(font.uniqueID):
											amountInstalled += 1

									completeSetName = ''
									if package.keyword != typeWorld.api.DEFAULT:
										completeSetName += package.name.getText(client.locale()) + ', '
									completeSetName += typeWorld.api.FILEEXTENSIONNAMES[formatName]

									html.append('<div class="section %s" id="%s">' % ('multipleFonts' if len(package.fonts) > 1 else '', completeSetName))

									html.append('<div class="title clear">')
									html.append('<div class="name left">%s</div>' % completeSetName)

									if len(package.fonts) > 1:

										html.append('<div class="more right" style="padding-top: 5px;">')
										html.append('<img src="file://##htmlroot##/more_darker.svg" style="height: 8px; position: relative; top: 0px;">')
										html.append('</div>')

										html.append('<div class="installButtons right" style="padding-top: 5px;">')
										html.append('<div class="clear">')

										if amountInstalled < len(package.fonts):
											html.append('<div class="install installButton right">')
											html.append('<a href="x-python://self.installAllFonts(____%s____, ____%s____, ____%s____, ____%s____, ____%s____)" class="installAllFonts installButton button">' % (self.b64encode(ID), self.b64encode(subscription.protocol.unsecretURL()), self.b64encode(family.uniqueID), self.b64encode(package.keyword), formatName))
											html.append('✓ #(Install All)')
											html.append('</a>')
											html.append('</div>') # .installButton

										if amountInstalled > 0:
											html.append('<div class="remove installButton right">')
											html.append('<a href="x-python://self.removeAllFonts(____%s____, ____%s____, ____%s____, ____%s____, ____%s____)" class="removeAllFonts removeButton button ">' % (self.b64encode(ID), self.b64encode(subscription.protocol.unsecretURL()), self.b64encode(family.uniqueID), self.b64encode(package.keyword), formatName))
											html.append('✕ #(Remove All)')
											html.append('</a>')
											html.append('</div>') # .installButton

										html.append('</div>') # .clear
										html.append('</div>') # .installButtons

									html.append('</div>') # .title

									for font in package.fonts:
										installedVersion = subscription.installedFontVersion(font.uniqueID)

										html.append('<div class="contextmenu font %s %s %s" id="%s">' % (self.b64encode(font.uniqueID), 'installed' if installedVersion else 'notInstalled', 'selected' if subscription.get('currentFont') == font.uniqueID else '', self.b64encode(font.uniqueID)))
										html.append('<div class="clear">')

										html.append('<div class="left" style="width: 50%;">')
										html.append(font.name.getText(client.locale()))
										if font.free:
											html.append('<span class="label free">free</span>')
										if font.status != 'stable':
											html.append('<span class="label pre">%s</span>' % font.status)
										if font.variableFont:
											html.append('<span class="label var">OTVar</span>')
										html.append('</div>') # .left

										html.append('<div class="left installedText">')
										html.append(self.fontInstalledText(font))
										html.append('</div>') # .left

										expiry = ''
										if font.expiryDuration:
											expiry = '%s\'' % font.expiryDuration
										if expiry:
											html.append('<div class="left expiryText">')
											html.append('⏲<span class="countdownMinutes" timestamp="%s">%s</span>' % (font.expiry, expiry))
											html.append('</div>') # .left

										if font.purpose == 'desktop':

											html.append('<div class="installButtons right">')
											html.append('<div class="installButton status install">')
											html.append('<a href="x-python://self.installFont(____%s____, ____%s____, ____%s____, ____%s____)" class="installButton button">' % (self.b64encode(subscription.parent.canonicalURL), self.b64encode(subscription.protocol.unsecretURL()), self.b64encode(font.uniqueID), font.getVersions()[-1].number if font.getVersions() else ''))
											html.append('✓ #(Install)')
											html.append('</a>')
											html.append('</div>') # installButton
											html.append('<div class="installButton status remove">')
											html.append('<a href="x-python://self.removeFont(____%s____, ____%s____, ____%s____)" class="removeButton button">' % (self.b64encode(subscription.parent.canonicalURL), self.b64encode(subscription.protocol.unsecretURL()), self.b64encode(font.uniqueID)))
											html.append('✕ #(Remove)')
											html.append('</a>')
											html.append('</div>') # installButton
											html.append('</div>') # .installButtons

											html.append('<div class="status loading right">')
											html.append('<a class="status">')
											html.append('''<img src="file://##htmlroot##/loading.gif" style="width: 50px; height: 13px; position: relative; top: 2px;">''')
											html.append('</a>')
											html.append('</div>') # .right

											html.append('<div class="more right">')
											html.append('<a class="more">')
											html.append('''<img src="file://##htmlroot##/more_lighter.svg" style="height: 8px; position: relative; top: 0px;">''')
											html.append('</a>')
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


				$("#main .font").click(function() {
					$("#main .font").removeClass('selected');
					$(this).addClass('selected');
					python("self.selectFont(____' + $(this).attr('id') + '____)");
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
				html = ''.join(map(str, html))
				html = html.replace('"', '\'')
				html = html.replace('\n', '')
				html = localizeString(html, html = True)
				html = self.replaceHTML(html)
				# print(html)
				js = '$("#main").html("' + html + '");'
				self.javaScript(js)

				# Set Sidebar Focus
				self.javaScript("$('#sidebar .publisher').removeClass('selected');")
				self.javaScript("$('#sidebar .subscription').removeClass('selected');")
				self.javaScript("$('#sidebar #%s.publisher').addClass('selected');" % b64ID)
				self.javaScript("recalcMinutesCountdown();");

				if subscription:
					self.javaScript("$('#sidebar #%s.subscription').addClass('selected');" % self.b64encode(subscription.protocol.unsecretURL()))

				self.setBadges()
				agent('amountOutdatedFonts %s' % client.amountOutdatedFonts())

				if subscription and subscription.get('currentFont'):
					self.selectFont(self.b64encode(subscription.get('currentFont')))

			self.javaScript("showMain();")


			# profile.disable()
			# profile.print_stats(sort='time')

		def fontInstalledText(self, font):

			html = []

			subscription = font.parent.parent.parent.parent.subscription
			installedVersion = subscription.installedFontVersion(font=font)

			if installedVersion:
				html.append('#(Installed): <span class="label installedVersion %s">%s</a>' % ('latestVersion' if installedVersion == font.getVersions()[-1].number else 'olderVersion', installedVersion))
			else:
				html.append('<span class="inactive notInstalled">#(Not Installed)</span>')
			return ''.join(html)


		def versionEncode(self, version):
			return version.replace('.', '_')

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

			if not client.preferences.get('currentPublisher'):
				self.javaScript("hideMain();")

			if client.preferences.get('currentPublisher') == 'pendingInvitations' and not client.preferences.get('pendingInvitations'):
				client.preferences.set('currentPublisher', '')

			if not client.preferences.get('currentPublisher'):
				self.javaScript("hideMain();")

			else:
				if not client.preferences.get('currentPublisher') and client.publishers():
					client.preferences.set('currentPublisher', client.publishers()[0].canonicalURL)
					self.setActiveSubscription(self.b64encode(client.publishers()[0].canonicalURL), self.b64encode(client.publishers()[0].subscriptions()[0].protocol.unsecretURL()))


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
						html.append('<div id="%s" class="contextmenu publisher line clear %s %s %s" lang="%s" dir="%s">' % (b64ID, _type, 'selected' if selected else '', 'expanded' if len(publisher.subscriptions()) > 1 else '', language, direction))
						html.append('<div class="name">')
						html.append('%s %s' % (name, '<img src="file://##htmlroot##/github.svg" style="position:relative; top: 3px; width:16px; height:16px;">' if publisher.get('type') == 'GitHub' else ''))
						html.append('</div>')
						html.append('<div class="reloadAnimation" style="display: %s;">' % ('block' if publisher.stillUpdating() else 'none'))
						html.append('<img src="file://##htmlroot##/reload.gif" style="position:relative; top: 2px; width:20px; height:20px;">')
						html.append('</div>')
						html.append('<div class="badges clear">')
						html.append('<div class="badge numbers outdated" style="display: %s;">' % ('block' if outdatedFonts else 'none'))
						html.append('%s' % (outdatedFonts or ''))
						html.append('</div>')
						html.append('<div class="badge numbers installed" style="display: %s;">' % ('block' if installedFonts else 'none'))
						html.append('%s' % (installedFonts or ''))
						html.append('</div>')
						html.append('</div>') # .badges

						# Identity Revealed Icon
						if len(publisher.subscriptions()) == 1:

							badges = []

							subscription = publisher.subscriptions()[0]
							if client.user() and subscription.get('revealIdentity'):
								badges.append('<div class="badge revealIdentity" style="display: block;" title="' + localizeString('#(YourIdentityWillBeRevealedTooltip)') + '"><img src="file://##htmlroot##/userIcon_Outline.svg" style="width: 16px; height: 16px; position: relative; top: 3px; margin-top: -3px;"></div>')

							if client.user() and subscription.invitationAccepted():
								badges.append('<div class="badge revealIdentity" style="display: block;" title="' + localizeString('#(IsInvitationExplanation)') + '"><img src="file://##htmlroot##/invitation.svg" style="width: 16px; height: 16px; position: relative; top: 3px; margin-top: -3px;"></div>')

							if badges:
								html.append('<div class="badges clear">')
								html.append(''.join(badges))
								html.append('</div>') # .badges

						html.append('<div class="alert noclick" style="display: %s;">' % ('block' if publisher.updatingProblem() else 'none'))
						html.append('<a href="x-python://self.displayPublisherSidebarAlert(____%s____)">' % b64ID)
						html.append('⚠️')
						html.append('</a>')
						html.append('</div>') # .alert
						html.append('</div>') # publisher
		#                html.append('</a>')

						html.append('<div class="subscriptions" style="display: %s;">' % ('block' if selected else 'none'))
						if len(publisher.subscriptions()) > 1:
							for i, subscription in enumerate(publisher.subscriptions()):

								amountInstalledFonts = subscription.amountInstalledFonts()
								amountOutdatedFonts = subscription.amountOutdatedFonts()
								if publisher.get('currentSubscription'):
									selected = subscription.protocol.unsecretURL() == publisher.subscription(publisher.get('currentSubscription')).protocol.unsecretURL()
								else:
									selected = False

								html.append('<div>')
								html.append('<div class="contextmenu subscription line clear %s" lang="%s" dir="%s" id="%s" publisherID="%s">' % ('selected' if selected else '', 'en', 'ltr', self.b64encode(subscription.protocol.unsecretURL()), b64ID))
								html.append('<div class="name">')
								html.append(subscription.name(locale=client.locale()))
								html.append('</div>')
								html.append('<div class="reloadAnimation" style="display: %s;">' % ('block' if subscription.stillUpdating() else 'none'))
								html.append('<img src="file://##htmlroot##/reload.gif" style="position:relative; top: 2px; width:20px; height:20px;">')
								html.append('</div>')
								html.append('<div class="badges clear">')
								html.append('<div class="badge numbers outdated" style="display: %s;">' % ('block' if amountOutdatedFonts else 'none'))
								html.append('%s' % amountOutdatedFonts)
								html.append('</div>')
								html.append('<div class="badge numbers installed" style="display: %s;">' % ('block' if amountInstalledFonts else 'none'))
								html.append('%s' % amountInstalledFonts)
								html.append('</div>')
								html.append('</div>') # .badges

								# Identity Revealed Icon
								badges = []

								if client.user() and subscription.get('revealIdentity'):
									badges.append('<div class="badge revealIdentity" style="display: %s;" title="' + localizeString('#(YourIdentityWillBeRevealedTooltip)') + '"><img src="file://##htmlroot##/userIcon_Outline.svg" style="width: 16px; height: 16px; position: relative; top: 3px; margin-top: -3px;"></div>')

								if client.user() and subscription.invitationAccepted():
									badges.append('<div class="badge revealIdentity" style="display: block;" title="' + localizeString('#(IsInvitationExplanation)') + '"><img src="file://##htmlroot##/invitation.svg" style="width: 16px; height: 16px; position: relative; top: 3px; margin-top: -3px;"></div>')

								if badges:
									html.append('<div class="badges clear">')
									html.append(''.join(badges))
									html.append('</div>') # .badges

								html.append('<div class="alert" style="display: %s;">' % ('block' if subscription.updatingProblem() else 'none'))
								html.append('<a href="x-python://self.displaySubscriptionSidebarAlert(____%s____)">' % self.b64encode(subscription.protocol.unsecretURL()))
								html.append('⚠️')
								html.append('</a>')
								html.append('</div>') # .alert
								html.append('</div>') # subscription
		#                        html.append('</a>')
								html.append('</div>')
								if i == 0:
									html.append('<div class="margin top"></div>')
							html.append('<div class="margin bottom"></div>')
						html.append('</div>')

						html.append('</div>') # .publisherWrapper


			if client.preferences.get('pendingInvitations'):
				html.append('<div class="headline">#(Invitations)</div>')

				selected = client.preferences.get('currentPublisher') == 'pendingInvitations'

				html.append('<div class="publisherWrapper">')
				html.append('<div id="%s" class="contextmenu publisher pendingInvitations line clear %s %s" lang="en" dir="ltr">' % ('', '', 'selected' if selected else ''))
				html.append('<div class="name">')
				html.append('#(Pending Invitations)…')
				html.append('</div>')
				html.append('<div class="badges clear">')
				html.append('<div class="badge numbers outdated" style="display: %s;">' % ('block'))
				html.append('%s' % (len(client.preferences.get('pendingInvitations'))))
				html.append('</div>')
				# html.append('<div class="badge installed" style="display: %s;">' % ('block' if installedFonts else 'none'))
				# html.append('%s' % (installedFonts or ''))
				# html.append('</div>')
				html.append('</div>') # .badges
				html.append('</div>')


	#// :not(.selected)
			html.append('''<script>



		$("#sidebar div.publisher").click(function() {

			if ($(this).hasClass('pendingInvitations')) {
				python('self.setPublisherHTML(____''' + self.b64encode('pendingInvitations') + '''____)');
			}

			else {
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

		$("#sidebar .subscription").hover(function() {
			$( this ).addClass( "hover" );
		  }, function() {
			$( this ).removeClass( "hover" );
		  }
		);

	});



	</script>''')

			html.append('</div>') #publishers


			# Print HTML
			html = ''.join(map(str, html))
			html = html.replace('"', '\'')
			html = localizeString(html, html = True)
			html = html.replace('\n', '')
			html = self.replaceHTML(html)
	#        self.log(html)
			js = '$("#sidebar").html("' + html + '");'

			self.javaScript(js)

			if client.user():
				self.javaScript('$("#userBadge #userName").html("%s");' % (client.userEmail() or 'no email found')) # (client.user()[:20] + '...')
				self.javaScript('$("#userBadge").show();')
			else:
				self.javaScript('$("#userBadge").hide();')


		def onLoad(self, event):

			self.log('MyApp.frame.onLoad()')
			self.fullyLoaded = True

			self.applyDarkMode()

			if MAC:
				self.javaScript("$('.sidebar').css('padding-top', '32px');")
				# self.javaScript("$('.panel').css('padding-left', '50px');")
				# self.javaScript("$('.panel').css('padding-top', '90px');")
				# self.javaScript("$('.panel').css('padding-bottom', '90px');")

				self.SetTitle('')

				# self.darkModeDetection = DarkModeDetection.alloc().initWithFrame_(NSMakeRect(0, 0, 40, 40))
				# self.darkModeDetection.app = self
				# print('darkModeDetection created', self.darkModeDetection)

			if WIN:
				self.javaScript("$('#atomButton .centerInner').css('padding-top', '72px');")

			self.setSideBarHTML()


			# Open drawer for newly added publisher
			if self.justAddedPublisher:
				self.handleURL(self.justAddedPublisher)
				self.justAddedPublisher = None


			if client.preferences.get('currentPublisher'):
				self.javaScript('$("#welcome").hide();')
				self.setPublisherHTML(self.b64encode(client.preferences.get('currentPublisher')))
			self.setBadges()

			if WIN and self.allowCheckForURLInFile:
				self.checkForURLInFile()

			if MAC:

				delegate = DarkModeDelegate.alloc().init()
				delegate.app = self
				NSDistributedNotificationCenter.defaultCenter().addObserver_selector_name_object_(delegate, delegate.darkModeChanged_, 'AppleInterfaceThemeChangedNotification', None)

			startWorker(self.onLoadDetached_consumer, self.onLoadDetached_worker)

			app = wx.GetApp()
			if app.startWithCommand:
				commands = app.startWithCommand.split(' ')
				if command[0] == 'javaScript':
					code = base64.b64decode(commands[1].encode()).decode()
					self.javaScript(code)


		def onLoadDetached_worker(self):

			for message in self.messages:
				self.message(message)

			# Ask to install agent
			seenDialogs = client.preferences.get('seenDialogs') or []
			if not 'installMenubarIcon' in seenDialogs:

				# Menu Bar is actually running, so don't do anything
				if not client.preferences.get('menuBarIcon'):
					dlg = wx.MessageDialog(None, localizeString("#(InstallMenubarIconQuestion)"), localizeString("#(ShowMenuBarIcon)"),wx.YES_NO | wx.ICON_QUESTION)
					dlg.SetYesNoLabels(localizeString('#(Yes)'), localizeString('#(No)'))
					result = dlg.ShowModal()
					if result == wx.ID_YES:
						installAgent()

				seenDialogs.append('installMenubarIcon')
				client.preferences.set('seenDialogs', seenDialogs)

			# Reinstall agent if outdated
			if agentIsRunning():
				agentVersion = agent('version')
				if semver.compare(APPVERSION, agentVersion) == 1:
					log('Agent is outdated (%s), needs restart.' % agentVersion)
					restartAgent(2)

			self.pullServerUpdates(force = True)


		def onLoadDetached_consumer(self, delayedResult):

			pass




		def checkForURLInFile(self):

			self.allowCheckForURLInFile = False

			from appdirs import user_data_dir
			openURLFilePath = os.path.join(user_data_dir('Type.World', 'Type.World'), 'url.txt')

			if os.path.exists(openURLFilePath):
				urlFile = open(openURLFilePath, 'r')
				url = urlFile.read().strip()
				urlFile.close()

				if self.fullyLoaded:
					self.handleURL(url)
				else:

					self.justAddedPublisher = url


				os.remove(openURLFilePath)
				time.sleep(.5)

			self.allowCheckForURLInFile = True


			return True



		def log(self, message):

			log(message)


		def setBadgeLabel(self, label):
			'''\
			Set dock icon badge
			'''
			label = str(label)
			if MAC and self._dockTile:
				self._dockTile.display()
				self._dockTile.setBadgeLabel_(label)

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
			amount = client.amountOutdatedFonts()
			if client.preferences.get('pendingInvitations'):
				amount += len(client.preferences.get('pendingInvitations'))
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



	class UpdateFrame(wx.Frame):
		def __init__(self, parent):

			super(UpdateFrame, self).__init__(parent)

			self.Bind(wx.EVT_CLOSE, self.onClose)

			if MAC:
				sparkle.checkForUpdatesInBackground()

			log('sparkle.checkForUpdateInformation() finished')

		def onClose(self, event = None):

			log('UpdateFrame.onCLose()')

			self.Destroy()



	if MAC:
		class NSAppDelegate(NSObject):
			def applicationWillFinishLaunching_(self, notification):

				log('applicationWillFinishLaunching_()')


				try:

					app = wx.GetApp()

				# 	app.CustomOnInit()
				# 	app.frame.setMenuBar()

					if app.startWithCommand == 'checkForUpdateInformation':

						from AppKit import NSApplicationActivationPolicyAccessory 
						NSApp().setActivationPolicy_(NSApplicationActivationPolicyAccessory)

				except:
					log(traceback.format_exc())

			def applicationDidFinishLaunching_(self, notification):

				log('applicationDidFinishLaunching_()')







	class MyApp(wx.App):

		def __init__(self, redirect=False, filename=None, useBestVisual=False, clearSigInt=True, startWithCommand = None):
			self.startWithCommand = startWithCommand

			super().__init__(redirect, filename, useBestVisual, clearSigInt)


		def OnPreInit(self):


			if MAC:
				if self.startWithCommand == 'checkForUpdateInformation': # Otherwise MacOpenURL() wont work
					NSApplication.sharedApplication().setDelegate_(NSAppDelegate.alloc().init())
					log('set NSAppDelegate')


		def MacOpenURL(self, url):
			
			log('MyApp.MacOpenURL(%s)' % url)

			if self.frame.fullyLoaded:
				self.frame.handleURL(url)
			else:
				self.frame.justAddedPublisher = url

			self.frame.Show()


		def OnInit(self):



			log('self.startWithCommand: %s' % self.startWithCommand)

			if self.startWithCommand:

				if self.startWithCommand == 'checkForUpdateInformation':

					if MAC:
						self.frame = UpdateFrame(None)

			else:


				if WIN:
					import winreg as wreg
					current_file = __file__
					key = wreg.CreateKey(wreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Internet Explorer\\Main\\FeatureControl\\FEATURE_BROWSER_EMULATION")
					wreg.SetValueEx(key, current_file, 0, wreg.REG_DWORD, 11001)


				frame = AppFrame(None)
				self.frame = frame

				# Window Styling
				if MAC:
					w = NSApp().mainWindow()
					w.setMovable_(False)

					from AppKit import NSLeftMouseDraggedMask, NSLeftMouseUpMask, NSScreen, NSLeftMouseUp


					class MyView(NSView):
						# def mouseDragged_(self, event):
						# 	event.window().setFrameOrigin_(NSPoint(event.window().frame().origin.x + event.deltaX(), event.window().frame().origin.y - event.deltaY()))

						def mouseDown_(self, event):

							_initialLocation = event.locationInWindow()

							while True:

								theEvent = w.nextEventMatchingMask_(NSLeftMouseDraggedMask | NSLeftMouseUpMask)
								point = theEvent.locationInWindow()
								screenVisibleFrame = NSScreen.mainScreen().visibleFrame()
								windowFrame = w.frame()
								newOrigin = windowFrame.origin


								# Get the mouse location in window coordinates.
								currentLocation = point

								# Update the origin with the difference between the new mouse location and the old mouse location.
								newOrigin.x += (currentLocation.x - _initialLocation.x)
								newOrigin.y += (currentLocation.y - _initialLocation.y)

								# Don't let window get dragged up under the menu bar
								if ((newOrigin.y + windowFrame.size.height) > (screenVisibleFrame.origin.y + screenVisibleFrame.size.height)):
									newOrigin.y = screenVisibleFrame.origin.y + (screenVisibleFrame.size.height - windowFrame.size.height)

								# Move the window to the new location
								w.setFrameOrigin_(newOrigin)

								if theEvent.type() == NSLeftMouseUp:
									break

							event.window().setFrameOrigin_(NSPoint(event.window().frame().origin.x + event.deltaX(), event.window().frame().origin.y - event.deltaY()))

						# def drawRect_(self, rect):
						# 	NSColor.yellowColor().set()
						# 	NSRectFill(rect)

					self.frame.dragView = MyView.alloc().initWithFrame_(NSMakeRect(0, 0, self.frame.GetSize()[0], 40))
					w.contentView().addSubview_(self.frame.dragView)

					self.frame.javaScript("$('.sidebar').css('padding-top', '32px');")
					self.frame.SetTitle('')

					w.setStyleMask_(1 << 0 | 1 << 1 | 1 << 2 | 1 << 3 | 1 << 15)
					w.setTitlebarAppearsTransparent_(1)

					w.setTitleVisibility_(1)
					toolbar = NSToolbar.alloc().init()
					toolbar.setShowsBaselineSeparator_(0)
					w.setToolbar_(toolbar)


				self.frame.log('MyApp.OnInit()')
				
				if MAC:
					self.frame.nsapp = NSApp()
					self.frame._dockTile = self.frame.nsapp.dockTile()


				html = ReadFromFile(os.path.join(os.path.dirname(__file__), 'htmlfiles', 'main', 'index.html'))

		#        html = html.replace('##jqueryuicss##', ReadFromFile(os.path.join(os.path.dirname(__file__), 'htmlfiles', 'main', 'css', 'jquery-ui.css')))
				html = html.replace('APPVERSION', APPVERSION)

				html = localizeString(html, html = True)
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

		


			return True

	#class MyNSApp(NSApp):


	intercomCommands = ['amountOutdatedFonts', 'startListener', 'killAgent', 'restartAgent', 'uninstallAgent', 'searchAppUpdate', 'daemonStart', 'pullServerUpdate', 'javaScript']


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



	def intercom(commands):

		lock()
		log('lock() from within intercom()')
		try:
			returnObject = None
			client.mode = 'headless'

			if not commands[0] in intercomCommands:
				log('Intercom: Command %s not registered' % (commands[0]))

			else:
				log('Intercom called with commands: %s' % commands)

				# if commands[0] == 'pullServerUpdate':

				# 	# Sync subscriptions
				# 	if not client.preferences.get('lastServerSync') or client.preferences.get('lastServerSync') < time.time() - PULLSERVERUPDATEINTERVAL:
				# 		success, message = client.downloadSubscriptions()
				# 		if success:
				# 			subscriptionsUpdatedNotification(message)


				if commands[0] == 'javaScript':

					app = wx.GetApp()

					if app:
						code = base64.b64decode(commands[1].encode()).decode()
						log(f'Calling javaScript({code})')
						app.frame.javaScript(code)

					else:
						app = MyApp(redirect = False, filename = None, startWithCommand = ' '.join(commands))
						app.MainLoop()



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
									success, message, changes = subscription.update()

									totalSuccess = totalSuccess and success   

									if not success:
										log(message)

									log('updated %s (%1.2fs)' % (subscription, time.time() - startTime))

							# Reset
							if client.allSubscriptionsUpdated():
								log('resetting timing')
								client.preferences.set('reloadSubscriptionsLastPerformed', int(time.time()))


					log('client.amountOutdatedFonts() %s' % (client.amountOutdatedFonts()))



					returnObject = client.amountOutdatedFonts()


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

				if commands[0] == 'searchAppUpdate':

					log('Started checkForUpdateInformation()')


					if MAC:
						app = MyApp(redirect = False, filename = None, startWithCommand = 'checkForUpdateInformation')
						app.MainLoop()


					if WIN:
						pywinsparkleDelegate.check_without_ui()


					log('Finished checkForUpdateInformation()')

				if commands[0] == 'daemonStart':

					agent('amountOutdatedFonts %s' % client.amountOutdatedFonts())

					unlock()
					log('unlock() from within intercom()')


		except:
			log(traceback.format_exc())

		unlock()
		log('unlock() from within intercom()')
		log('about to return reply: %s' % returnObject)
		return returnObject



	if len(sys.argv) > 1 and sys.argv[1] in intercomCommands:


		# Output to STDOUT
		log(intercom(sys.argv[1:]))

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
		client.delegate.app = app
	#	app = MyApp(redirect = False, filename = None)
		app.MainLoop()

except:
	log(traceback.format_exc())
	print(traceback.format_exc())