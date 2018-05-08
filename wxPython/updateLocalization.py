# -*- coding: utf-8 -*-

import os
from ynlib.web import GetHTTP
from ynlib.files import WriteToFile

json = GetHTTP('https://type.world/downloadLocalization?appID=world.type.guiapp')



WriteToFile(os.path.join(os.path.dirname(__file__), 'locales', 'localization.py'), ("localization = '%s'" % json))


print(json)

print('Updated localization')
