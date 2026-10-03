import sys
import webbrowser
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import replace
from datetime import datetime
from functools import partial

from PySide6 import QtCore
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QWidget

from buildnotifylib.adapters.settings_store import SettingsStore
from buildnotifylib.core import humanize
from buildnotifylib.core.diff import key
from buildnotifylib.core.errors import details, phrase, server_label, server_name
from buildnotifylib.core.menu_labels import about_html, labels
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
    with_server,
)
from buildnotifylib.core.ports import Connection
from buildnotifylib.core.sections import Section, grouped, sort_projects
from buildnotifylib.core.settings import AppSettings, ServerSettings
from buildnotifylib.ui.build_icons import BuildIcons
from buildnotifylib.ui.dialogs.preferences.dialog import PreferencesDialog
from buildnotifylib.ui.dialogs.server.dialog import ServerConfigurationDialog
from buildnotifylib.ui.widgets.placement import centre_on_cursor_screen
from buildnotifylib.version import VERSION

PLATFORM = sys.platform

OVERFLOW = 15
"""Above this many project rows, Passing projects move into a submenu."""
MAX_LABEL_CHARS = 45
"""Project labels wider than this many average characters lose their middle, so the job name and time survive."""


class AppMenu(QtCore.QObject):
    reload_data = QtCore.Signal()
    mutes_changed = QtCore.Signal()

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
        self.menu.setToolTipsVisible(True)
        self.store = store
        self.connection = connection
        self.build_icons = build_icons
        self.clock = clock
        self.projects: list[Project] = []
        self.unavailable: Sequence[ServerSnapshot] = ()
        self.mute_menu: QMenu | None = None
        self.error_menus: list[QMenu] = []
        self.passing_menu: QMenu | None = None
        self.create_default_menu_items()

    def update(self, projects: list[Project], unavailable: Sequence[ServerSnapshot] = ()):
        self.projects, self.unavailable = projects, unavailable
        self.menu.clear()
        self.create_error_items(unavailable, separate=not projects)
        self.create_project_items(projects)
        self.create_default_menu_items()

    def create_project_items(self, projects: list[Project]) -> None:
        if self.passing_menu is not None:
            self.passing_menu.deleteLater()
            self.passing_menu = None
        mutes = Mutes.from_settings(self.store.settings)
        for index, (section, members) in enumerate(grouped(self.sorted_projects(projects))):
            title = f"{section} ({len(members)})"
            target = self.menu
            if index:
                self.menu.addSeparator()
            if section is Section.PASSING and len(projects) > OVERFLOW:
                target = self.passing_menu = self.menu.addMenu(title)
                target.setToolTipsVisible(True)
            else:
                add_header(self.menu, title)
            for project in members:
                self.create_menu_item(target, project, mutes.mutes(project))

    def sorted_projects(self, projects: list[Project]) -> list[Project]:
        return sort_projects(projects, self.store.settings.sort_key)

    def create_error_items(self, servers: Sequence[ServerSnapshot], separate: bool):
        for menu in self.error_menus:
            menu.deleteLater()
        self.error_menus = [self.create_error_menu(server) for server in servers]
        if servers and separate:
            self.menu.addSeparator()

    def create_error_menu(self, snapshot: ServerSnapshot) -> QMenu:
        server = self.configured(snapshot.url)
        menu = QMenu(self.error_label(snapshot, server), self.menu)
        menu.setIcon(self.build_icons.for_status(None))
        for line in details(snapshot.error) if snapshot.error is not None else ["Unavailable"]:
            menu.addAction(line).setEnabled(False)
        menu.addSeparator()
        menu.addAction("Retry now").triggered.connect(self.reload_data)
        if server is not None:
            menu.addAction("Edit server...").triggered.connect(partial(self.edit_server_clicked, server))
        self.menu.addMenu(menu).setIconVisibleInMenu(True)
        return menu

    def configured(self, url: str) -> ServerSettings | None:
        return next((server for server in self.store.settings.servers if server.url == url), None)

    @staticmethod
    def error_label(snapshot: ServerSnapshot, server: ServerSettings | None) -> str:
        name = server_name(snapshot.url, server.prefix if server is not None else "")
        summary = phrase(snapshot.error) if snapshot.error is not None else "unavailable"
        at = (snapshot.error_at or datetime.now()).astimezone()
        when = at.strftime("%H:%M" if at.date() == datetime.now().astimezone().date() else "%Y-%m-%d %H:%M")
        return f"{name}: {summary} ({when})"

    def create_default_menu_items(self):
        if self.store.settings.servers:
            self.menu.addSeparator()
            self.menu.addAction("Check now").triggered.connect(self.reload_data)
            self.add_pause_action()
            self.menu.addMenu(self.create_mute_menu())
        else:
            self.add_empty_state()
        text = labels(PLATFORM)
        self.menu.addAction(QAction(text.about, self.menu, triggered=self.about_clicked))
        self.menu.addAction(QAction(text.preferences, self.menu, triggered=self.preferences_clicked))
        self.menu.addAction(QAction(text.quit, self.menu, triggered=self.exit))

    def add_empty_state(self) -> None:
        self.menu.addAction("No servers yet").setEnabled(False)
        self.menu.addAction("Add a server...").triggered.connect(self.add_server_clicked)
        self.menu.addSeparator()

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
        for server in self.store.settings.servers:
            title = server_label(server.url)
            projects = [p for p in self.sorted_projects(self.projects) if p.server_url == server.url]
            if projects:
                self.fill_server_mutes(menu.addMenu(title), server, projects)
            else:
                self.add_toggle(menu, f"Mute {title}", server.muted, partial(toggle_server, url=server.url))
        return menu

    def fill_server_mutes(self, menu: QMenu, server: ServerSettings, projects: list[Project]) -> None:
        self.add_toggle(menu, "Mute whole server", server.muted, partial(toggle_server, url=server.url))
        menu.addSeparator()
        muted = Mutes.from_settings(self.store.settings).projects
        for project in projects:
            self.add_toggle(menu, project.name, key(project) in muted, partial(toggle_project, project=project))

    def add_toggle(self, menu: QMenu, label: str, checked: bool, toggle: Callable[[AppSettings], AppSettings]):
        action = menu.addAction(label)
        action.setCheckable(True)
        action.setChecked(checked)
        action.triggered.connect(lambda: self.change(toggle(self.store.settings)))

    def change(self, settings: AppSettings):
        self.store.save(settings)
        self.update(self.projects, self.unavailable)
        self.mutes_changed.emit()

    def about_clicked(self, widget: QWidget):
        box = QMessageBox(self.menu)
        box.setWindowTitle(f"About BuildNotify {VERSION}")
        box.setText(about_html(VERSION))
        box.setIconPixmap(QApplication.windowIcon().pixmap(64, 64))
        centre_on_cursor_screen(box)
        box.exec()

    def preferences_clicked(self, widget: QWidget):
        counts = Counter(project.server_url for project in self.projects)
        dialog = PreferencesDialog(
            self.store.settings,
            self.connection,
            self.menu,
            keystore_available=self.store.keystore.is_available(),
            project_counts=dict(counts),
        )
        settings = dialog.open()
        dialog.deleteLater()
        if settings is not None:
            # Preferences doesn't edit mutes or the pause, and the tray may have changed them while the dialog was open.
            self.store.save(keep_mutes(settings, self.store.settings))
            self.reload_data.emit()

    def offer_first_server(self) -> None:
        settings = self.store.settings
        if settings.servers or settings.server_prompt_shown:
            return
        self.store.save(replace(settings, server_prompt_shown=True))
        self.add_server_clicked()

    def add_server_clicked(self) -> None:
        server = self.open_server_dialog(None)
        settings = self.store.settings
        if server is None or server.url in [s.url for s in settings.servers]:
            return
        self.change(replace(settings, servers=[*settings.servers, server]))
        self.reload_data.emit()

    def edit_server_clicked(self, server: ServerSettings) -> None:
        edited = self.open_server_dialog(server)
        settings = self.store.settings
        if edited is None or (edited.url != server.url and self.configured(edited.url) is not None):
            return
        # The tray may have muted the server or its projects while the dialog was open.
        self.change(keep_mutes(with_server(settings, server.url, lambda _: edited), settings))
        self.reload_data.emit()

    def open_server_dialog(self, server: ServerSettings | None) -> ServerSettings | None:
        dialog = ServerConfigurationDialog(
            server,
            self.store.settings.timeout_seconds,
            self.connection,
            self.menu,
            keystore_available=self.store.keystore.is_available(),
        )
        server = dialog.open()
        dialog.deleteLater()
        return server

    def exit(self, widget: QWidget):
        QApplication.quit()

    def create_menu_item(self, menu: QMenu, project: Project, muted: bool = False):
        full_label = project.label(self.store.settings.show_last_build_label)
        shown = elided(menu, full_label)
        build_time = project.build_time
        suffix = ""
        if self.store.settings.notify("lastBuildTimeForProject") and build_time is not None:
            suffix = ", " + humanize.compact(build_time, datetime.now(tz=build_time.tzinfo))
        status = project.get_build_status()
        icon = self.build_icons.for_muted(status) if muted else self.build_icons.for_status(status)
        action = menu.addAction(icon, shown + suffix + (" (muted)" if muted else ""))
        action.setIconVisibleInMenu(True)
        action.triggered.connect(partial(self.open_url, url=project.url))
        if shown != full_label or muted:
            action.setToolTip(full_label + (" (muted)" if muted else ""))

    def open_url(self, url: str):
        webbrowser.open(url)


def add_header(menu: QMenu, title: str) -> None:
    """A disabled row, since native macOS menus don't draw QMenu section titles."""
    menu.addAction(title).setEnabled(False)


def elided(menu: QMenu, label: str) -> str:
    metrics = menu.fontMetrics()
    return metrics.elidedText(label, QtCore.Qt.TextElideMode.ElideMiddle, metrics.averageCharWidth() * MAX_LABEL_CHARS)
