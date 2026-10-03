---
description: Feed URLs and sources for the CI servers BuildNotify supports: Jenkins, GoCD, Woodpecker, Crow CI, GitHub Actions and other cctray servers.
---

# Servers

BuildNotify reads any server that publishes a cctray.xml feed, and it can watch GitHub Actions directly. [cctray.org/servers](https://cctray.org/servers/) keeps the full list of servers with a feed. Replace the placeholders in angle brackets.

| Server | Feed URL | Source |
| --- | --- | --- |
| [Crow CI](crow.md) | `https://<host>/api/v1/badges/<owner>/<repo>/cc.xml` | Checked against a live Crow server. The Woodpecker path `/api/badges/...` returns HTML on Crow. |
| [Woodpecker CI](woodpecker.md) | `https://<host>/api/badges/<owner>/<repo>/cc.xml` | [cctray.org](https://cctray.org/servers/) |
| [Jenkins](jenkins.md) | `https://<host>/cc.xml` or `https://<host>/view/<name>/cc.xml` | `/cc.xml` is on [cctray.org](https://cctray.org/servers/) and needs the [CCtray XML plugin](https://plugins.jenkins.io/cctray-xml/), which also serves each view. |
| [GoCD](gocd.md) | `https://<host>/go/cctray.xml` | [cctray.org](https://cctray.org/servers/) |
| [Concourse](other.md) | `https://<host>/api/v1/teams/<team>/cc.xml` | [cctray.org](https://cctray.org/servers/) |
| [Drone CI](other.md) | `https://<host>/api/badges/<owner>/<name>/cc.xml` | [cctray.org](https://cctray.org/servers/) |
| [GitHub Actions](github-actions.md) | No feed. Set Source to `GitHub Actions`. | See [GitHub Actions](github-actions.md). |

Every page lists the URL pattern, the sign-in setting and a short example. How to fill in the server dialog is in [Preferences and the server dialog](../guide/preferences.md).
