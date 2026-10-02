from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

from buildnotifylib.core.model import Project, Status


class Change(StrEnum):
    FIXED = "Fixed builds"
    BROKEN = "Broken builds"
    STILL_FAILING = "Build is still failing"
    STILL_SUCCESSFUL = "Yet another successful build"


@dataclass(frozen=True)
class Event:
    change: Change
    project: Project


Key = tuple[str, str]

TRANSITIONS = {
    (Status.SUCCESS, Status.FAILURE): Change.BROKEN,
    (Status.FAILURE, Status.SUCCESS): Change.FIXED,
}
REPEATS = {Status.FAILURE: Change.STILL_FAILING, Status.SUCCESS: Change.STILL_SUCCESSFUL}
ARRIVALS = {Status.FAILURE: Change.BROKEN, Status.SUCCESS: Change.STILL_SUCCESSFUL}


def key(project: Project) -> Key:
    return project.server_url, project.name


def diff(old: Iterable[Project], new: Iterable[Project]) -> list[Event]:
    previous: dict[Key, Project] = {}
    for project in old:
        previous.setdefault(key(project), project)
    events = (event_for(previous.get(key(project)), project) for project in new)
    return [event for event in events if event is not None]


def event_for(old: Project | None, new: Project) -> Event | None:
    change = ARRIVALS.get(new.status) if old is None else change_between(old, new)
    return None if change is None else Event(change, new)


def change_between(old: Project, new: Project) -> Change | None:
    change = TRANSITIONS.get((old.status, new.status))
    if change is None and old.status is new.status and new.different_builds(old):
        change = REPEATS.get(new.status)
    return change


def labels(events: Iterable[Event], change: Change) -> list[str]:
    return [event.project.label() for event in events if event.change is change]
