import math
from importlib.resources import files

from PySide6 import QtCore, QtGui

ICONS = files("buildnotifylib") / "resources" / "icons"
TRAY_SIZE = QtCore.QSize(22, 22)
RASTER_SIZE = QtCore.QSize(128, 128)
SYMBOLIC = "-symbolic"
MUTED_OPACITY = 0.35


class BuildIcons:
    success_sleeping = "buildnotify-success"
    success_building = "buildnotify-success-building"
    failure_sleeping = "buildnotify-failure"
    failure_building = "buildnotify-failure-building"
    unavailable = "buildnotify-inactive"
    unreachable = "buildnotify-unreachable"

    def __init__(self):
        self.all_status = {
            "Success.Sleeping": self.success_sleeping,
            "Success.CheckingModifications": self.success_sleeping,
            "Success.Building": self.success_building,
            "Failure.Sleeping": self.failure_sleeping,
            "Failure.CheckingModifications": self.failure_sleeping,
            "Failure.Building": self.failure_building,
            "unavailable": self.unavailable,
            "unreachable": self.unreachable,
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

    def for_muted(self, status) -> QtGui.QIcon:
        return dimmed(self.for_status(status))

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


BADGE_COLOUR = QtGui.QColor("#c62828")
BADGE_HEIGHT = 0.5
BADGE_DIGIT_WIDTH = 0.45
BADGE_RING = 1.0


def badge_label(count: int) -> str:
    return str(count) if count < 100 else "99+"


def badge_rect(count: int, device_pixel_ratio: float) -> QtCore.QRectF:
    """Bottom-right badge in logical pixels, snapped to whole device pixels."""

    def snap(logical: float) -> float:
        return math.ceil(logical * device_pixel_ratio) / device_pixel_ratio

    height = snap(TRAY_SIZE.height() * BADGE_HEIGHT)
    extra_digits = len(badge_label(count)) - 1
    width = min(snap(height * (1 + BADGE_DIGIT_WIDTH * extra_digits)), TRAY_SIZE.width())
    return QtCore.QRectF(TRAY_SIZE.width() - width, TRAY_SIZE.height() - height, width, height)


def dimmed(icon: QtGui.QIcon) -> QtGui.QIcon:
    source = icon.pixmap(TRAY_SIZE)
    pixmap = QtGui.QPixmap(source.size())
    pixmap.setDevicePixelRatio(source.devicePixelRatio())
    pixmap.fill(QtCore.Qt.GlobalColor.transparent)
    painter = QtGui.QPainter(pixmap)
    painter.setOpacity(MUTED_OPACITY)
    painter.drawPixmap(0, 0, source)
    painter.end()
    return QtGui.QIcon(pixmap)


def draw_count(pixmap: QtGui.QPixmap, count: int) -> None:
    """Paint in logical pixels; QPainter scales to the pixmap's device pixel ratio."""
    rect = badge_rect(count, pixmap.devicePixelRatio())
    radius = rect.height() / 2
    ring = rect.adjusted(-BADGE_RING, -BADGE_RING, BADGE_RING, BADGE_RING)
    painter = QtGui.QPainter(pixmap)
    painter.setRenderHints(QtGui.QPainter.RenderHint.Antialiasing | QtGui.QPainter.RenderHint.TextAntialiasing)
    painter.setPen(QtCore.Qt.PenStyle.NoPen)
    painter.setBrush(BADGE_COLOUR)
    painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Clear)
    painter.drawRoundedRect(ring, radius + BADGE_RING, radius + BADGE_RING)
    painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_SourceOver)
    painter.drawRoundedRect(rect, radius, radius)
    draw_label(painter, rect, badge_label(count))
    painter.end()


def draw_label(painter: QtGui.QPainter, rect: QtCore.QRectF, label: str) -> None:
    font = painter.font()
    font.setBold(True)
    font.setPixelSize(round(rect.height() * 0.8))
    painter.setFont(font)
    painter.setPen(QtGui.QColor("white"))
    painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter, label)
