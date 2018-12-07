#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from cx_Freeze import setup, Executable
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

options = {
	'build': {'build_exe' : 'dysin/build'},
    'build_exe': {
		'build_exe' : 'dysin',
        'optimize': '2',
		'include_files': ('res', 'sav')
    },
}

executables = [
    Executable('run.pyw', base=base,  icon = "headicon.ico", targetName = "dysin.exe")
]

include_files=["headicon.ico"]

setup(name='Dysin',
      version='1.02',
      description='Desktop Widget',
      options=options,
      executables=executables, requires=['pymedia', 'PySide']
      )