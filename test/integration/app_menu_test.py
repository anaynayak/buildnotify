from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest
from PySide6 import QtCore
from PySide6.QtWidgets import QWidget

from buildnotifylib.adapters.credentials import Keystore
from buildnotifylib.adapters.settings_store import SettingsStore
from buildnotifylib.core.model import ServerSnapshot
from buildnotifylib.core.ports import CannotConnect, FetchError
from buildnotifylib.core.settings import AppSettings, ServerSettings, SortKey
from buildnotifylib.ui.app_menu import MAX_LABEL_CHARS, AppMenu
from buildnotifylib.ui.build_icons import BuildIcons
from buildnotifylib.ui.dialogs.preferences.dialog import PreferencesDialog
from test.fake_conf import ConfigBuilder
from test.project_builder import ProjectBuilder
from test.utils import FakeConnection, fake_content


@pytest.mark.functional
def test_should_set_menu_items_for_projects(qtbot):
    conf = ConfigBuilder().server("someurl").build()
    parent = QWidget()
    app_menu = AppMenu(parent, conf, BuildIcons(), FakeConnection(fake_content()))
    qtbot.addWidget(parent)
    project1 = (
        ProjectBuilder(
            {
                "name": "Project 1",
                "url": "dummyurl",
                "lastBuildStatus": "Success",
                "activity": "Sleeping",
                "lastBuildTime": "2016-09-17 11:31:12",
            }
        )
        .server("someurl")
        .build()
    )
    app_menu.update([project1])
    app_menu.menu.show()

    assert [str(a.text()) for a in app_menu.menu.actions()] == [
        "Passing (1)",
        "Project 1",
        "",
        "Pause notifications for 1 hour",
        "Mute",
        "About",
        "Preferences",
        "Exit",
    ]


@pytest.mark.functional
def test_should_suffix_build_time(qtbot):
    conf = ConfigBuilder(notifications={"lastBuildTimeForProject": True}).server("someurl").build()
    parent = QWidget()
    app_menu = AppMenu(parent, conf, BuildIcons(), FakeConnection(fake_content()))
    qtbot.addWidget(parent)
    one_year_ago = (datetime.now() - timedelta(days=367)).strftime("%Y-%m-%d %H:%M:%S")
    project1 = (
        ProjectBuilder(
            {
                "name": "Project 1",
                "url": "dummyurl",
                "lastBuildStatus": "Success",
                "activity": "Sleeping",
                "lastBuildTime": one_year_ago,
            }
        )
        .timezone("US/Central")
        .build()
    )

    app_menu.update([project1])
    app_menu.menu.show()

    assert [str(a.text()) for a in app_menu.menu.actions()] == [
        "Passing (1)",
        "Project 1, 1y",
        "",
        "Pause notifications for 1 hour",
        "Mute",
        "About",
        "Preferences",
        "Exit",
    ]


@pytest.mark.functional
def test_should_show_future_build_time_as_in(qtbot):
    conf = ConfigBuilder(notifications={"lastBuildTimeForProject": True}).build()
    parent = QWidget()
    app_menu = AppMenu(parent, conf, BuildIcons(), FakeConnection(fake_content()))
    qtbot.addWidget(parent)
    project1 = ProjectBuilder(
        {
            "name": "Project 1",
            "url": "dummyurl",
            "lastBuildStatus": "Success",
            "activity": "Sleeping",
            "lastBuildTime": (datetime.now() + timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%S"),
        }
    ).build()

    app_menu.update([project1])

    assert str(app_menu.menu.actions()[1].text()) == "Project 1, in 5h"


@pytest.mark.functional
def test_should_sort_by_name(qtbot):
    conf = (
        ConfigBuilder(notifications={"lastBuildTimeForProject": False}, sort_key=SortKey.NAME).server("someurl").build()
    )
    parent = QWidget()
    app_menu = AppMenu(parent, conf, BuildIcons(), FakeConnection(fake_content()))
    qtbot.addWidget(parent)
    time = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
    project1 = ProjectBuilder(
        {
            "name": "BProject",
            "url": "dummyurl",
            "lastBuildStatus": "Success",
            "activity": "Sleeping",
            "lastBuildTime": time,
        }
    ).build()

    project2 = ProjectBuilder(
        {
            "name": "AProject",
            "url": "dummyurl",
            "lastBuildStatus": "Success",
            "activity": "Sleeping",
            "lastBuildTime": time,
        }
    ).build()

    app_menu.update([project1, project2])
    app_menu.menu.show()

    assert [str(a.text()) for a in app_menu.menu.actions()] == [
        "Passing (2)",
        "AProject",
        "BProject",
        "",
        "Pause notifications for 1 hour",
        "Mute",
        "About",
        "Preferences",
        "Exit",
    ]


@pytest.mark.functional
def test_should_add_display_prefix(qtbot):
    conf = (
        ConfigBuilder(notifications={"lastBuildTimeForProject": False}, sort_key=SortKey.NAME)
        .server("Server1")
        .server("Server2")
        .build()
    )
    parent = QWidget()
    app_menu = AppMenu(parent, conf, BuildIcons(), FakeConnection(fake_content()))
    qtbot.addWidget(parent)
    time = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
    project1 = (
        ProjectBuilder(
            {
                "name": "BProject",
                "url": "dummyurl",
                "lastBuildStatus": "Success",
                "activity": "Sleeping",
                "lastBuildTime": time,
            }
        )
        .server("Server2")
        .prefix("R1")
        .build()
    )

    project2 = (
        ProjectBuilder(
            {
                "name": "AProject",
                "url": "dummyurl",
                "lastBuildStatus": "Success",
                "activity": "Sleeping",
                "lastBuildTime": time,
            }
        )
        .server("Server1")
        .build()
    )

    app_menu.update([project1, project2])
    app_menu.menu.show()

    assert [str(a.text()) for a in app_menu.menu.actions()] == [
        "Passing (2)",
        "AProject",
        "[R1] BProject",
        "",
        "Pause notifications for 1 hour",
        "Mute",
        "About",
        "Preferences",
        "Exit",
    ]


@pytest.mark.functional
def test_should_consider_prefix_for_sorting(qtbot):
    conf = (
        ConfigBuilder(notifications={"lastBuildTimeForProject": False}, sort_key=SortKey.NAME)
        .server("Server1")
        .server("Server2", prefix="R1")
        .build()
    )
    parent = QWidget()
    app_menu = AppMenu(parent, conf, BuildIcons(), FakeConnection(fake_content()))
    qtbot.addWidget(parent)
    time = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
    project1 = (
        ProjectBuilder(
            {
                "name": "BProject",
                "url": "dummyurl",
                "lastBuildStatus": "Success",
                "activity": "Sleeping",
                "lastBuildTime": time,
            }
        )
        .server("Server2")
        .prefix("R1")
        .build()
    )

    project2 = (
        ProjectBuilder(
            {
                "name": "AProject",
                "url": "dummyurl",
                "lastBuildStatus": "Success",
                "activity": "Sleeping",
                "lastBuildTime": time,
            }
        )
        .server("Server1")
        .prefix("R2")
        .build()
    )

    project3 = (
        ProjectBuilder(
            {
                "name": "CProject",
                "url": "dummyurl",
                "lastBuildStatus": "Success",
                "activity": "Sleeping",
                "lastBuildTime": time,
            }
        )
        .server("Server1")
        .prefix("R2")
        .build()
    )

    app_menu.update([project1, project2, project3])
    app_menu.menu.show()

    assert [str(a.text()) for a in app_menu.menu.actions()] == [
        "Passing (3)",
        "[R1] BProject",
        "[R2] AProject",
        "[R2] CProject",
        "",
        "Pause notifications for 1 hour",
        "Mute",
        "About",
        "Preferences",
        "Exit",
    ]


@pytest.mark.functional
def test_should_show_recent_build_first(qtbot):
    conf = (
        ConfigBuilder(notifications={"lastBuildTimeForProject": False}, sort_key=SortKey.LAST_BUILD_TIME)
        .server("someurl")
        .build()
    )
    parent = QWidget()
    app_menu = AppMenu(parent, conf, BuildIcons(), FakeConnection(fake_content()))
    qtbot.addWidget(parent)
    project1 = ProjectBuilder(
        {
            "name": "BProject",
            "url": "dummyurl",
            "lastBuildStatus": "Success",
            "activity": "Sleeping",
            "lastBuildTime": ((datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")),
        }
    ).build()

    project2 = ProjectBuilder(
        {
            "name": "AProject",
            "url": "dummyurl",
            "lastBuildStatus": "Success",
            "activity": "Sleeping",
            "lastBuildTime": ((datetime.now() - timedelta(0)).strftime("%Y-%m-%d %H:%M:%S")),
        }
    ).build()

    app_menu.update([project1, project2])
    app_menu.menu.show()

    assert [str(a.text()) for a in app_menu.menu.actions()] == [
        "Passing (2)",
        "AProject",
        "BProject",
        "",
        "Pause notifications for 1 hour",
        "Mute",
        "About",
        "Preferences",
        "Exit",
    ]


@pytest.mark.functional
def test_should_show_preferences(qtbot, mocker):
    conf = ConfigBuilder().build()
    parent = QWidget()
    app_menu = AppMenu(parent, conf, BuildIcons(), FakeConnection(fake_content()))
    qtbot.addWidget(parent)

    mocker.patch.object(PreferencesDialog, "open", return_value=AppSettings(interval_seconds=30))
    with qtbot.waitSignal(app_menu.reload_data, timeout=1000):
        app_menu.preferences_clicked(None)

    assert conf.settings.interval_seconds == 30


@pytest.mark.functional
def test_should_sort_and_label_projects_with_unparseable_build_time(qtbot):
    conf = (
        ConfigBuilder(notifications={"lastBuildTimeForProject": True}, sort_key=SortKey.LAST_BUILD_TIME)
        .server("someurl")
        .build()
    )
    parent = QWidget()
    app_menu = AppMenu(parent, conf, BuildIcons(), FakeConnection(fake_content()))
    qtbot.addWidget(parent)
    broken = (
        ProjectBuilder(
            {
                "name": "Broken",
                "url": "dummyurl",
                "lastBuildStatus": "Success",
                "activity": "Sleeping",
                "lastBuildTime": "garbage",
            }
        )
        .timezone("No/Such_Zone")
        .build()
    )
    recent = ProjectBuilder(
        {
            "name": "Recent",
            "url": "dummyurl",
            "lastBuildStatus": "Success",
            "activity": "Sleeping",
            "lastBuildTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        }
    ).build()

    app_menu.update([broken, recent])

    assert [str(a.text()) for a in app_menu.menu.actions()] == [
        "Passing (2)",
        "Recent, now",
        "Broken",
        "",
        "Pause notifications for 1 hour",
        "Mute",
        "About",
        "Preferences",
        "Exit",
    ]


@pytest.mark.functional
def test_should_quit_the_application_on_exit(qtbot, mocker):
    parent = QWidget()
    app_menu = AppMenu(parent, ConfigBuilder().build(), BuildIcons(), FakeConnection(fake_content()))
    qtbot.addWidget(parent)
    quit_app = mocker.patch("buildnotifylib.ui.app_menu.QApplication.quit")
    sys_exit = mocker.patch("sys.exit")

    app_menu.exit(None)

    quit_app.assert_called_once()
    sys_exit.assert_not_called()


@pytest.mark.functional
def test_should_delete_preferences_dialog_after_use(qtbot, mocker):
    parent = QWidget()
    app_menu = AppMenu(parent, ConfigBuilder().build(), BuildIcons(), FakeConnection(fake_content()))
    qtbot.addWidget(parent)
    mocker.patch.object(PreferencesDialog, "open", return_value=None)
    delete_later = mocker.patch.object(PreferencesDialog, "deleteLater")

    app_menu.preferences_clicked(None)

    delete_later.assert_called_once()


def test_should_pass_the_injected_connection_to_preferences(qtbot, mocker):
    conf = ConfigBuilder().build()
    parent = QWidget()
    qtbot.addWidget(parent)
    connection = FakeConnection(fake_content())
    app_menu = AppMenu(parent, conf, BuildIcons(), connection)
    preferences = mocker.patch("buildnotifylib.ui.app_menu.PreferencesDialog")
    preferences.return_value.open.return_value = None

    app_menu.preferences_clicked(None)

    preferences.assert_called_once_with(conf.settings, connection, app_menu.menu, keystore_available=True)


def test_should_tell_preferences_the_keystore_is_unavailable(qtbot, mocker):
    conf = ConfigBuilder().build()
    parent = QWidget()
    qtbot.addWidget(parent)
    mocker.patch.object(conf.keystore, "is_available", return_value=False)
    app_menu = AppMenu(parent, conf, BuildIcons(), FakeConnection(fake_content()))
    preferences = mocker.patch("buildnotifylib.ui.app_menu.PreferencesDialog")
    preferences.return_value.open.return_value = None

    app_menu.preferences_clicked(None)

    assert preferences.call_args.kwargs == {"keystore_available": False}


@pytest.fixture
def error_menu(qtbot):
    parent = QWidget()
    qtbot.addWidget(parent)
    yield AppMenu(parent, ConfigBuilder().server("someurl").build(), BuildIcons(), FakeConnection(fake_content()))


@pytest.mark.functional
def test_should_show_an_enabled_row_with_a_short_error_and_its_time_for_an_unavailable_server(error_menu):
    app_menu = error_menu
    at = datetime.now().astimezone().replace(hour=9, minute=5)
    down = ServerSnapshot(
        "https://user:hunter2@ci.example.com/cc.xml?token=s3cret",
        error=FetchError("HTTP 503 Unavailable", 503),
        error_at=at,
    )
    project1 = ProjectBuilder({"name": "Project 1", "lastBuildStatus": "Success", "activity": "Sleeping"}).build()

    app_menu.update([project1], [down])

    actions = app_menu.menu.actions()
    assert [a.text() for a in actions] == [
        "ci.example.com: HTTP 503 (09:05)",
        "Passing (1)",
        "Project 1",
        "",
        "Pause notifications for 1 hour",
        "Mute",
        "About",
        "Preferences",
        "Exit",
    ]
    assert actions[0].isEnabled()


@pytest.mark.functional
def test_should_name_an_error_row_after_the_server_prefix(mute_menu):
    app_menu = mute_menu(ServerSettings(CI, prefix="jenkins"))

    app_menu.update([], [ServerSnapshot(CI, error=CannotConnect("Could not connect to ci"), error_at=NOW)])

    assert app_menu.menu.actions()[0].text().startswith("jenkins: can't connect (")


@pytest.mark.functional
def test_should_date_an_error_row_from_an_earlier_day(error_menu):
    app_menu = error_menu
    at = datetime(2026, 1, 2, 3, 4).astimezone()

    app_menu.update([], [ServerSnapshot("http://ci:8080/cc.xml", error=TimeoutError("Timed out"), error_at=at)])

    assert app_menu.menu.actions()[0].text() == "ci:8080: timed out (2026-01-02 03:04)"


@pytest.mark.functional
def test_should_keep_tracebacks_out_of_the_error_row_and_its_details(error_menu):
    app_menu = error_menu
    error = RuntimeError('boom\nTraceback (most recent call last):\n  File "x.py", line 1')

    app_menu.update([], [ServerSnapshot("http://ci/cc.xml", error=error)])

    row = app_menu.menu.actions()[0]
    assert row.text().startswith("ci: request failed (")
    assert texts(row.menu())[0] == "boom"


@pytest.mark.functional
def test_should_list_the_full_message_a_hint_and_actions_under_an_error_row(mute_menu):
    app_menu = mute_menu(ServerSettings(CI))
    error = FetchError("HTTP 401 for https://user:hunter2@ci/cc.xml?token=s3cret", 401)

    app_menu.update([], [ServerSnapshot(CI, error=error, error_at=NOW)])

    details = app_menu.menu.actions()[0].menu()
    assert texts(details) == [
        "HTTP 401 for ci",
        "Sign-in failed - check the username and token",
        "",
        "Retry now",
        "Edit server...",
    ]
    assert not any("hunter2" in text or "s3cret" in text for text in texts(details))


@pytest.mark.functional
def test_should_poll_again_on_retry_now(mute_menu, qtbot):
    app_menu = mute_menu(ServerSettings(CI))
    app_menu.update([], [ServerSnapshot(CI, error=CannotConnect("Could not connect to ci"), error_at=NOW)])

    with qtbot.waitSignal(app_menu.reload_data, timeout=1000):
        action(app_menu.menu.actions()[0].menu(), "Retry now").trigger()


@pytest.mark.functional
def test_should_edit_the_unavailable_server_and_poll_again(mute_menu, qtbot, mocker):
    app_menu = mute_menu(ServerSettings(CI, prefix="old"), ServerSettings(OTHER))
    app_menu.update([], [ServerSnapshot(CI, error=CannotConnect("Could not connect to ci"), error_at=NOW)])
    dialog = mocker.patch("buildnotifylib.ui.app_menu.ServerConfigurationDialog")
    dialog.return_value.open.return_value = ServerSettings(CI, prefix="new")

    with qtbot.waitSignal(app_menu.reload_data, timeout=1000):
        action(app_menu.menu.actions()[0].menu(), "Edit server...").trigger()

    edited = dialog.call_args.args[0]
    assert (edited.url, edited.prefix) == (CI, "old")
    assert [(s.url, s.prefix) for s in reopened(app_menu).servers] == [(CI, "new"), (OTHER, "")]


@pytest.mark.functional
def test_should_not_let_an_edit_duplicate_another_server(mute_menu, qtbot, mocker):
    app_menu = mute_menu(ServerSettings(CI), ServerSettings(OTHER))
    app_menu.update([], [ServerSnapshot(CI, error=CannotConnect("Could not connect to ci"), error_at=NOW)])
    dialog = mocker.patch("buildnotifylib.ui.app_menu.ServerConfigurationDialog")
    dialog.return_value.open.return_value = ServerSettings(OTHER)

    with qtbot.assertNotEmitted(app_menu.reload_data):
        action(app_menu.menu.actions()[0].menu(), "Edit server...").trigger()

    assert [s.url for s in reopened(app_menu).servers] == [CI, OTHER]


CI = "http://ci/cc.xml"
OTHER = "http://other/cc.xml"
NOW = datetime(2026, 10, 2, 12, 0, tzinfo=UTC)


def built(name, server_url=CI):
    attrs = {"name": name, "lastBuildStatus": "Success", "activity": "Sleeping"}
    return ProjectBuilder(attrs).server(server_url).build()


@pytest.fixture
def mute_menu(qtbot):
    parents = []

    def make(*servers, now=NOW, **fields):
        parent = QWidget()
        parents.append(parent)
        qtbot.addWidget(parent)
        store = ConfigBuilder(servers=list(servers), **fields).build()
        return AppMenu(parent, store, BuildIcons(), FakeConnection(fake_content()), clock=lambda: now)

    yield make


def texts(menu):
    return [a.text() for a in menu.actions()]


def action(menu, text):
    return next(a for a in menu.actions() if a.text() == text)


def submenu(app_menu):
    return action(app_menu.menu, "Mute").menu()


def reopened(app_menu):
    path = app_menu.store.qsettings.fileName()
    return SettingsStore(QtCore.QSettings(path, QtCore.QSettings.Format.IniFormat), Keystore()).settings


@pytest.mark.functional
def test_should_mark_muted_projects_but_keep_them_in_the_menu(mute_menu):
    app_menu = mute_menu(ServerSettings(CI, muted_projects=["api"]), ServerSettings(OTHER, muted=True))

    app_menu.update([built("api"), built("web"), built("docs", OTHER)])

    assert texts(app_menu.menu)[0] == "Passing (3)"
    assert sorted(texts(app_menu.menu)[1:4]) == ["api (muted)", "docs (muted)", "web"]


@pytest.mark.functional
def test_should_list_servers_and_projects_to_mute(mute_menu):
    app_menu = mute_menu(ServerSettings(CI, muted_projects=["api"]), ServerSettings(OTHER, muted=True))

    app_menu.update([built("api"), built("web")])

    menu = submenu(app_menu)
    assert sorted(texts(menu)) == sorted(["ci/cc.xml", "other/cc.xml", "", "api", "web"])
    checked = {a.text(): a.isChecked() for a in menu.actions() if a.isCheckable()}
    assert checked == {"ci/cc.xml": False, "other/cc.xml": True, "api": True, "web": False}


@pytest.mark.functional
def test_should_show_an_empty_state_without_servers(mute_menu):
    app_menu = mute_menu()

    app_menu.update([])

    assert texts(app_menu.menu) == ["No servers yet", "Add a server...", "", "About", "Preferences", "Exit"]
    assert not action(app_menu.menu, "No servers yet").isEnabled()


@pytest.mark.functional
def test_should_add_a_server_from_the_empty_menu(mute_menu, qtbot, mocker):
    app_menu = mute_menu()
    dialog = mocker.patch("buildnotifylib.ui.app_menu.ServerConfigurationDialog")
    dialog.return_value.open.return_value = ServerSettings(CI)

    with qtbot.waitSignal(app_menu.reload_data, timeout=1000):
        action(app_menu.menu, "Add a server...").trigger()

    dialog.assert_called_once_with(None, 10, app_menu.connection, app_menu.menu, keystore_available=True)
    assert [server.url for server in reopened(app_menu).servers] == [CI]
    assert "Pause notifications for 1 hour" in texts(app_menu.menu)
    assert "Add a server..." not in texts(app_menu.menu)


@pytest.mark.functional
def test_should_save_nothing_when_adding_a_server_is_cancelled(mute_menu, qtbot, mocker):
    app_menu = mute_menu()
    dialog = mocker.patch("buildnotifylib.ui.app_menu.ServerConfigurationDialog")
    dialog.return_value.open.return_value = None

    with qtbot.assertNotEmitted(app_menu.reload_data):
        action(app_menu.menu, "Add a server...").trigger()

    assert reopened(app_menu).servers == []


@pytest.mark.functional
def test_should_open_the_server_dialog_once_on_first_run(mute_menu, mocker):
    app_menu = mute_menu()
    dialog = mocker.patch("buildnotifylib.ui.app_menu.ServerConfigurationDialog")
    dialog.return_value.open.return_value = None

    app_menu.offer_first_server()
    app_menu.offer_first_server()

    dialog.assert_called_once()
    assert reopened(app_menu).server_prompt_shown is True


@pytest.mark.functional
def test_should_not_open_the_server_dialog_on_first_run_once_prompted(mute_menu, mocker):
    dialog = mocker.patch("buildnotifylib.ui.app_menu.ServerConfigurationDialog")

    mute_menu(server_prompt_shown=True).offer_first_server()

    dialog.assert_not_called()


@pytest.mark.functional
def test_should_not_open_the_server_dialog_on_first_run_with_servers(mute_menu, mocker):
    dialog = mocker.patch("buildnotifylib.ui.app_menu.ServerConfigurationDialog")

    mute_menu(ServerSettings(CI)).offer_first_server()

    dialog.assert_not_called()


@pytest.mark.functional
def test_should_mute_a_server_from_the_menu_and_persist_it(mute_menu):
    app_menu = mute_menu(ServerSettings(CI))
    app_menu.update([built("api")])

    action(submenu(app_menu), "ci/cc.xml").trigger()

    assert app_menu.store.settings.servers[0].muted
    assert reopened(app_menu).servers[0].muted
    assert texts(app_menu.menu)[1] == "api (muted)"
    assert action(submenu(app_menu), "ci/cc.xml").isChecked()


@pytest.mark.functional
def test_should_unmute_a_project_from_the_menu_and_persist_it(mute_menu):
    app_menu = mute_menu(ServerSettings(CI, muted_projects=["api"]))
    app_menu.update([built("api")])

    action(submenu(app_menu), "api").trigger()

    assert reopened(app_menu).servers[0].muted_projects == []
    assert texts(app_menu.menu)[1] == "api"


@pytest.mark.functional
def test_should_pause_for_an_hour_and_persist_the_expiry(mute_menu):
    app_menu = mute_menu(ServerSettings(CI))
    app_menu.update([built("api")])

    action(app_menu.menu, "Pause notifications for 1 hour").trigger()

    assert reopened(app_menu).paused_until == NOW + timedelta(hours=1)
    until = (NOW + timedelta(hours=1)).astimezone().strftime("%H:%M")
    assert f"Resume notifications (paused until {until})" in texts(app_menu.menu)


@pytest.mark.functional
def test_should_resume_from_the_menu(mute_menu):
    paused_until = NOW + timedelta(minutes=30)
    app_menu = mute_menu(ServerSettings(CI), paused_until=paused_until)
    app_menu.update([])
    resume = f"Resume notifications (paused until {paused_until.astimezone().strftime('%H:%M')})"

    action(app_menu.menu, resume).trigger()

    assert reopened(app_menu).paused_until is None
    assert "Pause notifications for 1 hour" in texts(app_menu.menu)


@pytest.mark.functional
def test_should_offer_to_pause_again_once_the_pause_expired(mute_menu):
    app_menu = mute_menu(ServerSettings(CI), paused_until=NOW - timedelta(seconds=1))

    app_menu.update([])

    assert "Pause notifications for 1 hour" in texts(app_menu.menu)


@pytest.mark.functional
def test_should_keep_a_pause_set_while_preferences_is_open(mute_menu, mocker):
    app_menu = mute_menu(ServerSettings(CI))
    app_menu.update([])
    snapshot = app_menu.store.settings

    def pause_from_the_tray():
        action(app_menu.menu, "Pause notifications for 1 hour").trigger()
        return replace(snapshot, interval_seconds=30)

    mocker.patch.object(PreferencesDialog, "open", side_effect=pause_from_the_tray)

    app_menu.preferences_clicked(None)

    assert reopened(app_menu).paused_until == NOW + timedelta(hours=1)
    assert reopened(app_menu).interval_seconds == 30


@pytest.mark.functional
def test_should_keep_mutes_toggled_while_preferences_is_open(mute_menu, mocker):
    app_menu = mute_menu(ServerSettings(CI, muted_projects=["api"]), ServerSettings(OTHER))
    app_menu.update([built("api"), built("web")])
    snapshot = app_menu.store.settings

    def mute_from_the_tray():
        action(submenu(app_menu), "other/cc.xml").trigger()
        action(submenu(app_menu), "api").trigger()
        action(submenu(app_menu), "web").trigger()
        return replace(snapshot, interval_seconds=30)

    mocker.patch.object(PreferencesDialog, "open", side_effect=mute_from_the_tray)

    app_menu.preferences_clicked(None)

    servers = reopened(app_menu).servers
    assert [(s.muted, s.muted_projects) for s in servers] == [(False, ["web"]), (True, [])]
    assert reopened(app_menu).interval_seconds == 30


def project_with(name, status, activity="Sleeping"):
    attrs = {"name": name, "lastBuildStatus": status, "activity": activity, "url": f"http://ci/{name}"}
    return ProjectBuilder(attrs).server(CI).build()


@pytest.mark.functional
def test_should_group_projects_under_status_headers_with_counts(mute_menu):
    app_menu = mute_menu(ServerSettings(CI), sort_key=SortKey.NAME)
    projects = [
        project_with("web", "Success"),
        project_with("api", "Failure", "Building"),
        project_with("new", "Unknown"),
        project_with("deploy", "Success", "Building"),
        project_with("docs", "Success"),
        project_with("e2e", "Failure"),
    ]

    app_menu.update(projects)

    assert texts(app_menu.menu)[:11] == [
        "Failing (2)",
        "api",
        "e2e",
        "Building (1)",
        "deploy",
        "Passing (2)",
        "docs",
        "web",
        "Unknown (1)",
        "new",
        "",
    ]
    headers = [a for a in app_menu.menu.actions() if a.isSeparator() and a.text()]
    assert [a.text() for a in headers] == ["Failing (2)", "Building (1)", "Passing (2)", "Unknown (1)"]


@pytest.mark.functional
def test_should_omit_empty_sections(mute_menu):
    app_menu = mute_menu(ServerSettings(CI))

    app_menu.update([project_with("api", "Success")])

    assert texts(app_menu.menu)[:3] == ["Passing (1)", "api", ""]


def many(count, status, activity="Sleeping"):
    return [project_with(f"{status.lower()}-{n:02}", status, activity) for n in range(count)]


@pytest.mark.functional
def test_should_keep_passing_projects_top_level_at_the_threshold(mute_menu):
    app_menu = mute_menu(ServerSettings(CI), sort_key=SortKey.NAME)

    app_menu.update(many(2, "Failure") + many(13, "Success"))

    assert "success-12" in texts(app_menu.menu)
    assert not any(a.menu() for a in app_menu.menu.actions() if a.text().startswith("Passing"))


@pytest.mark.functional
def test_should_collapse_passing_projects_into_a_submenu_above_the_threshold(mute_menu):
    app_menu = mute_menu(ServerSettings(CI), sort_key=SortKey.NAME)

    app_menu.update(many(2, "Failure") + many(1, "Success", "Building") + many(13, "Success"))

    assert texts(app_menu.menu)[:8] == [
        "Failing (2)",
        "failure-00",
        "failure-01",
        "Building (1)",
        "success-00",
        "Passing (13)",
        "Passing (13)",
        "",
    ]
    passing = app_menu.menu.actions()[6].menu()
    assert texts(passing) == [f"success-{n:02}" for n in range(13)]


@pytest.mark.functional
def test_should_open_a_project_from_the_passing_submenu(mute_menu, mocker):
    app_menu = mute_menu(ServerSettings(CI))
    browser = mocker.patch("buildnotifylib.ui.app_menu.webbrowser.open")
    app_menu.update(many(16, "Success"))

    action(app_menu.menu.actions()[1].menu(), "success-03").trigger()

    browser.assert_called_once_with("http://ci/success-03")


LONG = "platform-team >> " + "very-long-folder-name >> " * 6 + "nightly-e2e"


@pytest.mark.functional
def test_should_elide_a_long_label_in_the_middle_and_keep_the_build_time(mute_menu):
    app_menu = mute_menu(ServerSettings(CI, muted_projects=[LONG]), notifications={"lastBuildTimeForProject": True})
    built_at = (datetime.now() - timedelta(minutes=18)).strftime("%Y-%m-%dT%H:%M:%S")
    attrs = {"name": LONG, "lastBuildStatus": "Success", "activity": "Sleeping", "lastBuildTime": built_at}

    app_menu.update([ProjectBuilder(attrs).server(CI).build()])

    row = app_menu.menu.actions()[1]
    assert row.text().startswith("platform-team >> ")
    assert row.text().endswith("nightly-e2e, 18m (muted)")
    assert "\N{HORIZONTAL ELLIPSIS}" in row.text() and len(row.text()) < len(LONG)
    metrics = app_menu.menu.fontMetrics()
    label = row.text().removesuffix(", 18m (muted)")
    assert metrics.horizontalAdvance(label) <= metrics.averageCharWidth() * MAX_LABEL_CHARS
    assert row.toolTip() == LONG
    assert app_menu.menu.toolTipsVisible()


@pytest.mark.functional
def test_should_leave_a_short_label_whole(mute_menu):
    app_menu = mute_menu(ServerSettings(CI))

    app_menu.update([built("api")])

    assert app_menu.menu.actions()[1].text() == "api"
