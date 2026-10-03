import os

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from buildnotifylib.adapters.settings_store import SettingsStore
from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.no_tray_message import no_tray_message
from buildnotifylib.core.ports import Connection, Hook
from buildnotifylib.ui.app_notification import AppNotification
from buildnotifylib.ui.app_ui import AppUi
from buildnotifylib.ui.build_icons import BuildIcons
from buildnotifylib.ui.poller import Poller


class BuildNotify:
    TRAY_RETRIES = 5
    EXIT_WAIT_MS = 2000

    def __init__(
        self,
        app: QApplication,
        store: SettingsStore,
        connection: Connection,
        hook: Hook,
        interval: int = 2000,
    ):
        self.store = store
        self.connection = connection
        self.hook = hook
        self.build_icons = BuildIcons()
        self.app = app
        self.app.setWindowIcon(self.build_icons.for_status("Success.Sleeping"))
        self.ready = False
        self.tray_attempts = 0
        self.tray_timer = QTimer()
        self.tray_timer.timeout.connect(self.retry_tray)
        self.tray_timer.start(interval)

    def retry_tray(self):
        attempt = self.tray_attempts
        self.tray_attempts += 1
        if self.tray_attempts >= self.TRAY_RETRIES:
            self.tray_timer.stop()
        self.delayed_start(attempt)

    def delayed_start(self, event_count: int):
        if self.ready:
            return
        if not QSystemTrayIcon.isSystemTrayAvailable():
            if event_count == self.TRAY_RETRIES - 1:
                self.show_no_tray_message()
                self.app.exit(1)
            return
        self.ready = True
        self.tray_timer.stop()
        self.run_app()

    def show_no_tray_message(self):
        text = no_tray_message(os.environ.get("XDG_CURRENT_DESKTOP"))
        box = QMessageBox(QMessageBox.Icon.Critical, "BuildNotify", text)
        box.setWindowTitle("BuildNotify")
        box.setWindowIcon(self.build_icons.for_status("Success.Sleeping"))
        box.exec()

    def run_app(self):
        self.poller = Poller(self.store, self.connection, self.app)
        self.poller.updated.connect(self.update_projects)
        self.app_ui = AppUi(self.app, self.store, self.build_icons, self.connection)
        self.app_ui.reload_data.connect(self.poller.reload)
        self.app_notification = AppNotification(self.store, self.app_ui.tray, self.hook)
        self.poller.start()
        QTimer.singleShot(0, self.app_ui.app_menu.offer_first_server)

    def update_projects(self, integration_status: OverallIntegrationStatus):
        self.app_notification.update_projects(integration_status)
        self.app_ui.update_projects(integration_status)

    def wait_for_workers(self) -> bool:
        if not hasattr(self, "poller"):
            return True
        return self.poller.wait(self.EXIT_WAIT_MS)
