from PyQt4 import QtGui
from time import strftime
import build_icons
from app_menu import AppMenu

class AppUi:
    def __init__(self, conf):
        self.widget = QtGui.QWidget()
        self.build_icons = build_icons.BuildIcons(conf.icon_dir)
        self.tray = QtGui.QSystemTrayIcon(self.build_icons.for_status(None), self.widget)
        self.tray.show()
        self.app_menu = AppMenu(self.tray, self.widget, conf, self.build_icons);

    def update_projects(self,updated_projects):
        self.tray.setIcon(self.build_icons.for_status(updated_projects.get_build_status()))
        count = str(len(updated_projects.get_failing_builds()))
        if count is "0":
            count = ""
        self.app_menu.update(updated_projects.all_projects)
#        self.failing_build_count.set_label(count)
        self.lastcheck = "Last checked: " + strftime("%Y-%m-%d %H:%M:%S")
#        self.tray.showMessage("self.lastcheck", "asdasd", QtGui.QSystemTrayIcon.Information,1000)
        self.tray.setToolTip(self.lastcheck)
        self.projects = updated_projects
        pass