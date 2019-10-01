# -*- coding: utf-8 -*-


from AppKit import NSDockTilePlugIn


class AppBadge(NSDockTilePlugIn):

	def setDockTile_(self, dockTile):

		if dockTile:
			dockTile.setBadgeLabel_('X')

	# def setDockTile(self, dockTile):

	# 	if dockTile:
	# 		dockTile.setBadgeLabel_('X')
