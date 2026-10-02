import re

import pytest
import requests_mock
from PyQt5.QtWidgets import QWidget

from buildnotifylib.adapters.http import HttpConnection
from buildnotifylib.ui.buildnotify import BuildNotify
from buildnotifylib.ui.poller import Poller
from test.fake_conf import ConfigBuilder
from test.utils import FakeConnection, GatedConnection, fake_content


class NoHook:
    def run(self, script, status, projects):
        pass


def idle_connection():
    return FakeConnection(fake_content())


@pytest.mark.functional
def test_should_consolidate_build_status(qtbot, mocker):
    mocker.patch("buildnotifylib.ui.buildnotify.QSystemTrayIcon.isSystemTrayAvailable", return_value=True)
    with requests_mock.Mocker() as m:
        url = "http://localhost:8080/cc.xml"
        m.get(url, text=fake_content())
        parent = QWidget()
        conf = ConfigBuilder().server(url).build()
        b = BuildNotify(parent, conf, HttpConnection(), NoHook(), 10)
        qtbot.addWidget(b.app)
        parent.show()

        qtbot.waitUntil(lambda: hasattr(b, "app_ui"))

        def projects_loaded():
            assert len([str(a.text()) for a in b.app_ui.app_menu.menu.actions()]) == 11

        qtbot.waitUntil(lambda: re.compile("Last checked.*").match(b.app_ui.tray.toolTip()) is not None, timeout=5000)
        qtbot.waitUntil(projects_loaded)


def no_tray_app(mocker):
    mocker.patch("buildnotifylib.ui.buildnotify.QSystemTrayIcon.isSystemTrayAvailable", return_value=False)
    critical = mocker.patch("buildnotifylib.ui.buildnotify.QMessageBox.critical")
    app = mocker.MagicMock()
    b = BuildNotify(app, ConfigBuilder().build(), idle_connection(), NoHook(), 60000)
    run_app = mocker.patch.object(b, "run_app")
    return b, app, critical, run_app


def test_should_wait_for_tray_without_running_app(mocker):
    b, app, critical, run_app = no_tray_app(mocker)

    for count in range(4):
        b.delayed_start(count)

    run_app.assert_not_called()
    critical.assert_not_called()
    app.exit.assert_not_called()


def test_should_show_no_tray_message_and_exit_after_last_retry(mocker):
    b, app, critical, run_app = no_tray_app(mocker)

    for count in range(5):
        b.delayed_start(count)

    critical.assert_called_once()
    app.exit.assert_called_once_with(1)
    run_app.assert_not_called()


@pytest.mark.functional
def test_should_retry_the_tray_on_a_timer_then_show_the_no_tray_message(qtbot, mocker):
    mocker.patch("buildnotifylib.ui.buildnotify.QSystemTrayIcon.isSystemTrayAvailable", return_value=False)
    critical = mocker.patch("buildnotifylib.ui.buildnotify.QMessageBox.critical")
    app = mocker.MagicMock()

    b = BuildNotify(app, ConfigBuilder().build(), idle_connection(), NoHook(), 10)

    qtbot.waitUntil(lambda: app.exit.called, timeout=2000)
    critical.assert_called_once()
    app.exit.assert_called_once_with(1)
    assert not b.tray_timer.isActive()


def test_should_run_app_once_when_tray_is_available(mocker):
    mocker.patch("buildnotifylib.ui.buildnotify.QSystemTrayIcon.isSystemTrayAvailable", return_value=True)
    b = BuildNotify(mocker.MagicMock(), ConfigBuilder().build(), idle_connection(), NoHook(), 60000)
    run_app = mocker.patch.object(b, "run_app")

    for count in range(5):
        b.delayed_start(count)

    run_app.assert_called_once()


def test_should_wait_for_the_poller(mocker):
    mocker.patch("buildnotifylib.ui.buildnotify.QSystemTrayIcon.isSystemTrayAvailable", return_value=False)
    b = BuildNotify(mocker.MagicMock(), ConfigBuilder().build(), idle_connection(), NoHook(), 60000)
    b.wait_for_workers()
    b.poller = mocker.MagicMock()

    b.wait_for_workers()

    b.poller.wait.assert_called_once_with(BuildNotify.EXIT_WAIT_MS)


def test_should_give_up_waiting_for_a_stuck_fetch(qapp, mocker):
    mocker.patch("buildnotifylib.ui.buildnotify.QSystemTrayIcon.isSystemTrayAvailable", return_value=False)
    mocker.patch.object(BuildNotify, "EXIT_WAIT_MS", 50)
    b = BuildNotify(mocker.MagicMock(), ConfigBuilder().build(), idle_connection(), NoHook(), 60000)
    url = "http://localhost:8080/cc.xml"
    connection = GatedConnection(fake_content(), slow=[url])
    b.poller = Poller(ConfigBuilder().server(url).build(), connection)
    b.poller.reload()

    try:
        assert b.wait_for_workers() is False
    finally:
        connection.release.set()
        b.poller.wait(5000)


def test_should_poll_through_the_injected_connection(qapp, mocker):
    mocker.patch("buildnotifylib.ui.buildnotify.QSystemTrayIcon.isSystemTrayAvailable", return_value=False)
    app_ui = mocker.patch("buildnotifylib.ui.buildnotify.AppUi")
    app_notification = mocker.patch("buildnotifylib.ui.buildnotify.AppNotification")
    connection = FakeConnection(fake_content())
    hook = NoHook()
    b = BuildNotify(qapp, ConfigBuilder().build(), connection, hook, 60000)
    mocker.patch.object(Poller, "start")

    b.run_app()

    assert b.poller.connection is connection
    app_ui.assert_called_once_with(qapp, b.store, b.build_icons, connection)
    app_notification.assert_called_once_with(b.store, app_ui.return_value.tray, hook)
    assert b.poller.parent() is qapp
    Poller.start.assert_called_once_with()
