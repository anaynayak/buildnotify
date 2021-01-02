import sys
from time import strftime

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget, QSystemTrayIcon, QApplication

from buildnotifylib.app_menu import AppMenu
from buildnotifylib.build_icons import BuildIcons
from buildnotifylib.config import Config
from buildnotifylib.core.projects import OverallIntegrationStatus


class AppUi(QtCore.QObject):
    reload_data = QtCore.pyqtSignal()

    def __init__(self, parent: QApplication, conf: Config, build_icons: BuildIcons):
        super(AppUi, self).__init__(parent)
        self.widget = QWidget()
        self.build_icons = build_icons
        self.tray = QSystemTrayIcon(self.build_icons.for_status(None), self.widget)
        self.tray.show()
        self.app_menu = AppMenu(self.widget, conf, self.build_icons)
        self.app_menu.reload_data.connect(self.reload_data)  # type: ignore
        self.tray.setContextMenu(self.app_menu.menu)
        self.tray.activated.connect(self.show_menu)

    def show_menu(self, reason):
        if not sys.platform.startswith('darwin') and reason == QSystemTrayIcon.Trigger:
            self.app_menu.menu.popup(QCursor.pos())

    def update_projects(self, integration_status: OverallIntegrationStatus):
        count = len(integration_status.get_failing_builds())
        self.tray.setIcon(self.build_icons.for_aggregate_status(integration_status.get_build_status(), count))
        self.app_menu.update(integration_status.get_projects())
        self.tray.setToolTip("Last checked: " + strftime("%Y-%m-%d %H:%M:%S"))
