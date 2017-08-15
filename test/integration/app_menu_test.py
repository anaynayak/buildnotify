import pytest
from PyQt5.QtWidgets import QWidget
from datetime import datetime
from dateutil.relativedelta import relativedelta

from buildnotifylib.app_menu import AppMenu
from buildnotifylib.preferences import PreferencesDialog
from buildnotifylib.build_icons import BuildIcons
from test.fake_conf import ConfigBuilder
from test.project_builder import ProjectBuilder


@pytest.mark.functional
def test_should_set_menu_items_for_projects(qtbot):
    conf = ConfigBuilder().server('someurl').build()
    parent = QWidget()
    app_menu = AppMenu(parent, conf, BuildIcons())
    qtbot.addWidget(parent)
    project1 = ProjectBuilder({
        'name': 'Project 1',
        'url': 'dummyurl',
        'lastBuildStatus': 'Success',
        'activity': 'Sleeping',
        'lastBuildTime': '2016-09-17 11:31:12'
    }).server('someurl').build()
    app_menu.update([project1])
    app_menu.menu.show()

    assert [str(a.text()) for a in app_menu.menu.actions()] == ['Project 1',
                                                                "",
                                                                "About",
                                                                "Preferences",
                                                                "Exit"]


@pytest.mark.functional
def test_should_suffix_build_time(qtbot):
    conf = ConfigBuilder({'values/lastBuildTimeForProject': True}).build()
    parent = QWidget()
    app_menu = AppMenu(parent, conf, BuildIcons())
    qtbot.addWidget(parent)
    oneYearAgo = (datetime.now() - relativedelta(years=1, days=1)).strftime("%Y-%m-%d %H:%M:%S")
    project1 = ProjectBuilder({
        'name': 'Project 1',
        'url': 'dummyurl',
        'lastBuildStatus': 'Success',
        'activity': 'Sleeping',
        'lastBuildTime': oneYearAgo
    }).timezone('US/Central').build()

    app_menu.update([project1])
    app_menu.menu.show()

    assert [str(a.text()) for a in app_menu.menu.actions()] == ['Project 1, 1 year ago',
                                                                "",
                                                                "About",
                                                                "Preferences",
                                                                "Exit"]


@pytest.mark.functional
def test_should_sort_by_name(qtbot):
    conf = ConfigBuilder({'values/lastBuildTimeForProject': False, 'sort_key': 'sort_name'}).build()
    parent = QWidget()
    app_menu = AppMenu(parent, conf, BuildIcons())
    qtbot.addWidget(parent)
    time = (datetime.now() - relativedelta(years=1)).strftime("%Y-%m-%d %H:%M:%S")
    project1 = ProjectBuilder({
        'name': 'BProject',
        'url': 'dummyurl',
        'lastBuildStatus': 'Success',
        'activity': 'Sleeping',
        'lastBuildTime': time
    }).build()

    project2 = ProjectBuilder({
        'name': 'AProject',
        'url': 'dummyurl',
        'lastBuildStatus': 'Success',
        'activity': 'Sleeping',
        'lastBuildTime': time
    }).build()

    app_menu.update([project1, project2])
    app_menu.menu.show()

    assert [str(a.text()) for a in app_menu.menu.actions()] == ['AProject',
                                                                'BProject',
                                                                "",
                                                                "About",
                                                                "Preferences",
                                                                "Exit"]


@pytest.mark.functional
def test_should_add_display_prefix(qtbot):
    conf = ConfigBuilder({'values/lastBuildTimeForProject': False, 'sort_key': 'sort_name'}).server("Server1").server(
        "Server2").build()
    parent = QWidget()
    app_menu = AppMenu(parent, conf, BuildIcons())
    qtbot.addWidget(parent)
    time = (datetime.now() - relativedelta(years=1)).strftime("%Y-%m-%d %H:%M:%S")
    project1 = ProjectBuilder({
        'name': 'BProject',
        'url': 'dummyurl',
        'lastBuildStatus': 'Success',
        'activity': 'Sleeping',
        'lastBuildTime': time
    }).server('Server2').prefix('R1').build()

    project2 = ProjectBuilder({
        'name': 'AProject',
        'url': 'dummyurl',
        'lastBuildStatus': 'Success',
        'activity': 'Sleeping',
        'lastBuildTime': time
    }).server('Server1').build()

    app_menu.update([project1, project2])
    app_menu.menu.show()

    assert [str(a.text()) for a in app_menu.menu.actions()] == ['AProject',
                                                                '[R1] BProject',
                                                                "",
                                                                "About",
                                                                "Preferences",
                                                                "Exit"]


@pytest.mark.functional
def test_should_consider_prefix_for_sorting(qtbot):
    conf = ConfigBuilder({'values/lastBuildTimeForProject': False, 'sort_key': 'sort_name'}).server("Server1").server(
        "Server2", {
            'display_prefix/Server2': 'R1'}).build()
    parent = QWidget()
    app_menu = AppMenu(parent, conf, BuildIcons())
    qtbot.addWidget(parent)
    time = (datetime.now() - relativedelta(years=1)).strftime("%Y-%m-%d %H:%M:%S")
    project1 = ProjectBuilder({
        'name': 'BProject', 'url': 'dummyurl', 'lastBuildStatus': 'Success',
        'activity': 'Sleeping', 'lastBuildTime': time
    }).server('Server2').prefix('R1').build()

    project2 = ProjectBuilder({
        'name': 'AProject', 'url': 'dummyurl', 'lastBuildStatus': 'Success',
        'activity': 'Sleeping', 'lastBuildTime': time
    }).server('Server1').prefix('R2').build()

    project3 = ProjectBuilder({
        'name': 'CProject', 'url': 'dummyurl', 'lastBuildStatus': 'Success',
        'activity': 'Sleeping', 'lastBuildTime': time
    }).server('Server1').prefix('R2').build()

    app_menu.update([project1, project2, project3])
    app_menu.menu.show()

    assert [str(a.text()) for a in app_menu.menu.actions()] == ['[R1] BProject',
                                                                '[R2] AProject',
                                                                '[R2] CProject',
                                                                "",
                                                                "About",
                                                                "Preferences",
                                                                "Exit"]


@pytest.mark.functional
def test_should_show_recent_build_first(qtbot):
    conf = ConfigBuilder({'values/lastBuildTimeForProject': False, 'sort_key': 'sort_build_time'}).build()
    parent = QWidget()
    app_menu = AppMenu(parent, conf, BuildIcons())
    qtbot.addWidget(parent)
    project1 = ProjectBuilder({
        'name': 'BProject',
        'url': 'dummyurl',
        'lastBuildStatus': 'Success',
        'activity': 'Sleeping',
        'lastBuildTime': ((datetime.now() - relativedelta(years=1)).strftime("%Y-%m-%d %H:%M:%S"))
    }).build()

    project2 = ProjectBuilder({
        'name': 'AProject',
        'url': 'dummyurl',
        'lastBuildStatus': 'Success',
        'activity': 'Sleeping',
        'lastBuildTime': ((datetime.now() - relativedelta(years=0)).strftime("%Y-%m-%d %H:%M:%S"))
    }).build()

    app_menu.update([project1, project2])
    app_menu.menu.show()

    assert [str(a.text()) for a in app_menu.menu.actions()] == ['AProject',
                                                                'BProject',
                                                                "",
                                                                "About",
                                                                "Preferences",
                                                                "Exit"]


@pytest.mark.functional
def test_should_show_preferences(qtbot, mocker):
    conf = ConfigBuilder().build()
    parent = QWidget()
    app_menu = AppMenu(parent, conf, BuildIcons())
    qtbot.addWidget(parent)

    mocker.patch.object(PreferencesDialog, 'open', return_value="some preferences")
    mocker.patch.object(conf, 'update_preferences')
    with qtbot.waitSignal(app_menu.reload_data, timeout=1000) as blocker:
        app_menu.preferences_clicked(None)
