#!/usr/bin/python
# -*- coding: utf-8 -*-

###########################################################################################################
#
#
#   General Plugin
#
#   Read the docs:
#   https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/General%20Plugin
#
#
###########################################################################################################


#from AppKit import NSDockTilePlugIn

import traceback
from AppKit import NSLog

try:

    import objc
    NSDockTilePlugIn = objc.protocolNamed("NSDockTilePlugIn")
    #
    class AppBadge(NSObject):
        __pyobjc_protocols__ = [NSDockTilePlugIn]

        def setDockTile_(self, dockTile):
            dockTile.setBadgeLabel_(str(3))

except:
    NSLog('Type.World: ' + traceback.format_exc())