import os
import re
import shlex
import subprocess

from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.backoff import Backoff
from buildnotifylib.core.diff import Change, Event, diff, labels
from buildnotifylib.core.settings import AppSettings
from buildnotifylib.notifications import Notification


class ProjectStatusNotification:
    def __init__(
        self,
        settings: AppSettings,
        old_integration_status: OverallIntegrationStatus,
        current_integration_status: OverallIntegrationStatus,
        notification: Notification,
        backoff: Backoff | None = None,
    ):
        self.settings = settings
        self.old_integration_status = old_integration_status
        self.current_integration_status = current_integration_status
        self.notification = notification
        self.backoff = backoff or Backoff()

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
            self.run_custom_script(message, ",".join(builds))

    def run_custom_script(self, status: str, projects: str):
        command = substitute_placeholders(self.settings.custom_script, {"#status#": status, "#projects#": projects})
        env = dict(os.environ, BUILDNOTIFY_STATUS=status, BUILDNOTIFY_PROJECTS=projects)
        subprocess.Popen(command, shell=True, env=env)


PLACEHOLDER_TOKENS = re.compile(r"#status#|#projects#|.", re.DOTALL)


def substitute_placeholders(script: str, values: dict[str, str]) -> str:
    parts, quote, escaped = [], "", False
    for token in PLACEHOLDER_TOKENS.findall(script):
        replace = token in values and not escaped
        quote, escaped = next_shell_state(token, quote, escaped)
        parts.append(quote + shlex.quote(values[token]) + quote if replace else token)
    return "".join(parts)


def next_shell_state(token: str, quote: str, escaped: bool) -> tuple[str, bool]:
    if escaped or len(token) > 1:
        return quote, False
    if token == "\\" and quote != "'":
        return quote, True
    if token in ('"', "'") and quote in ("", token):
        return ("" if quote else token), False
    return quote, False
