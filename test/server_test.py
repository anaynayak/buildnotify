import unittest

from buildnotifylib.core.server import ContinuousIntegrationServer, FilteredContinuousIntegrationServer
from test.project_builder import ProjectBuilder


class FilteredContinuousIntegrationServerTest(unittest.TestCase):
    def test_should_remove_excluded_projects(self):
        project1 = ProjectBuilder({'name': 'a'}).build()
        project2 = ProjectBuilder({'name': 'b'}).build()

        server = FilteredContinuousIntegrationServer(ContinuousIntegrationServer("someurl", [project1, project2]), ['a'])

        self.assertEquals([project2], server.get_projects())

    def test_prefix_shouldnt_affect_exclusion(self):
        project1 = ProjectBuilder({'name': 'a'}).prefix('s1').build()
        project2 = ProjectBuilder({'name': 'b'}).prefix('s1').build()

        server = FilteredContinuousIntegrationServer(ContinuousIntegrationServer("someurl", [project1, project2]), ['a'])

        self.assertEquals([project2], server.get_projects())


if __name__ == '__main__':
    unittest.main()
