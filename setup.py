#!/usr/bin/env python

from os import getenv

from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


def version():
    return getenv('BUILD_VERSION', "2.0.0")


setup(name='BuildNotify',
      version=version(),
      description='Cruise Control build monitor for Windows/Linux/Mac',
      keywords='cctray ccmenu buildnotify ubuntu linux cruisecontrol continuous integration ci',
      author='Anay Nayak',
      install_requires=['pytz', 'PyQt5', 'python-dateutil', 'requests'],
      author_email='anayak007@gmail.com',
      url="https://anaynayak.github.io/buildnotify/",
      license='GPL v3',
      long_description=readme(),
      packages=['buildnotifylib', 'buildnotifylib.core',
                'buildnotifylib.generated'],
      package_dir={'buildnotifylib': 'buildnotifylib'},
      data_files=[
          ('share/applications', ['buildnotify.desktop']),
          ('share/pixmaps', ['buildnotify.svg']),
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
