import sys

from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMessageBox

from buildnotifylib.app_notification import AppNotification
from buildnotifylib.app_ui import AppUi
from buildnotifylib.build_icons import BuildIcons
from buildnotifylib.config import Config
from buildnotifylib.core.projects import ProjectsPopulator, OverallIntegrationStatus
from buildnotifylib.core.timed_event import TimedEvent
from buildnotifylib.core.repeat_timed_event import RepeatTimedEvent


class BuildNotify(object):
    TRAY_RETRIES = 5

    def __init__(self, app: QApplication, conf=None, interval=2000):
        self.conf = conf if conf is not None else Config()
        self.build_icons = BuildIcons()
        self.app = app
        self.app.setWindowIcon(self.build_icons.for_status("Success.Sleeping"))
        self.ready = False
        self.timed_event = RepeatTimedEvent(self.app, self.delayed_start, self.TRAY_RETRIES, interval)
        self.timed_event.start()

    def delayed_start(self, event_count: int):
        if self.ready:
            return
        if not QSystemTrayIcon.isSystemTrayAvailable():
            if event_count == self.TRAY_RETRIES - 1:
                QMessageBox.critical(None, "BuildNotify", "I couldn't detect any system tray on this system.")
                self.app.exit(1)
            return
        self.ready = True
        self.run_app()

    def run_app(self):
        self.projects_populator = ProjectsPopulator(self.conf, self.app)
        self.projects_populator.updated_projects.connect(self.update_projects)
        self.app_ui = AppUi(self.app, self.conf, self.build_icons)
        self.app_ui.reload_data.connect(self.reload_project_data)
        self.app_notification = AppNotification(self.conf, self.app_ui.tray)
        self.auto_poll()

    def reload_project_data(self):
        self.projects_populator.reload()

    def update_projects(self, integration_status: OverallIntegrationStatus):
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

    @staticmethod
    def start():
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        buildnotify = BuildNotify(app)
        sys.exit(buildnotify.app.exec_())


if __name__ == '__main__':
    BuildNotify.start()
