import unittest

from buildnotifylib.core.projects import OverallIntegrationStatus, ProjectLoader
from buildnotifylib.core.server import ContinuousIntegrationServer
from buildnotifylib.serverconfig import ServerConfig
from project_builder import ProjectBuilder
from cStringIO import StringIO

class OverallIntegrationStatusTest(unittest.TestCase):
    def test_should_consolidate_build_status(self):
        project1 = ProjectBuilder({'name': 'a', 'lastBuildStatus': 'Success', 'activity': 'Sleeping'}).build()
        project2 = ProjectBuilder({'name': 'a', 'lastBuildStatus': 'Success', 'activity': 'Sleeping'}).build()
        status = OverallIntegrationStatus([ContinuousIntegrationServer("someurl", [project1, project2])])
        self.assertEquals('Success.Sleeping', status.get_build_status())

    def test_should_mark_failed_if_even_one_failed(self):
        project1 = ProjectBuilder({'name': 'a', 'lastBuildStatus': 'Success', 'activity': 'Sleeping'}).build()
        project2 = ProjectBuilder({'name': 'a', 'lastBuildStatus': 'Failure', 'activity': 'Sleeping'}).build()
        status = OverallIntegrationStatus([ContinuousIntegrationServer("someurl", [project1, project2])])
        self.assertEquals('Failure.Sleeping', status.get_build_status())

    def test_should_mark_failed_if_even_one_failed_across_servers(self):
        project1 = ProjectBuilder({'name': 'a', 'lastBuildStatus': 'Success', 'activity': 'Sleeping'}).build()
        project2 = ProjectBuilder({'name': 'a', 'lastBuildStatus': 'Failure', 'activity': 'Sleeping'}).build()
        status = OverallIntegrationStatus([
            ContinuousIntegrationServer("url1", [project1]),
            ContinuousIntegrationServer('url2', [project2])
        ])
        self.assertEquals('Failure.Sleeping', status.get_build_status())

    def test_should_identify_failing_builds(self):
        project1 = ProjectBuilder({'name': 'a', 'lastBuildStatus': 'Success', 'activity': 'Sleeping'}).build()
        project2 = ProjectBuilder({'name': 'a', 'lastBuildStatus': 'Failure', 'activity': 'Sleeping'}).build()
        status = OverallIntegrationStatus([ContinuousIntegrationServer("someurl", [project1, project2])])
        self.assertEquals([project2], status.get_failing_builds())


class ProjectLoaderTest(unittest.TestCase):
    def test_should_load_feed(self):
        class MockConnection:
            def __init__(self):
                pass
            def connect(self, server, timeout):
                return StringIO("""<?xml version="1.0" encoding="UTF-8"?>
                                        <Projects>
                                            <Project name="project" activity="Sleeping" lastBuildStatus="Success" lastBuildTime="2009-06-12T06:54:35" webUrl="http://local/url"/>
                                        </Projects>
""")
        response = ProjectLoader(ServerConfig('url', [], '', '', '', ''), 10, MockConnection()).get_data()
        projects = response.server.get_projects()
        self.assertEquals(1, len(projects))
        self.assertEquals("project", projects[0].name)
        self.assertEquals("Sleeping", projects[0].activity)
        self.assertEquals("Success", projects[0].status)
        self.assertEquals(False, response.server.unavailable)

    def test_should_respond_even_if_things_fail(self):
        class MockConnection:
            def __init__(self):
                pass
            def connect(self, server, timeout):
                raise Exception("something went wrong")
        response = ProjectLoader(ServerConfig('url', [], '', '', '', ''), 10, MockConnection()).get_data()
        projects = response.server.get_projects()
        self.assertEquals(0, len(projects))
        self.assertEquals(True, response.server.unavailable)

if __name__ == '__main__':
    unittest.main()
