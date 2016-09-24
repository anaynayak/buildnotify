import keyring
import keyring.backend
import os
import pytest
import re
from PyQt4 import QtGui
from PyQt4.QtGui import QWidget

from buildnotifylib import BuildNotify
from test.fake_conf import ConfigBuilder
from test.fake_keyring import FakeKeyring


@pytest.mark.functional
def test_should_consolidate_build_status(qtbot):
    keyring.set_keyring(FakeKeyring())
    parent = QWidget()
    file = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../../data/cctray.xml")
    conf = ConfigBuilder().server("file://" + file).build()
    b = BuildNotify(parent, conf, 10)
    qtbot.addWidget(b.app)
    parent.show()

    qtbot.waitUntil(lambda: hasattr(b, 'app_ui'))
    def projects_loaded():
        assert len([str(a.text()) for a in b.app_ui.app_menu.menu.actions()]) == 11
    qtbot.waitUntil(projects_loaded)
    if QtGui.QSystemTrayIcon.isSystemTrayAvailable():
      qtbot.waitUntil(lambda: re.compile("Last checked.*").match(b.app_ui.tray.toolTip()) is not None)
