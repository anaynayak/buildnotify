import pynotify
from project_status_notification import ProjectStatusNotification

class AppNotification:
    def __init__(self):
        if not pynotify.init(" buildnotify "):
            sys.exit(1)
        self.notification = pynotify.Notification("buildnotify", "buildnotify", None, None)
        self.projects = None
        self.notification.update("buildnotify", "Cruise applet has started...")

    def update_projects(self, updated_projects):
        if self.projects is not None :
            ProjectStatusNotification(self.projects, updated_projects, self.notification).show_notifications()
        self.projects = updated_projects
