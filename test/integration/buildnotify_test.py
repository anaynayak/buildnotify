import os
import re

import pytest
import requests_mock
from PyQt5.QtWidgets import QWidget

from buildnotifylib import BuildNotify
from test.fake_conf import ConfigBuilder
from test.utils import fake_content


@pytest.mark.functional
def test_should_consolidate_build_status(qtbot, mocker):
    mocker.patch('buildnotifylib.buildnotify.QSystemTrayIcon.isSystemTrayAvailable', return_value=True)
    with requests_mock.Mocker() as m:
        url = 'http://localhost:8080/cc.xml'
        m.get(url, text=fake_content())
        parent = QWidget()
        conf = ConfigBuilder().server(url).build()
        b = BuildNotify(parent, conf, 10)
        qtbot.addWidget(b.app)
        parent.show()

        qtbot.waitUntil(lambda: hasattr(b, 'app_ui'))

        def projects_loaded():
            assert len([str(a.text()) for a in b.app_ui.app_menu.menu.actions()]) == 11

        qtbot.waitUntil(lambda: re.compile("Last checked.*").match(b.app_ui.tray.toolTip()) is not None, timeout=5000)
        qtbot.waitUntil(projects_loaded)


def no_tray_app(mocker):
    mocker.patch('buildnotifylib.buildnotify.QSystemTrayIcon.isSystemTrayAvailable', return_value=False)
    critical = mocker.patch('buildnotifylib.buildnotify.QMessageBox.critical')
    app = mocker.MagicMock()
    b = BuildNotify(app, ConfigBuilder().build(), 60000)
    run_app = mocker.patch.object(b, 'run_app')
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


def test_should_run_app_once_when_tray_is_available(mocker):
    mocker.patch('buildnotifylib.buildnotify.QSystemTrayIcon.isSystemTrayAvailable', return_value=True)
    b = BuildNotify(mocker.MagicMock(), ConfigBuilder().build(), 60000)
    run_app = mocker.patch.object(b, 'run_app')

    for count in range(5):
        b.delayed_start(count)

    run_app.assert_called_once()
