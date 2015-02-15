import sys
import os
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import unittest
from buildnotifylib.core.projects import Project


class ProjectTest(unittest.TestCase):
    def test_should_ignore_empty_last_build_time(self):
        project = Project({
            'lastBuildTime': '',
            'server_url': 'i',
            'name': 'g',
            'lastBuildStatus': 'n',
            'activity': 'o',
            'url': 'r'}
        )
        self.assertEquals(datetime.datetime.now().date(), project.get_last_build_time().date())

    def test_should_correctly_parse_project(self):
        project = Project({
            'server_url': 'url',
            'name': 'proj1',
            'lastBuildStatus': 'Success',
            'activity': 'Sleeping',
            'url': 'someurl',
            'lastBuildLabel': '120',
            'lastBuildTime': '2009-05-29T13:54:07'
        })

        self.assertEquals('url', project.server_url)
        self.assertEquals('proj1', project.name)
        self.assertEquals('Success', project.status)
        self.assertEquals('someurl', project.url)
        self.assertEquals('Sleeping', project.activity)
        self.assertEquals('2009-05-29T13:54:07', project.last_build_time)
        self.assertEquals('120', project.last_build_label)
        self.assertEquals(datetime.datetime(2009, 5, 29, 13, 54, 7), project.get_last_build_time())


if __name__ == '__main__':
    unittest.main()
