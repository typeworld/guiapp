# -*- coding: utf-8 -*-

import os
from ynlib.web import GetHTTP
from ynlib.files import WriteToFile
import json

j = GetHTTP('https://type.world/downloadLocalization?appID=world.type.guiapp,world.type.agent').decode()
print(type(j))

a = json.loads(j)

path = os.path.join(os.path.dirname(__file__), 'locales', 'localization.json')
WriteToFile(path, json.dumps(a))


print(j)

a = json.loads(j)

print('Updated localization')
