from PyQt5.QtWidgets import QSystemTrayIcon, QWidget


class Notification(object):
    def __init__(self, widget: QWidget):
        self.widget = widget

    def show_message(self, title: str, text: str):
        self.widget.showMessage(title, text, QSystemTrayIcon.Information, 3000)
