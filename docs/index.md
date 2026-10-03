---
description: BuildNotify is a system tray app that shows CI build status and notifies you when a build breaks or is fixed. Works with Jenkins, GoCD, Woodpecker, GitHub Actions and any cctray feed.
---

# BuildNotify

[![PyPI version](https://img.shields.io/pypi/v/buildnotify.svg)](https://pypi.org/project/buildnotify/)
[![MIT licence](https://img.shields.io/github/license/anaynayak/buildnotify.svg)](https://github.com/anaynayak/buildnotify/blob/main/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/anaynayak/buildnotify.svg)](https://github.com/anaynayak/buildnotify/issues)
[![CI status](https://github.com/anaynayak/buildnotify/actions/workflows/main.yml/badge.svg)](https://github.com/anaynayak/buildnotify/actions/workflows/main.yml)

## Your CI status in the system tray

BuildNotify watches Jenkins, GoCD, Woodpecker, GitHub Actions and any cctray feed, and tells you when a build breaks or is fixed. It runs on Linux, macOS and Windows.

![Tray menu listing failing and passing projects](images/projectlist.png){ width="360" }

```commandline
uv tool install buildnotify
```

[Install guide](installation.md){ .md-button .md-button--primary }
[Quick start](quickstart.md){ .md-button }
[Changelog](changelog.md){ .md-button }

Also available with pipx, as a Flatpak bundle and as a development build. See [Install](installation.md).

## Works with

<div class="grid cards" markdown>

- **[Jenkins](servers/jenkins.md)**

    A `/cc.xml` feed from the CCTray XML plugin.

- **[GoCD](servers/gocd.md)**

    The `/go/cctray.xml` feed.

- **[Woodpecker CI](servers/woodpecker.md) and [Crow CI](servers/crow.md)**

    The `cc.xml` badge feed of a repository.

- **[GitHub Actions](servers/github-actions.md)**

    Read directly from the GitHub API, with workflow and branch filters.

- **[Other cctray servers](servers/other.md)**

    Concourse, Drone CI and anything else that publishes cctray.xml.

</div>

## What you get

1. The tray icon shows the overall status and a count of failing projects.
2. The menu groups projects as failing, building, passing and unknown, and opens a project on click.
3. Notifications for broken, fixed and still failing builds, and a custom script you can run on each one.
4. Mute a server or project, or pause all notifications for an hour.
5. A server that can't be reached shows in the menu with the reason.

## Next

1. [Quick start](quickstart.md)
2. [Servers](servers/index.md)
3. [Guides](usage.md)
4. [Reference](reference.md)
5. [Troubleshooting](troubleshooting.md)
6. [Security and privacy](security.md)
7. [FAQ](faq.md)
8. [Contributing](contributing.md)
