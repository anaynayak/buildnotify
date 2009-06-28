class ProjectStatusNotification:
    def __init__(self, old_projects, current_projects, notification):
        self.project_status = ProjectStatus(old_projects, current_projects)
        self.notification = notification

    def show_notifications(self):
        self.show_notification_msg(self.project_status.successful_builds(), "Fixed builds")
        self.show_notification_msg(self.project_status.failing_builds(), "Broken builds")
    
    def show_notification_msg(self, builds, message):
        if builds == []:
            return
        self.notification.update(message, "\n".join(builds), None)
        if not self.notification.show():
            print "Failed to send notification."
            gtk.main_quit()
        
class ProjectStatus:
    def __init__(self, old_projects, current_projects): 
        self.old_projects = old_projects
        self.current_projects = current_projects
    
    def failing_builds(self):
        current_status = self.current_projects.to_map()
        old_status = self.old_projects.to_map()
        broken_builds = self.remove_all(current_status['Failure'], old_status['Failure'])
        return broken_builds
    def successful_builds(self):
        current_status = self.current_projects.to_map()
        old_status = self.old_projects.to_map()
        fixed_builds = self.remove_all(current_status['Success'], old_status['Success'])
        return fixed_builds
        
    def still_failing_builds(self):
        pass
    def still_sucessful_builds(self):
        pass
    
    def remove_all(self, source, removal):
        return filter(lambda ele: ele not in removal, source)
    

