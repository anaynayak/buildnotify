from PyQt4 import QtGui
from time import strftime
from app_menu import AppMenu

class AppUi:
    def __init__(self, conf, build_icons):
        self.widget = QtGui.QWidget()
        self.build_icons = build_icons
        self.tray = QtGui.QSystemTrayIcon(self.build_icons.for_status(None), self.widget)
        self.tray.show()
        self.app_menu = AppMenu(self.tray, self.widget, conf, self.build_icons);

    def update_projects(self,integration_status):
        count = str(len(integration_status.get_failing_builds()))
        self.tray.setIcon(self.build_icons.for_aggregate_status(integration_status.get_build_status(), count))
        self.app_menu.update(integration_status.get_projects())
        self.lastcheck = "Last checked: " + strftime("%Y-%m-%d %H:%M:%S")
        self.tray.setToolTip(self.lastcheck)
