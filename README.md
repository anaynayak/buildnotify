# BuildNotify

[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/anaynayak/buildnotify/badge)](https://scorecard.dev/viewer/?uri=github.com/anaynayak/buildnotify)

BuildNotify is a CCMenu/CCTray equivalent for Linux, macOS and Windows. It resides in your system tray and notifies you of the build status for different projects on your continuous integration servers. BuildNotify is largely inspired from the awesome CCMenu available for Mac.

## Features

BuildNotify shows the status of your builds in the system tray, lists projects in a menu grouped by status, and notifies you when a build breaks or is fixed. You can run your own script on a notification, mute a server or project, and pick colour or shape tray icons. It reads cctray.xml feeds and GitHub Actions. The [documentation site](https://anaynayak.github.io/buildnotify/) has the guides.

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

## Installing a development build

Every push to `main` replaces the [dev pre-release](https://github.com/anaynayak/buildnotify/releases/tag/dev) with a wheel, an sdist and a Flatpak bundle. These builds are untested by users and may be broken. The wheel has a `.devN` version, so uv and pip only pick it up when you ask for it:

```sh
uv tool install --prerelease allow https://github.com/anaynayak/buildnotify/releases/download/dev/<wheel file name>
```

Take the exact file name from the release page. Development builds are never published to PyPI.

## Verifying a release

Releases are built by GitHub Actions from a tag, published to PyPI with trusted publishing and attached to a GitHub Release. Each file has build provenance and SBOM attestations. After downloading the wheel, check it with the [GitHub CLI](https://cli.github.com/):

```sh
gh attestation verify buildnotify-3.0.0-py3-none-any.whl --repo anaynayak/buildnotify
```

PyPI also lists the PEP 740 attestation for each file. See [Development](DEVELOPMENT.md#verifying-a-release) for the SBOM check and reproducible builds.

## Command line options

1. `--settings PATH` reads and writes settings in this INI file instead of the default location.
2. `--debug` logs every fetch.

## Supported continuous integration systems

Anything that publishes a cctray.xml feed. See https://cctray.org/servers/

GitHub Actions is read directly from the GitHub API, with optional workflow and branch filters.

## Documentation

1. [Installation](https://anaynayak.github.io/buildnotify/installation.html)
2. [Quick start](https://anaynayak.github.io/buildnotify/quickstart.html)
3. [Reference](https://anaynayak.github.io/buildnotify/reference.html)
4. [Troubleshooting](https://anaynayak.github.io/buildnotify/troubleshooting.html)
5. [Security and privacy](https://anaynayak.github.io/buildnotify/security.html)
6. [Frequently asked questions](https://anaynayak.github.io/buildnotify/faq.html)
7. [Changelog](https://anaynayak.github.io/buildnotify/changelog.html)
8. [Contributing](https://anaynayak.github.io/buildnotify/contributing.html)
