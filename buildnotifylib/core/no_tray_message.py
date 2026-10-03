GNOME_HINT = (
    "GNOME does not show tray icons by itself. Install and enable the AppIndicator and "
    "KStatusNotifierItem Support extension (gnome-shell-extension-appindicator), then start BuildNotify again."
)


def no_tray_message(desktop: str | None) -> str:
    message = "BuildNotify needs a system tray. I couldn't detect one on this system."
    if desktop and "GNOME" in desktop.upper():
        message += "\n\n" + GNOME_HINT
    return message
