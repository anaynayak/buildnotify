from PyQt4 import QtGui, QtCore
import icons_rc

class BuildIcons:
    success_sleeping = 'icon-success.svg'
    success_building = 'icon-success-building.svg'
    failure_sleeping = 'icon-failure.svg'
    failure_building = 'icon-failure-building.svg'
    unavailable = 'icon-inactive.svg'
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

    def for_aggregate_status(self, status, count):
        if count is "0":
            return self.for_status(status)
        icon = self.for_status(status)
        pixmap = icon.pixmap(22,22)
        painter = QtGui.QPainter(pixmap)
        painter.setOpacity(1)
        painter.drawText(pixmap.rect(), QtCore.Qt.AlignCenter, count)
        painter.end()
        return QtGui.QIcon(pixmap)

    def get_path(self, status):
        if self.all_status.has_key(status):
            return self.resource_path % self.all_status[status]
        return self.resource_path % self.all_status['unavailable']
