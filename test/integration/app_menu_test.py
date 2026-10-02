from datetime import datetime, timedelta

import pytest
from PyQt5.QtWidgets import QWidget

from buildnotifylib.app_menu import AppMenu
from buildnotifylib.build_icons import BuildIcons
from buildnotifylib.core.settings import AppSettings, SortKey
from buildnotifylib.preferences import PreferencesDialog
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

    assert [str(a.text()) for a in app_menu.menu.actions()] == ["Project 1", "", "About", "Preferences", "Exit"]


@pytest.mark.functional
def test_should_suffix_build_time(qtbot):
    conf = ConfigBuilder(notifications={"lastBuildTimeForProject": True}).build()
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
        "Project 1, 1 year ago",
        "",
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

    assert str(app_menu.menu.actions()[0].text()) == "Project 1, in 5 hours"


@pytest.mark.functional
def test_should_sort_by_name(qtbot):
    conf = ConfigBuilder(notifications={"lastBuildTimeForProject": False}, sort_key=SortKey.NAME).build()
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
        "AProject",
        "BProject",
        "",
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
        "AProject",
        "[R1] BProject",
        "",
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
        "[R1] BProject",
        "[R2] AProject",
        "[R2] CProject",
        "",
        "About",
        "Preferences",
        "Exit",
    ]


@pytest.mark.functional
def test_should_show_recent_build_first(qtbot):
    conf = ConfigBuilder(notifications={"lastBuildTimeForProject": False}, sort_key=SortKey.LAST_BUILD_TIME).build()
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
        "AProject",
        "BProject",
        "",
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
    conf = ConfigBuilder(notifications={"lastBuildTimeForProject": True}, sort_key=SortKey.LAST_BUILD_TIME).build()
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
        "Recent, 1 minute ago",
        "Broken",
        "",
        "About",
        "Preferences",
        "Exit",
    ]


@pytest.mark.functional
def test_should_quit_the_application_on_exit(qtbot, mocker):
    parent = QWidget()
    app_menu = AppMenu(parent, ConfigBuilder().build(), BuildIcons(), FakeConnection(fake_content()))
    qtbot.addWidget(parent)
    quit_app = mocker.patch("buildnotifylib.app_menu.QApplication.quit")
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
    preferences = mocker.patch("buildnotifylib.app_menu.PreferencesDialog")
    preferences.return_value.open.return_value = None

    app_menu.preferences_clicked(None)

    preferences.assert_called_once_with(conf.settings, connection, app_menu.menu)
