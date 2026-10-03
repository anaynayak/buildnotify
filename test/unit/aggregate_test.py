import unittest
from datetime import UTC, datetime

from hypothesis import given
from hypothesis import strategies as st

from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.diff import Change, diff
from buildnotifylib.core.model import Activity, ServerSnapshot, Status
from buildnotifylib.core.mute import Mutes, audible
from test.project_builder import ProjectBuilder
from test.strategies import project_lists


class OverallIntegrationStatusTest(unittest.TestCase):
    def test_should_consolidate_build_status(self):
        project1 = ProjectBuilder({"name": "a", "lastBuildStatus": "Success", "activity": "Sleeping"}).build()
        project2 = ProjectBuilder({"name": "a", "lastBuildStatus": "Success", "activity": "Sleeping"}).build()
        status = OverallIntegrationStatus([ServerSnapshot("someurl", (project1, project2))])
        self.assertEqual("Success.Sleeping", status.get_build_status())

    def test_should_mark_failed_if_even_one_failed(self):
        project1 = ProjectBuilder({"name": "a", "lastBuildStatus": "Success", "activity": "Sleeping"}).build()
        project2 = ProjectBuilder({"name": "a", "lastBuildStatus": "Failure", "activity": "Sleeping"}).build()
        status = OverallIntegrationStatus([ServerSnapshot("someurl", (project1, project2))])
        self.assertEqual("Failure.Sleeping", status.get_build_status())

    def test_should_mark_failed_if_even_one_failed_across_servers(self):
        project1 = ProjectBuilder({"name": "a", "lastBuildStatus": "Success", "activity": "Sleeping"}).build()
        project2 = ProjectBuilder({"name": "a", "lastBuildStatus": "Failure", "activity": "Sleeping"}).build()
        status = OverallIntegrationStatus([ServerSnapshot("url1", (project1,)), ServerSnapshot("url2", (project2,))])
        self.assertEqual("Failure.Sleeping", status.get_build_status())

    def test_any_failure_should_outrank_any_success(self):
        for failure in ["Sleeping", "Building", "CheckingModifications"]:
            for success in ["Sleeping", "Building", "CheckingModifications"]:
                with self.subTest(failure=failure, success=success):
                    status = overall_status(("Success", success), ("Failure", failure))
                    self.assertEqual("Failure." + failure, status.get_build_status())

    def test_should_rank_building_above_idle_within_a_status(self):
        self.assertEqual(
            "Failure.Building",
            overall_status(
                ("Failure", "CheckingModifications"), ("Failure", "Building"), ("Failure", "Sleeping")
            ).get_build_status(),
        )
        self.assertEqual(
            "Success.Building",
            overall_status(
                ("Success", "CheckingModifications"), ("Success", "Building"), ("Success", "Sleeping")
            ).get_build_status(),
        )

    def test_exception_should_count_as_failure(self):
        for activity in ["Sleeping", "Building", "CheckingModifications"]:
            with self.subTest(activity=activity):
                status = overall_status(("Success", "Building"), ("Exception", activity))
                self.assertEqual("Failure." + activity, status.get_build_status())
                self.assertEqual(1, len(status.get_failing_builds()))

    def test_unknown_should_rank_below_success_and_failure(self):
        self.assertEqual(
            "Success.Sleeping", overall_status(("Unknown", "Building"), ("Success", "Sleeping")).get_build_status()
        )
        self.assertEqual(
            "Failure.Sleeping", overall_status(("Unknown", "Building"), ("Failure", "Sleeping")).get_build_status()
        )

    def test_unknown_should_have_its_own_status(self):
        self.assertEqual(
            "Unknown.Building", overall_status(("Unknown", "Sleeping"), ("Unknown", "Building")).get_build_status()
        )
        self.assertEqual("Unknown.Sleeping", overall_status(("Bogus", "Sleeping")).get_build_status())
        self.assertEqual("Unknown.Unknown", overall_status(("Success", "Pending")).get_build_status())
        self.assertEqual([], overall_status(("Unknown", "Sleeping")).get_failing_builds())

    def test_should_identify_failing_builds(self):
        project1 = ProjectBuilder({"name": "a", "lastBuildStatus": "Success", "activity": "Sleeping"}).build()
        project2 = ProjectBuilder({"name": "a", "lastBuildStatus": "Failure", "activity": "Sleeping"}).build()
        status = OverallIntegrationStatus([ServerSnapshot("someurl", (project1, project2))])
        self.assertEqual([project2], status.get_failing_builds())


def overall_status(*statuses):
    projects = [
        ProjectBuilder({"name": f"p{i}", "lastBuildStatus": status, "activity": activity}).build()
        for i, (status, activity) in enumerate(statuses)
    ]
    return OverallIntegrationStatus([ServerSnapshot("someurl", tuple(projects))])


def aggregate_status(projects):
    return OverallIntegrationStatus([ServerSnapshot("someurl", tuple(projects))]).get_build_status()


KNOWN_ACTIVITIES = [Activity.BUILDING, Activity.SLEEPING, Activity.CHECKING_MODIFICATIONS]


FAILURES = project_lists(status=st.just(Status.FAILURE), activity=st.sampled_from(KNOWN_ACTIVITIES))


@given(project_lists(), FAILURES.filter(bool))
def test_failure_should_outrank_success(others, failures):
    assert (aggregate_status(others + failures) or "").startswith("Failure.")


@given(project_lists())
def test_overall_status_should_not_depend_on_order(items):
    assert aggregate_status(items) == aggregate_status(list(reversed(items)))


def test_should_have_no_status_without_projects():
    assert aggregate_status([]) is None


def test_should_summarise_failing_builds():
    status = overall_status(("Failure", "Sleeping"), ("Success", "Sleeping"), ("Failure", "Building"))

    assert status.failing_summary() == "2 failing: p0, p2"


def test_should_summarise_a_green_board():
    assert overall_status(("Success", "Sleeping")).failing_summary() == "No failing builds"


def test_should_name_failing_builds_with_their_prefix():
    project = ProjectBuilder({"name": "api", "lastBuildStatus": "Failure", "activity": "Sleeping"}, prefix="go").build()
    status = OverallIntegrationStatus([ServerSnapshot("someurl", (project,))])

    assert status.failing_summary() == "1 failing: [go] api"


def test_should_cap_the_names_in_the_summary():
    status = overall_status(*[("Failure", "Sleeping")] * 7)

    assert status.failing_summary() == "7 failing: p0, p1, p2, p3, p4 and 2 more"


def test_should_be_unreachable_only_when_every_server_is_down_with_nothing_cached():
    project = ProjectBuilder({"name": "a", "lastBuildStatus": "Success", "activity": "Sleeping"}).build()
    down, up = ServerSnapshot("a", error=TimeoutError()), ServerSnapshot("b", (project,))
    cached = ServerSnapshot("c", (project,), TimeoutError())
    assert OverallIntegrationStatus([down, down]).unreachable()
    assert not OverallIntegrationStatus([down, up]).unreachable()
    assert not OverallIntegrationStatus([down, cached]).unreachable()
    assert not OverallIntegrationStatus([]).unreachable()


def snapshot(url, name, prefix=None):
    return ServerSnapshot(url, (ProjectBuilder({"name": name}, url=url, prefix=prefix).build(),))


def labels(*snapshots):
    return [project.label() for project in OverallIntegrationStatus(snapshots).get_projects()]


def test_should_name_the_server_only_when_a_project_name_collides_across_servers():
    found = labels(snapshot("http://ci-a.example:8080/cc.xml", "web"), snapshot("http://ci-b.example/cc.xml", "web"))

    assert found == ["[ci-a.example:8080] web", "[ci-b.example] web"]


def test_should_leave_unique_names_and_prefixed_rows_alone():
    found = labels(
        snapshot("http://a/cc.xml", "web"),
        snapshot("http://b/cc.xml", "api"),
        snapshot("http://c/cc.xml", "web", prefix="c"),
    )

    assert found == ["web", "api", "[c] web"]


def test_should_not_treat_a_repeated_name_on_one_server_as_a_collision():
    both = ServerSnapshot("http://a/cc.xml", snapshot("http://a/cc.xml", "web").projects * 2)

    assert labels(both, snapshot("http://b/cc.xml", "api")) == ["web", "web", "api"]


def failing(url, name, status):
    attrs = {"name": name, "lastBuildStatus": status, "activity": "Sleeping"}
    return ServerSnapshot(url, (ProjectBuilder(attrs, url=url).build(),))


def test_should_keep_matching_mutes_and_diffs_by_server_and_name_when_the_label_changes():
    a, b = "http://a/cc.xml", "http://b/cc.xml"
    before = OverallIntegrationStatus([failing(a, "web", "Success")])
    after = OverallIntegrationStatus([failing(a, "web", "Failure"), failing(b, "web", "Success")])
    mutes = Mutes(projects=frozenset({(a, "web")}))

    events = [e for e in diff(before.get_projects(), after.get_projects()) if e.project.server_url == a]

    assert [(e.change, e.project.label()) for e in events] == [(Change.BROKEN, "[a] web")]
    assert audible(events, mutes, datetime.now(UTC)) == []
    assert [e.project.label() for e in audible(events, Mutes(), datetime.now(UTC))] == ["[a] web"]


def test_should_not_report_a_row_as_new_when_only_its_label_changed():
    a, b = "http://a/cc.xml", "http://b/cc.xml"
    before = OverallIntegrationStatus([failing(a, "web", "Failure")])
    after = OverallIntegrationStatus([failing(a, "web", "Failure"), failing(b, "web", "Failure")])

    events = diff(before.get_projects(), after.get_projects())

    assert [(e.change, e.project.server_url) for e in events] == [(Change.BROKEN, b)]


def muted_status():
    a, b = "http://a/cc.xml", "http://b/cc.xml"
    status = OverallIntegrationStatus(
        [
            ServerSnapshot(a, (project(a, "api", "Failure"), project(a, "web", "Success"))),
            ServerSnapshot(b, (project(b, "docs", "Failure"), project(b, "site", "Success"))),
        ]
    )
    return status, a, b


def project(url, name, status):
    return ProjectBuilder({"name": name, "lastBuildStatus": status, "activity": "Sleeping"}, url=url).build()


def test_should_ignore_muted_projects_in_the_failing_count_and_summary():
    status, a, _ = muted_status()
    mutes = Mutes(projects=frozenset({(a, "api")}))

    assert [p.name for p in status.get_failing_builds(mutes)] == ["docs"]
    assert status.failing_summary(mutes) == "1 failing: docs"
    assert status.muted_count(mutes) == 1


def test_should_ignore_every_project_on_a_muted_server():
    status, a, _ = muted_status()
    mutes = Mutes(servers=frozenset({a}))

    assert [p.name for p in status.get_failing_builds(mutes)] == ["docs"]
    assert status.muted_count(mutes) == 2


def test_should_show_the_icon_for_the_unmuted_projects_when_failures_are_muted():
    status, a, b = muted_status()

    assert status.get_build_status(Mutes(projects=frozenset({(a, "api"), (b, "docs")}))) == "Success.Sleeping"
    assert status.get_build_status(Mutes(servers=frozenset({a, b}))) is None
    assert status.failing_summary(Mutes(servers=frozenset({a, b}))) == "No failing builds"


def test_should_not_let_the_pause_change_the_status():
    status, _, _ = muted_status()
    paused = Mutes(paused_until=datetime(2999, 1, 1, tzinfo=UTC))

    assert status.get_build_status(paused) == status.get_build_status()
    assert len(status.get_failing_builds(paused)) == 2
    assert status.muted_count(paused) == 0
