import os
import sys

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from buildnotifylib.adapters.http import HttpConnection
from buildnotifylib.adapters.settings_store import SettingsStore
from buildnotifylib.app_notification import AppNotification
from buildnotifylib.app_ui import AppUi
from buildnotifylib.build_icons import BuildIcons
from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.ports import Connection
from buildnotifylib.core.projects import ProjectsPopulator
from buildnotifylib.core.repeat_timed_event import RepeatTimedEvent
from buildnotifylib.core.timed_event import TimedEvent


class BuildNotify:
    TRAY_RETRIES = 5
    EXIT_WAIT_MS = 2000

    def __init__(
        self,
        app: QApplication,
        store: SettingsStore | None = None,
        interval=2000,
        connection: Connection | None = None,
    ):
        self.store = store if store is not None else SettingsStore(QSettings("BuildNotify", "BuildNotify"))
        self.connection = connection or HttpConnection()
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
        self.projects_populator = ProjectsPopulator(self.store, self.connection, self.app)
        self.projects_populator.updated_projects.connect(self.update_projects)
        self.app_ui = AppUi(self.app, self.store, self.build_icons)
        self.app_ui.reload_data.connect(self.reload_project_data)
        self.app_notification = AppNotification(self.store, self.app_ui.tray)
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
        self.timed_event.set_interval(self.store.settings.interval_seconds * 1000)
        self.timed_event.start()

    def wait_for_workers(self) -> bool:
        if not hasattr(self, "projects_populator"):
            return True
        return self.projects_populator.wait(self.EXIT_WAIT_MS)

    @staticmethod
    def start():
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        buildnotify = BuildNotify(app)
        exit_code = buildnotify.app.exec_()
        if not buildnotify.wait_for_workers():
            sys.stdout.flush()
            os._exit(exit_code)
        else:
            sys.exit(exit_code)


if __name__ == "__main__":
    BuildNotify.start()
