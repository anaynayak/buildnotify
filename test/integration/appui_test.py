import re
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest
from PySide6 import QtWidgets

from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.model import ServerSnapshot
from buildnotifylib.ui.app_ui import AppUi
from buildnotifylib.ui.build_icons import SMALL_TRAY_SIZE, TRAY_SIZE, BuildIcons
from test.fake_conf import ConfigBuilder
from test.project_builder import ProjectBuilder
from test.utils import FakeConnection, fake_content


@pytest.mark.functional
def test_should_update_tooltip_on_poll(qtbot):
    conf = ConfigBuilder().server("someurl").build()
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
    widget = AppUi(parent, ConfigBuilder().server("someurl").build(), BuildIcons(), FakeConnection(fake_content()))
    projects = tuple(
        ProjectBuilder({"name": name, "lastBuildStatus": status, "activity": "Sleeping"}).build()
        for name, status in [("api", "Failure"), ("docs", "Success"), ("web", "Failure")]
    )

    widget.update_projects(OverallIntegrationStatus([ServerSnapshot("someurl", projects)]))

    assert widget.tray.toolTip().splitlines()[0] == "2 failing: api, web"


@pytest.mark.functional
def test_should_list_unavailable_servers_in_the_menu(qtbot):
    parent = QtWidgets.QWidget()
    qtbot.addWidget(parent)
    widget = AppUi(parent, ConfigBuilder().build(), BuildIcons(), FakeConnection(fake_content()))
    down = ServerSnapshot("http://ci/cc.xml", error=TimeoutError("Timed out"))

    widget.update_projects(OverallIntegrationStatus([down, ServerSnapshot("http://up/cc.xml")]))

    assert widget.app_menu.menu.actions()[0].text().startswith("ci: timed out (")


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


def test_should_build_the_tray_icon_with_the_same_arguments_whatever_the_screen_ratio(qtbot, mocker, monkeypatch):
    monkeypatch.setattr("buildnotifylib.ui.app_ui.sys.platform", "linux")
    parent = QtWidgets.QWidget()
    qtbot.addWidget(parent)
    widget = AppUi(parent, ConfigBuilder().build(), BuildIcons(), FakeConnection(fake_content()))
    mocker.patch.object(widget.widget, "devicePixelRatio", return_value=2.0)
    icon = mocker.spy(widget.build_icons, "for_aggregate_status")
    project = ProjectBuilder({"name": "api", "lastBuildStatus": "Failure", "activity": "Sleeping"}).build()

    widget.update_projects(OverallIntegrationStatus([ServerSnapshot("someurl", (project,))]))

    icon.assert_called_once_with("Failure.Sleeping", 1, symbolic=False, size=TRAY_SIZE)


@pytest.mark.parametrize("symbolic", [False, True])
def test_should_pick_tray_icons_from_the_symbolic_icons_setting(qtbot, mocker, symbolic):
    parent = QtWidgets.QWidget()
    qtbot.addWidget(parent)
    widget = AppUi(parent, ConfigBuilder(symbolic_icons=symbolic).build(), BuildIcons(), FakeConnection(fake_content()))
    icon = mocker.spy(widget.build_icons, "for_aggregate_status")

    widget.update_projects(OverallIntegrationStatus([]))

    assert icon.call_args.kwargs["symbolic"] is symbolic


@pytest.mark.functional
def test_should_say_no_servers_are_configured_in_the_tooltip(qtbot):
    parent = QtWidgets.QWidget()
    qtbot.addWidget(parent)
    widget = AppUi(parent, ConfigBuilder().build(), BuildIcons(), FakeConnection(fake_content()))
    assert widget.tray.toolTip() == "No servers configured"

    widget.update_projects(OverallIntegrationStatus([]))

    assert widget.tray.toolTip() == "No servers configured"


def down(url):
    return ServerSnapshot(url, error=TimeoutError("Timed out"))


@pytest.mark.functional
def test_should_say_no_server_can_be_reached_when_all_are_down_with_nothing_cached(qtbot):
    parent = QtWidgets.QWidget()
    qtbot.addWidget(parent)
    store = ConfigBuilder().server("a").server("b").build()
    widget = AppUi(parent, store, BuildIcons(), FakeConnection(fake_content()))

    widget.update_projects(OverallIntegrationStatus([down("http://a"), down("http://b")]))

    assert widget.tray.toolTip().splitlines()[0] == "Can't reach any server"


@pytest.mark.functional
def test_should_summarise_cached_projects_when_all_servers_are_down(qtbot):
    parent = QtWidgets.QWidget()
    qtbot.addWidget(parent)
    widget = AppUi(parent, ConfigBuilder().server("a").build(), BuildIcons(), FakeConnection(fake_content()))
    cached = ProjectBuilder({"name": "api", "lastBuildStatus": "Success", "activity": "Sleeping"}).build()
    snapshot = ServerSnapshot("http://a", (cached,), TimeoutError("Timed out"))

    widget.update_projects(OverallIntegrationStatus([snapshot]))

    assert widget.tray.toolTip().splitlines()[0] == "No failing builds"


def make_ui():
    conf = ConfigBuilder().server("someurl").build()
    return AppUi(QtWidgets.QWidget(), conf, BuildIcons(), FakeConnection(fake_content()))


def snapshot(*projects, url="someurl"):
    return OverallIntegrationStatus([ServerSnapshot(url, tuple(projects))])


@pytest.mark.functional
@pytest.mark.parametrize(
    "status, activity, expected",
    [
        ("Success", "Sleeping", "Success.Sleeping"),
        ("Success", "Building", "Success.Building"),
        ("Failure", "Sleeping", "Failure.Sleeping"),
        ("Failure", "Building", "Failure.Building"),
    ],
)
def test_should_pick_the_icon_state_for_each_aggregate_status(qtbot, status, activity, expected):
    widget = make_ui()
    project = ProjectBuilder({"name": "a", "lastBuildStatus": status, "activity": activity}).build()

    assert widget.icon_state(snapshot(project)) == expected


@pytest.mark.functional
def test_should_pick_unknown_icon_state_when_there_are_no_projects(qtbot):
    widget = make_ui()

    assert widget.icon_state(snapshot()) is None


@pytest.mark.functional
def test_should_pick_unreachable_icon_state_when_every_server_is_down(qtbot):
    widget = make_ui()
    down = OverallIntegrationStatus([ServerSnapshot("someurl", error=TimeoutError("Timed out"))])

    assert widget.icon_state(down) == "unreachable"


TOOLTIP_NOW = datetime(2026, 10, 3, 10, 0, tzinfo=UTC)


def tooltip_for(qtbot, conf):
    widget = AppUi(QtWidgets.QWidget(), conf, BuildIcons(), FakeConnection(fake_content()), clock=lambda: TOOLTIP_NOW)
    project = ProjectBuilder({"name": "a", "lastBuildStatus": "Success", "activity": "Sleeping"}).build()
    widget.update_projects(snapshot(project))
    return widget.tray.toolTip()


@pytest.mark.functional
def test_should_say_when_notifications_are_paused_in_the_tooltip(qtbot):
    until = TOOLTIP_NOW + timedelta(minutes=30)
    tip = tooltip_for(qtbot, ConfigBuilder(paused_until=until).server("someurl").build())

    assert f"Notifications paused until {until.astimezone().strftime('%H:%M')}" in tip.splitlines()


@pytest.mark.functional
def test_should_not_mention_a_pause_that_has_expired(qtbot):
    until = TOOLTIP_NOW - timedelta(minutes=30)

    assert "paused" not in tooltip_for(qtbot, ConfigBuilder(paused_until=until).server("someurl").build())


@pytest.mark.functional
def test_should_show_the_server_count_in_the_tooltip(qtbot):
    conf = ConfigBuilder().server("someurl").server("other").build()

    assert "2 servers" in tooltip_for(qtbot, conf).splitlines()
    assert "1 server" in tooltip_for(qtbot, ConfigBuilder().server("someurl").build()).splitlines()


def test_should_draw_16_px_tray_icons_on_windows(qtbot, mocker, monkeypatch):
    parent = QtWidgets.QWidget()
    qtbot.addWidget(parent)
    widget = AppUi(parent, ConfigBuilder().build(), BuildIcons(), FakeConnection(fake_content()))
    icon = mocker.spy(widget.build_icons, "for_aggregate_status")
    monkeypatch.setattr("buildnotifylib.ui.app_ui.sys.platform", "win32")

    widget.update_projects(OverallIntegrationStatus([]))

    assert icon.call_args.kwargs["size"] == SMALL_TRAY_SIZE


def muted_ui(qtbot, **server_fields):
    conf = ConfigBuilder().server("http://someurl", **server_fields).build()
    parent = QtWidgets.QWidget()
    qtbot.addWidget(parent)
    widget = AppUi(parent, conf, BuildIcons(), FakeConnection(fake_content()))
    projects = [
        ProjectBuilder(
            {"name": name, "lastBuildStatus": "Failure", "activity": "Sleeping"}, url="http://someurl"
        ).build()
        for name in ("api", "web")
    ]
    status = OverallIntegrationStatus([ServerSnapshot("http://someurl", tuple(projects))])
    widget.update_projects(status)
    widget.parent_widget = parent  # the parent owns the C++ object, so it must outlive the helper
    return widget


@pytest.mark.functional
def test_should_leave_muted_projects_out_of_the_tooltip_count_and_say_how_many_are_muted(qtbot):
    widget = muted_ui(qtbot, muted_projects=["api"])

    lines = widget.tray.toolTip().splitlines()

    assert lines[0] == "1 failing: web"
    assert "1 muted" in lines


@pytest.mark.functional
def test_should_restore_the_count_at_once_when_a_server_is_unmuted(qtbot):
    widget = muted_ui(qtbot, muted=True)
    assert widget.tray.toolTip().splitlines()[0] == "No failing builds"
    assert "2 muted" in widget.tray.toolTip().splitlines()

    settings = widget.store.settings
    widget.app_menu.change(replace(settings, servers=[replace(settings.servers[0], muted=False)]))

    assert widget.tray.toolTip().splitlines()[0] == "2 failing: api, web"
    assert "muted" not in widget.tray.toolTip()
