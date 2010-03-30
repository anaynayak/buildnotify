#!/usr/bin/env python

from setuptools import setup

setup (name='BuildNotify',
       version='0.2.5',
       description='Cruise Control build monitor for Windows/Linux/Mac',
       keywords='cctray ccmenu buildnotify ubuntu linux cruisecontrol continuous integration ci',
       author='Anay Nayak',
       requires = ['pytz'],
       author_email='anayak007@gmail.com',
       url = "http://bitbucket.org/Anay/buildnotify/",
       license='GPL v3',
       long_description = 'BuildNotify is a cruise control system tray monitor which works on Windows/Linux/Mac.' +
       'It was largely inspired from CCMenu and lets you monitor multiple continuous integration servers with' +
       'customizable build notifications for all projects',
       packages=['buildnotifylib'],
       scripts = ['buildnotifyapplet.py'])

