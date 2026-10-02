from datetime import datetime

from PySide6.QtWidgets import QSystemTrayIcon

from buildnotifylib.adapters.settings_store import SettingsStore
from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.backoff import Backoff
from buildnotifylib.core.diff import Change, diff
from buildnotifylib.core.errors import server_name
from buildnotifylib.core.mute import Clock, Mutes, audible, audible_servers, system_clock
from buildnotifylib.core.ports import Hook
from buildnotifylib.core.settings import AppSettings
from buildnotifylib.core.toasts import Server, Toast, for_change, reachable, unreachable
from buildnotifylib.ui.notifications import Notification

FAILURES = (("fixedBuild", Change.FIXED), ("brokenBuild", Change.BROKEN), ("stillFailingBuild", Change.STILL_FAILING))
CONNECTIVITY = "connectivityIssues"


class AppNotification:
    """Owns the notification state across polls: the previous status, the connectivity back-off, and the
    servers whose connectivity toast is still waiting for a "reachable again"."""

    def __init__(self, store: SettingsStore, widget: QSystemTrayIcon | None, hook: Hook, clock: Clock = system_clock):
        self.store = store
        self.hook = hook
        self.clock = clock
        self.notification = Notification(widget)
        self.integration_status: OverallIntegrationStatus | None = None
        self.backoff = Backoff()
        self.reported: set[str] = set()

    def update_projects(self, new_integration_status: OverallIntegrationStatus):
        if self.integration_status is not None:
            self.show_notifications(self.store.settings, self.integration_status, new_integration_status)
        self.integration_status = new_integration_status

    def show_notifications(self, settings: AppSettings, old: OverallIntegrationStatus, new: OverallIntegrationStatus):
        mutes, now = Mutes.from_settings(settings), self.clock()
        events = audible(diff(old.get_projects(), new.get_projects()), mutes, now)
        for setting, change in FAILURES:
            self.show(settings, setting, for_change(events, change))
        self.show_connectivity(settings, new, mutes, now)
        self.show(settings, "successfulBuild", for_change(events, Change.STILL_SUCCESSFUL))

    def show_connectivity(self, settings: AppSettings, status: OverallIntegrationStatus, mutes: Mutes, now: datetime):
        down = [server.url for server in status.unavailable_servers()]
        self.backoff, due = self.backoff.advance(down)
        shown = audible_servers(due, mutes, now)
        recovered = audible_servers(self.recovered(status, down), mutes, now)
        if settings.notify(CONNECTIVITY):
            self.reported.update(shown)
        self.show(settings, CONNECTIVITY, unreachable(self.named(settings, shown)))
        self.show(settings, CONNECTIVITY, reachable(self.named(settings, recovered)))

    def recovered(self, status: OverallIntegrationStatus, down: list[str]) -> list[str]:
        polled = {server.url for server in status.servers}
        recovered = [url for url in sorted(self.reported) if url in polled and url not in down]
        self.reported = {url for url in self.reported if url in down}
        return recovered

    @staticmethod
    def named(settings: AppSettings, urls: list[str]) -> list[Server]:
        prefixes = {server.url: server.prefix for server in settings.servers}
        return [(server_name(url, prefixes.get(url, "")), url) for url in urls]

    def show(self, settings: AppSettings, setting: str, toast: Toast | None):
        if toast is None or not settings.notify(setting):
            return
        self.notification.show(toast)
        if settings.custom_script_enabled:
            self.hook.run(settings.custom_script, toast.status, ",".join(toast.projects))
