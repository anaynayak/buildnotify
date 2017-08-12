from PyQt5 import QtGui, QtCore


class BuildIcons:
    success_sleeping = 'buildnotify-success'
    success_building = 'buildnotify-success-building'
    failure_sleeping = 'buildnotify-failure'
    failure_building = 'buildnotify-failure-building'
    unavailable = 'buildnotify-inactive'
    resource_path = ":/status/icons/%s.svg"
    theme_resource_path = "%s"

    def __init__(self):
        self.all_status = {'Success.Sleeping': self.success_sleeping, 'Success.CheckingModifications': self.success_sleeping, 'Success.Building': self.success_building,
                           'Failure.Sleeping': self.failure_sleeping, 'Failure.CheckingModifications': self.failure_sleeping, 'Failure.Building': self.failure_building,
                           'unavailable': self.unavailable}

    def for_status(self, status):
        return QtGui.QIcon.fromTheme(self.get_path(self.theme_resource_path, status), QtGui.QIcon(self.get_path(self.resource_path, status)))

    def for_aggregate_status(self, status, count):
        if count is "0":
            return self.for_status(status)
        icon = self.for_status(status)
        pixmap = icon.pixmap(22, 22)
        painter = QtGui.QPainter(pixmap)
        painter.setOpacity(1)
        painter.drawText(pixmap.rect(), QtCore.Qt.AlignCenter, count)
        painter.end()
        return QtGui.QIcon(pixmap)

    def get_path(self, resource_path, status):
        if status in self.all_status:
            return resource_path % self.all_status[status]
        return resource_path % self.all_status['unavailable']
