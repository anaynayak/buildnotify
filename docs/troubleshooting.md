# Troubleshooting

## No tray icon on GNOME

GNOME Shell doesn't show tray icons on its own. Without a tray, BuildNotify says "BuildNotify needs a system tray. I couldn't detect one on this system." and exits with code 1. On GNOME the message also names the extension.

1. Install the [AppIndicator and KStatusNotifierItem Support](https://extensions.gnome.org/extension/615/appindicator-support/) extension. On Debian and Ubuntu the package is `gnome-shell-extension-appindicator`.
2. Enable it. Ubuntu ships it enabled as "Ubuntu AppIndicators".
3. Start BuildNotify again.

Log out and back in if the extension doesn't show up after installing.

## The keyring is missing or locked

Passwords and tokens are stored in the system keyring. When none is available, the server dialog disables the sign-in fields and says that credentials can't be stored without a system keyring.

1. On Linux, the keyring needs a Secret Service provider such as GNOME Keyring or KWallet, running on the session D-Bus. A minimal window manager session often has none. Install and start one, then reopen the dialog.
2. The `keyring` package comes with BuildNotify. A `uv tool` or `pipx` install has it in the tool's own environment, so you don't install it yourself.
3. The Flatpak bundle is allowed to talk to `org.freedesktop.secrets`. It still needs a Secret Service provider on the host.
4. If the keyring is locked, unlock it when your desktop asks.

If saving to the keyring fails, BuildNotify doesn't show an error, and the password isn't stored. Add the server again after fixing the keyring.

## Certificate not trusted

A server with a self-signed or private-CA certificate shows `certificate not trusted` on its menu row, with `Edit the server to connect anyway`. In the server dialog, Test connection asks whether to connect anyway.

1. Accept to turn off certificate checks for that one server. The dialog shows `Certificate checks off for <host>`.
2. Click `Turn checks back on` to restore them. They also come back if you change the host.
3. Checks stay on for every other server.

The better fix is to install the CA certificate on the machine, then turn checks back on. See [Security and privacy](security.md#certificate-checks).

## GitHub rate limits

Without a token, GitHub allows 60 requests an hour. A server that hits the limit shows `GitHub rate limit reached - add a token` on its menu row, and the menu shows when BuildNotify will try again.

1. Add a token to the server. A fine-grained token needs the "Actions: read" permission. See [GitHub Actions](servers/github-actions.md).
2. Servers that use the same token share one limit, and servers without a token share another, so one busy repository can use up the limit for the others.
3. Raise the check interval on the Advanced tab of Preferences. See the [Reference](reference.md#advanced-tab).

## Sign-in failed or not found

A menu row of `sign-in failed` means the server answered 401 or 403. Check the user name and the token. `not found` means HTTP 404, which usually means a wrong feed URL or repository. `not a cctray feed` means the URL answered, but not with a cctray feed. See [Servers](servers/index.md) for the URL pattern of each CI.

## Logging with --debug

Start BuildNotify from a terminal with `--debug` to log every fetch to standard error. Use a throwaway settings file to leave your real settings alone:

```commandline
buildnotify --debug --settings /tmp/buildnotify.ini
```

Include the log, with any tokens and internal host names removed, when you [report a bug](https://github.com/anaynayak/buildnotify/issues).
