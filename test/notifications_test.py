from PyQt5.QtWidgets import QSystemTrayIcon

from buildnotifylib.ui.notifications import Notification


def test_should_show_message_on_tray(mocker):
    tray = mocker.Mock()

    Notification(tray).show_message("title", "text")

    tray.showMessage.assert_called_once_with("title", "text", QSystemTrayIcon.Information, 3000)
