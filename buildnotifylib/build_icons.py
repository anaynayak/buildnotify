from PyQt4 import QtGui
import icons_rc

class BuildIcons:
    success_sleeping = '/icon-success.png'
    success_building = '/icon-success-building.png'
    failure_sleeping = '/icon-failure.png'
    failure_building = '/icon-failure-building.png'
    unavailable = '/icon-inactive.png'
    resource_path = ":/status/icons/%s"
    
    def __init__(self):
        self.all_status = {'Success.Sleeping':self.success_sleeping,
         'Success.CheckingModifications': self.success_sleeping,
         'Success.Building':self.success_building, 
         'Failure.Sleeping':self.failure_sleeping, 
         'Failure.CheckingModifications': self.failure_sleeping,
         'Failure.Building': self.failure_building, 
         'unavailable':self.unavailable }
 
    def for_status(self, status):
        return QtGui.QIcon(self.get_path(status))

    def get_path(self, status):
        if self.all_status.has_key(status):
            return self.resource_path % self.all_status[status]
        return self.resource_path % self.all_status['unavailable']
