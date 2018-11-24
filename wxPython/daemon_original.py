import threading, time, sys, os, traceback, ctypes, plistlib
from threading import Thread

import platform
WIN = platform.system() == 'Windows'
MAC = platform.system() == 'Darwin'

DEBUG = True
APPVERSION = 'n/a'



# Adjust __file__ to point to executable on runtime
try:
	__file__ = os.path.abspath(__file__)
except:
	__file__ = sys.executable

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

		while True:

			if self.stopped():
				return

			time.sleep(1)


t = StoppableThread()
t.counter = 0
t.start()


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

	t.stop()

signal.signal(signal.SIGBREAK, exit_signal_handler)
signal.signal(signal.SIGTERM, exit_signal_handler)
signal.signal(signal.SIGINT, exit_signal_handler)

log('end of loop')
