import sys
import webbrowser

from PyQt4 import QtGui
from PyQt4 import QtCore
from buildnotifylib.core.distance_of_time import DistanceOfTime
from preferences import PreferencesDialog
from version import VERSION


class AppMenu(QtCore.QObject):
    reload_data = QtCore.pyqtSignal()

    def __init__(self, widget, conf, build_icons):
        super(AppMenu, self).__init__(widget)
        self.menu = QtGui.QMenu(widget)
        self.conf = conf
        self.build_icons = build_icons
        self.create_default_menu_items()

    def update(self, projects):
        self.menu.clear()
        for project in self.sorted_projects(projects):
            icon = self.build_icons.for_status(project.get_build_status())
            self.create_menu_item(project.name, icon, project.url, project.get_last_build_time(),
                                  project.server_url)
        self.create_default_menu_items()

    def sorted_projects(self, projects):
        if self.conf.get_sort_by_name():
            return sorted(projects, key=lambda p: p.name)
        return sorted(projects, key=lambda p: p.get_last_build_time(), reverse=True)

    def create_default_menu_items(self):
        self.menu.addSeparator()
        self.menu.addAction(QtGui.QAction("About", self.menu, triggered=self.about_clicked))
        self.menu.addAction(QtGui.QAction("Preferences", self.menu, triggered=self.preferences_clicked))
        self.menu.addAction(QtGui.QAction("Exit", self.menu, triggered=self.exit))

    def about_clicked(self, widget):
        QtGui.QMessageBox.about(self.menu, "About BuildNotify %s" % VERSION,
                                "<b>BuildNotify %s</b> has been developed using PyQt4 and serves as a build notification tool for cruise control. In case of any suggestions/bugs," % VERSION +
                                "please visit <a href=\"http://bitbucket.org/Anay/buildnotify\">http://bitbucket.org/Anay/buildnotify</a> and provide your feedback.")

    def preferences_clicked(self, widget):
        self.preferences_dialog = PreferencesDialog(self.conf, self.menu)
        if self.preferences_dialog.exec_() == QtGui.QDialog.Accepted:
            self.preferences_dialog.save()
            self.reload_data.emit()

    def exit(self, widget):
        sys.exit()

    def create_menu_item(self, label, icon, url, last_build_time, server_url):
        menu_item_label = label
        if self.conf.get_display_prefix(server_url):
            menu_item_label = "[" + self.conf.get_display_prefix(server_url) + "] " + menu_item_label
        if self.conf.get_value("lastBuildTimeForProject"):
            menu_item_label = menu_item_label + ", " + DistanceOfTime(last_build_time, self.conf.get_project_timezone(url, server_url)).age() + " ago"

        action = self.menu.addAction(icon, menu_item_label)
        action.setIconVisibleInMenu(True)
        receiver = lambda url=url: self.open_url(self, url)
        QtCore.QObject.connect(action, QtCore.SIGNAL('triggered()'), receiver)

    def open_url(self, something, url):
        webbrowser.open(url)
