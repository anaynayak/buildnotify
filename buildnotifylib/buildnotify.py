from app_ui import AppUi
from app_notification import AppNotification
from config import Config
from projects import ProjectsPopulator
from PyQt4 import QtGui, QtCore
import sys
import build_icons

class BuildNotify:
    def __init__(self):
        self.conf = Config()
        app = QtGui.QApplication(sys.argv)
        buildIcons = build_icons.BuildIcons()
        icon = buildIcons.for_status("Success.Sleeping")
        app.setWindowIcon(icon)
        if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
            QtGui.QMessageBox.critical(None, "BuildNotify",
                    "I couldn't detect any system tray on this system.")
            sys.exit(1)

        QtGui.QApplication.setQuitOnLastWindowClosed(False)
        self.run_app(app, buildIcons)
        sys.exit(app.exec_())

    def run_app(self, app, buildIcons):
        self.projects_populator = ProjectsPopulator(self.conf)
        self.app_ui = AppUi(self.conf, buildIcons)
        self.app_notification = AppNotification(self.conf, self.app_ui.tray)
        self.projects_populator.add_listener(self.app_notification)
        self.projects_populator.add_listener(self.app_ui)
        self.auto_poll(app)
        self.check_nodes()

    def auto_poll(self, app):
        self.timer = QtCore.QTimer()
        app.connect(self.timer, QtCore.SIGNAL('timeout()'), self.check_nodes)
        self.timer.setInterval(1000)
        self.timer.setSingleShot(True)
        self.timer.start()

    def check_nodes(self):
        self.projects_populator.load_from_server(self.conf)
        self.timer.setInterval(self.conf.check_interval * 1000)
        self.timer.setSingleShot(True)
        self.timer.start()

if __name__== '__main__':
    BuildNotify()
