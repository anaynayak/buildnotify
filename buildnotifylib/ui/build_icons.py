import math
from importlib.resources import files

from PySide6 import QtCore, QtGui

ICONS = files("buildnotifylib") / "resources" / "icons"
TRAY_SIZE = QtCore.QSize(22, 22)
SMALL_TRAY_SIZE = QtCore.QSize(16, 16)
EXCLAIM_BELOW = 20
RASTER_SIZE = QtCore.QSize(128, 128)
SYMBOLIC = "-symbolic"
MUTED_OPACITY = 0.35
TRAY_RATIOS = (1.0, 2.0)


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
        self,
        status,
        count: int,
        symbolic: bool = False,
        size: QtCore.QSize = TRAY_SIZE,
    ) -> QtGui.QIcon:
        return tray_icon(self.for_status(status, symbolic), count, size)

    def for_muted(self, status) -> QtGui.QIcon:
        return tray_icon(self.for_status(status), 0, TRAY_SIZE, MUTED_OPACITY)

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


def badge_label(count: int, size: QtCore.QSize = TRAY_SIZE) -> str:
    """Digits are too small to read below EXCLAIM_BELOW px, so say only that something failed."""
    if size.height() < EXCLAIM_BELOW:
        return "!"
    return str(count) if count < 100 else "99+"


def badge_rect(count: int, device_pixel_ratio: float, size: QtCore.QSize = TRAY_SIZE) -> QtCore.QRectF:
    """Bottom-right badge in logical pixels, snapped to whole device pixels."""

    def snap(logical: float) -> float:
        return math.ceil(logical * device_pixel_ratio) / device_pixel_ratio

    height = snap(size.height() * BADGE_HEIGHT)
    extra_digits = len(badge_label(count, size)) - 1
    width = min(snap(height * (1 + BADGE_DIGIT_WIDTH * extra_digits)), size.width())
    return QtCore.QRectF(size.width() - width, size.height() - height, width, height)


def tray_icon(source: QtGui.QIcon, count: int, size: QtCore.QSize, opacity: float = 1.0) -> QtGui.QIcon:
    """Every tray state goes through here, so macOS gets the same logical size with 1x and 2x pixmaps."""
    icon = QtGui.QIcon()
    for ratio in TRAY_RATIOS:
        pixmap = source.pixmap(size, ratio)
        if opacity < 1.0:
            pixmap = faded(pixmap, opacity)
        if count:
            draw_count(pixmap, count, size)
        icon.addPixmap(pixmap)
    return icon


def faded(source: QtGui.QPixmap, opacity: float) -> QtGui.QPixmap:
    pixmap = QtGui.QPixmap(source.size())
    pixmap.setDevicePixelRatio(source.devicePixelRatio())
    pixmap.fill(QtCore.Qt.GlobalColor.transparent)
    painter = QtGui.QPainter(pixmap)
    painter.setOpacity(opacity)
    painter.drawPixmap(0, 0, source)
    painter.end()
    return pixmap


def draw_count(pixmap: QtGui.QPixmap, count: int, size: QtCore.QSize = TRAY_SIZE) -> None:
    """Paint in logical pixels; QPainter scales to the pixmap's device pixel ratio."""
    rect = badge_rect(count, pixmap.devicePixelRatio(), size)
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
    draw_label(painter, rect, badge_label(count, size))
    painter.end()


def draw_label(painter: QtGui.QPainter, rect: QtCore.QRectF, label: str) -> None:
    font = painter.font()
    font.setBold(True)
    font.setPixelSize(round(rect.height() * 0.8))
    painter.setFont(font)
    painter.setPen(QtGui.QColor("white"))
    painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter, label)
