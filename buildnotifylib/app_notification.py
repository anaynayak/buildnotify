from project_status_notification import ProjectStatusNotification
from notifications import Notification

class AppNotification:
    def __init__(self, config, widget):
        self.config = config
        self.notification = Notification(widget)
        self.integration_status = None
        
    def update_projects(self, new_integration_status):
        if self.integration_status is not None :
            ProjectStatusNotification(self.config, self.integration_status, new_integration_status, self.notification).show_notifications()
        self.integration_status = new_integration_status
