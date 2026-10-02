import webbrowser
from datetime import datetime
from functools import partial

from PySide6 import QtCore
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QWidget

from buildnotifylib.adapters.settings_store import SettingsStore
from buildnotifylib.core import humanize
from buildnotifylib.core.model import Project
from buildnotifylib.core.ports import Connection
from buildnotifylib.core.settings import SortKey
from buildnotifylib.ui.build_icons import BuildIcons
from buildnotifylib.ui.dialogs.preferences import PreferencesDialog
from buildnotifylib.version import VERSION


class AppMenu(QtCore.QObject):
    reload_data = QtCore.Signal()

    def __init__(self, widget: QWidget, store: SettingsStore, build_icons: BuildIcons, connection: Connection):
        super().__init__(widget)
        self.menu = QMenu(widget)
        self.store = store
        self.connection = connection
        self.build_icons = build_icons
        self.create_default_menu_items()

    def update(self, projects: list[Project]):
        self.menu.clear()
        for project in self.sorted_projects(projects):
            icon = self.build_icons.for_status(project.get_build_status())
            self.create_menu_item(project, icon)
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

    def create_default_menu_items(self):
        self.menu.addSeparator()
        self.menu.addAction(QAction("About", self.menu, triggered=self.about_clicked))
        self.menu.addAction(QAction("Preferences", self.menu, triggered=self.preferences_clicked))
        self.menu.addAction(QAction("Exit", self.menu, triggered=self.exit))

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
            self.store.save(settings)
            self.reload_data.emit()

    def exit(self, widget: QWidget):
        QApplication.quit()

    def create_menu_item(self, project: Project, icon: QIcon):
        menu_item_label = project.label(self.store.settings.show_last_build_label)
        build_time = project.build_time
        if self.store.settings.notify("lastBuildTimeForProject") and build_time is not None:
            menu_item_label = menu_item_label + ", " + humanize.relative(build_time, datetime.now(tz=build_time.tzinfo))

        action = self.menu.addAction(icon, menu_item_label)
        action.setIconVisibleInMenu(True)
        action.triggered.connect(partial(self.open_url, url=project.url))

    def open_url(self, url: str):
        webbrowser.open(url)
