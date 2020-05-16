# System imports

import os, sys

# Adjust __file__ for Windows executable
try:
	__file__ = os.path.abspath(__file__)

except:
	__file__ = sys.executable

sys.path.insert(0, os.path.dirname(__file__))



from intercom import *
import intercom
import typeworld.client

class IntercomDelegate(intercom.IntercomDelegate):
	def exitSignalCalled(self):
		quitIcon()

global intercomApp
intercomApp = TypeWorldApp(delegate = IntercomDelegate())

log('Start %s' % intercomApp)

try:


	import locales

	def getClient():

		global prefDir

		if WIN:
			prefFile = os.path.join(prefDir, 'preferences.json')
			prefs = typeworld.client.JSON(prefFile)
		else:
			prefs = typeworld.client.AppKitNSUserDefaults('world.type.guiapp')

		client = typeworld.client.APIClient(preferences = prefs, online = False)

		return client

	client = getClient()


	def localize(key, html = False):
		string = locales.localize(key, client.locale())
		if html:
			string = string.replace('\n', '<br />')
		return string


	def openApp():

		log('openApp()')

		global intercomApp
		intercomApp.open()


	def setStatus(amountOutdatedFonts, notification = False):

		if amountOutdatedFonts > 0:
			icon.icon = image_notification

			if notification:
				intercomApp.notification(localize('XFontUpdatesAvailable').replace('%numberOfFonts%', str(amountOutdatedFonts)), localize('Click to open Type.World app'))

		else:
			icon.icon = image

	def getAmountOutdatedFonts(force = False):
		
		if force:
			return intercomApp.speak('amountOutdatedFonts force')
		else:
			return intercomApp.speak('amountOutdatedFonts')

	def searchAppUpdate():
		return intercomApp.speak('searchAppUpdate')

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

		if not intercomApp.isOpen():

			# Has never been checked, set to long time ago
			if not client.preferences.get('appUpdateLastSearched'):
				client.preferences.set('appUpdateLastSearched', int(time.time()) - 30 * 24 * 60 * 60) # set to one month ago

			if int(client.preferences.get('appUpdateLastSearched')) < int(time.time()) - UPDATESEARCHINTERVAL: # 24 * 60 * 60
				log('Calling searchAppUpdate()')
				time.sleep(15)
				searchAppUpdate()
				client.preferences.set('appUpdateLastSearched', int(time.time())) # set to now

		# # Sync subscriptions
		# if not client.preferences.get('lastServerSync') or client.preferences.get('lastServerSync') < time.time() - PULLSERVERUPDATEINTERVAL:
		# 	intercomApp.speak('pullServerUpdate')


	# Prevent second start
	if MAC and not appIsRunning('world.type.agent') or WIN and not appIsRunning('TypeWorld Taskbar Agent.exe'):


		# Set up tray icon
		from pystray import MenuItem as item
		import pystray

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


		menu = (
			item(localize('Open Type.World App'), openApp, default=True),
			item(localize('Check for font updates now'), checkForUpdates),
		)#, pystray.Menu.SEPARATOR, item('Quit', quitIcon))

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
					intercomApp.open()

			nsApp = NSApplication.sharedApplication()
			delegate = Delegate.alloc().init()
			nsApp.setDelegate_(delegate)
			nsApp.setActivationPolicy_(NSApplicationActivationPolicyProhibited)

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

				intercomApp.speak('daemonStart')

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

		log('About to start icon')

		if WIN:
			icon.run(sigint=quitIcon)

		log('Icon started')

		if MAC:
			from PyObjCTools import AppHelper
			AppHelper.runEventLoop()

except:
	log(traceback.format_exc())