import sys
from time import strftime

from PySide6 import QtCore
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QWidget

from buildnotifylib.adapters.settings_store import SettingsStore
from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.ports import Connection
from buildnotifylib.ui.app_menu import AppMenu
from buildnotifylib.ui.build_icons import BuildIcons


class AppUi(QtCore.QObject):
    reload_data = QtCore.Signal()

    def __init__(self, parent: QApplication, store: SettingsStore, build_icons: BuildIcons, connection: Connection):
        super().__init__(parent)
        self.widget = QWidget()
        self.store = store
        self.build_icons = build_icons
        self.tray = QSystemTrayIcon(self.build_icons.for_status(None, store.settings.symbolic_icons), self.widget)
        self.tray.show()
        self.app_menu = AppMenu(self.widget, store, self.build_icons, connection)
        self.app_menu.reload_data.connect(self.reload_data)
        self.tray.setContextMenu(self.app_menu.menu)
        self.tray.activated.connect(self.show_menu)
        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.tray.hide)

    def show_menu(self, reason):
        if not sys.platform.startswith("darwin") and reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.app_menu.menu.popup(QCursor.pos())

    def update_projects(self, integration_status: OverallIntegrationStatus):
        count = len(integration_status.get_failing_builds())
        status = integration_status.get_build_status()
        ratio, symbolic = self.widget.devicePixelRatio(), self.store.settings.symbolic_icons
        self.tray.setIcon(self.build_icons.for_aggregate_status(status, count, ratio, symbolic=symbolic))
        self.app_menu.update(integration_status.get_projects())
        self.tray.setToolTip(f"{integration_status.failing_summary()}\nLast checked: {strftime('%Y-%m-%d %H:%M:%S')}")
