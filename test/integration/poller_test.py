import logging
import threading
import time

import pytest
import requests_mock
from PyQt5 import sip
from PyQt5.QtCore import QObject, pyqtSignal

from buildnotifylib.adapters.http import HttpConnection
from buildnotifylib.adapters.settings_store import SettingsStore
from buildnotifylib.core.diff import Change, diff, labels
from buildnotifylib.core.model import ServerSnapshot
from buildnotifylib.core.projects import ProjectLoader
from buildnotifylib.core.settings import AppSettings, ServerSettings
from buildnotifylib.ui.poller import Deadline, Fetch, Poller
from test.fake_conf import ConfigBuilder
from test.utils import FakeConnection, GatedConnection, fake_content

URL = "http://localhost:8080/cc.xml"
SLOW = "http://slow:8080/cc.xml"
FAST = "http://fast:8080/cc.xml"


def cctray(status):
    return (
        f'<Projects><Project name="proj1" activity="Sleeping" lastBuildStatus="{status}" lastBuildLabel="1" '
        'lastBuildTime="2009-06-12T06:54:35" webUrl="http://local/url"/></Projects>'
    )


@pytest.fixture
def make_poller(qtbot):
    pollers = []

    def make(store, connection=None):
        poller = Poller(store, connection or HttpConnection())
        pollers.append(poller)
        return poller

    yield make
    for poller in pollers:
        poller.wait(5000)


def poll(qtbot, poller, **response):
    with requests_mock.Mocker() as m:
        m.get(URL, **response)
        with qtbot.waitSignal(poller.updated, timeout=1000) as blocker:
            poller.reload()
        poller.wait(1000)
    return blocker.args[0]


@pytest.mark.functional
def test_should_report_an_empty_status_without_servers(qtbot, make_poller):
    poller = make_poller(ConfigBuilder().build())

    with qtbot.waitSignal(poller.updated, timeout=1000) as blocker:
        poller.reload()

    assert blocker.args[0].get_projects() == []


def record_fetch_threads(mocker):
    threads = []
    original = ProjectLoader.get_data

    def get_data(loader):
        threads.append(threading.get_ident())
        return original(loader)

    mocker.patch.object(ProjectLoader, "get_data", get_data)
    return threads


@pytest.mark.functional
def test_should_fetch_off_the_gui_thread_and_report_on_it(qtbot, mocker, make_poller):
    threads = record_fetch_threads(mocker)
    poller = make_poller(ConfigBuilder().server(URL).build())
    reported = []
    poller.updated.connect(lambda status: reported.append(threading.get_ident()))

    status = poll(qtbot, poller, text=fake_content())

    assert threads and threading.get_ident() not in threads
    assert reported == [threading.get_ident()]
    assert len(status.get_projects()) > 0


@pytest.mark.functional
@pytest.mark.parametrize("trigger", ["poll", "reload"])
def test_should_read_server_configs_on_the_gui_thread(qtbot, mocker, make_poller, trigger):
    conf = ConfigBuilder().server(URL).build()
    threads = []
    settings = conf.settings

    def read_settings():
        threads.append(threading.get_ident())
        return settings

    settings_property = mocker.PropertyMock(side_effect=read_settings)
    mocker.patch.object(SettingsStore, "settings", settings_property, create=True)
    poller = make_poller(conf, FakeConnection(cctray("Success")))

    with qtbot.waitSignal(poller.updated, timeout=1000):
        getattr(poller, trigger)()
    poller.wait(1000)

    assert set(threads) == {threading.get_ident()}


@pytest.mark.functional
def test_should_keep_last_known_projects_while_server_is_down(qtbot, make_poller):
    poller = make_poller(ConfigBuilder().server(URL).build())

    poll(qtbot, poller, text=cctray("Failure"))
    status = poll(qtbot, poller, status_code=500)

    assert [s.url for s in status.unavailable_servers()] == [URL]
    assert [p.name for p in status.get_projects()] == ["proj1"]
    assert status.get_build_status() == "Failure.Sleeping"


@pytest.mark.functional
def test_should_apply_new_excludes_to_last_known_projects(qtbot, make_poller):
    conf = ConfigBuilder().server(URL).build()
    poller = make_poller(conf)

    poll(qtbot, poller, text=cctray("Failure"))
    conf.settings.servers[0].excluded_projects = ["proj1"]
    status = poll(qtbot, poller, status_code=500)

    assert status.get_projects() == []


@pytest.mark.functional
def test_should_report_broken_build_after_outage(qtbot, make_poller):
    poller = make_poller(ConfigBuilder().server(URL).build())

    poll(qtbot, poller, text=cctray("Success"))
    down = poll(qtbot, poller, status_code=500)
    up = poll(qtbot, poller, text=cctray("Failure"))

    assert labels(diff(down.get_projects(), up.get_projects()), Change.BROKEN) == ["proj1"]
    assert up.unavailable_servers() == []


@pytest.mark.functional
def test_reload_during_a_fetch_should_fetch_again_with_new_config(qtbot, make_poller):
    conf = ConfigBuilder().server(URL).build()
    connection = GatedConnection(cctray("Success"), slow=[URL])
    poller = make_poller(conf, connection)
    statuses = []
    poller.updated.connect(statuses.append)

    poller.reload()
    conf.save(AppSettings())
    poller.reload()
    connection.release.set()
    qtbot.waitUntil(lambda: len(statuses) == 2, timeout=2000)

    assert [p.name for p in statuses[0].get_projects()] == ["proj1"]
    assert statuses[1].get_projects() == []


@pytest.mark.functional
def test_should_fetch_through_the_injected_connection(qtbot, make_poller):
    connection = FakeConnection(cctray("Success"))
    poller = make_poller(ConfigBuilder().server(URL).build(), connection)

    with qtbot.waitSignal(poller.updated, timeout=1000) as blocker:
        poller.reload()

    assert [p.name for p in blocker.args[0].get_projects()] == ["proj1"]
    assert connection.urls == [URL]


@pytest.mark.functional
def test_a_slow_server_should_not_delay_the_others(qtbot, make_poller):
    conf = ConfigBuilder(timeout_seconds=30).server(SLOW).server(FAST).build()
    connection = GatedConnection(cctray("Success"), slow=[SLOW])
    poller = make_poller(conf, connection)

    try:
        poller.reload()
        qtbot.waitUntil(lambda: connection.started == {SLOW, FAST} and connection.done == [FAST], timeout=2000)
    finally:
        connection.release.set()


@pytest.mark.functional
def test_should_report_the_others_when_a_server_misses_the_deadline(qtbot, mocker, make_poller):
    mocker.patch.object(Deadline, "GRACE_MS", 0)
    conf = ConfigBuilder(timeout_seconds=2).server(SLOW).server(FAST).build()
    connection = GatedConnection(cctray("Success"), slow=[SLOW])
    poller = make_poller(conf, connection)
    started = time.monotonic()

    try:
        with qtbot.waitSignal(poller.updated, timeout=4000) as blocker:
            poller.reload()
        assert time.monotonic() - started < 4
        status = blocker.args[0]
        assert [s.url for s in status.unavailable_servers()] == [SLOW]
        assert [p.server_url for p in status.get_projects()] == [FAST]
    finally:
        connection.release.set()


@pytest.mark.functional
def test_should_log_a_poll_skipped_while_a_fetch_is_running(qtbot, caplog, make_poller):
    connection = GatedConnection(cctray("Success"), slow=[URL])
    poller = make_poller(ConfigBuilder().server(URL).build(), connection)
    statuses = []
    poller.updated.connect(statuses.append)

    try:
        with caplog.at_level(logging.INFO, logger="buildnotifylib.ui.poller"):
            poller.poll()
            poller.poll()
    finally:
        connection.release.set()
    qtbot.waitUntil(lambda: len(statuses) == 1, timeout=2000)

    assert "Skipping poll" in caplog.text
    assert connection.urls == [URL]


@pytest.mark.functional
def test_should_not_refetch_a_server_still_running_after_the_deadline(qtbot, caplog, mocker, make_poller):
    mocker.patch.object(Deadline, "GRACE_MS", 0)
    conf = ConfigBuilder(timeout_seconds=0).server(SLOW).build()
    connection = GatedConnection(cctray("Success"), slow=[SLOW])
    poller = make_poller(conf, connection)

    try:
        with qtbot.waitSignal(poller.updated, timeout=1000):
            poller.reload()
        with caplog.at_level(logging.INFO, logger="buildnotifylib.ui.poller"):
            with qtbot.waitSignal(poller.updated, timeout=1000) as blocker:
                poller.reload()
    finally:
        connection.release.set()
    assert poller.wait(5000)

    assert connection.urls == [SLOW]
    assert [s.url for s in blocker.args[0].unavailable_servers()] == [SLOW]
    assert f"Skipping {SLOW}" in caplog.text


@pytest.mark.functional
def test_should_poll_on_the_timer_and_reread_the_interval(qtbot, make_poller):
    connection = FakeConnection(cctray("Success"))
    conf = ConfigBuilder(interval_seconds=60).server(URL).build()
    poller = make_poller(conf, connection)

    with qtbot.waitSignal(poller.updated, timeout=1000):
        poller.start(first_poll_ms=10)

    assert poller.timer.interval() == 60_000
    assert poller.timer.parent() is poller


class Receiver(QObject):
    done = pyqtSignal(ServerSnapshot)


class FailingLoader(ProjectLoader):
    def get_data(self):
        raise OSError("stdout is gone")


def test_fetch_should_report_a_crashing_loader_as_an_unavailable_server(qtbot):
    receiver = Receiver()
    results = []
    receiver.done.connect(results.append)

    Fetch(FailingLoader(ServerSettings(URL), 1, FakeConnection("")), receiver, "done").run()

    assert [(s.url, str(s.error)) for s in results] == [(URL, "stdout is gone")]


def test_fetch_should_drop_the_result_when_the_receiver_is_gone(qtbot):
    receiver = Receiver()
    fetch = Fetch(ProjectLoader(ServerSettings(URL), 1, FakeConnection(cctray("Success"))), receiver, "done")
    sip.delete(receiver)

    fetch.run()


@pytest.mark.functional
def test_should_keep_a_late_response_as_the_last_known_projects(qtbot, mocker, make_poller):
    mocker.patch.object(Deadline, "GRACE_MS", 0)
    conf = ConfigBuilder(timeout_seconds=0).server(SLOW).build()
    connection = GatedConnection(cctray("Failure"), slow=[SLOW])
    poller = make_poller(conf, connection)

    with qtbot.waitSignal(poller.updated, timeout=1000) as blocker:
        poller.reload()
    connection.release.set()
    qtbot.waitUntil(lambda: SLOW not in poller.in_flight, timeout=2000)

    assert blocker.args[0].get_projects() == []
    assert [p.name for p in poller.last_known[SLOW]] == ["proj1"]


def test_deadline_should_retire_older_generations(qtbot, mocker):
    mocker.patch.object(Deadline, "GRACE_MS", 0)
    on_expire = mocker.Mock()
    owner = QObject()
    deadline = Deadline(owner, on_expire)

    first = deadline.begin(0)
    second = deadline.begin(0)
    assert (deadline.is_current(first), deadline.is_current(second)) == (False, True)

    deadline.invalidate()
    assert not deadline.is_current(second)
    qtbot.waitUntil(lambda: on_expire.call_count == 1)
