from setuptools import setup
import os


version = '0.1.3'

APP = ['appbadge.py']
DATA_FILES = []
OPTIONS = {
#           'frameworks': ['Python.framework'],
           'plist': {
                'NSPrincipalClass': 'AppBadge',
                },
           'extension': '.docktileplugin',
           'semi_standalone': True,
           }

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

