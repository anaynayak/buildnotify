import sys
import webbrowser

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QMessageBox, QAction, QMenu
from buildnotifylib.core.distance_of_time import DistanceOfTime
from preferences import PreferencesDialog
from version import VERSION


class AppMenu(QtCore.QObject):
    reload_data = QtCore.pyqtSignal()

    def __init__(self, widget, conf, build_icons):
        super(AppMenu, self).__init__(widget)
        self.menu = QMenu(widget)
        self.conf = conf
        self.build_icons = build_icons
        self.create_default_menu_items()

    def update(self, projects):
        self.menu.clear()
        for project in self.sorted_projects(projects):
            icon = self.build_icons.for_status(project.get_build_status())
            self.create_menu_item(project, icon)
        self.create_default_menu_items()

    def sorted_projects(self, projects):
        if self.conf.get_sort_by_name():
            return sorted(projects, key=lambda p: p.label())
        return sorted(projects, key=lambda p: p.get_last_build_time(), reverse=True)

    def create_default_menu_items(self):
        self.menu.addSeparator()
        self.menu.addAction(QAction("About", self.menu, triggered=self.about_clicked))
        self.menu.addAction(QAction("Preferences", self.menu, triggered=self.preferences_clicked))
        self.menu.addAction(QAction("Exit", self.menu, triggered=self.exit))

    def about_clicked(self, widget):
        QMessageBox.about(self.menu, "About BuildNotify %s" % VERSION,
                                "<b>BuildNotify %s</b> has been developed using PyQt5 and serves as a build notification tool for cruise control. In case of any suggestions/bugs," % VERSION +
                                "please visit <a href=\"http://bitbucket.org/Anay/buildnotify\">http://bitbucket.org/Anay/buildnotify</a> and provide your feedback.")

    def preferences_clicked(self, widget):
        preferences = PreferencesDialog(self.conf, self.menu).open()
        if preferences is not None:
            self.conf.update_preferences(preferences)
            self.reload_data.emit()

    def exit(self, widget):
        sys.exit()

    def create_menu_item(self, project, icon):
        menu_item_label = project.label()
        if self.conf.get_value("lastBuildTimeForProject"):
            menu_item_label = menu_item_label + ", " + DistanceOfTime(project.get_last_build_time()).age() + " ago"

        action = self.menu.addAction(icon, menu_item_label)
        action.setIconVisibleInMenu(True)
        action.triggered.connect(self.open_url(project.url))

    def open_url(self, url):
        return lambda: webbrowser.open(url)
