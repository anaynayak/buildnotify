import re

import pytest
from PyQt5 import QtWidgets

from buildnotifylib.app_ui import AppUi
from buildnotifylib.build_icons import BuildIcons
from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.model import ServerSnapshot
from test.fake_conf import ConfigBuilder
from test.project_builder import ProjectBuilder
from test.utils import FakeConnection, fake_content


@pytest.mark.functional
def test_should_update_tooltip_on_poll(qtbot):
    conf = ConfigBuilder().build()
    parent = QtWidgets.QWidget()
    qtbot.addWidget(parent)
    widget = AppUi(parent, conf, BuildIcons(), FakeConnection(fake_content()))
    project1 = ProjectBuilder(
        {"name": "a", "lastBuildStatus": "Success", "activity": "Sleeping", "lastBuildTime": "2016-09-17 11:31:12"}
    ).build()
    servers = [ServerSnapshot("someurl", (project1,))]

    widget.update_projects(OverallIntegrationStatus(servers))

    assert re.compile(r"Last checked: \d{4}-\d\d-\d\d \d\d:\d\d:\d\d").match(str(widget.tray.toolTip())) is not None


def test_should_hide_tray_when_app_is_quitting(qtbot, qapp):
    parent = QtWidgets.QWidget()
    qtbot.addWidget(parent)
    widget = AppUi(parent, ConfigBuilder().build(), BuildIcons(), FakeConnection(fake_content()))
    assert widget.tray.isVisible()

    qapp.aboutToQuit.emit()

    assert not widget.tray.isVisible()


def test_should_hand_the_injected_connection_to_the_menu(qtbot):
    parent = QtWidgets.QWidget()
    qtbot.addWidget(parent)
    connection = FakeConnection(fake_content())

    widget = AppUi(parent, ConfigBuilder().build(), BuildIcons(), connection)

    assert widget.app_menu.connection is connection
