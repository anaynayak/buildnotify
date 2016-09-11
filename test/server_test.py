import unittest

from buildnotifylib.core.project import Project
from buildnotifylib.core.server import ContinuousIntegrationServer, FilteredContinuousIntegrationServer


class FilteredContinuousIntegrationServerTest(unittest.TestCase):
    def test_should_remove_excluded_projects(self):
        class Attrs(dict):
            def __missing__(self, key):
                return key

        project1 = Project(Attrs({'name': 'a'}))
        project2 = Project(Attrs({'name': 'b'}))
        server = FilteredContinuousIntegrationServer(ContinuousIntegrationServer("someurl", [project1, project2]), ['a'])
        self.assertEquals([project2], server.get_projects())


if __name__ == '__main__':
    unittest.main()
