# System imports

import threading, time, sys, os, traceback, plistlib
from threading import Thread
import platform

WIN = platform.system() == 'Windows'
MAC = platform.system() == 'Darwin'

if WIN:
	import ctypes

DEBUG = True
APPVERSION = 'n/a'

LOOPDURATION = 60
UPDATESEARCHINTERVAL = 24 * 60 * 60
CURRENTLYUPDATING = False
PULLSERVERUPDATEINTERVAL = 60

# Adjust __file__ to point to executable on runtime
try:
	__file__ = os.path.abspath(__file__)
except:
	__file__ = sys.executable

sys.path.insert(0, os.path.dirname(__file__))

if WIN:
	from appdirs import user_data_dir
	prefDir = user_data_dir('Type.World', 'Type.World')
elif MAC:
	prefDir = os.path.expanduser('~/Library/Preferences/')

import logging
if WIN and DEBUG:
	filename = os.path.join(prefDir, os.path.basename(__file__) + '.txt')
	if os.path.exists(filename):
		os.remove(filename)
	logging.basicConfig(filename=filename,level=logging.DEBUG)

def log(message):
	if DEBUG:
		if WIN:
			logging.debug(message)
		if MAC:
			from AppKit import NSLog
			NSLog('Type.World Agent: %s' % message)

log('Start')

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


try:


	# This is shit as it requires separate internet access permissions for the agent (Little Snitch).

	# if MAC:
	# 	# URL to Appcast.xml, eg. https://yourserver.com/Appcast.xml
	# 	APPCAST_URL = 'https://type.world/downloads/guiapp/appcast.xml'
	# 	# Path to Sparkle's "Sparkle.framework" inside your app bundle

	# 	if '.app' in os.path.dirname(__file__):
	# 		SPARKLE_PATH = os.path.join(os.path.dirname(__file__), '..', 'Frameworks', 'Sparkle.framework')
	# 	else:
	# 		SPARKLE_PATH = '/Users/yanone/Code/Sparkle/Sparkle.framework'

	# 	from objc import pathForFramework, loadBundle
	# 	sparkle_path = pathForFramework(SPARKLE_PATH)
	# 	objc_namespace = dict()
	# 	loadBundle('Sparkle', objc_namespace, bundle_path=sparkle_path)

	# 	from AppKit import NSBundle
	# 	bundle = NSBundle.bundleWithIdentifier_('world.type.guiapp')
	# 	sparkle = objc_namespace['SUUpdater'].updaterForBundle_(bundle)
	# #       sparkle.setAutomaticallyDownloadsUpdates_(True)
	# 	NSURL = objc_namespace['NSURL']
	# 	sparkle.setFeedURL_(NSURL.URLWithString_(APPCAST_URL))


	# 	from AppKit import NSObject
	# 	class SparkleUpdateDelegate(NSObject):
	# 		def updater_didFindValidUpdate_(self, updater, appcastItem):
	# 			log('sparkleUpdateDelegate.updater_didFindValidUpdate_()')
	# 		def updaterDidNotFindUpdate_(self, updater):
	# 			log('sparkleUpdateDelegate.updaterDidNotFindUpdate_()')

	# 	sparkleDelegate = SparkleUpdateDelegate.alloc().init()
	# 	sparkle.setDelegate_(sparkleDelegate)
	# 	sparkle.checkForUpdateInformation()



	# App-specific imports

	import locales


	if MAC:
		import objc 
		from AppKit import NSObject, NSApp, NSLog, NSApplication, NSUserNotification, NSUserNotificationCenter, NSApplicationActivationPolicyProhibited, NSRunningApplication, \
			NSApplicationActivateAllWindows, NSWorkspace, NSImage, NSBundle
	if WIN:
		import pystray._util.win32 as win32
		import win32gui, win32con


	import signal

	def exit_signal_handler(signal, frame):

		# template = zroya.Template(zroya.TemplateType.ImageAndText4)
		# template.setFirstLine('Quit Signal')
		# # template.setSecondLine(str(signal))
		# # template.setThirdLine(str(frame))
		# expiration = 24 * 60 * 60 * 1000 # one day
		# template.setExpiration(expiration) # One day
		# notificationID = zroya.show(template)

		log('exit_signal_handler()')
		log(signal)
		log(frame)

		quitIcon()

	#signal.signal(signal.SIGBREAK, exit_signal_handler)
	signal.signal(signal.SIGTERM, exit_signal_handler)
	signal.signal(signal.SIGINT, exit_signal_handler)





	from multiprocessing.connection import Client

	from ynlib.system import Execute
	import typeWorldClient

	if MAC:
		mainAppPath = str(NSWorkspace.sharedWorkspace().URLForApplicationWithBundleIdentifier_('world.type.guiapp'))[7:]
	if WIN:
		mainAppPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'TypeWorld.exe'))

	if WIN:
		import zroya
		zroya.init("Type.World", "Type.World", "Type.World", "guiapp", "Version")



	def getClient():

		global prefDir

		if WIN:
			prefFile = os.path.join(prefDir, 'preferences.json')
			prefs = typeWorldClient.JSON(prefFile)
		else:
			prefs = typeWorldClient.AppKitNSUserDefaults('world.type.guiapp')

		client = typeWorldClient.APIClient(preferences = prefs)

		return client

	client = getClient()


	log('mainAppPath: %s' % mainAppPath)

	log(client)


	def localize(key, html = False):
		string = locales.localize('world.type.agent', key, client.locale())
		if html:
			string = string.replace('\n', '<br />')
		return string


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

	if MAC:
		plist = plistlib.readPlist(os.path.join(os.path.dirname(__file__), '..', 'Info.plist'))
		APPVERSION = plist['CFBundleShortVersionString']

	elif WIN:
		APPVERSION = getFileProperties(__file__)['StringFileInfo']['ProductVersion'].strip()

		if len(APPVERSION.split('.')) == 4:
			APPVERSION = '.'.join(APPVERSION.split('.')[0:-1])

	#	APPVERSION += '-' + BUILDSTAGE


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

	# Prevent second start
	if not appIsRunning('world.type.agent'):


		def setStatus(amountOutdatedFonts, notification = False):

			if amountOutdatedFonts > 0:
				icon.icon = image_notification

				if notification:

					if MAC:
						notification = NSUserNotification.alloc().init()
						notification.setTitle_(localize('XFontUpdatesAvailable').replace('%numberOfFonts%', str(amountOutdatedFonts)))
						notification.setInformativeText_(localize('Click to open Type.World app'))
						notificationCenter.deliverNotification_(notification)

					if WIN:
						template = zroya.Template(zroya.TemplateType.ImageAndText4)
						template.setFirstLine(localize('XFontUpdatesAvailable').replace('%numberOfFonts%', str(amountOutdatedFonts)))
						expiration = 24 * 60 * 60 * 1000 # one day
						if int(client.preferences.get('reloadSubscriptionsInterval')) != -1:
							expiration = int(client.preferences.get('reloadSubscriptionsInterval')) * 1000
						template.setExpiration(expiration) # One day
						template.addAction(localize('Open Type.World App'))
						notificationID = zroya.show(template) # , on_action=onAction

			else:
				icon.icon = image


		def execute(command):

			log('about to execute %s' % (command))

			# if WIN:

			# if WIN:
			#     ctypes.windll.shell32.ShellExecuteW(None, None, command, parameter, None, 1)


			from ynlib.system import Execute
			if WIN:
				Execute("cmd /min /C \"set __COMPAT_LAYER=RUNASINVOKER && start \"\" %s\"" % command)
			if MAC:
				Execute(command)


		def getAmountOutdatedFonts(force = False):
			
			if force:
				return replyFromMothership('amountOutdatedFonts force')
			else:
				return replyFromMothership('amountOutdatedFonts')

		def searchAppUpdate():
			CURRENTLYUPDATING = True
			return replyFromMothership('searchAppUpdate')
			CURRENTLYUPDATING = False

		def replyFromMothership(command):

			log('replyFromMothership(%s)' % command)

			reply = None

			if WIN:
				ID = 'TypeWorld.exe'
			if MAC:
				ID = 'world.type.guiapp'


			if appIsRunning(ID):

				log('app is running, connecting to host')

				address = ('localhost', 65500)
				conn = Client(address)
				conn.send(command)
				reply = conn.recv()

				conn.close()

			else:

				log('app is not running')

				amountOutdatedFonts = 0
				if mainAppPath:

					if WIN:
						log('about to start app with startListener command')

						call = '"%s" startListener' % mainAppPath

						startListenerThread = Thread(target=execute, args=(call, ))
						startListenerThread.start()

						log('started app with startListener command')

						loop = 0
						while True:

							if PID('TypeWorld.exe'):
								break

							time.sleep(.5)
							loop += 1

						time.sleep(.5)

						address = ('localhost', 65500)
						conn = Client(address)
						conn.send(command)
						reply = conn.recv()
						conn.close()

						log('received reply after %s loops' % loop)

						address = ('localhost', 65500)
						conn = Client(address)
						conn.send('closeListener')
						conn.close()

						log('shut down app with closeListener')

					if MAC:
						log('about to start app with %s command' % command)
						call = '"%s" %s' % (os.path.join(mainAppPath, 'Contents', 'MacOS', 'Type.World'), command)
						log('call: %s' % call)
						response = Execute(call).strip()
						if response:
							log(response)
						reply = response


			log('replyFromMothership(%s) finished' % command)

			return reply


		def checkForUpdates():
			amountOutdatedFonts = getAmountOutdatedFonts(force = True)
			setStatus(amountOutdatedFonts, notification = True)

		def autoReloadSubscriptions(force = True):

			log('started autoReloadSubscriptions()')

			client = getClient()

			log(client)

			# Preference is set to check automatically
			if (client.preferences.get('reloadSubscriptionsInterval') and int(client.preferences.get('reloadSubscriptionsInterval') != -1) or force):

				# Has never been checked, set to long time ago
				if not client.preferences.get('reloadSubscriptionsLastPerformed'):
					client.preferences.set('reloadSubscriptionsLastPerformed', int(time.time()) - int(client.preferences.get('reloadSubscriptionsInterval')) - 10)

				# See if we should check now

				log('reloadSubscriptionsLastPerformed: %s' % client.preferences.get('reloadSubscriptionsLastPerformed'))
				log('reloadSubscriptionsInterval: %s' % client.preferences.get('reloadSubscriptionsInterval'))
				if (int(client.preferences.get('reloadSubscriptionsLastPerformed')) < int(time.time()) - int(client.preferences.get('reloadSubscriptionsInterval'))) or force:

					setStatus(getAmountOutdatedFonts(), notification = True)


			# APP UPDATE

			if MAC and not appIsRunning('world.type.guiapp') or WIN and not appIsRunning('TypeWorld.exe'):

				# Has never been checked, set to long time ago
				if not client.preferences.get('appUpdateLastSearched'):
					client.preferences.set('appUpdateLastSearched', int(time.time()) - 30 * 24 * 60 * 60) # set to one month ago

				if int(client.preferences.get('appUpdateLastSearched')) < int(time.time()) - UPDATESEARCHINTERVAL: # 24 * 60 * 60
					log('Calling searchAppUpdate()')
					time.sleep(15)
					searchAppUpdate()
					client.preferences.set('appUpdateLastSearched', int(time.time())) # set to now

			# Sync subscriptions
			if not client.preferences.get('lastServerSync') or client.preferences.get('lastServerSync') < time.time() - PULLSERVERUPDATEINTERVAL:
				replyFromMothership('pullServerUpdate')



		# Set up tray icon
		from pystray import MenuItem as item
		import pystray

		def onClick(data):
			openApp()

		def onAction(nid, action_id):
			if action_id == 0:
				openApp()


		def openApp(url = None):

			while CURRENTLYUPDATING:
				time.sleep(.5)

			if WIN:

				pid = PID('TypeWorld.exe')

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


			if MAC:
				ID = 'world.type.guiapp'
				# App is running, so activate it
				apps = list(NSRunningApplication.runningApplicationsWithBundleIdentifier_(ID))
				if apps:
					mainApp = apps[0]
					mainApp.activateWithOptions_(1 << 1)

				# Not running, launch it
				else:
					NSWorkspace.sharedWorkspace().launchAppWithBundleIdentifier_options_additionalEventParamDescriptor_launchIdentifier_(ID, 0, None, None)

		def closeListener():
			address = ('localhost', 65501)
			myConn = Client(address)
			myConn.send('closeListener')
			myConn.close()


		def quitIcon():

			closeListenerThread = Thread(target=closeListener)
			closeListenerThread.start()

			time.sleep(1)

			t.stop()
			t.join()


			icon.stop()

			# if MAC:
			# 	app.terminate_(None)

			# if WIN:
			# 	exit()



		menu = (item(localize('Open Type.World App'), openApp, default=True), item(localize('Check for font updates now'), checkForUpdates))#, pystray.Menu.SEPARATOR, item('Quit', quitIcon))
		if MAC:
			image = NSImage.alloc().initWithContentsOfFile_(NSBundle.mainBundle().pathForResource_ofType_('MacSystemTrayIcon', 'pdf'))
			image.setTemplate_(True)
			image_notification = NSImage.alloc().initWithContentsOfFile_(NSBundle.mainBundle().pathForResource_ofType_('MacSystemTrayIcon_Notification', 'pdf'))
			image_notification.setTemplate_(True)
		if WIN:

			image = win32.LoadImage(
					None,
					os.path.join(os.path.dirname(__file__), 'icon', 'TaskbarIcon.ico'),
					win32.IMAGE_ICON,
					0,
					0,
					win32.LR_DEFAULTSIZE | win32.LR_LOADFROMFILE)
			image_notification = win32.LoadImage(
					None,
					os.path.join(os.path.dirname(__file__), 'icon', 'TaskbarIcon_Notification.ico'),
					win32.IMAGE_ICON,
					0,
					0,
					win32.LR_DEFAULTSIZE | win32.LR_LOADFROMFILE)

		icon = pystray.Icon("Type.World", image, "Type.World", menu)


		if MAC:
			class Delegate(NSObject):
				def applicationDidFinishLaunching_(self, aNotification):
					icon.run()

			NSUserNotificationCenterDelegate = objc.protocolNamed('NSUserNotificationCenterDelegate')
			class NotificationDelegate(NSObject, protocols=[NSUserNotificationCenterDelegate]):

				def userNotificationCenter_didActivateNotification_(self, center, aNotification):
					openApp()

			app = NSApplication.sharedApplication()
			delegate = Delegate.alloc().init()
			app.setDelegate_(delegate)
			app.setActivationPolicy_(NSApplicationActivationPolicyProhibited)

			notificationCenter = NSUserNotificationCenter.defaultUserNotificationCenter()
			notificationCenterDelegate = NotificationDelegate.alloc().init()
			notificationCenter.setDelegate_(notificationCenterDelegate)


		class StoppableThread(threading.Thread):
			"""Thread class with a stop() method. The thread itself has to check
			regularly for the stopped() condition."""

			def __init__(self, *args, **kwargs):
				super(StoppableThread, self).__init__(*args, **kwargs)
				self._stopped = threading.Event()

			def stop(self):
				self._stopped.set()

			def stopped(self):
				return self._stopped.isSet()

			def run(self):

				log('beginning of run()')

				# First run
#				autoReloadSubscriptions(force = False)
				setStatus(getAmountOutdatedFonts(), notification = False)

				replyFromMothership('daemonStart')

				log('about to start inner loop')

				while True:

#					log(self.counter)

					if self.stopped():
						return

					if self.counter == LOOPDURATION:
						log('calling autoReloadSubscriptions() from inner loop')

						if WIN:
							path = os.path.expanduser('~/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Type.World.lnk')
							if os.path.exists(path):
								os.remove(path)

						autoReloadSubscriptions(force = False)
						self.counter = 0


					else:
						self.counter += 1

						if WIN:
							win32gui.PumpWaitingMessages()

					time.sleep(1)



		t = StoppableThread()
		t.counter = 0
		t.start()
		log('started main loop thread')

		intercomCommands = ['amountOutdatedFonts', 'version', 'quit']

		def intercom(commands):

			if not commands[0] in intercomCommands:
				log('Intercom: Command %s not registered' % (commands[0]))
				return

			if commands[0] == 'amountOutdatedFonts':

				if len(commands) > 1:
					amountOutdatedFonts = int(commands[1])
					setStatus(amountOutdatedFonts)

			if commands[0] == 'version':

				return APPVERSION

			if commands[0] == 'quit':
				quitIcon()


		def listenerFunction():
			from multiprocessing.connection import Listener

			address = ('localhost', 65501)
			listener = Listener(address)

			log('Server started')

			while True:
				conn = listener.accept()
				command = conn.recv()
				commands = command.split(' ')

				if command == 'closeListener':
					conn.close()
					break

				response = None

				if commands[0] in intercomCommands:
					response = intercom(commands)
					conn.send(response)

				conn.close()


			listener.close()

		log('About to start listener server')


		listenerThread = Thread(target=listenerFunction)
		listenerThread.start()


		ENDSESSION_CLOSEAPP = 0x1

		# def restartManagerListenerFunction():

		# 	while True:
		# 		msg = win32gui.GetMessage(None, 0, 0)

		# 		if msg:

		# 			if msg.message == win32con.WM_QUERYENDSESSION:
		# 				if msg.lparam == ENDSESSION_CLOSEAPP:

		# 			win32gui.DispatchMessage(msg)
		# 			if msg and msg.message == win32con.WM_QUIT:
		# 				return msg.wparam



		# restartManagerListenerThread = Thread(target=restartManagerListenerFunction)
		# restartManagerListenerThread.start()


		log('About to start icon')


		def exit_signal_handler(signal, frame):

			# template = zroya.Template(zroya.TemplateType.ImageAndText4)
			# template.setFirstLine('Quit Signal')
			# # template.setSecondLine(str(signal))
			# # template.setThirdLine(str(frame))
			# expiration = 24 * 60 * 60 * 1000 # one day
			# template.setExpiration(expiration) # One day
			# notificationID = zroya.show(template)

			quitIcon()


		def setupExitHandlers():

			signal.signal(signal.SIGBREAK, exit_signal_handler)
			signal.signal(signal.SIGTERM, exit_signal_handler)
			signal.signal(signal.SIGINT, exit_signal_handler)

		#setupExitHandlers()




		if WIN:
			""" Testing Windows shutdown events """

			import win32con
			import win32api
			import win32gui
			import sys
			import time

			def log_info(msg):
				""" Prints """
				print(msg)
				f = open("c:\\test.log", "a")
				f.write(msg + "\n")
				f.close()

			def wndproc(hwnd, msg, wparam, lparam):
				
				log("wndproc: %s" % msg)
				log("wndproc wparam: %s" % wparam)
				log("wndproc lparamparam: %s" % lparam)

				if msg == win32con.WM_QUERYENDSESSION and lparam == 1:
					quitIcon()
					return True

				if msg == win32con.WM_ENDSESSION:
					quitIcon()
					return 0

				if msg == win32con.WM_CLOSE:
					quitIcon()

				if msg == win32con.WM_DESTROY:
					quitIcon()

				if msg == win32con.WM_QUIT:
					quitIcon()


			log("*** STARTING ***")
			hinst = win32api.GetModuleHandle(None)
			wndclass = win32gui.WNDCLASS()
			wndclass.hInstance = hinst
			wndclass.lpszClassName = "testWindowClass"
			messageMap = { win32con.WM_QUERYENDSESSION : wndproc,
						   win32con.WM_ENDSESSION : wndproc,
						   win32con.WM_QUIT : wndproc,
						   win32con.WM_DESTROY : wndproc,
						   win32con.WM_CLOSE : wndproc }

			wndclass.lpfnWndProc = messageMap

			# try:
			myWindowClass = win32gui.RegisterClass(wndclass)
			hwnd = win32gui.CreateWindowEx(win32con.WS_EX_LEFT,
										 myWindowClass, 
										 "testMsgWindow", 
										 0, 
										 0, 
										 0, 
										 win32con.CW_USEDEFAULT, 
										 win32con.CW_USEDEFAULT, 
										 0, # not win32con.HWND_MESSAGE (see https://stackoverflow.com/questions/1411186/python-windows-shutdown-events)
										 0, 
										 hinst, 
										 None)
			# except Exception, e:
			# 	log_info("Exception: %s" % str(e))


			if hwnd is None:
				log("hwnd is none!")
			else:
				log("hwnd: %s" % hwnd)

			# while True:
			# 	win32gui.PumpWaitingMessages()
			# 	time.sleep(1)

		if WIN:
			icon.run(sigint=exit_signal_handler)

		log('Icon started')


		if MAC:
			from PyObjCTools import AppHelper
			AppHelper.runEventLoop()

except:
	log(traceback.format_exc())