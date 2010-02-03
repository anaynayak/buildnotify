import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..","src")))

import unittest
from projects import Project
from projects import Projects
from project_status_notification import ProjectStatus
class ProjectStatusNotificationTest(unittest.TestCase):
    def test_should_identify_failing_builds(self):
        old_projects = [Project({'name':'proj1', 'lastBuildStatus':'Success', 'activity': 'Sleeping', 'url': 'someurl', 'lastBuildTime': '2009-05-29T13:54:07'}), Project({'name':'proj2', 'lastBuildStatus':'Success', 'activity': 'Sleeping', 'url': 'someurl', 'lastBuildTime': '2009-05-29T13:54:37'})]
        new_projects = [Project({'name':'proj1', 'lastBuildStatus':'Success', 'activity': 'Sleeping', 'url': 'someurl', 'lastBuildTime': '2009-05-29T13:54:07'}), Project({'name':'proj2', 'lastBuildStatus':'Failure', 'activity': 'Sleeping', 'url': 'someurl', 'lastBuildTime': '2009-05-29T13:54:37'})]
        failing_builds = ProjectStatus(Projects(old_projects), Projects(new_projects)).failing_builds()
        self.assertEquals(1,len(failing_builds))
        self.assertEquals("proj2", failing_builds[0])
        
    def test_should_identify_fixed_builds(self):
        old_projects = [Project({'name':'proj1', 'lastBuildStatus':'Failure', 'activity': 'Sleeping', 'url': 'someurl', 'lastBuildTime': '2009-05-29T13:54:07'}), Project({'name':'proj2', 'lastBuildStatus':'Failure', 'activity': 'Sleeping', 'url': 'someurl', 'lastBuildTime': '2009-05-29T13:54:37'})]
        new_projects = [Project({'name':'proj1', 'lastBuildStatus':'Success', 'activity': 'Sleeping', 'url': 'someurl', 'lastBuildTime': '2009-05-29T13:54:07'}), Project({'name':'proj2', 'lastBuildStatus':'Failure', 'activity': 'Sleeping', 'url': 'someurl', 'lastBuildTime': '2009-05-29T13:54:37'})]
        successful_builds = ProjectStatus(Projects(old_projects), Projects(new_projects)).successful_builds()
        self.assertEquals(1,len(successful_builds))
        self.assertEquals("proj1", successful_builds[0])
    def test_should_identify_still_failing_builds(self):
        old_projects = [Project({'name':'proj1', 'lastBuildStatus':'Success', 'activity': 'Sleeping', 'url': 'someurl', 'lastBuildTime': '2009-05-29T13:54:07'}), Project({'name':'stillfailingbuild', 'lastBuildStatus':'Failure', 'activity': 'Sleeping', 'url': 'someurl', 'lastBuildTime': '2009-05-29T13:54:37'})]
        new_projects = [Project({'name':'proj1', 'lastBuildStatus':'Success', 'activity': 'Sleeping', 'url': 'someurl', 'lastBuildTime': '2009-05-29T13:54:07'}), Project({'name':'stillfailingbuild', 'lastBuildStatus':'Failure', 'activity': 'Sleeping', 'url': 'someurl', 'lastBuildTime': '2009-05-29T13:54:47'})]    
        still_failing_builds = ProjectStatus(Projects(old_projects), Projects(new_projects)).still_failing_builds()
        self.assertEquals(1,len(still_failing_builds))
        self.assertEquals("stillfailingbuild", still_failing_builds[0])
    def test_should_identify_still_successful_builds(self):
        old_projects = [Project({'name':'proj1', 'lastBuildStatus':'Success', 'activity': 'Sleeping', 'url': 'someurl', 'lastBuildTime': '2009-05-29T13:54:07'}), Project({'name':'Successbuild', 'lastBuildStatus':'Success', 'activity': 'Sleeping', 'url': 'someurl', 'lastBuildTime': '2009-05-29T13:54:37'})]
        new_projects = [Project({'name':'proj1', 'lastBuildStatus':'Success', 'activity': 'Sleeping', 'url': 'someurl', 'lastBuildTime': '2009-05-29T13:54:07'}), Project({'name':'Successbuild', 'lastBuildStatus':'Success', 'activity': 'Sleeping', 'url': 'someurl', 'lastBuildTime': '2009-05-29T13:54:47'})]    
        still_successful_builds = ProjectStatus(Projects(old_projects), Projects(new_projects)).still_successful_builds()
        self.assertEquals(1,len(still_successful_builds))
        self.assertEquals("Successbuild", still_successful_builds[0])
    def test_should_identify_new_builds(self):
        old_projects = [Project({'name':'proj1', 'lastBuildStatus':'Success', 'activity': 'Sleeping', 'url': 'someurl', 'lastBuildTime': '2009-05-29T13:54:07'})]
        new_projects = [Project({'name':'proj1', 'lastBuildStatus':'Success', 'activity': 'Sleeping', 'url': 'someurl', 'lastBuildTime': '2009-05-29T13:54:07'}), Project({'name':'Successbuild', 'lastBuildStatus':'Success', 'activity': 'Sleeping', 'url': 'someurl', 'lastBuildTime': '2009-05-29T13:54:47'})]    
        still_successful_builds = ProjectStatus(Projects(old_projects), Projects(new_projects)).still_successful_builds()
        self.assertEquals(1, len(still_successful_builds))
        self.assertEquals("Successbuild", still_successful_builds[0])

if __name__ == '__main__':
    unittest.main()

