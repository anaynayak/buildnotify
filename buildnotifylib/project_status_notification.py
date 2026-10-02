import os
import re
import shlex
import subprocess
from datetime import datetime
from typing import Optional

from buildnotifylib.config import Config
from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.diff import Change, Event, diff, labels
from buildnotifylib.notifications import Notification


class ProjectStatusNotification:
    def __init__(
        self,
        config: Config,
        old_integration_status: OverallIntegrationStatus,
        current_integration_status: OverallIntegrationStatus,
        notification: Notification,
        timed_project_filter: Optional["TimedProjectFilter"] = None,
    ):
        self.config = config
        self.old_integration_status = old_integration_status
        self.current_integration_status = current_integration_status
        self.notification = notification
        self.timed_project_filter = timed_project_filter or TimedProjectFilter()

    def show_notifications(self):
        events = diff(self.old_integration_status.get_projects(), self.current_integration_status.get_projects())
        self.show_change(events, "fixedBuild", Change.FIXED)
        self.show_change(events, "brokenBuild", Change.BROKEN)
        self.show_change(events, "stillFailingBuild", Change.STILL_FAILING)
        self.show_notification_msg(
            self.config.get_value("connectivityIssues"), self.unavailable_server_urls(), "Connectivity issues"
        )
        self.show_change(events, "successfulBuild", Change.STILL_SUCCESSFUL)

    def show_change(self, events: list[Event], setting: str, change: Change):
        self.show_notification_msg(self.config.get_value(setting), labels(events, change), change)

    def unavailable_server_urls(self) -> list[str]:
        urls = [server.url for server in self.current_integration_status.unavailable_servers()]
        return self.timed_project_filter.filter(urls)

    def show_notification_msg(self, show_notification: bool, builds: list[str], message: str):
        if show_notification is False or builds == []:
            return
        self.notification.show_message(message, "\n".join(builds))
        if self.config.get_custom_script_enabled():
            self.run_custom_script(message, ",".join(builds))

    def run_custom_script(self, status: str, projects: str):
        command = substitute_placeholders(self.config.get_custom_script(), {"#status#": status, "#projects#": projects})
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


class TimedProjectFilter:
    fact = [1, 2, 3, 5, 8, 13, 21]

    def __init__(self):
        self.map: dict[str, tuple[datetime, int]] = {}

    def filter(self, urls: list[str]) -> list[str]:
        self.map = {url: state for url, state in self.map.items() if url in urls}
        return [url for url in urls if self.is_new(url)]

    def is_new(self, url: str) -> bool:
        if url not in self.map:
            self.map[url] = (datetime.now(), 1)
            return True
        connection_time, fail_count = self.map[url]
        fail_count += 1
        if self.fact[len(self.fact) - 1] <= fail_count:
            fail_count = 1
        self.map[url] = (connection_time, fail_count)
        return fail_count in self.fact
