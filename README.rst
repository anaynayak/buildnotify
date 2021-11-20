BuildNotify
===========

BuildNotify is a CCMenu/CCTray equivalent for Ubuntu. It resides in your system tray and notifies you of the build status for different projects on your continuous integration servers. BuildNotify is largely inspired from the awesome CCMenu available for Mac.

Features
========

* Monitor projects on multiple CruiseControl continuous integration servers.
* Access to overall continuous integration status from the system tray.
* Access individual project pages through the tray menu.
* Receive notifications for fixed/broken/still failing builds.
* Easy access to the last build time for each project
* Customize build notifications.

.. image:: https://anaynayak.github.io/buildnotify/images/projectlist.png

Building from source
====================

The ubuntu package is pretty old! You can use the pypi package which is in sync with latest releases.

To do so do the following::

    pipx run --spec=buildnotify buildnotifyapplet.py

this will launch buildnotifyapplet.py and show a icon in the menubar.


Installing from PyPI
====================

``pip install buildnotify --pre``

Launch using ``.local/bin/buildnotifyapplet.py``


Supported continuous integration systems
========================================
- See https://cctray.org/servers/

