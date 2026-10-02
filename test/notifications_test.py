from PySide6.QtWidgets import QSystemTrayIcon

from buildnotifylib.core.toasts import Toast
from buildnotifylib.ui.notifications import Notification

INFO, WARNING = QSystemTrayIcon.MessageIcon.Information, QSystemTrayIcon.MessageIcon.Warning


def test_should_show_message_on_tray(mocker):
    tray = mocker.Mock()

    Notification(tray).show(Toast("title", "text", "status", []))

    tray.showMessage.assert_called_once_with("title", "text", INFO, 3000)


def test_should_show_a_warning_icon_for_a_warning(mocker):
    tray = mocker.Mock()

    Notification(tray).show(Toast("title", "text", "status", [], warning=True))

    tray.showMessage.assert_called_once_with("title", "text", WARNING, 3000)


def test_should_open_the_url_of_the_last_toast_when_clicked(mocker):
    opened = []
    notification = Notification(mocker.Mock(), opened.append)
    notification.show(Toast("a", "a", "status", [], url="http://ci/a"))
    notification.show(Toast("b", "b", "status", [], url="http://ci/b"))

    notification.clicked()

    assert opened == ["http://ci/b"]


def test_should_pop_up_the_tray_menu_when_a_toast_without_url_is_clicked(mocker):
    tray, opened = mocker.Mock(), []
    notification = Notification(tray, opened.append)
    notification.show(Toast("2 builds failed", "a, b", "status", []))

    notification.clicked()

    assert opened == []
    tray.contextMenu.return_value.popup.assert_called_once()


def test_should_connect_the_click_signal(mocker):
    tray = mocker.Mock()

    notification = Notification(tray)

    tray.messageClicked.connect.assert_called_once_with(notification.clicked)
