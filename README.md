# Type.World GUI App


[![AppVeyor Build Status](https://ci.appveyor.com/api/projects/status/github/typeworld/guiapp?svg=true)](https://ci.appveyor.com/project/typeworld/guiapp)
[![codecov](https://codecov.io/gh/typeworld/guiapp/branch/master/graph/badge.svg)](https://codecov.io/gh/typeworld/guiapp)

Compiled versions of this app are available [here](https://type.world/app/).

If you want to run this code directly, you need to install [wxPython](https://wiki.wxpython.org/How%20to%20install%20wxPython) as well as the Python libraries [typeworld](https://github.com/typeworld/api/tree/master/Python/Lib/typeworld) and [ynlib](https://github.com/yanone/ynlib).

# Dependencies

`pip install wxPython babel`

Further:

`pip install modulegraph macholib dmgbuild pystray`

# Translations

If you care about translating Type.World’s user interface, please refrain from adding your translation to the `json` file and then PR-ing it. The translations are maintained in an online collaborative database on [type.world](https://type.world), which isn’t finished yet. Adding translations is slated for the Beta phase which starts end of January 2020.

Instead, please get in touch and I'll note your participation:

* English/German: Yanone
* Spanish: [Adolfo Jayme-Barrientos](https://github.com/fitojb)

# Build

Install "Developer ID Certificate" code signing certificate through XCode -> Account.

# Test

Run compiled app in Python virtual environment to check for missing dependencies.

# Code Coverage Tests

I can’t get `codecov` to run on AppVeyor on Mac at this point because running `app.py` fails with:
```
This program needs access to the screen. Please run with a
Framework build of python, and only when you are logged in
on the main display of your Mac.```

They suggest to use `pythonw` which also I couldn't get to run for Python 3.

So instead I currently run coverage tests locally:
`./codecov.sh`

Coverage tests should be run directly after each git push, as the locally executed code will be mapped
to the current git version. Maybe I can get this to work automatically after each push.

The Windows selftest runs fine on AppVeyor, so this is added automatically.