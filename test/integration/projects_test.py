import threading

import pytest
import requests_mock
from PyQt5.QtCore import QThread

from test.fake_conf import ConfigBuilder
from test.utils import fake_content
from buildnotifylib.core.projects import ProjectsPopulator, ProjectLoader
from buildnotifylib.project_status_notification import ProjectStatus

URL = 'http://localhost:8080/cc.xml'


@pytest.mark.functional
def test_should_fetch_projects(qtbot):
    populator = ProjectsPopulator(ConfigBuilder().build())
    with qtbot.waitSignal(populator.updated_projects, timeout=1000):
        populator.process([])


def record_fetch_threads(mocker):
    threads = []
    original = ProjectLoader.get_data

    def get_data(loader):
        threads.append(threading.get_ident())
        return original(loader)

    mocker.patch.object(ProjectLoader, 'get_data', get_data)
    return threads


@pytest.mark.functional
def test_reload_should_fetch_off_the_gui_thread(qtbot, mocker):
    threads = record_fetch_threads(mocker)
    with requests_mock.Mocker() as m:
        m.get(URL, text=fake_content())
        populator = ProjectsPopulator(ConfigBuilder().server(URL).build())
        with qtbot.waitSignal(populator.updated_projects, timeout=1000) as blocker:
            populator.reload()
        populator.wait()

    assert threads and threading.get_ident() not in threads
    assert len(blocker.args[0].get_projects()) > 0
    assert populator.findChildren(QThread) == []


@pytest.mark.functional
@pytest.mark.parametrize('trigger', ['load_from_server', 'reload'])
def test_should_read_server_configs_on_the_gui_thread(qtbot, mocker, trigger):
    conf = ConfigBuilder().server(URL).build()
    threads = []
    original = conf.get_server_configs

    def get_server_configs():
        threads.append(threading.get_ident())
        return original()

    mocker.patch.object(conf, 'get_server_configs', get_server_configs)
    with requests_mock.Mocker() as m:
        m.get(URL, text=fake_content())
        populator = ProjectsPopulator(conf)
        with qtbot.waitSignal(populator.updated_projects, timeout=1000):
            getattr(populator, trigger)()
        populator.wait()

    assert threads == [threading.get_ident()]


def cctray(status):
    return ('<Projects><Project name="proj1" activity="Sleeping" lastBuildStatus="%s" lastBuildLabel="1" '
            'lastBuildTime="2009-06-12T06:54:35" webUrl="http://local/url"/></Projects>' % status)


def poll(qtbot, populator, configs, **response):
    with requests_mock.Mocker() as m:
        m.get(URL, **response)
        with qtbot.waitSignal(populator.updated_projects, timeout=1000) as blocker:
            populator.process(configs)
    return blocker.args[0]


@pytest.mark.functional
def test_should_keep_last_known_projects_while_server_is_down(qtbot):
    conf = ConfigBuilder().server(URL).build()
    populator = ProjectsPopulator(conf)
    configs = conf.get_server_configs()

    poll(qtbot, populator, configs, text=cctray('Failure'))
    status = poll(qtbot, populator, configs, status_code=500)

    assert [s.url for s in status.unavailable_servers()] == [URL]
    assert [p.name for p in status.get_projects()] == ['proj1']
    assert status.get_build_status() == 'Failure.Sleeping'


@pytest.mark.functional
def test_should_report_broken_build_after_outage(qtbot):
    conf = ConfigBuilder().server(URL).build()
    populator = ProjectsPopulator(conf)
    configs = conf.get_server_configs()

    poll(qtbot, populator, configs, text=cctray('Success'))
    down = poll(qtbot, populator, configs, status_code=500)
    up = poll(qtbot, populator, configs, text=cctray('Failure'))

    assert ProjectStatus(down.get_projects(), up.get_projects()).failing_builds() == ['proj1']
    assert up.unavailable_servers() == []
