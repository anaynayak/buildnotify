#!/usr/bin/env python

from setuptools import setup
import sys
import os
import user

print "Environment details:"
print sys.version
print sys.platform
print sys.path

print "Installing applet:"
setup (name='BuildNotify',
       version='0.1.1',
       description='Cruise Control build monitor for Windows/Linux/Mac',
       keywords='cctray ccmenu buildnotify ubuntu linux cruisecontrol continuous integration ci',
       author='Anay Nayak',
       requires = ['pytz'],
       author_email='anayak007@gmail.com',
       url = "http://bitbucket.org/Anay/buildnotify/",
       license='GPL v3',
       long_description = 'BuildNotify is a system tray application which works on Windows/Linux/Mac. It was largely inspired from CCMenu',
       packages=['buildnotifylib'],
       scripts = ['buildnotifyapplet.py'])

