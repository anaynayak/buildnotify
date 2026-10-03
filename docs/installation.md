# Installation instructions

## Requirements

1. Python 3.11 or newer.
2. PySide6 6.8 or newer. It is installed along with BuildNotify from PyPI.
3. A desktop with a system tray. Without one, BuildNotify says "BuildNotify needs a system tray. I couldn't detect one on this system." and exits.

### GNOME

GNOME Shell doesn't show tray icons on its own. Install and enable the [AppIndicator and KStatusNotifierItem Support](https://extensions.gnome.org/extension/615/appindicator-support/) extension. Ubuntu ships it enabled as "Ubuntu AppIndicators".

## Install

=== "Linux"

    Install BuildNotify as a tool with [uv](https://docs.astral.sh/uv/) or [pipx](https://pipx.pypa.io/). Both put it in its own environment and add the `buildnotify` command to your path.

    ```commandline
    uv tool install buildnotify
    ```

    ```commandline
    pipx install buildnotify
    ```

    Launch it with `buildnotify`. To try it without installing, run `uvx buildnotify`. On GNOME, read the [AppIndicator note](#gnome) first.

=== "macOS"

    Install BuildNotify as a tool with [uv](https://docs.astral.sh/uv/) or [pipx](https://pipx.pypa.io/). Both put it in its own environment and add the `buildnotify` command to your path.

    ```commandline
    uv tool install buildnotify
    ```

    ```commandline
    pipx install buildnotify
    ```

    Launch it with `buildnotify`. To try it without installing, run `uvx buildnotify`.

=== "Windows"

    Install BuildNotify as a tool with [uv](https://docs.astral.sh/uv/) or [pipx](https://pipx.pypa.io/). Both put it in its own environment and add the `buildnotify` command to your path.

    ```commandline
    uv tool install buildnotify
    ```

    ```commandline
    pipx install buildnotify
    ```

    Launch it with `buildnotify`. To try it without installing, run `uvx buildnotify`. Custom scripts have [a Windows limitation](guide/notifications.md#custom-script).

=== "Flatpak"

    Each [release](https://github.com/anaynayak/buildnotify/releases) has a `BuildNotify.flatpak` bundle. Download it and install it for your user:

    ```commandline
    flatpak install --user BuildNotify.flatpak
    flatpak run io.github.anaynayak.BuildNotify
    ```

    The bundle needs the KDE runtime, which Flatpak fetches from Flathub if it is configured.

## Upgrade and uninstall

=== "uv"

    ```commandline
    uv tool upgrade buildnotify
    uv tool uninstall buildnotify
    ```

=== "pipx"

    ```commandline
    pipx upgrade buildnotify
    pipx uninstall buildnotify
    ```

=== "Flatpak"

    Install the newer bundle over the old one. To remove the app:

    ```commandline
    flatpak uninstall --user io.github.anaynayak.BuildNotify
    ```

Uninstalling doesn't remove your settings. On Linux they are in `~/.config/BuildNotify/BuildNotify.conf`.

## Install a development build

Every push to `main` replaces the [dev pre-release](https://github.com/anaynayak/buildnotify/releases/tag/dev) with a wheel, an sdist and a Flatpak bundle. These builds may be broken. The wheel has a `.devN` version, so uv and pip only install it when you ask for it:

```commandline
uv tool install --prerelease allow https://github.com/anaynayak/buildnotify/releases/download/dev/<wheel file name>
```

Take the exact file name from the release page. Development builds are never published to PyPI.

## Ubuntu and Debian packages

Debian last shipped BuildNotify 0.3.5, in buster, and current Debian and Ubuntu releases have no package. Thanks to Daniel Lintott for getting BuildNotify integrated into the main debian archive. The old PPA at [https://launchpad.net/~anay/+archive/ppa](https://launchpad.net/~anay/+archive/ppa) is no longer updated. Use the PyPI package to get 3.0.

## Upgrading from 2.x

On its first start, 3.0 moves the 2.x server settings to a new layout. It writes the new layout first, and removes the old keys only once the new ones are on disk. Passwords and tokens stay in the system keyring under the same entries.

2.x can't read the new layout. If you might go back to 2.x, copy your settings first. On Linux they are in `~/.config/BuildNotify/BuildNotify.conf`.

Once you have installed the application, [follow the quick start](quickstart.md) to add your first server, or see the [supported servers](servers/index.md)
