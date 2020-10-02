from typing import Optional

from PyQt5.QtWidgets import QWidget
from buildnotifylib.core.projects import OverallIntegrationStatus

from buildnotifylib.config import Config
from buildnotifylib.notifications import Notification
from buildnotifylib.project_status_notification import ProjectStatusNotification


class AppNotification(object):
    def __init__(self, config: Config, widget: QWidget):
        self.config = config
        self.notification = Notification(widget)
        self.integration_status: Optional[OverallIntegrationStatus] = None

    def update_projects(self, new_integration_status: OverallIntegrationStatus):
        if self.integration_status is not None:
            ProjectStatusNotification(self.config, self.integration_status, new_integration_status,
                                      self.notification).show_notifications()
        self.integration_status = new_integration_status
