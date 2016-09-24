import unittest

from buildnotifylib.core.server import ContinuousIntegrationServer, FilteredContinuousIntegrationServer
from test.project_builder import ProjectBuilder


class FilteredContinuousIntegrationServerTest(unittest.TestCase):
    def test_should_remove_excluded_projects(self):
        class Attrs(dict):
            def __missing__(self, key):
                return key

        project1 = ProjectBuilder(Attrs({'name': 'a'})).build()
        project2 = ProjectBuilder(Attrs({'name': 'b'})).build()
        server = FilteredContinuousIntegrationServer(ContinuousIntegrationServer("someurl", [project1, project2]), ['a'])
        self.assertEquals([project2], server.get_projects())


if __name__ == '__main__':
    unittest.main()
