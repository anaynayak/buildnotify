# Quick start

## 1. Install

```commandline
uv tool install buildnotify
buildnotify
```

Other ways to install, and the GNOME note, are on the [Installation](installation.md) page. A new icon appears in your system tray.

## 2. Add your first server

On the first launch with no servers, the server dialog opens once. Until a server is added, the menu offers `Add a server...`, which opens the same dialog.

![Tray menu with no servers](images/empty-menu.png)

1. Paste the feed url, such as `https://ci.example.org/cc.xml`. The [Servers](servers/index.md) pages have the url pattern for each CI.
2. Under Sign in, choose `None`, `Username and password` or `Token`.
3. Click Test connection to see how many projects the feed has, and untick the ones you don't want.
4. Save.

![Server dialog for a cctray feed](images/server-cctray.png)

To watch GitHub Actions instead, set Source to `GitHub Actions`. See [GitHub Actions](servers/github-actions.md).

## 3. What you will see

The tray icon shows the overall status, and the menu lists your projects grouped as failing, building, passing and unknown. Click a project to open it on the CI server.

![Tray menu](images/projectlist.png)

BuildNotify notifies you when a build fails, is fixed, fails again or passes. Next:

1. [Tray and menu](guide/tray-menu.md)
2. [Notifications and custom script](guide/notifications.md)
3. [Muting and pausing](guide/muting.md)
