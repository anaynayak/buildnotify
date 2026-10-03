# Reference

Every setting, option and variable in one place. For how to use them, see [Preferences and the server dialog](guide/preferences.md).

## Preferences

Preferences has four tabs. A change takes effect when you click OK.

### Servers tab

Lists the monitored servers. See [the server dialog](#server-dialog) for the fields of each one.

### Menu tab

| Field | Values | Default |
| --- | --- | --- |
| Show last build time | on, off | on |
| Show build label | on, off | off |
| Tray icon | Colour, Shapes | Colour |
| Sort projects | Failing first, Name, Last build time | Failing first |

An install from an earlier version keeps the sort order it had.

### Notifications tab

| Field | Default |
| --- | --- |
| Passes | off |
| Fails | on |
| Is fixed | on |
| Fails again | on |
| A server can't be reached | on |
| Run a script on each notification | off |
| Script | empty |

The script field is only enabled while the box above it is ticked. See [Custom script variables](#custom-script-variables).

### Advanced tab

| Field | Range | Default |
| --- | --- | --- |
| Check every | 10 to 3600 seconds | 120 |
| Give up after | 1 to 300 seconds | 10 |

## Server dialog

The first field is Source: `cctray feed` (the default) or `GitHub Actions`.

### cctray feed

| Field | Notes | Default |
| --- | --- | --- |
| Feed URL | Must start with `http://` or `https://`. A URL typed without a scheme gets `https://`. | empty |
| Sign in | None, Username and password, or Token | None |
| Username | Shown for Username and password | empty |
| Password | Hidden characters. Shown as Bearer token for Token, without the `Bearer` keyword | empty |
| Display prefix | Shown in brackets before each project name | empty |
| Time zone for feed times | In Advanced. Type part of a zone name to find it | Use the feed's offset |
| Certificate checks | In Advanced. Off only after you accept an untrusted certificate, for that server | on |
| Projects | Ticked projects are monitored. Projects added to the feed later are included | all |

### GitHub Actions

| Field | Notes | Default |
| --- | --- | --- |
| Repository | `owner/name`, or a pasted `github.com` URL | empty |
| Workflow | A file such as `ci.yml`, or the workflow name | all workflows |
| Branch | A branch name | all branches |
| Token | Optional for public repositories. Needs Actions: read | empty |
| Display prefix | As above. Without one, the repository name is used | empty |

GitHub servers have no Advanced section.

## Command line options

```commandline
buildnotify [-h] [--debug] [--settings PATH]
```

| Option | Effect |
| --- | --- |
| `--debug` | Logs every fetch, at debug level. Without it, only warnings are logged. |
| `--settings PATH` | Reads and writes settings in this INI file instead of the default location. |
| `-h`, `--help` | Prints the usage and exits. |

Other arguments are passed to Qt.

## Settings file location

Settings are stored with Qt's `QSettings`, under the organisation and application name `BuildNotify`.

| Platform | Location |
| --- | --- |
| Linux | `~/.config/BuildNotify/BuildNotify.conf` (inferred from Qt's defaults, not checked on a machine) |
| Flatpak | `~/.var/app/io.github.anaynayak.BuildNotify/config/BuildNotify/BuildNotify.conf` |
| macOS | `~/Library/Preferences/com.buildnotify.BuildNotify.plist` (observed on a Mac) |
| Windows | The registry key `HKEY_CURRENT_USER\Software\BuildNotify\BuildNotify` (inferred from Qt's defaults, not checked on a machine) |
| With `--settings PATH` | The INI file at `PATH` |

Passwords and tokens are not in this file. They are in the system keyring, one entry per server. See [Security and privacy](security.md#where-credentials-are-stored).

## Custom script variables

The script runs through the platform shell with these environment variables.

| Variable | Value |
| --- | --- |
| `BUILDNOTIFY_STATUS` | `Broken builds`, `Fixed builds`, `Build is still failing`, `Yet another successful build`, `Connectivity issues` or `Connectivity restored` |
| `BUILDNOTIFY_PROJECTS` | Every affected project, or the server URL for connectivity notifications, separated by commas. Never shortened. |

The older `#status#` and `#projects#` placeholders are still replaced, shell-quoted, except on Windows where such a script is not run. The [notifications guide](guide/notifications.md#custom-script) has examples.
