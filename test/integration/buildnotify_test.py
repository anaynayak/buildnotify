import os
import re

import pytest
from PyQt4.QtGui import QWidget

from buildnotifylib import BuildNotify
from test.fake_conf import ConfigBuilder


@pytest.mark.functional
def test_should_consolidate_build_status(qtbot):
    parent = QWidget()
    file = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../../data/cctray.xml")
    conf = ConfigBuilder().server("file://" + file).build()
    b = BuildNotify(parent, conf, 10)
    qtbot.addWidget(b.app)
    parent.show()

    qtbot.waitUntil(lambda: hasattr(b, 'app_ui'))
    qtbot.waitUntil(lambda: re.compile("Last checked.*").match(b.app_ui.tray.toolTip()) is not None)
