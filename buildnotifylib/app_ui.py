from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QSystemTrayIcon

from time import strftime
from app_menu import AppMenu


class AppUi(QtCore.QObject):
    reload_data = QtCore.pyqtSignal()

    def __init__(self, parent, conf, build_icons):
        super(AppUi, self).__init__(parent)
        self.widget = QWidget()
        self.build_icons = build_icons
        self.tray = QSystemTrayIcon(self.build_icons.for_status(None), self.widget)
        self.tray.show()
        self.app_menu = AppMenu(self.widget, conf, self.build_icons)
        self.app_menu.reload_data.connect(self.reload_data)
        self.tray.setContextMenu(self.app_menu.menu)

    def update_projects(self, integration_status):
        count = str(len(integration_status.get_failing_builds()))
        self.tray.setIcon(self.build_icons.for_aggregate_status(integration_status.get_build_status(), count))
        self.app_menu.update(integration_status.get_projects())
        self.tray.setToolTip("Last checked: " + strftime("%Y-%m-%d %H:%M:%S"))