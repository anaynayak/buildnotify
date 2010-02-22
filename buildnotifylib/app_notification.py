import pynotify
from project_status_notification import ProjectStatusNotification

class AppNotification:
    def __init__(self):
        if not pynotify.init(" buildnotify "):
            sys.exit(1)
        self.notification = pynotify.Notification("buildnotify", "buildnotify", None, None)
        self.integration_status = None
        self.notification.update("buildnotify", "Buildnotify has started...")

    def update_projects(self, new_integration_status):
        if self.integration_status is not None :
            ProjectStatusNotification(self.integration_status, new_integration_status, self.notification).show_notifications()
        self.integration_status = new_integration_status
