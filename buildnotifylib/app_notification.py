from PyQt5.QtWidgets import QWidget

from buildnotifylib.config import Config
from buildnotifylib.core.projects import OverallIntegrationStatus
from buildnotifylib.notifications import Notification
from buildnotifylib.project_status_notification import ProjectStatusNotification, TimedProjectFilter


class AppNotification:
    def __init__(self, config: Config, widget: QWidget):
        self.config = config
        self.notification = Notification(widget)
        self.integration_status: OverallIntegrationStatus | None = None
        self.timed_project_filter = TimedProjectFilter()

    def update_projects(self, new_integration_status: OverallIntegrationStatus):
        if self.integration_status is not None:
            ProjectStatusNotification(
                self.config,
                self.integration_status,
                new_integration_status,
                self.notification,
                self.timed_project_filter,
            ).show_notifications()
        self.integration_status = new_integration_status
