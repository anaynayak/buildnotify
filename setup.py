#!/usr/bin/env python

from setuptools import setup

setup(name='BuildNotify',
      version="1.0.0",
      description='Cruise Control build monitor for Windows/Linux/Mac',
      keywords='cctray ccmenu buildnotify ubuntu linux cruisecontrol continuous integration ci',
      author='Anay Nayak',
      requires=['pytz'],
      author_email='anayak007@gmail.com',
      url="http://bitbucket.org/Anay/buildnotify/",
      license='GPL v3',
      long_description='BuildNotify is a cruise control system tray monitor which works on Windows/Linux/Mac.' +
                       'It was largely inspired from CCMenu and lets you monitor multiple continuous integration '
                       'servers with customizable build notifications for all projects',
      packages=['buildnotifylib', 'buildnotifylib.core', 'buildnotifylib.generated'],
      package_dir={'buildnotifylib': 'buildnotifylib'},
      data_files=[
          ('share/applications', ['buildnotify.desktop']),
          ('share/pixmaps', ['icons/buildnotify.svg']),
      ],
      classifiers=[
          'Intended Audience :: Developers',
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Topic :: Software Development',
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'Intended Audience :: End Users/Desktop',
          'Environment :: X11 Applications :: Qt',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: User Interfaces',
          'Topic :: Software Development :: Widget Sets'
      ],
      scripts=['buildnotifyapplet.py'])
