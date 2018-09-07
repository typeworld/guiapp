from setuptools import setup
import os


APP = ['cefpython.py']
DATA_FILES = []
OPTIONS = {'argv_emulation': False, # this puts the names of dropped files into sys.argv when starting the app.
           }





setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)


