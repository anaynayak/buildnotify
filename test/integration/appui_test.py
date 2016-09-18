import pytest
import re
from PyQt4 import QtGui

from buildnotifylib.app_ui import AppUi
from buildnotifylib.build_icons import BuildIcons
from buildnotifylib.core.projects import OverallIntegrationStatus
from buildnotifylib.core.server import ContinuousIntegrationServer
from test.fake_conf import ConfigBuilder
from test.project_builder import ProjectBuilder


@pytest.mark.functional
def test_should_update_tooltip_on_poll(qtbot):
    conf = ConfigBuilder().build()
    widget = AppUi(QtGui.QWidget(), conf, BuildIcons())
    qtbot.addWidget(widget)
    project1 = ProjectBuilder({
        'name': 'a',
        'lastBuildStatus': 'Success',
        'activity': 'Sleeping',
        'lastBuildTime': '2016-09-17 11:31:12'
    }).build()
    servers = [ContinuousIntegrationServer('someurl', [project1])]

    widget.update_projects(OverallIntegrationStatus(servers))

    assert re.compile("Last checked: \d{4}-\d\d-\d\d \d\d:\d\d:\d\d").match(str(widget.tray.toolTip())) is not None
