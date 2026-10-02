from PyQt5.QtWidgets import QSystemTrayIcon

from buildnotifylib.adapters.settings_store import SettingsStore
from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.backoff import Backoff
from buildnotifylib.core.ports import Hook
from buildnotifylib.notifications import Notification
from buildnotifylib.project_status_notification import ProjectStatusNotification


class AppNotification:
    def __init__(self, store: SettingsStore, widget: QSystemTrayIcon, hook: Hook):
        self.store = store
        self.hook = hook
        self.notification = Notification(widget)
        self.integration_status: OverallIntegrationStatus | None = None
        self.backoff = Backoff()

    def update_projects(self, new_integration_status: OverallIntegrationStatus):
        if self.integration_status is not None:
            notifier = ProjectStatusNotification(
                self.store.settings,
                self.integration_status,
                new_integration_status,
                self.notification,
                self.hook,
                self.backoff,
            )
            notifier.show_notifications()
            self.backoff = notifier.backoff
        self.integration_status = new_integration_status
