import webbrowser
from collections.abc import Callable

from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QSystemTrayIcon

from buildnotifylib.core.toasts import Toast

TIMEOUT_MS = 3000


class Notification:
    """Shows toasts on the tray icon. A click opens the last toast's url, or pops up the tray menu without one."""

    def __init__(self, widget: QSystemTrayIcon | None, open_url: Callable[[str], object] = webbrowser.open):
        self.widget = widget
        self.open_url = open_url
        self.url: str | None = None
        if widget is not None:
            widget.messageClicked.connect(self.clicked)

    def show(self, toast: Toast):
        self.url = toast.url
        icon = QSystemTrayIcon.MessageIcon.Warning if toast.warning else QSystemTrayIcon.MessageIcon.Information
        if self.widget is not None:
            self.widget.showMessage(toast.title, toast.body, icon, TIMEOUT_MS)

    def clicked(self):
        if self.url is not None:
            self.open_url(self.url)
            return
        menu = self.widget.contextMenu() if self.widget is not None else None
        if menu is not None:
            menu.popup(QCursor.pos())
