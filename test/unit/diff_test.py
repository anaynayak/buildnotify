import unittest

from hypothesis import given

from buildnotifylib.core.diff import Change, diff, labels
from test.project_builder import ProjectBuilder
from test.strategies import unique_project_lists


class Builds:
    def __init__(self, events):
        self.events = events

    def failing_builds(self):
        return labels(self.events, Change.BROKEN)

    def successful_builds(self):
        return labels(self.events, Change.FIXED)

    def still_failing_builds(self):
        return labels(self.events, Change.STILL_FAILING)

    def still_successful_builds(self):
        return labels(self.events, Change.STILL_SUCCESSFUL)


class DiffTest(unittest.TestCase):
    def test_should_identify_failing_builds(self):
        old_projects = [
            ProjectBuilder(
                {
                    "name": "proj1",
                    "lastBuildStatus": "Success",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildTime": "2009-05-29T13:54:07",
                }
            ).build(),
            ProjectBuilder(
                {
                    "name": "proj2",
                    "lastBuildStatus": "Success",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildTime": "2009-05-29T13:54:37",
                }
            ).build(),
        ]
        new_projects = [
            ProjectBuilder(
                {
                    "name": "proj1",
                    "lastBuildStatus": "Success",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildTime": "2009-05-29T13:54:07",
                }
            ).build(),
            ProjectBuilder(
                {
                    "name": "proj2",
                    "lastBuildStatus": "Failure",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildTime": "2009-05-29T13:54:37",
                }
            ).build(),
        ]
        failing_builds = DiffTest.build(old_projects, new_projects).failing_builds()
        self.assertEqual(1, len(failing_builds))
        self.assertEqual("proj2", failing_builds[0])

    def test_should_identify_fixed_builds(self):
        old_projects = [
            ProjectBuilder(
                {
                    "name": "proj1",
                    "lastBuildStatus": "Failure",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildTime": "2009-05-29T13:54:07",
                }
            ).build(),
            ProjectBuilder(
                {
                    "name": "proj2",
                    "lastBuildStatus": "Failure",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildTime": "2009-05-29T13:54:37",
                }
            ).build(),
        ]
        new_projects = [
            ProjectBuilder(
                {
                    "name": "proj1",
                    "lastBuildStatus": "Success",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildTime": "2009-05-29T13:54:07",
                }
            ).build(),
            ProjectBuilder(
                {
                    "name": "proj2",
                    "lastBuildStatus": "Failure",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildTime": "2009-05-29T13:54:37",
                }
            ).build(),
        ]
        successful_builds = DiffTest.build(old_projects, new_projects).successful_builds()
        self.assertEqual(1, len(successful_builds))
        self.assertEqual("proj1", successful_builds[0])

    def test_should_treat_exception_as_failure(self):
        def project(status, label):
            return ProjectBuilder(
                {
                    "name": "proj1",
                    "lastBuildStatus": status,
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildLabel": label,
                    "lastBuildTime": "2009-05-29T13:54:07",
                }
            ).build()

        self.assertEqual(
            ["proj1"], DiffTest.build([project("Success", "1")], [project("Exception", "2")]).failing_builds()
        )
        self.assertEqual(
            ["proj1"],
            DiffTest.build([project("Exception", "1")], [project("Success", "2")]).successful_builds(),
        )
        self.assertEqual(
            ["proj1"],
            DiffTest.build([project("Failure", "1")], [project("Exception", "2")]).still_failing_builds(),
        )

    def test_should_identify_still_failing_builds(self):
        old_projects = [
            ProjectBuilder(
                {
                    "name": "proj1",
                    "lastBuildStatus": "Success",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildLabel": "1",
                    "lastBuildTime": "2009-05-29T13:54:07",
                }
            ).build(),
            ProjectBuilder(
                {
                    "name": "stillfailingbuild",
                    "lastBuildStatus": "Failure",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildLabel": "10",
                    "lastBuildTime": "2009-05-29T13:54:37",
                }
            ).build(),
        ]
        new_projects = [
            ProjectBuilder(
                {
                    "name": "proj1",
                    "lastBuildStatus": "Success",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildLabel": "1",
                    "lastBuildTime": "2009-05-29T13:54:07",
                }
            ).build(),
            ProjectBuilder(
                {
                    "name": "stillfailingbuild",
                    "lastBuildStatus": "Failure",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildLabel": "11",
                    "lastBuildTime": "2009-05-29T13:54:47",
                }
            ).build(),
        ]
        still_failing_builds = DiffTest.build(old_projects, new_projects).still_failing_builds()
        self.assertEqual(1, len(still_failing_builds))
        self.assertEqual("stillfailingbuild", still_failing_builds[0])

    def test_should_identify_still_successful_builds(self):
        old_projects = [
            ProjectBuilder(
                {
                    "name": "proj1",
                    "lastBuildStatus": "Success",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildLabel": "1",
                    "lastBuildTime": "2009-05-29T13:54:07",
                }
            ).build(),
            ProjectBuilder(
                {
                    "name": "Successbuild",
                    "lastBuildStatus": "Success",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildLabel": "10",
                    "lastBuildTime": "2009-05-29T13:54:37",
                }
            ).build(),
        ]
        new_projects = [
            ProjectBuilder(
                {
                    "name": "proj1",
                    "lastBuildStatus": "Success",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildLabel": "1",
                    "lastBuildTime": "2009-05-29T13:54:07",
                }
            ).build(),
            ProjectBuilder(
                {
                    "name": "Successbuild",
                    "lastBuildStatus": "Success",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildLabel": "11",
                    "lastBuildTime": "2009-05-29T13:54:47",
                }
            ).build(),
        ]
        still_successful_builds = DiffTest.build(old_projects, new_projects).still_successful_builds()
        self.assertEqual(1, len(still_successful_builds))
        self.assertEqual("Successbuild", still_successful_builds[0])

    def test_should_match_projects_by_server_url_and_name(self):
        def build(server, status):
            attrs = {"name": "proj1", "lastBuildStatus": status, "activity": "Sleeping", "url": "someurl"}
            return ProjectBuilder(attrs).server(server).build()

        old_projects = [build("s1", "Success"), build("s2", "Failure")]
        new_projects = [build("s2", "Failure"), build("s1", "Success")]
        self.assertEqual([], diff(old_projects, new_projects))

    def test_should_identify_new_builds(self):
        old_projects = [
            ProjectBuilder(
                {
                    "name": "proj1",
                    "lastBuildStatus": "Success",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildTime": "2009-05-29T13:54:07",
                }
            ).build()
        ]
        new_projects = [
            ProjectBuilder(
                {
                    "name": "proj1",
                    "lastBuildStatus": "Success",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildTime": "2009-05-29T13:54:07",
                }
            ).build(),
            ProjectBuilder(
                {
                    "name": "Successbuild",
                    "lastBuildStatus": "Success",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildTime": "2009-05-29T13:54:47",
                }
            ).build(),
        ]
        still_successful_builds = DiffTest.build(old_projects, new_projects).still_successful_builds()
        self.assertEqual(1, len(still_successful_builds))
        self.assertEqual("Successbuild", still_successful_builds[0])

    def test_should_include_prefix_in_notification(self):
        old_projects = [
            ProjectBuilder(
                {
                    "name": "proj1",
                    "lastBuildStatus": "Success",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildTime": "2009-05-29T13:54:07",
                }
            )
            .prefix("R1")
            .build()
        ]
        new_projects = [
            ProjectBuilder(
                {
                    "name": "proj1",
                    "lastBuildStatus": "Success",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildTime": "2009-05-29T13:54:07",
                }
            )
            .prefix("R1")
            .build(),
            ProjectBuilder(
                {
                    "name": "Successbuild",
                    "lastBuildStatus": "Success",
                    "activity": "Sleeping",
                    "url": "someurl",
                    "lastBuildTime": "2009-05-29T13:54:47",
                }
            )
            .prefix("R1")
            .build(),
        ]
        still_successful_builds = DiffTest.build(old_projects, new_projects).still_successful_builds()
        self.assertEqual(1, len(still_successful_builds))
        self.assertEqual("[R1] Successbuild", still_successful_builds[0])

    @classmethod
    def build(cls, old_projects, new_projects):
        return Builds(diff(old_projects, new_projects))


@given(unique_project_lists())
def test_identical_poll_should_produce_no_events(projects):
    assert diff(projects, projects) == []


@given(unique_project_lists(), unique_project_lists())
def test_should_produce_at_most_one_event_per_project(old, new):
    assert len(diff(old, new)) <= len(new)
