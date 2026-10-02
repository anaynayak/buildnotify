import unittest

from buildnotifylib.core.continous_integration_server import ContinuousIntegrationServer
from buildnotifylib.core.projects import OverallIntegrationStatus, ProjectLoader
from buildnotifylib.serverconfig import ServerConfig

from .project_builder import ProjectBuilder


class OverallIntegrationStatusTest(unittest.TestCase):
    def test_should_consolidate_build_status(self):
        project1 = ProjectBuilder({"name": "a", "lastBuildStatus": "Success", "activity": "Sleeping"}).build()
        project2 = ProjectBuilder({"name": "a", "lastBuildStatus": "Success", "activity": "Sleeping"}).build()
        status = OverallIntegrationStatus([ContinuousIntegrationServer("someurl", [project1, project2])])
        self.assertEqual("Success.Sleeping", status.get_build_status())

    def test_should_mark_failed_if_even_one_failed(self):
        project1 = ProjectBuilder({"name": "a", "lastBuildStatus": "Success", "activity": "Sleeping"}).build()
        project2 = ProjectBuilder({"name": "a", "lastBuildStatus": "Failure", "activity": "Sleeping"}).build()
        status = OverallIntegrationStatus([ContinuousIntegrationServer("someurl", [project1, project2])])
        self.assertEqual("Failure.Sleeping", status.get_build_status())

    def test_should_mark_failed_if_even_one_failed_across_servers(self):
        project1 = ProjectBuilder({"name": "a", "lastBuildStatus": "Success", "activity": "Sleeping"}).build()
        project2 = ProjectBuilder({"name": "a", "lastBuildStatus": "Failure", "activity": "Sleeping"}).build()
        status = OverallIntegrationStatus(
            [ContinuousIntegrationServer("url1", [project1]), ContinuousIntegrationServer("url2", [project2])]
        )
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
        status = OverallIntegrationStatus([ContinuousIntegrationServer("someurl", [project1, project2])])
        self.assertEqual([project2], status.get_failing_builds())


def overall_status(*statuses):
    projects = [
        ProjectBuilder({"name": f"p{i}", "lastBuildStatus": status, "activity": activity}).build()
        for i, (status, activity) in enumerate(statuses)
    ]
    return OverallIntegrationStatus([ContinuousIntegrationServer("someurl", projects)])


class MockConnection:
    def __init__(self, data):
        self.data = data

    def connect(self, server, timeout, additional_headers=None):
        return self.data


class ProjectLoaderTest(unittest.TestCase):
    def test_should_load_feed(self):
        connection = MockConnection("""<?xml version="1.0" encoding="UTF-8"?>
                                <Projects>
                                    <Project name="project"
                                        activity="Sleeping"
                                        lastBuildStatus="Success"
                                        lastBuildTime="2009-06-12T06:54:35"
                                        webUrl="http://local/url"/>
                                </Projects>""")
        response = ProjectLoader(ServerConfig("url", [], "", "", "", ""), 10, connection).get_data()
        projects = response.server.get_projects()
        self.assertEqual(1, len(projects))
        self.assertEqual("project", projects[0].name)
        self.assertEqual("Sleeping", projects[0].activity)
        self.assertEqual("Success", projects[0].status)
        self.assertEqual(False, response.server.unavailable)

    def test_should_respond_even_if_things_fail(self):
        error = Exception("something went wrong")

        class FailingConnection:
            def connect(self, server, timeout, additional_headers=None):
                raise error

        response = ProjectLoader(ServerConfig("url", [], "", "", "", ""), 10, FailingConnection()).get_data()
        projects = response.server.get_projects()
        self.assertEqual(0, len(projects))
        self.assertEqual(True, response.server.unavailable)
        self.assertIs(error, response.error)

    def test_should_mark_server_unavailable_for_html_body(self):
        self.assert_unavailable("<html><body><form>Login</form></body></html")

    def test_should_mark_server_unavailable_for_empty_body(self):
        self.assert_unavailable("")

    def test_should_mark_server_unavailable_for_truncated_xml(self):
        self.assert_unavailable('<?xml version="1.0"?><Projects><Project name="project" activity=')

    def test_should_reject_entity_declarations(self):
        self.assert_unavailable(
            '<?xml version="1.0"?><!DOCTYPE Projects [<!ENTITY a "aaaaaaaaaa">]>'
            '<Projects><Project name="&a;" activity="Sleeping"/></Projects>'
        )

    def test_should_report_error_for_non_cctray_feed(self):
        body = '<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"><title>All builds</title></feed>'
        response = self.assert_unavailable(body)
        self.assertIn("feed", str(response.error))

    def assert_unavailable(self, body):
        response = ProjectLoader(ServerConfig("url", [], "", "", "", ""), 10, MockConnection(body)).get_data()
        self.assertEqual([], response.server.get_projects())
        self.assertEqual(True, response.server.unavailable)
        self.assertEqual(True, response.failed())
        return response

    def test_should_set_display_prefix(self):
        connection = MockConnection("""<?xml version="1.0" encoding="UTF-8"?>
                                        <Projects>
                                            <Project name="project"
                                                activity="Sleeping"
                                                lastBuildStatus="Success"
                                                lastBuildTime="2009-06-12T06:54:35"
                                                webUrl="http://local/url"/>
                                        </Projects>""")
        response = ProjectLoader(ServerConfig("url", [], "", "RELEASE", "", ""), 10, connection).get_data()
        projects = response.server.get_projects()
        self.assertEqual(1, len(projects))
        self.assertEqual("[RELEASE] project", projects[0].label())


if __name__ == "__main__":
    unittest.main()
