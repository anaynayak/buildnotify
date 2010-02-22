from PyQt4 import QtGui, QtCore
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

    def for_aggregate_status(self, status, count):
        if count is "0":
            return self.for_status(status)
        self.textFont = QtGui.QFont()
        self.textFont.setPixelSize(12)
        pixmap = QtGui.QPixmap(self.get_path(status))
        painter = QtGui.QPainter(pixmap)
        painter.setFont(self.textFont)
        painter.drawText(pixmap.rect(), QtCore.Qt.AlignCenter, count)
        painter.end()
        return QtGui.QIcon(pixmap)

    def get_path(self, status):
        if self.all_status.has_key(status):
            return self.resource_path % self.all_status[status]
        return self.resource_path % self.all_status['unavailable']

    def for_count(self, count):
        pixmap = QtGui.QPixmap(24, 24)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.drawText(pixmap.rect(), QtCore.Qt.AlignCenter, count)
        painter.end()
        return QtGui.QIcon(pixmap)
