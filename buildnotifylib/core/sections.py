"""The tray menu's status sections: Failing, Building, Passing and Unknown, in that order."""

from enum import StrEnum

from buildnotifylib.core.aggregate import rank
from buildnotifylib.core.model import Activity, Project, Status


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
