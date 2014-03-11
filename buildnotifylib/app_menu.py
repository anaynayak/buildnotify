import sys
import webbrowser

from PyQt4 import QtGui
from PyQt4 import QtCore
from buildnotifylib.core.distance_of_time import DistanceOfTime
from preferences import PreferencesDialog
from version import VERSION


class AppMenu:
    def __init__(self, app, tray, widget, conf, build_icons):
        self.menu = QtGui.QMenu(widget)
        tray.setContextMenu(self.menu)
        self.conf = conf
        self.app = app
        self.build_icons = build_icons
        self.create_default_menu_items()

    def update(self, projects):
        projects.sort(lambda x, y: (x.last_build_time - y.last_build_time).days)
        self.menu.clear()
        for project in projects:
            self.create_menu_item(project.name, self.build_icons.for_status(project.get_build_status()), project.url, project.last_build_time, project.server_url)
        self.create_default_menu_items()

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
            self.app.emit(QtCore.SIGNAL('reload_project_data'))

    def exit(self, widget):
        sys.exit()

    def create_menu_item(self, label, icon, url, last_build_time, server_url):

        menu_item_label = label
        if self.conf.get_value("lastBuildTimeForProject"):
            menu_item_label = label + ", " + DistanceOfTime(last_build_time, self.conf.get_project_timezone(url, server_url)).age() + " ago"

        action = self.menu.addAction(icon, menu_item_label)
        action.setIconVisibleInMenu(True)
        receiver = lambda url=url: self.open_url(self, url)
        QtCore.QObject.connect(action, QtCore.SIGNAL('triggered()'), receiver)

    def open_url(self, something, url):
        webbrowser.open(url)
