"""Place tray dialogs on the screen the user is looking at; Qt would use the primary screen."""

from PySide6.QtCore import QPoint
from PySide6.QtGui import QCursor, QGuiApplication
from PySide6.QtWidgets import QWidget


def centre_on_cursor_screen(widget: QWidget) -> None:
    screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
    if screen is None:
        return
    widget.adjustSize()
    area = screen.availableGeometry()
    size = widget.frameGeometry().size()
    x = area.left() + (area.width() - size.width()) // 2
    y = area.top() + (area.height() - size.height()) // 2
    x = max(area.left(), min(x, area.right() + 1 - size.width()))
    y = max(area.top(), min(y, area.bottom() + 1 - size.height()))
    widget.move(QPoint(x, y))
