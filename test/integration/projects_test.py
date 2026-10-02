import threading

import pytest
import requests_mock
from PyQt5.QtCore import QThread

from buildnotifylib.adapters.http import HttpConnection
from buildnotifylib.adapters.settings_store import SettingsStore
from buildnotifylib.core.diff import Change, diff, labels
from buildnotifylib.core.projects import ProjectLoader
from buildnotifylib.core.settings import AppSettings
from buildnotifylib.projects_populator import ProjectsPopulator
from test.fake_conf import ConfigBuilder
from test.utils import FakeConnection, fake_content

URL = "http://localhost:8080/cc.xml"


@pytest.mark.functional
def test_should_fetch_projects(qtbot):
    populator = ProjectsPopulator(ConfigBuilder().build(), HttpConnection())
    with qtbot.waitSignal(populator.updated_projects, timeout=1000):
        populator.process([])


def record_fetch_threads(mocker):
    threads = []
    original = ProjectLoader.get_data

    def get_data(loader):
        threads.append(threading.get_ident())
        return original(loader)

    mocker.patch.object(ProjectLoader, "get_data", get_data)
    return threads


@pytest.mark.functional
def test_reload_should_fetch_off_the_gui_thread(qtbot, mocker):
    threads = record_fetch_threads(mocker)
    with requests_mock.Mocker() as m:
        m.get(URL, text=fake_content())
        populator = ProjectsPopulator(ConfigBuilder().server(URL).build(), HttpConnection())
        with qtbot.waitSignal(populator.updated_projects, timeout=1000) as blocker:
            populator.reload()
        populator.wait()

    assert threads and threading.get_ident() not in threads
    assert len(blocker.args[0].get_projects()) > 0
    assert populator.findChildren(QThread) == []


@pytest.mark.functional
@pytest.mark.parametrize("trigger", ["load_from_server", "reload"])
def test_should_read_server_configs_on_the_gui_thread(qtbot, mocker, trigger):
    conf = ConfigBuilder().server(URL).build()
    threads = []
    settings = conf.settings

    def read_settings():
        threads.append(threading.get_ident())
        return settings

    settings_property = mocker.PropertyMock(side_effect=read_settings)
    mocker.patch.object(SettingsStore, "settings", settings_property, create=True)
    with requests_mock.Mocker() as m:
        m.get(URL, text=fake_content())
        populator = ProjectsPopulator(conf, HttpConnection())
        with qtbot.waitSignal(populator.updated_projects, timeout=1000):
            getattr(populator, trigger)()
        populator.wait()

    assert set(threads) == {threading.get_ident()}


def cctray(status):
    return (
        f'<Projects><Project name="proj1" activity="Sleeping" lastBuildStatus="{status}" lastBuildLabel="1" '
        'lastBuildTime="2009-06-12T06:54:35" webUrl="http://local/url"/></Projects>'
    )


def poll(qtbot, populator, configs, **response):
    with requests_mock.Mocker() as m:
        m.get(URL, **response)
        with qtbot.waitSignal(populator.updated_projects, timeout=1000) as blocker:
            populator.process(configs)
    return blocker.args[0]


@pytest.mark.functional
def test_should_keep_last_known_projects_while_server_is_down(qtbot):
    conf = ConfigBuilder().server(URL).build()
    populator = ProjectsPopulator(conf, HttpConnection())
    configs = conf.settings.servers

    poll(qtbot, populator, configs, text=cctray("Failure"))
    status = poll(qtbot, populator, configs, status_code=500)

    assert [s.url for s in status.unavailable_servers()] == [URL]
    assert [p.name for p in status.get_projects()] == ["proj1"]
    assert status.get_build_status() == "Failure.Sleeping"


@pytest.mark.functional
def test_should_apply_new_excludes_to_last_known_projects(qtbot):
    conf = ConfigBuilder().server(URL).build()
    populator = ProjectsPopulator(conf, HttpConnection())

    poll(qtbot, populator, conf.settings.servers, text=cctray("Failure"))
    conf.settings.servers[0].excluded_projects = ["proj1"]
    status = poll(qtbot, populator, conf.settings.servers, status_code=500)

    assert status.get_projects() == []


@pytest.mark.functional
def test_should_report_broken_build_after_outage(qtbot):
    conf = ConfigBuilder().server(URL).build()
    populator = ProjectsPopulator(conf, HttpConnection())
    configs = conf.settings.servers

    poll(qtbot, populator, configs, text=cctray("Success"))
    down = poll(qtbot, populator, configs, status_code=500)
    up = poll(qtbot, populator, configs, text=cctray("Failure"))

    assert labels(diff(down.get_projects(), up.get_projects()), Change.BROKEN) == ["proj1"]
    assert up.unavailable_servers() == []


@pytest.mark.functional
def test_reload_during_a_fetch_should_fetch_again_with_new_config(qtbot, mocker):
    conf = ConfigBuilder().server(URL).build()
    release = threading.Event()
    original = ProjectLoader.get_data

    def get_data(loader):
        release.wait(5)
        return original(loader)

    mocker.patch.object(ProjectLoader, "get_data", get_data)
    statuses = []
    with requests_mock.Mocker() as m:
        m.get(URL, text=cctray("Success"))
        populator = ProjectsPopulator(conf, HttpConnection())
        populator.updated_projects.connect(statuses.append)
        populator.load_from_server()
        conf.save(AppSettings())
        populator.reload()
        release.set()
        qtbot.waitUntil(lambda: len(statuses) == 2, timeout=2000)
        populator.wait()

    assert statuses[1].get_projects() == []


@pytest.mark.functional
def test_should_fetch_through_the_injected_connection(qtbot):
    conf = ConfigBuilder().server(URL).build()
    connection = FakeConnection(cctray("Success"))
    populator = ProjectsPopulator(conf, connection)

    with qtbot.waitSignal(populator.updated_projects, timeout=1000) as blocker:
        populator.process(conf.settings.servers)
    populator.process(conf.settings.servers)

    assert [p.name for p in blocker.args[0].get_projects()] == ["proj1"]
    assert connection.urls == [URL, URL]
