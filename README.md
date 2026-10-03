# BuildNotify

BuildNotify is a CCMenu/CCTray equivalent for Linux, macOS and Windows. It resides in your system tray and notifies you of the build status for different projects on your continuous integration servers. BuildNotify is largely inspired from the awesome CCMenu available for Mac.

## Features

1. Monitor projects on multiple continuous integration servers that publish a cctray.xml feed, and GitHub Actions workflows.
2. Access to overall continuous integration status from the system tray.
3. Access individual project pages through the tray menu.
4. Receive notifications for fixed/broken/still failing builds.
5. Easy access to the last build time and build label for each project.
6. Customize build notifications, or run your own script when a build changes.
7. Optional single-colour tray icons (Shapes) that differ by shape.
8. Unreachable servers show in the tray menu with their last error.
9. Mute a server or project, or pause all notifications for an hour, from the tray menu.

![Project list](https://anaynayak.github.io/buildnotify/images/projectlist.png)

## Installing from PyPI

BuildNotify needs Python 3.11 or newer. Install it as a tool with [uv](https://docs.astral.sh/uv/) or [pipx](https://pipx.pypa.io/):

```sh
uv tool install buildnotify
# or
pipx install buildnotify
```

Launch it using `buildnotify`. This will show an icon in the system tray.

To try it without installing:

```sh
uvx buildnotify
```

The Ubuntu and Debian packages are pretty old, so use the PyPI package to get the latest release. See the [installation page](https://anaynayak.github.io/buildnotify/installation.html) for requirements and the GNOME tray note.

## Command line options

1. `--settings PATH` reads and writes settings in this INI file instead of the default location.
2. `--debug` logs every fetch.

## Supported continuous integration systems

Anything that publishes a cctray.xml feed. See https://cctray.org/servers/

GitHub Actions is read directly from the GitHub API, with optional workflow and branch filters.

## Documentation

1. [Installation](https://anaynayak.github.io/buildnotify/installation.html)
2. [Configuration and usage](https://anaynayak.github.io/buildnotify/usage.html)
3. [Frequently asked questions](https://anaynayak.github.io/buildnotify/faq.html)
4. [Changelog](https://github.com/anaynayak/buildnotify/blob/main/CHANGELOG)
5. [Development](https://github.com/anaynayak/buildnotify/blob/main/DEVELOPMENT.md)
