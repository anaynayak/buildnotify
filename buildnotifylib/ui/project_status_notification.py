from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.backoff import Backoff
from buildnotifylib.core.diff import Change, Event, diff, labels
from buildnotifylib.core.ports import Hook
from buildnotifylib.core.settings import AppSettings
from buildnotifylib.ui.notifications import Notification


class ProjectStatusNotification:
    def __init__(
        self,
        settings: AppSettings,
        old_integration_status: OverallIntegrationStatus,
        current_integration_status: OverallIntegrationStatus,
        notification: Notification,
        hook: Hook,
        backoff: Backoff | None = None,
    ):
        self.settings = settings
        self.old_integration_status = old_integration_status
        self.current_integration_status = current_integration_status
        self.notification = notification
        self.backoff = backoff or Backoff()
        self.hook = hook

    def show_notifications(self):
        events = diff(self.old_integration_status.get_projects(), self.current_integration_status.get_projects())
        self.show_change(events, "fixedBuild", Change.FIXED)
        self.show_change(events, "brokenBuild", Change.BROKEN)
        self.show_change(events, "stillFailingBuild", Change.STILL_FAILING)
        self.show_notification_msg(
            self.settings.notify("connectivityIssues"), self.unavailable_server_urls(), "Connectivity issues"
        )
        self.show_change(events, "successfulBuild", Change.STILL_SUCCESSFUL)

    def show_change(self, events: list[Event], setting: str, change: Change):
        self.show_notification_msg(self.settings.notify(setting), labels(events, change), change)

    def unavailable_server_urls(self) -> list[str]:
        urls = [server.url for server in self.current_integration_status.unavailable_servers()]
        self.backoff, shown = self.backoff.advance(urls)
        return shown

    def show_notification_msg(self, show_notification: bool, builds: list[str], message: str):
        if show_notification is False or builds == []:
            return
        self.notification.show_message(message, "\n".join(builds))
        if self.settings.custom_script_enabled:
            self.hook.run(self.settings.custom_script, message, ",".join(builds))
