import os
import re
import shlex
import subprocess
from collections.abc import Callable
from datetime import datetime
from typing import Optional

from buildnotifylib.config import Config
from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.model import Project, Status
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
        project_status = ProjectStatus(
            self.old_integration_status.get_projects(), self.current_integration_status.get_projects()
        )

        self.show_notification_msg(
            self.config.get_value("fixedBuild"), project_status.successful_builds(), "Fixed builds"
        )
        self.show_notification_msg(
            self.config.get_value("brokenBuild"), project_status.failing_builds(), "Broken builds"
        )
        self.show_notification_msg(
            self.config.get_value("stillFailingBuild"), project_status.still_failing_builds(), "Build is still failing"
        )
        self.show_notification_msg(
            self.config.get_value("connectivityIssues"), self.unavailable_server_urls(), "Connectivity issues"
        )
        self.show_notification_msg(
            self.config.get_value("successfulBuild"),
            project_status.still_successful_builds(),
            "Yet another successful build",
        )

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


class ProjectTuple:
    def __init__(self, current_project: Project, old_project: Project | None):
        self.current_project = current_project
        self.old_project = old_project

    def has_failed(self) -> bool:
        return self.status(Status.FAILURE, Status.SUCCESS)

    def has_succeeded(self) -> bool:
        return self.status(Status.SUCCESS, Status.FAILURE)

    def has_been_successful(self) -> bool:
        return (self.old_project is None) or (
            self.status(Status.SUCCESS, Status.SUCCESS) and self.current_project.different_builds(self.old_project)
        )

    def has_been_failing(self) -> bool:
        return self.status(Status.FAILURE, Status.FAILURE) and self.current_project.different_builds(self.old_project)  # type: ignore

    def status(self, new_status: Status, old_status: Status) -> bool:
        return (
            self.current_project.status is new_status
            and self.old_project is not None
            and self.old_project.status is old_status
        )


class ProjectStatus:
    def __init__(self, old_projects: list[Project], current_projects: list[Project]):
        self.old_projects = old_projects
        self.current_projects = current_projects

    def failing_builds(self) -> list[str]:
        return self.filter_all(lambda project_tuple: project_tuple.has_failed())

    def successful_builds(self) -> list[str]:
        return self.filter_all(lambda project_tuple: project_tuple.has_succeeded())

    def still_failing_builds(self) -> list[str]:
        return self.filter_all(lambda project_tuple: project_tuple.has_been_failing())

    def still_successful_builds(self) -> list[str]:
        return self.filter_all(lambda project_tuple: project_tuple.has_been_successful())

    def filter_all(self, filter_fn: Callable[[ProjectTuple], bool]):
        project_tuples = [self.tuple_for(project) for project in self.current_projects]
        return [project_tuple.current_project.label() for project_tuple in project_tuples if filter_fn(project_tuple)]

    def tuple_for(self, new_project: Project) -> ProjectTuple:
        for project in self.old_projects:
            if new_project.matches(project):
                return ProjectTuple(new_project, project)
        return ProjectTuple(new_project, None)
