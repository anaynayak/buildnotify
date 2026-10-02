from PyQt5.QtWidgets import QSystemTrayIcon


class Notification:
    def __init__(self, widget: QSystemTrayIcon):
        self.widget = widget

    def show_message(self, title: str, text: str):
        self.widget.showMessage(title, text, QSystemTrayIcon.Information, 3000)
