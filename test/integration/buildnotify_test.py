import os
import re

import keyring
import keyring.backend
import pytest
import requests_mock
from PyQt5.QtWidgets import QWidget, QSystemTrayIcon

from buildnotifylib import BuildNotify
from test.fake_conf import ConfigBuilder
from test.fake_keyring import FakeKeyring
from test.utils import fake_content


@pytest.mark.functional
def test_should_consolidate_build_status(qtbot):
    with requests_mock.Mocker() as m:
        url = 'http://localhost:8080/cc.xml'
        m.get(url, text=fake_content())
        keyring.set_keyring(FakeKeyring())
        parent = QWidget()
        conf = ConfigBuilder().server(url).build()
        b = BuildNotify(parent, conf, 10)
        qtbot.addWidget(b.app)
        parent.show()

        qtbot.waitUntil(lambda: hasattr(b, 'app_ui'))

        def projects_loaded():
            assert len([str(a.text()) for a in b.app_ui.app_menu.menu.actions()]) == 11

        if QSystemTrayIcon.isSystemTrayAvailable():
            qtbot.waitUntil(lambda: re.compile("Last checked.*").match(b.app_ui.tray.toolTip()) is not None, timeout=5000)
            qtbot.waitUntil(projects_loaded)
