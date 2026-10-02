from importlib.resources import files

from PySide6 import QtCore, QtGui

ICONS = files("buildnotifylib") / "resources" / "icons"
TRAY_SIZE = QtCore.QSize(22, 22)
RASTER_SIZE = QtCore.QSize(128, 128)
SYMBOLIC = "-symbolic"


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

    def for_status(self, status, symbolic: bool = False) -> QtGui.QIcon:
        name = self.icon_name(status, symbolic)
        if symbolic and not QtGui.QIcon.hasThemeIcon(name):
            # fromTheme would fall back to the theme's coloured icon by dropping the suffix.
            return self.fallback(name)
        return QtGui.QIcon.fromTheme(name, self.fallback(name))

    def fallback(self, name: str) -> QtGui.QIcon:
        return QtGui.QIcon(QtGui.QPixmap.fromImage(rasterise((ICONS / f"{name}.svg").read_bytes())))

    def for_aggregate_status(
        self, status, count: int, device_pixel_ratio: float = 1.0, symbolic: bool = False
    ) -> QtGui.QIcon:
        if count == 0:
            return self.for_status(status, symbolic)
        pixmap = self.for_status(status, symbolic).pixmap(TRAY_SIZE, device_pixel_ratio)
        draw_count(pixmap, count)
        return QtGui.QIcon(pixmap)

    def icon_name(self, status: str, symbolic: bool = False) -> str:
        return self.all_status.get(status, self.unavailable) + (SYMBOLIC if symbolic else "")


def rasterise(svg: bytes) -> QtGui.QImage:
    """Render at a fixed size well above the tray's, so HiDPI screens scale down, not up."""
    buffer = QtCore.QBuffer()
    buffer.setData(QtCore.QByteArray(svg))
    buffer.open(QtCore.QIODevice.OpenModeFlag.ReadOnly)
    reader = QtGui.QImageReader(buffer, b"svg")
    reader.setScaledSize(RASTER_SIZE)
    return reader.read()


def draw_count(pixmap: QtGui.QPixmap, count: int) -> None:
    """Paint in logical pixels; QPainter scales to the pixmap's device pixel ratio."""
    painter = QtGui.QPainter(pixmap)
    painter.setRenderHint(QtGui.QPainter.RenderHint.TextAntialiasing)
    font = painter.font()
    font.setBold(True)
    font.setPixelSize(TRAY_SIZE.height() * 2 // 3)
    painter.setFont(font)
    rect = QtCore.QRect(QtCore.QPoint(0, 0), TRAY_SIZE)
    painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter, str(count))
    painter.end()
