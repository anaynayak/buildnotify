import re

import pytest
from PySide6 import QtWidgets

from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.model import ServerSnapshot
from buildnotifylib.ui.app_ui import AppUi
from buildnotifylib.ui.build_icons import BuildIcons
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

    assert re.compile(r"Last checked: \d{4}-\d\d-\d\d \d\d:\d\d:\d\d$").search(widget.tray.toolTip()) is not None


@pytest.mark.functional
def test_should_list_failing_projects_in_tooltip(qtbot):
    parent = QtWidgets.QWidget()
    qtbot.addWidget(parent)
    widget = AppUi(parent, ConfigBuilder().build(), BuildIcons(), FakeConnection(fake_content()))
    projects = tuple(
        ProjectBuilder({"name": name, "lastBuildStatus": status, "activity": "Sleeping"}).build()
        for name, status in [("api", "Failure"), ("docs", "Success"), ("web", "Failure")]
    )

    widget.update_projects(OverallIntegrationStatus([ServerSnapshot("someurl", projects)]))

    assert widget.tray.toolTip().splitlines()[0] == "2 failing: api, web"


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


def test_should_render_the_tray_icon_at_the_screen_pixel_ratio(qtbot, mocker):
    parent = QtWidgets.QWidget()
    qtbot.addWidget(parent)
    widget = AppUi(parent, ConfigBuilder().build(), BuildIcons(), FakeConnection(fake_content()))
    mocker.patch.object(widget.widget, "devicePixelRatio", return_value=2.0)
    icon = mocker.spy(widget.build_icons, "for_aggregate_status")
    project = ProjectBuilder({"name": "api", "lastBuildStatus": "Failure", "activity": "Sleeping"}).build()

    widget.update_projects(OverallIntegrationStatus([ServerSnapshot("someurl", (project,))]))

    icon.assert_called_once_with("Failure.Sleeping", 1, 2.0)
