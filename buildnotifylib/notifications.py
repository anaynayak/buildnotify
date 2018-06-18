import notify2

from PyQt5.QtWidgets import QSystemTrayIcon


class Notification(object):
    def __init__(self, widget):
        self.widget = widget
        self.notification = None

        if notify2.init(" buildnotify "):
            self.notification = notify2.Notification("buildnotify", "buildnotify", None)

    def show_message(self, title, text):
        if self.notification:
            self.notification.update(title, text, None)
        if self.notification is None or not self.notification.show():
            self.widget.showMessage(title, text, QSystemTrayIcon.Information, 3000)
