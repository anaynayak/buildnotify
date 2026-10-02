import pytest

from buildnotifylib.core.diff import Change, Event
from buildnotifylib.core.model import Activity, Project, Status
from buildnotifylib.core.toasts import Toast, for_change, reachable, unreachable


def project(name, prefix=None, label=None, url=None):
    url = url or f"http://ci/{name}"
    return Project("http://ci", name, Status.FAILURE, Activity.SLEEPING, url, "", None, label, prefix)


def events(change, *projects):
    return [Event(change, p) for p in projects]


@pytest.mark.parametrize(
    ("change", "title"),
    [
        (Change.BROKEN, "Build failed: [jenkins] nightly"),
        (Change.FIXED, "Build fixed: [jenkins] nightly"),
        (Change.STILL_FAILING, "Still failing: [jenkins] nightly"),
        (Change.STILL_SUCCESSFUL, "Build passed: [jenkins] nightly"),
    ],
)
def test_should_name_the_project_in_the_title_of_a_single_project_toast(change, title):
    toast = for_change(events(change, project("nightly", prefix="jenkins")), change)

    assert toast is not None and toast.title == title


@pytest.mark.parametrize(
    ("change", "title"),
    [
        (Change.BROKEN, "2 builds failed"),
        (Change.FIXED, "2 builds fixed"),
        (Change.STILL_FAILING, "2 builds still failing"),
        (Change.STILL_SUCCESSFUL, "2 builds passed"),
    ],
)
def test_should_count_the_projects_in_the_title_of_a_multi_project_toast(change, title):
    toast = for_change(events(change, project("a"), project("b")), change)

    assert toast is not None and toast.title == title


def test_should_show_the_name_and_build_label_in_a_single_project_body():
    toast = for_change(events(Change.BROKEN, project("nightly", label="1234")), Change.BROKEN)

    assert toast is not None and toast.body == "nightly - label 1234"


def test_should_show_only_the_name_when_there_is_no_build_label():
    toast = for_change(events(Change.BROKEN, project("nightly")), Change.BROKEN)

    assert toast is not None and toast.body == "nightly"


@pytest.mark.parametrize(
    ("count", "body"),
    [
        (2, "p0, p1"),
        (3, "p0, p1, p2"),
        (4, "p0, p1, p2 and 1 more"),
        (20, "p0, p1, p2 and 17 more"),
    ],
)
def test_should_cap_the_names_in_a_multi_project_body(count, body):
    toast = for_change(events(Change.BROKEN, *[project(f"p{i}") for i in range(count)]), Change.BROKEN)

    assert toast is not None and toast.body == body


@pytest.mark.parametrize(
    ("change", "warning"),
    [(Change.BROKEN, True), (Change.STILL_FAILING, True), (Change.FIXED, False), (Change.STILL_SUCCESSFUL, False)],
)
def test_should_warn_only_about_failures(change, warning):
    toast = for_change(events(change, project("a")), change)

    assert toast is not None and toast.warning is warning


def test_should_open_the_project_url_for_a_single_project_toast():
    toast = for_change(events(Change.BROKEN, project("a", url="http://ci/job/a")), Change.BROKEN)

    assert toast is not None and toast.url == "http://ci/job/a"


def test_should_have_no_url_for_a_multi_project_toast():
    toast = for_change(events(Change.BROKEN, project("a"), project("b")), Change.BROKEN)

    assert toast is not None and toast.url is None


def test_should_keep_the_legacy_status_and_every_name_for_the_script():
    names = [project(f"p{i}", prefix="ci") for i in range(5)]

    toast = for_change(events(Change.BROKEN, *names), Change.BROKEN)

    assert toast is not None
    assert (toast.status, toast.projects) == ("Broken builds", [f"[ci] p{i}" for i in range(5)])


def test_should_only_include_events_of_the_change():
    mixed = [Event(Change.BROKEN, project("a")), Event(Change.FIXED, project("b"))]

    toast = for_change(mixed, Change.FIXED)

    assert toast is not None and toast.title == "Build fixed: b"


def test_should_have_no_toast_without_events():
    assert for_change(events(Change.FIXED, project("a")), Change.BROKEN) is None


def test_should_name_the_server_that_cannot_be_reached():
    toast = unreachable([("ci.example.org", "http://ci.example.org/cc.xml")])

    feed = "http://ci.example.org/cc.xml"
    assert toast == Toast("Can't reach ci.example.org", feed, "Connectivity issues", [feed], warning=True)


def test_should_count_the_servers_that_cannot_be_reached():
    toast = unreachable([("a", "http://a"), ("b", "http://b"), ("c", "http://c"), ("d", "http://d")])

    assert toast is not None
    assert (toast.title, toast.body, toast.warning) == ("Can't reach 4 servers", "a, b, c and 1 more", True)


def test_should_say_the_server_is_reachable_again():
    toast = reachable([("ci.example.org", "http://ci.example.org/cc.xml")])

    assert toast == Toast(
        "ci.example.org is reachable again",
        "http://ci.example.org/cc.xml",
        "Connectivity restored",
        ["http://ci.example.org/cc.xml"],
    )


def test_should_count_the_servers_that_are_reachable_again():
    toast = reachable([("a", "http://a"), ("b", "http://b")])

    assert toast is not None
    assert (toast.title, toast.body, toast.warning) == ("2 servers are reachable again", "a, b", False)


def test_should_have_no_server_toast_without_servers():
    assert (unreachable([]), reachable([])) == (None, None)
