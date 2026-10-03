---
description: Choose which BuildNotify notifications to show and run a custom script on each one, with the environment variables it gets.
---

# Notifications and custom script

## Notifications

BuildNotify shows a notification when a build fails, is fixed, fails again or passes, and when a server can't be reached. Each kind can be turned off in Preferences.

1. A notification about one project names it in the title, such as `Build failed: [jenkins] nightly-e2e`, with the build label below. Clicking it opens the project page.
2. A notification about several projects counts them, such as `3 builds failed`, and lists up to three names followed by `and N more`. Clicking it opens the tray menu.
3. Failures, and servers that can't be reached, use the warning icon. Fixed and passed builds use the information icon.
4. A server that can't be reached is named by its menu prefix or host, as in `Can't reach ci.example.org`. While it stays down the notification repeats after 1, 2, 3, 5, 8, 13 and 21 failed checks, then starts over. When it answers again, `ci.example.org is reachable again` follows.

## Custom script

BuildNotify can run a script each time it shows a notification. Turn on "Run a script on each notification" and enter the command. It runs through the platform shell (`/bin/sh` on Linux and macOS, `cmd.exe` on Windows).

The script gets two environment variables:

1. `BUILDNOTIFY_STATUS`: the kind of notification: `Broken builds`, `Fixed builds`, `Build is still failing`, `Yet another successful build`, `Connectivity issues` or `Connectivity restored`. These are the 2.x notification titles, kept so existing scripts still work, and they differ from the titles BuildNotify now shows.
2. `BUILDNOTIFY_PROJECTS`: every affected project (or server url for connectivity notifications), separated by commas. Unlike the notification, the list is never shortened.

For example:

```commandline
notify-send "$BUILDNOTIFY_STATUS" "$BUILDNOTIFY_PROJECTS"
```

Scripts from 2.x can keep using the `#status#` and `#projects#` placeholders. Each one is replaced with a shell-quoted value, and the quoting follows the surrounding quotes, so `notify-send "#status#" "#projects#"` still works. A placeholder escaped with a backslash is left alone.

On Windows, `cmd.exe` has no quoting that makes `&`, `|`, `^` and `%` safe, so a script that uses `#status#` or `#projects#` is not run. BuildNotify logs a warning instead. Read `%BUILDNOTIFY_STATUS%` and `%BUILDNOTIFY_PROJECTS%` in the script.
