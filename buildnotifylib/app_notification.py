from PyQt5.QtWidgets import QSystemTrayIcon

from buildnotifylib.config import Config
from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.backoff import Backoff
from buildnotifylib.notifications import Notification
from buildnotifylib.project_status_notification import ProjectStatusNotification


class AppNotification:
    def __init__(self, config: Config, widget: QSystemTrayIcon):
        self.config = config
        self.notification = Notification(widget)
        self.integration_status: OverallIntegrationStatus | None = None
        self.backoff = Backoff()

    def update_projects(self, new_integration_status: OverallIntegrationStatus):
        if self.integration_status is not None:
            notifier = ProjectStatusNotification(
                self.config, self.integration_status, new_integration_status, self.notification, self.backoff
            )
            notifier.show_notifications()
            self.backoff = notifier.backoff
        self.integration_status = new_integration_status
