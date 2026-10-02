import copy
import logging
from collections import Counter
from collections.abc import Callable
from typing import Any

from PyQt5.QtCore import QObject, QRunnable, QThreadPool, QTimer, pyqtBoundSignal, pyqtSignal, pyqtSlot

from buildnotifylib.adapters.settings_store import SettingsStore
from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.model import Project, ServerSnapshot
from buildnotifylib.core.ports import Connection
from buildnotifylib.core.projects import ProjectLoader
from buildnotifylib.core.settings import ServerSettings

log = logging.getLogger(__name__)


class Fetch(QRunnable):
    """Runs a task on a pool thread and hands its result back only through a signal."""

    def __init__(self, task: Callable[[], ServerSnapshot], done: pyqtBoundSignal, *args: Any):
        super().__init__()
        self.task = task
        self.done = done
        self.args = args

    def run(self):
        self.done.emit(*self.args, self.task())


class Cycle:
    def __init__(self, generation: int, configs: list[ServerSettings]):
        self.generation = generation
        self.configs = configs
        self.results: list[ServerSnapshot | None] = [None] * len(configs)

    def complete(self) -> bool:
        return all(result is not None for result in self.results)

    def missing(self) -> list[int]:
        return [index for index, result in enumerate(self.results) if result is None]


class Poller(QObject):
    """Polls every server in parallel and reports one OverallIntegrationStatus per cycle.

    Settings are read on the GUI thread; pool threads only run ProjectLoader and emit `fetched`.
    """

    FIRST_POLL_MS = 1000
    DEADLINE_GRACE_MS = 2000

    updated = pyqtSignal(OverallIntegrationStatus)
    fetched = pyqtSignal(int, int, str, ServerSnapshot)

    def __init__(self, store: SettingsStore, connection: Connection, parent: QObject | None = None):
        super().__init__(parent)
        self.store = store
        self.connection = connection
        self.pool = QThreadPool(self)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll)
        self.deadline = QTimer(self)
        self.deadline.setSingleShot(True)
        self.deadline.timeout.connect(self.expire)
        self.fetched.connect(self.on_fetched)
        self.last_known: dict[str, tuple[Project, ...]] = {}
        self.in_flight: Counter[str] = Counter()
        self.cycle: Cycle | None = None
        self.generation = 0
        self.reload_pending = False

    def start(self, first_poll_ms: int = FIRST_POLL_MS):
        self.timer.start(first_poll_ms)

    def wait(self, msecs: int) -> bool:
        return self.pool.waitForDone(msecs)

    def poll(self):
        self.timer.setInterval(self.store.settings.interval_seconds * 1000)
        if self.cycle is not None:
            log.info("Skipping poll: the previous fetch is still running")
            return
        self.fetch()

    def reload(self):
        if self.cycle is not None:
            self.reload_pending = True
            return
        self.fetch()

    def fetch(self):
        settings = self.store.settings
        self.generation += 1
        self.cycle = Cycle(self.generation, copy.deepcopy(settings.servers))
        busy = set(self.in_flight)
        for index, config in enumerate(self.cycle.configs):
            self.start_fetch(index, config, settings.timeout_seconds, busy)
        self.deadline.start(settings.timeout_seconds * 1000 + self.DEADLINE_GRACE_MS)
        self.finish_if_complete()

    def start_fetch(self, index: int, config: ServerSettings, timeout: int, busy: set[str]):
        if config.url in busy:
            log.info("Skipping %s: its previous fetch is still running", config.url)
            self.record(index, ServerSnapshot(config.url, error=TimeoutError("previous fetch still running")))
            return
        self.in_flight[config.url] += 1
        self.pool.setMaxThreadCount(max(self.pool.maxThreadCount(), self.in_flight.total()))
        loader = ProjectLoader(config, timeout, self.connection)
        self.pool.start(Fetch(loader.get_data, self.fetched, self.generation, index, config.url))

    @pyqtSlot(int, int, str, ServerSnapshot)
    def on_fetched(self, generation: int, index: int, url: str, snapshot: ServerSnapshot):
        self.in_flight[url] -= 1
        if self.in_flight[url] <= 0:
            del self.in_flight[url]
        if self.cycle is None or self.cycle.generation != generation:
            log.info("Ignoring a late response from %s", url)
            return
        self.record(index, snapshot)
        self.finish_if_complete()

    def expire(self):
        if self.cycle is None:
            return
        for index in self.cycle.missing():
            url = self.cycle.configs[index].url
            log.warning("No response from %s before the poll deadline", url)
            self.record(index, ServerSnapshot(url, error=TimeoutError("no response before the poll deadline")))
        self.finish_if_complete()

    def record(self, index: int, snapshot: ServerSnapshot):
        assert self.cycle is not None
        excluded = self.cycle.configs[index].excluded_projects
        self.cycle.results[index] = self.with_last_known(snapshot, excluded)

    def finish_if_complete(self):
        if self.cycle is None or not self.cycle.complete():
            return
        results = [result for result in self.cycle.results if result is not None]
        self.cycle = None
        self.deadline.stop()
        self.updated.emit(OverallIntegrationStatus(results))
        if self.reload_pending:
            self.reload_pending = False
            self.fetch()

    def with_last_known(self, snapshot: ServerSnapshot, excluded: list[str]) -> ServerSnapshot:
        if snapshot.unavailable:
            cached = tuple(p for p in self.last_known.get(snapshot.url, ()) if p.name not in excluded)
            return ServerSnapshot(snapshot.url, cached, snapshot.error)
        self.last_known[snapshot.url] = snapshot.projects
        return snapshot
