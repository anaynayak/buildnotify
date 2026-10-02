import webbrowser
from collections.abc import Callable, Sequence
from datetime import datetime
from functools import partial

from PySide6 import QtCore
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QWidget

from buildnotifylib.adapters.settings_store import SettingsStore
from buildnotifylib.core import humanize
from buildnotifylib.core.diff import key
from buildnotifylib.core.errors import server_label, summarize
from buildnotifylib.core.model import Project, ServerSnapshot
from buildnotifylib.core.mute import (
    Clock,
    Mutes,
    keep_mutes,
    pause,
    resume,
    system_clock,
    toggle_project,
    toggle_server,
)
from buildnotifylib.core.ports import Connection
from buildnotifylib.core.settings import AppSettings, SortKey
from buildnotifylib.ui.build_icons import BuildIcons
from buildnotifylib.ui.dialogs.preferences import PreferencesDialog
from buildnotifylib.version import VERSION


class AppMenu(QtCore.QObject):
    reload_data = QtCore.Signal()

    def __init__(
        self,
        widget: QWidget,
        store: SettingsStore,
        build_icons: BuildIcons,
        connection: Connection,
        clock: Clock = system_clock,
    ):
        super().__init__(widget)
        self.menu = QMenu(widget)
        self.store = store
        self.connection = connection
        self.build_icons = build_icons
        self.clock = clock
        self.projects: list[Project] = []
        self.unavailable: Sequence[ServerSnapshot] = ()
        self.mute_menu: QMenu | None = None
        self.create_default_menu_items()

    def update(self, projects: list[Project], unavailable: Sequence[ServerSnapshot] = ()):
        self.projects, self.unavailable = projects, unavailable
        self.menu.clear()
        self.create_error_items(unavailable)
        mutes = Mutes.from_settings(self.store.settings)
        for project in self.sorted_projects(projects):
            icon = self.build_icons.for_status(project.get_build_status())
            self.create_menu_item(project, icon, mutes.mutes(project))
        self.create_default_menu_items()

    def sorted_projects(self, projects: list[Project]) -> list[Project]:
        if self.store.settings.sort_key is SortKey.NAME:
            return sorted(projects, key=lambda p: p.label())
        return sorted(projects, key=self.build_time_key, reverse=True)

    @staticmethod
    def build_time_key(project: Project) -> tuple[bool, float]:
        build_time = project.build_time
        if build_time is None:
            return False, 0.0
        return True, build_time.timestamp()

    def create_error_items(self, servers: Sequence[ServerSnapshot]):
        icon = self.build_icons.for_status(None)
        for server in servers:
            action = self.menu.addAction(icon, self.error_label(server))
            action.setIconVisibleInMenu(True)
            action.setEnabled(False)
        if servers:
            self.menu.addSeparator()

    @staticmethod
    def error_label(server: ServerSnapshot) -> str:
        summary = summarize(server.error) if server.error is not None else "Unavailable"
        at = (server.error_at or datetime.now()).astimezone()
        when = at.strftime("%H:%M" if at.date() == datetime.now().astimezone().date() else "%Y-%m-%d %H:%M")
        return f"{server_label(server.url)}: {summary} ({when})"

    def create_default_menu_items(self):
        self.menu.addSeparator()
        self.add_pause_action()
        self.menu.addMenu(self.create_mute_menu())
        self.menu.addAction(QAction("About", self.menu, triggered=self.about_clicked))
        self.menu.addAction(QAction("Preferences", self.menu, triggered=self.preferences_clicked))
        self.menu.addAction(QAction("Exit", self.menu, triggered=self.exit))

    def add_pause_action(self) -> None:
        until = self.store.settings.paused_until
        if until is not None and until > self.clock():
            label = f"Resume notifications (paused until {until.astimezone().strftime('%H:%M')})"
            self.menu.addAction(label).triggered.connect(lambda: self.change(resume(self.store.settings)))
        else:
            action = self.menu.addAction("Pause notifications for 1 hour")
            action.triggered.connect(lambda: self.change(pause(self.store.settings, self.clock())))

    def create_mute_menu(self) -> QMenu:
        if self.mute_menu is not None:
            self.mute_menu.deleteLater()
        menu = self.mute_menu = QMenu("Mute", self.menu)
        settings = self.store.settings
        for server in settings.servers:
            self.add_toggle(menu, server_label(server.url), server.muted, partial(toggle_server, url=server.url))
        if settings.servers and self.projects:
            menu.addSeparator()
        mutes = Mutes.from_settings(settings)
        for project in self.sorted_projects(self.projects):
            muted = key(project) in mutes.projects
            self.add_toggle(menu, project.label(), muted, partial(toggle_project, project=project))
        menu.setEnabled(bool(settings.servers))
        return menu

    def add_toggle(self, menu: QMenu, label: str, checked: bool, toggle: Callable[[AppSettings], AppSettings]):
        action = menu.addAction(label)
        action.setCheckable(True)
        action.setChecked(checked)
        action.triggered.connect(lambda: self.change(toggle(self.store.settings)))

    def change(self, settings: AppSettings):
        self.store.save(settings)
        self.update(self.projects, self.unavailable)

    def about_clicked(self, widget: QWidget):
        QMessageBox.about(
            self.menu,
            f"About BuildNotify {VERSION}",
            f"<b>BuildNotify {VERSION}</b> has been developed using PySide6 and serves as a build notification tool "
            "for cruise control. In case of any suggestions/bugs,"
            'please visit <a href="https://git.io/buildnotify">https://git.io/buildnotify</a> '
            "and provide your feedback.",
        )

    def preferences_clicked(self, widget: QWidget):
        dialog = PreferencesDialog(
            self.store.settings, self.connection, self.menu, keystore_available=self.store.keystore.is_available()
        )
        settings = dialog.open()
        dialog.deleteLater()
        if settings is not None:
            # Preferences doesn't edit mutes or the pause, and the tray may have changed them while the dialog was open.
            self.store.save(keep_mutes(settings, self.store.settings))
            self.reload_data.emit()

    def exit(self, widget: QWidget):
        QApplication.quit()

    def create_menu_item(self, project: Project, icon: QIcon, muted: bool = False):
        menu_item_label = project.label(self.store.settings.show_last_build_label)
        build_time = project.build_time
        if self.store.settings.notify("lastBuildTimeForProject") and build_time is not None:
            menu_item_label = menu_item_label + ", " + humanize.relative(build_time, datetime.now(tz=build_time.tzinfo))
        if muted:
            menu_item_label += " (muted)"

        action = self.menu.addAction(icon, menu_item_label)
        action.setIconVisibleInMenu(True)
        action.triggered.connect(partial(self.open_url, url=project.url))

    def open_url(self, url: str):
        webbrowser.open(url)
