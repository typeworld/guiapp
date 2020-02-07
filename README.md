# Type.World GUI App

Compiled versions of this app are available [here](https://type.world/app/).

If you want to run this code directly, you need to install [wxPython](https://wiki.wxpython.org/How%20to%20install%20wxPython) as well as the Python libraries [typeWorld](https://github.com/typeWorld/api/tree/master/Python/Lib/typeWorld) and [ynlib](https://github.com/yanone/ynlib).

# Dependencies

`pip install wxPython babel`

Further:

`pip install modulegraph macholib dmgbuild`

# Translations

If you care about translating Type.World’s user interface, please refrain from adding your translation to the `json` file and then PR-ing it. The translations are maintained in an online collaborative database on [type.world](https://type.world), which isn’t finished yet. Adding translations is slated for the Beta phase which starts end of January 2020.

Instead, please get in touch and I'll note your participation:

* English/German: Yanone
* Spanish: [Adolfo Jayme-Barrientos](https://github.com/fitojb)

# Build

Install "Developer ID Certificate" code signing certificate through XCode -> Account.

# Test

Run compiled app in Python virtual environment to check for missing dependencies.