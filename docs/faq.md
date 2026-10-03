---
description: Answers to common BuildNotify questions about requirements, supported servers, settings and notifications.
---

# FAQ

## What all do I need to run this on my machine?

Python 3.11 or newer and a desktop with a system tray. The steps specified in the [Installation](installation.md) page should help you get started.

## I don't see the tray icon

See [Troubleshooting](troubleshooting.md#no-tray-icon-on-gnome).

## Why is BuildNotify not a gnome-applet anymore?

Well, it turns out that there are a lot more desktop environments other than Gnome which are being actively used by users and writing an application which works on everything is a real pain.

## Does this work on Windows or Mac?

Yes. The application is written with Qt so that it can work across different environments, and the tests run on Linux, macOS and Windows. If it worked for your XYZ configuration, do let me know.

On Windows, a custom script has to read the `BUILDNOTIFY_STATUS` and `BUILDNOTIFY_PROJECTS` environment variables. Scripts that use `#status#` or `#projects#` are not run there. See [Custom script](guide/notifications.md#custom-script).

## Why Qt? Why not Xyz?

Qt saved me from the pain of writing environment specific code as currently there is no uniform way of providing system tray applications which would work on KDE/Gnome/MyOwnDesktopEnvironment. Besides, it works for Windows/Mac for free.

## Why PySide6 instead of PyQt5?

3.0 moved from PyQt5 to PySide6, the Qt 6 binding maintained by the Qt Company. Qt 5 is end of life, and PySide6 is LGPL licensed and ships its own type hints. It is installed from PyPI along with BuildNotify, so there's nothing to set up.

## Can I point BuildNotify at a local file:// feed?

No. The HTTP client can't fetch `file://` urls, so 2.x accepted them and then failed with a connection error. 3.0 rejects them in the server dialog and accepts only `http://` and `https://`. Serve the file over HTTP instead, for example with `python3 -m http.server`.

## Will upgrading lose my servers?

No. 3.0 moves the 2.x settings to its new layout on first start, and passwords stay in the keyring. 2.x can't read the new layout, so copy your settings before upgrading if you might go back. See [Upgrading from 2.x](installation.md#upgrading-from-2x).
