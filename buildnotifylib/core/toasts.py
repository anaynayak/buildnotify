"""The wording, severity and click target of each notification."""

from collections.abc import Sequence
from dataclasses import dataclass

from buildnotifylib.core.diff import Change, Event
from buildnotifylib.core.model import Project

TOAST_NAMES = 3
CONNECTIVITY_ISSUES = "Connectivity issues"
CONNECTIVITY_RESTORED = "Connectivity restored"
WARNINGS = (Change.BROKEN, Change.STILL_FAILING)
ONE = {
    Change.BROKEN: "Build failed: {}",
    Change.FIXED: "Build fixed: {}",
    Change.STILL_FAILING: "Still failing: {}",
    Change.STILL_SUCCESSFUL: "Build passed: {}",
}
MANY = {
    Change.BROKEN: "{} builds failed",
    Change.FIXED: "{} builds fixed",
    Change.STILL_FAILING: "{} builds still failing",
    Change.STILL_SUCCESSFUL: "{} builds passed",
}

Server = tuple[str, str]
"""A server's display name and its url."""


@dataclass(frozen=True)
class Toast:
    title: str
    body: str
    status: str
    """BUILDNOTIFY_STATUS for the custom script; the 2.x titles, so existing scripts keep working."""
    projects: list[str]
    """BUILDNOTIFY_PROJECTS for the custom script: every name, uncapped."""
    warning: bool = False
    url: str | None = None
    """Opened when the toast is clicked; None pops up the tray menu."""


def capped(names: Sequence[str]) -> str:
    listed = ", ".join(names[:TOAST_NAMES])
    return f"{listed} and {len(names) - TOAST_NAMES} more" if len(names) > TOAST_NAMES else listed


def for_change(events: Sequence[Event], change: Change) -> Toast | None:
    projects = [event.project for event in events if event.change is change]
    if not projects:
        return None
    names = [project.label() for project in projects]
    warning = change in WARNINGS
    if len(projects) == 1:
        title, body = ONE[change].format(names[0]), single_body(projects[0])
        return Toast(title, body, change, names, warning, projects[0].url)
    return Toast(MANY[change].format(len(names)), capped(names), change, names, warning)


def single_body(project: Project) -> str:
    return f"{project.name} - label {project.last_build_label}" if project.last_build_label else project.name


def unreachable(servers: Sequence[Server]) -> Toast | None:
    return server_toast(servers, "Can't reach {}", "Can't reach {} servers", CONNECTIVITY_ISSUES, warning=True)


def reachable(servers: Sequence[Server]) -> Toast | None:
    one, many = "{} is reachable again", "{} servers are reachable again"
    return server_toast(servers, one, many, CONNECTIVITY_RESTORED, warning=False)


def server_toast(servers: Sequence[Server], one: str, many: str, status: str, warning: bool) -> Toast | None:
    if not servers:
        return None
    names, urls = [name for name, _ in servers], [url for _, url in servers]
    if len(servers) == 1:
        return Toast(one.format(names[0]), urls[0], status, urls, warning)
    return Toast(many.format(len(names)), capped(names), status, urls, warning)
