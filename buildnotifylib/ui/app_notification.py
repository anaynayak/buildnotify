from PySide6.QtWidgets import QSystemTrayIcon

from buildnotifylib.adapters.settings_store import SettingsStore
from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.backoff import Backoff
from buildnotifylib.core.diff import Change, Event, diff, labels
from buildnotifylib.core.mute import Clock, Mutes, audible, audible_servers, system_clock
from buildnotifylib.core.ports import Hook
from buildnotifylib.core.settings import AppSettings
from buildnotifylib.ui.notifications import Notification


class AppNotification:
    """Owns the notification state across polls: the previous status and the connectivity back-off."""

    def __init__(self, store: SettingsStore, widget: QSystemTrayIcon, hook: Hook, clock: Clock = system_clock):
        self.store = store
        self.hook = hook
        self.clock = clock
        self.notification = Notification(widget)
        self.integration_status: OverallIntegrationStatus | None = None
        self.backoff = Backoff()

    def update_projects(self, new_integration_status: OverallIntegrationStatus):
        if self.integration_status is not None:
            self.show_notifications(self.store.settings, self.integration_status, new_integration_status)
        self.integration_status = new_integration_status

    def show_notifications(self, settings: AppSettings, old: OverallIntegrationStatus, new: OverallIntegrationStatus):
        mutes, now = Mutes.from_settings(settings), self.clock()
        events = audible(diff(old.get_projects(), new.get_projects()), mutes, now)
        self.show_change(settings, events, "fixedBuild", Change.FIXED)
        self.show_change(settings, events, "brokenBuild", Change.BROKEN)
        self.show_change(settings, events, "stillFailingBuild", Change.STILL_FAILING)
        urls = audible_servers(self.unavailable_server_urls(new), mutes, now)
        self.show_notification_msg(settings, settings.notify("connectivityIssues"), urls, "Connectivity issues")
        self.show_change(settings, events, "successfulBuild", Change.STILL_SUCCESSFUL)

    def show_change(self, settings: AppSettings, events: list[Event], setting: str, change: Change):
        self.show_notification_msg(settings, settings.notify(setting), labels(events, change), change)

    def unavailable_server_urls(self, status: OverallIntegrationStatus) -> list[str]:
        self.backoff, shown = self.backoff.advance([server.url for server in status.unavailable_servers()])
        return shown

    def show_notification_msg(self, settings: AppSettings, show_notification: bool, builds: list[str], message: str):
        if show_notification is False or builds == []:
            return
        self.notification.show_message(message, "\n".join(builds))
        if settings.custom_script_enabled:
            self.hook.run(settings.custom_script, message, ",".join(builds))
