"""Render the docs screenshots offscreen from fixture data and a fixed clock.

Run it with `just screenshots`. The offscreen platform has no native style, so every widget
uses Fusion; the images look the same on any machine.
"""

import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["TZ"] = "UTC"
time.tzset()

from PySide6.QtCore import QPoint, QRect, Qt  # noqa: E402
from PySide6.QtGui import QColor, QPainter, QPixmap  # noqa: E402
from PySide6.QtWidgets import QApplication, QWidget  # noqa: E402

from buildnotifylib.adapters.http import HttpConnection  # noqa: E402
from buildnotifylib.core import cctray  # noqa: E402
from buildnotifylib.core.aggregate import OverallIntegrationStatus  # noqa: E402
from buildnotifylib.core.model import ServerSnapshot  # noqa: E402
from buildnotifylib.core.settings import AppSettings, ServerSettings, SourceKind  # noqa: E402
from buildnotifylib.ui import app_menu  # noqa: E402
from buildnotifylib.ui.build_icons import TRAY_SIZE, BuildIcons  # noqa: E402
from buildnotifylib.ui.dialogs.preferences.dialog import PreferencesDialog  # noqa: E402
from buildnotifylib.ui.dialogs.server.dialog import ServerConfigurationDialog  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FEEDS = ROOT / "test" / "fixtures" / "cctray"
OUT = ROOT / "docs" / "images"
NOW = datetime(2026, 9, 30, 10, 0, tzinfo=UTC)
JENKINS = ServerSettings("https://jenkins.example.org/cc.xml", prefix="jenkins")
GOCD = ServerSettings("https://gocd.example.org/go/cctray.xml", prefix="gocd")
OFFLINE = ServerSettings("https://ci.example.org/cctray.xml")
GITHUB = ServerSettings(
    "", kind=SourceKind.GITHUB, repository="octo-org/hello-world", workflow="ci.yml", branch="main", prefix="gh"
)
SERVERS = [JENKINS, GOCD, OFFLINE, GITHUB]
TRAY_STATES = [
    ("Success.Sleeping", 0),
    ("Success.Building", 0),
    ("Failure.Sleeping", 1),
    ("Failure.Building", 2),
    (None, 0),
]


class FixedClock(datetime):
    @classmethod
    def now(cls, tz=None):
        return NOW if tz is None else NOW.astimezone(tz)


class NoKeystore:
    def is_available(self) -> bool:
        return True


class Store:
    """Just enough of SettingsStore for the menu, with nothing saved anywhere."""

    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.keystore = NoKeystore()

    def save(self, settings: AppSettings) -> None:
        self.settings = settings


def snapshot(server: ServerSettings, feed: str) -> ServerSnapshot:
    projects = cctray.parse((FEEDS / feed).read_bytes(), server)
    return ServerSnapshot(server.url, tuple(projects))


def status() -> OverallIntegrationStatus:
    offline = ServerSnapshot(OFFLINE.url, error=ConnectionError("Could not connect"), error_at=NOW)
    return OverallIntegrationStatus([snapshot(JENKINS, "jenkins.xml"), snapshot(GOCD, "gocd.xml"), offline])


def save(widget: QWidget, name: str) -> None:
    widget.adjustSize()
    widget.grab().save(str(OUT / name))
    print(f"wrote docs/images/{name}")


def tray_menu(settings: AppSettings, icons: BuildIcons) -> None:
    app_menu.datetime = FixedClock  # type: ignore[misc]
    host = QWidget()
    menu = app_menu.AppMenu(host, Store(settings), icons, HttpConnection(), clock=lambda: NOW)  # type: ignore[arg-type]
    overall = status()
    menu.update(overall.get_projects(), overall.unavailable_servers())
    save(menu.menu, "projectlist.png")


def preferences(settings: AppSettings) -> None:
    dialog = PreferencesDialog(settings, HttpConnection())
    dialog.resize(560, 420)
    for index, name in enumerate(["servers.png", "notifications.png", "misc.png"]):
        dialog.tabs.setCurrentIndex(index)
        dialog.tabs.currentWidget().adjustSize()
        dialog.grab().save(str(OUT / name))
        print(f"wrote docs/images/{name}")


def server_dialog(server: ServerSettings, name: str) -> None:
    save(ServerConfigurationDialog(server, 10, HttpConnection()), name)


def tray_icons(icons: BuildIcons) -> None:
    size, gap = TRAY_SIZE.width() * 2, 12
    rows = [False, True]
    canvas = QPixmap(len(TRAY_STATES) * (size + gap) + gap, len(rows) * (size + gap) + gap)
    canvas.fill(QColor("#2b2b2b"))
    painter = QPainter(canvas)
    for row, symbolic in enumerate(rows):
        for column, (state, count) in enumerate(TRAY_STATES):
            icon = icons.for_aggregate_status(state, count, 2.0, symbolic=symbolic)
            target = QRect(QPoint(gap + column * (size + gap), gap + row * (size + gap)), TRAY_SIZE * 2)
            icon.paint(painter, target, Qt.AlignmentFlag.AlignCenter)
    painter.end()
    canvas.save(str(OUT / "tray-icons.png"))
    print("wrote docs/images/tray-icons.png")


def main() -> None:
    app = QApplication(sys.argv[:1])
    app.setStyle("Fusion")
    settings = AppSettings(servers=SERVERS, interval_seconds=60)
    icons = BuildIcons()
    tray_menu(settings, icons)
    preferences(settings)
    server_dialog(JENKINS, "server-cctray.png")
    server_dialog(GITHUB, "server-github.png")
    tray_icons(icons)


if __name__ == "__main__":
    main()
