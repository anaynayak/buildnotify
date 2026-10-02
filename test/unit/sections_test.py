from datetime import UTC, datetime

import pytest
from hypothesis import given

from buildnotifylib.core.model import Activity, Project, Status
from buildnotifylib.core.sections import Section, grouped, section_of, sort_projects
from buildnotifylib.core.settings import SortKey
from test.strategies import project_lists


def project(name: str, status: Status, activity: Activity = Activity.SLEEPING) -> Project:
    return Project("http://ci", name, status, activity, "http://ci/" + name)


@pytest.mark.parametrize(
    "status, activity, section",
    [
        (Status.FAILURE, Activity.SLEEPING, Section.FAILING),
        (Status.FAILURE, Activity.BUILDING, Section.FAILING),
        (Status.FAILURE, Activity.CHECKING_MODIFICATIONS, Section.FAILING),
        (Status.SUCCESS, Activity.BUILDING, Section.BUILDING),
        (Status.UNKNOWN, Activity.BUILDING, Section.BUILDING),
        (Status.SUCCESS, Activity.SLEEPING, Section.PASSING),
        (Status.SUCCESS, Activity.CHECKING_MODIFICATIONS, Section.PASSING),
        (Status.UNKNOWN, Activity.SLEEPING, Section.UNKNOWN),
        (Status.SUCCESS, Activity.UNKNOWN, Section.UNKNOWN),
        (Status.FAILURE, Activity.UNKNOWN, Section.UNKNOWN),
    ],
)
def test_should_put_a_project_in_the_section_for_its_status(status, activity, section):
    assert section_of(project("a", status, activity)) is section


def test_should_group_in_section_order_keeping_the_order_within_and_omitting_empty_sections():
    a, b = project("a", Status.SUCCESS), project("b", Status.UNKNOWN)
    c, d = project("c", Status.FAILURE), project("d", Status.SUCCESS)

    assert grouped([a, b, c, d]) == [(Section.FAILING, [c]), (Section.PASSING, [a, d]), (Section.UNKNOWN, [b])]


@given(project_lists())
def test_grouping_should_keep_every_project_once(projects):
    assert sorted(id(p) for _, members in grouped(projects) for p in members) == sorted(id(p) for p in projects)


def built_at(name: str, status: Status, hour: int, activity: Activity = Activity.SLEEPING) -> Project:
    at = datetime(2026, 10, 2, hour, tzinfo=UTC)
    return Project("http://ci", name, status, activity, "http://ci/" + name, at.isoformat(), at)


A, B = built_at("b-old", Status.FAILURE, 8), built_at("a-new", Status.FAILURE, 11)
C = built_at("c-building", Status.FAILURE, 9, Activity.BUILDING)
UNDATED = project("undated", Status.FAILURE)


@pytest.mark.parametrize(
    "key, order",
    [
        (SortKey.NAME, [B, A, C, UNDATED]),
        (SortKey.LAST_BUILD_TIME, [B, C, A, UNDATED]),
        (SortKey.STATUS, [C, B, A, UNDATED]),
    ],
)
def test_should_sort_by_name_by_time_or_failing_first(key, order):
    assert sort_projects([A, UNDATED, B, C], key) == order
