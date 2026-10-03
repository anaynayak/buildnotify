# BuildNotify

[![PyPI version](https://img.shields.io/pypi/v/buildnotify.svg)](https://pypi.org/project/buildnotify/)
[![MIT licence](https://img.shields.io/github/license/anaynayak/buildnotify.svg)](https://github.com/anaynayak/buildnotify/blob/main/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/anaynayak/buildnotify.svg)](https://github.com/anaynayak/buildnotify/issues)
[![CI status](https://github.com/anaynayak/buildnotify/actions/workflows/main.yml/badge.svg)](https://github.com/anaynayak/buildnotify/actions/workflows/main.yml)

BuildNotify is a CCMenu/CCTray equivalent for Linux, macOS and Windows. It resides in your system tray and notifies you of the build status for different projects on your continuous integration servers. BuildNotify is largely inspired from the awesome CCMenu available for Mac.

1. [Installation](installation.md)
2. [Quick start](quickstart.md)
3. [Servers](servers/index.md)
4. [Guides](usage.md)
5. [Frequently asked questions](faq.md)

# Features

1. Monitor projects on multiple continuous integration servers that publish a cctray.xml feed, and GitHub Actions workflows.
2. Access to overall continuous integration status from the system tray.
3. Access individual project pages through the tray menu.
4. Receive notifications for fixed/broken/still failing builds.
5. Easy access to the last build time and build label for each project.
6. Customize build notifications, or run your own script when a build changes.
7. Optional single-colour symbolic tray icons that differ by shape.
8. Unreachable servers show in the tray menu with their last error.
9. Mute a server or project, or pause all notifications for an hour, from the tray menu.

![Project List](images/projectlist.png)
