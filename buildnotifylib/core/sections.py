"""The tray menu's status sections: Failing, Building, Passing and Unknown, in that order."""

from enum import StrEnum

from buildnotifylib.core.aggregate import rank
from buildnotifylib.core.model import Activity, Project, Status
from buildnotifylib.core.settings import SortKey


class Section(StrEnum):
    FAILING = "Failing"
    BUILDING = "Building"
    PASSING = "Passing"
    UNKNOWN = "Unknown"


def section_of(project: Project) -> Section:
    status, activity = rank(project)
    if status is Status.FAILURE:
        return Section.FAILING
    if activity is Activity.BUILDING:
        return Section.BUILDING
    if status is Status.SUCCESS:
        return Section.PASSING
    return Section.UNKNOWN


def grouped(projects: list[Project]) -> list[tuple[Section, list[Project]]]:
    """The non-empty sections in order, each keeping the order its projects came in."""
    members: dict[Section, list[Project]] = {section: [] for section in Section}
    for project in projects:
        members[section_of(project)].append(project)
    return [(section, found) for section, found in members.items() if found]


def sort_projects(projects: list[Project], key: SortKey) -> list[Project]:
    """Failing first puts building projects ahead within a section; it and the time sort show the newest first."""
    if key is SortKey.NAME:
        return sorted(projects, key=lambda p: p.label())
    by_time = sorted(projects, key=build_time_key, reverse=True)
    if key is SortKey.STATUS:
        return sorted(by_time, key=lambda p: p.activity is not Activity.BUILDING)
    return by_time


def build_time_key(project: Project) -> tuple[bool, float]:
    build_time = project.build_time
    if build_time is None:
        return False, 0.0
    return True, build_time.timestamp()
