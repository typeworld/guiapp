# -*- coding: utf-8 -*-

import os
from ynlib.web import GetHTTP
from ynlib.files import WriteToFile

json = GetHTTP('https://type.world/type.world/downloadLocalization?appID=world.type.guiapp')
WriteToFile(os.path.join(os.path.dirname(__file__), 'locales', 'content.json'), json)

print 'Updated localization'
