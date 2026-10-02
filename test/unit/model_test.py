import dataclasses

import pytest

from buildnotifylib.core.model import Activity, Project, ServerSnapshot, Status, normalise_url


@pytest.mark.parametrize(
    "raw, status",
    [
        ("Success", Status.SUCCESS),
        ("Failure", Status.FAILURE),
        ("Exception", Status.FAILURE),
        ("Bogus", Status.UNKNOWN),
    ],
)
def test_should_parse_status(raw, status):
    assert Status.parse(raw) is status


@pytest.mark.parametrize(
    "raw, activity",
    [
        ("Building", Activity.BUILDING),
        ("CheckingModifications", Activity.CHECKING_MODIFICATIONS),
        ("", Activity.UNKNOWN),
    ],
)
def test_should_parse_activity(raw, activity):
    assert Activity.parse(raw) is activity


def test_failure_should_outrank_success_and_unknown():
    assert Status.FAILURE.priority < Status.SUCCESS.priority < Status.UNKNOWN.priority


def test_building_should_outrank_idle_activities():
    assert [a.priority for a in (Activity.BUILDING, Activity.SLEEPING, Activity.CHECKING_MODIFICATIONS)] == [0, 1, 2]


def project(**overrides):
    fields = dict(server_url="s", name="p", status=Status.SUCCESS, activity=Activity.SLEEPING, url="http://u")
    return Project(**(fields | overrides))


def test_project_should_be_frozen():
    with pytest.raises(dataclasses.FrozenInstanceError):
        project().name = "other"


def test_should_combine_status_and_activity():
    assert project(status=Status.FAILURE, activity=Activity.BUILDING).get_build_status() == "Failure.Building"


def test_should_label_with_prefix_and_build_label():
    assert project(prefix="R1", last_build_label="42").label(True) == "[R1] p (42)"
    assert project(last_build_label="42").label() == "p"


def test_should_match_on_server_and_name():
    assert project().matches(project(status=Status.FAILURE))
    assert not project().matches(project(server_url="other"))


def test_snapshot_should_be_unavailable_only_with_an_error():
    assert not ServerSnapshot("s", (project(),)).unavailable
    assert ServerSnapshot("s", error=OSError("down")).unavailable


@pytest.mark.parametrize(
    "url, expected",
    [("1.2.3.4:8080/cc.xml", "http://1.2.3.4:8080/cc.xml"), ("https://10.0.0.1/p", "https://10.0.0.1/p")],
)
def test_should_add_missing_scheme(url, expected):
    assert normalise_url(url) == expected


def build(label, build_time):
    return project(last_build_label=label, last_build_time=build_time)


def test_should_treat_same_label_and_time_as_same_build():
    assert not build("1", "2009-05-29T13:54:07").different_builds(build("1", "2009-05-29T13:54:07"))


def test_should_detect_new_label():
    assert build("2", "2009-05-29T13:54:07").different_builds(build("1", "2009-05-29T13:54:07"))


def test_should_detect_new_build_time_with_same_label():
    assert build("", "2009-05-29T14:00:00").different_builds(build("", "2009-05-29T13:54:07"))
