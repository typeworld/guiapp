# -*- coding: utf-8 -*-


from AppKit import NSObject

print('started...')

class AppBadge(NSObject):

	def setDockTile_(self, dockTile):

		if dockTile:
			dockTile.setBadgeLabel_('X')

	def setDockTile(self, dockTile):

		if dockTile:
			dockTile.setBadgeLabel_('X')
