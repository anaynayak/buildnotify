from dataclasses import dataclass

PROJECT_URL = "https://github.com/anaynayak/buildnotify"


@dataclass(frozen=True)
class MenuLabels:
    preferences: str
    about: str
    quit: str


def labels(platform: str) -> MenuLabels:
    return MenuLabels(
        preferences="Settings..." if platform == "darwin" else "Preferences...",
        about="About BuildNotify",
        quit="Exit" if platform == "win32" else "Quit BuildNotify",
    )


def about_html(version: str) -> str:
    return (
        f"<b>BuildNotify {version}</b> shows CI build status from cctray feeds and GitHub Actions "
        "in the system tray.<br><br>"
        f'Suggestions and bug reports are welcome at <a href="{PROJECT_URL}">{PROJECT_URL}</a>.'
    )
