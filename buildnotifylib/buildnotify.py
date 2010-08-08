from app_ui import AppUi
from app_notification import AppNotification
from config import Config
from projects import ProjectsPopulator
from PyQt4 import QtGui, QtCore
import sys
import build_icons
from timed_event import TimedEvent, RepeatTimedEvent

class BuildNotify:
    def __init__(self):
        self.conf = Config()
        self.app = QtGui.QApplication(sys.argv)
        self.buildIcons = build_icons.BuildIcons()
        icon = self.buildIcons.for_status("Success.Sleeping")
        self.app.setWindowIcon(icon)
        self.ready = False
        self.timed_event = RepeatTimedEvent(self.app, self.delayed_start, 5)
        QtGui.QApplication.setQuitOnLastWindowClosed(False)
        self.timed_event.start()
        sys.exit(self.app.exec_())

    def delayed_start(self, event_count):
        if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
            if (event_count == 5) :
                QtGui.QMessageBox.critical(None, "BuildNotify",
                    "I couldn't detect any system tray on this system.")
                sys.exit(1)
            self.timed_event.start()
        if not self.ready:
            self.ready = True
            self.run_app()

    def run_app(self):
        self.projects_populator = ProjectsPopulator(self.conf, self.app)
        self.app.connect(self.projects_populator, QtCore.SIGNAL('updated_projects'), self.update_projects)
        self.app_ui = AppUi(self.conf, self.buildIcons)
        self.app_notification = AppNotification(self.conf, self.app_ui.tray)
        self.auto_poll()
        
    def update_projects(self, integration_status):
        self.app_notification.update_projects(integration_status)
        self.app_ui.update_projects(integration_status)

    def auto_poll(self):
        self.timed_event = TimedEvent(self.app, self.check_nodes)
        self.timed_event.set_interval(1000)
        self.timed_event.start()

    def check_nodes(self):
        self.projects_populator.load_from_server()
        self.timed_event.set_interval(self.conf.get_interval_in_millis())
        self.timed_event.start()

if __name__== '__main__':
    BuildNotify()
