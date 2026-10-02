import threading

import pytest
import requests_mock
from PyQt5.QtCore import QThread

from test.fake_conf import ConfigBuilder
from test.utils import fake_content
from buildnotifylib.core.projects import ProjectsPopulator, ProjectLoader

URL = 'http://localhost:8080/cc.xml'


@pytest.mark.functional
def test_should_fetch_projects(qtbot):
    conf = ConfigBuilder().build()
    populator = ProjectsPopulator(conf)
    with qtbot.waitSignal(populator.updated_projects, timeout=1000):
        populator.process()


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
