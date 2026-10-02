import unittest

from buildnotifylib.core.projects import ProjectLoader
from buildnotifylib.serverconfig import ServerConfig

from .utils import fake_content


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
        projects = response.projects
        self.assertEqual(1, len(projects))
        self.assertEqual("project", projects[0].name)
        self.assertEqual("Sleeping", projects[0].activity)
        self.assertEqual("Success", projects[0].status)
        self.assertEqual(False, response.unavailable)

    def test_should_respond_even_if_things_fail(self):
        error = Exception("something went wrong")

        class FailingConnection:
            def connect(self, server, timeout, additional_headers=None):
                raise error

        response = ProjectLoader(ServerConfig("url", [], "", "", "", ""), 10, FailingConnection()).get_data()
        projects = response.projects
        self.assertEqual(0, len(projects))
        self.assertEqual(True, response.unavailable)
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
        self.assertEqual((), response.projects)
        self.assertEqual(True, response.unavailable)
        return response

    def test_should_drop_excluded_projects(self):
        config = ServerConfig("url", ["orbit-M"], "", "", "", "")
        projects = ProjectLoader(config, 10, MockConnection(fake_content())).get_data().projects
        self.assertEqual(6, len(projects))
        self.assertNotIn("orbit-M", [p.name for p in projects])

    def test_should_keep_excluded_projects_on_request(self):
        config = ServerConfig("url", ["orbit-M"], "", "", "", "")
        loader = ProjectLoader(config, 10, MockConnection(fake_content()), apply_excludes=False)
        self.assertEqual(7, len(loader.get_data().projects))

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
        projects = response.projects
        self.assertEqual(1, len(projects))
        self.assertEqual("[RELEASE] project", projects[0].label())


if __name__ == "__main__":
    unittest.main()
