#!/usr/bin/env python

from setuptools import setup
import sys, os

packages_path = os.path.abspath(os.path.dirname(__file__))

datafiles = []
icon_files = []
doc_files = []

prefix = sys.prefix + '/'
ipath_desktop_file = '%sshare/applications/' % prefix
ipath_icons = '%sshare/pixmaps/' % prefix
path_images = packages_path + '/icons/'
ipath_docs = '%sshare/doc/buildnotify/' % prefix

def append_if_valid(target, tuple):
    if os.path.exists(tuple[0]):
        target.append(tuple)
        
append_if_valid(datafiles, (ipath_desktop_file,[packages_path + '/buildnotify.desktop']))

docs = ['AUTHORS','INSTALL','LICENSE','README','THANKS']
for doc in docs:
	doc_files.append(packages_path + '/' + doc)

icons = ['buildnotify.png']
for icon in icons:
    icon_files.append(path_images + icon)

append_if_valid(datafiles, (ipath_icons, icon_files))
append_if_valid(datafiles, (ipath_docs, doc_files))

setup (name='BuildNotify',
       version='0.2.4',
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
       data_files = datafiles,
       scripts = ['buildnotifyapplet.py'])

