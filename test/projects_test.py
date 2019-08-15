import unittest

from buildnotifylib.core.continous_integration_server import ContinuousIntegrationServer
from buildnotifylib.core.projects import OverallIntegrationStatus, ProjectLoader
from buildnotifylib.serverconfig import ServerConfig
from .project_builder import ProjectBuilder
from io import StringIO


class OverallIntegrationStatusTest(unittest.TestCase):
    def test_should_consolidate_build_status(self):
        project1 = ProjectBuilder({'name': 'a', 'lastBuildStatus': 'Success', 'activity': 'Sleeping'}).build()
        project2 = ProjectBuilder({'name': 'a', 'lastBuildStatus': 'Success', 'activity': 'Sleeping'}).build()
        status = OverallIntegrationStatus([ContinuousIntegrationServer("someurl", [project1, project2])])
        self.assertEqual('Success.Sleeping', status.get_build_status())

    def test_should_mark_failed_if_even_one_failed(self):
        project1 = ProjectBuilder({'name': 'a', 'lastBuildStatus': 'Success', 'activity': 'Sleeping'}).build()
        project2 = ProjectBuilder({'name': 'a', 'lastBuildStatus': 'Failure', 'activity': 'Sleeping'}).build()
        status = OverallIntegrationStatus([ContinuousIntegrationServer("someurl", [project1, project2])])
        self.assertEqual('Failure.Sleeping', status.get_build_status())

    def test_should_mark_failed_if_even_one_failed_across_servers(self):
        project1 = ProjectBuilder({'name': 'a', 'lastBuildStatus': 'Success', 'activity': 'Sleeping'}).build()
        project2 = ProjectBuilder({'name': 'a', 'lastBuildStatus': 'Failure', 'activity': 'Sleeping'}).build()
        status = OverallIntegrationStatus([
            ContinuousIntegrationServer("url1", [project1]),
            ContinuousIntegrationServer('url2', [project2])
        ])
        self.assertEqual('Failure.Sleeping', status.get_build_status())

    def test_should_identify_failing_builds(self):
        project1 = ProjectBuilder({'name': 'a', 'lastBuildStatus': 'Success', 'activity': 'Sleeping'}).build()
        project2 = ProjectBuilder({'name': 'a', 'lastBuildStatus': 'Failure', 'activity': 'Sleeping'}).build()
        status = OverallIntegrationStatus([ContinuousIntegrationServer("someurl", [project1, project2])])
        self.assertEqual([project2], status.get_failing_builds())


class MockConnection(object):
    def __init__(self, data):
        self.data = data

    def connect(self, server, timeout):
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
        response = ProjectLoader(ServerConfig('url', [], '', '', '', ''), 10, connection).get_data()
        projects = response.server.get_projects()
        self.assertEqual(1, len(projects))
        self.assertEqual("project", projects[0].name)
        self.assertEqual("Sleeping", projects[0].activity)
        self.assertEqual("Success", projects[0].status)
        self.assertEqual(False, response.server.unavailable)

    def test_should_respond_even_if_things_fail(self):
        class MockConnection(object):
            def __init__(self):
                pass

            def connect(self, server, timeout):
                raise Exception("something went wrong")

        response = ProjectLoader(ServerConfig('url', [], '', '', '', ''), 10, MockConnection()).get_data()
        projects = response.server.get_projects()
        self.assertEqual(0, len(projects))
        self.assertEqual(True, response.server.unavailable)

    def test_should_set_display_prefix(self):
        connection = MockConnection("""<?xml version="1.0" encoding="UTF-8"?>
                                        <Projects>
                                            <Project name="project" 
                                                activity="Sleeping" 
                                                lastBuildStatus="Success" 
                                                lastBuildTime="2009-06-12T06:54:35" 
                                                webUrl="http://local/url"/>
                                        </Projects>""")
        response = ProjectLoader(ServerConfig('url', [], '', 'RELEASE', '', ''), 10, connection).get_data()
        projects = response.server.get_projects()
        self.assertEqual(1, len(projects))
        self.assertEqual("[RELEASE] project", projects[0].label())


if __name__ == '__main__':
    unittest.main()
