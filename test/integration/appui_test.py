import pytest
import re
from PyQt5 import QtWidgets

from buildnotifylib.app_ui import AppUi
from buildnotifylib.build_icons import BuildIcons
from buildnotifylib.core.projects import OverallIntegrationStatus
from buildnotifylib.core.continous_integration_server import ContinuousIntegrationServer
from test.fake_conf import ConfigBuilder
from test.project_builder import ProjectBuilder


@pytest.mark.functional
def test_should_update_tooltip_on_poll(qtbot):
    conf = ConfigBuilder().build()
    parent = QtWidgets.QWidget()
    qtbot.addWidget(parent)
    widget = AppUi(parent, conf, BuildIcons())
    project1 = ProjectBuilder({
        'name': 'a',
        'lastBuildStatus': 'Success',
        'activity': 'Sleeping',
        'lastBuildTime': '2016-09-17 11:31:12'
    }).build()
    servers = [ContinuousIntegrationServer('someurl', [project1])]

    widget.update_projects(OverallIntegrationStatus(servers))

    assert re.compile(r"Last checked: \d{4}-\d\d-\d\d \d\d:\d\d:\d\d").match(str(widget.tray.toolTip())) is not None


def test_should_hide_tray_when_app_is_quitting(qtbot, qapp):
    parent = QtWidgets.QWidget()
    qtbot.addWidget(parent)
    widget = AppUi(parent, ConfigBuilder().build(), BuildIcons())
    assert widget.tray.isVisible()

    qapp.aboutToQuit.emit()

    assert not widget.tray.isVisible()
