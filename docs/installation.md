# Installation instructions

## Requirements

1. Python 3.11 or newer.
2. PySide6 6.8 or newer. It is installed along with BuildNotify from PyPI.
3. A desktop with a system tray. Without one, BuildNotify says "I couldn't detect any system tray on this system." and exits.

### GNOME

GNOME Shell doesn't show tray icons on its own. Install and enable the [AppIndicator and KStatusNotifierItem Support](https://extensions.gnome.org/extension/615/appindicator-support/) extension. Ubuntu ships it enabled as "Ubuntu AppIndicators".

## Install from PyPI

Install BuildNotify as a tool with [uv](https://docs.astral.sh/uv/) or [pipx](https://pipx.pypa.io/). Both put it in its own environment and add the `buildnotify` command to your path.

```commandline
uv tool install buildnotify
```

```commandline
pipx install buildnotify
```

Launch it with `buildnotify`. To try it without installing, run `uvx buildnotify`.

To upgrade, run `uv tool upgrade buildnotify` or `pipx upgrade buildnotify`.

## Ubuntu and Debian packages

`sudo apt-get install buildnotify` still works, but the package in the archive is pretty old. Thanks to Daniel Lintott for getting BuildNotify integrated into the main debian archive. The old PPA at [https://launchpad.net/~anay/+archive/ppa](https://launchpad.net/~anay/+archive/ppa) is no longer updated. Use the PyPI package to get 3.0.

## Upgrading from 2.x

On its first start, 3.0 moves the 2.x server settings to a new layout. It writes the new layout first, and removes the old keys only once the new ones are on disk. Passwords and tokens stay in the system keyring under the same entries.

2.x can't read the new layout. If you might go back to 2.x, copy your settings first. On Linux they are in `~/.config/BuildNotify/BuildNotify.conf`.

Once you have installed the application, [you can configure it to monitor CI servers](usage.md)
