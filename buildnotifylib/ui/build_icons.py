from importlib.resources import files

from PySide6 import QtCore, QtGui

ICONS = files("buildnotifylib") / "resources" / "icons"


class BuildIcons:
    success_sleeping = "buildnotify-success"
    success_building = "buildnotify-success-building"
    failure_sleeping = "buildnotify-failure"
    failure_building = "buildnotify-failure-building"
    unavailable = "buildnotify-inactive"

    def __init__(self):
        self.all_status = {
            "Success.Sleeping": self.success_sleeping,
            "Success.CheckingModifications": self.success_sleeping,
            "Success.Building": self.success_building,
            "Failure.Sleeping": self.failure_sleeping,
            "Failure.CheckingModifications": self.failure_sleeping,
            "Failure.Building": self.failure_building,
            "unavailable": self.unavailable,
        }

    def for_status(self, status) -> QtGui.QIcon:
        name = self.icon_name(status)
        return QtGui.QIcon.fromTheme(name, self.fallback(name))

    def fallback(self, name: str) -> QtGui.QIcon:
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData((ICONS / f"{name}.svg").read_bytes())
        return QtGui.QIcon(pixmap)

    def for_aggregate_status(self, status, count) -> QtGui.QIcon:
        if count == 0:
            return self.for_status(status)
        icon = self.for_status(status)
        pixmap = icon.pixmap(22, 22)
        painter = QtGui.QPainter(pixmap)
        painter.setOpacity(1)
        painter.drawText(pixmap.rect(), QtCore.Qt.AlignmentFlag.AlignCenter, str(count))
        painter.end()
        return QtGui.QIcon(pixmap)

    def icon_name(self, status: str) -> str:
        return self.all_status.get(status, self.unavailable)
