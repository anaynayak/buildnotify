import unittest

from buildnotifylib.core.continous_integration_server import ContinuousIntegrationServer
from buildnotifylib.core.projects import OverallIntegrationStatus
from buildnotifylib.project_status_notification import ProjectStatus, ProjectStatusNotification
from test.fake_conf import ConfigBuilder
from test.project_builder import ProjectBuilder


class ProjectStatusTest(unittest.TestCase):
    def test_should_identify_failing_builds(self):
        old_projects = [
            ProjectBuilder({'name': 'proj1', 'lastBuildStatus': 'Success', 'activity': 'Sleeping', 'url': 'someurl',
                            'lastBuildTime': '2009-05-29T13:54:07'}).build(),
            ProjectBuilder({'name': 'proj2', 'lastBuildStatus': 'Success', 'activity': 'Sleeping', 'url': 'someurl',
                            'lastBuildTime': '2009-05-29T13:54:37'}).build()]
        new_projects = [
            ProjectBuilder({'name': 'proj1', 'lastBuildStatus': 'Success', 'activity': 'Sleeping', 'url': 'someurl',
                            'lastBuildTime': '2009-05-29T13:54:07'}).build(),
            ProjectBuilder({'name': 'proj2', 'lastBuildStatus': 'Failure', 'activity': 'Sleeping', 'url': 'someurl',
                            'lastBuildTime': '2009-05-29T13:54:37'}).build()]
        failing_builds = ProjectStatusTest.build(old_projects, new_projects).failing_builds()
        self.assertEquals(1, len(failing_builds))
        self.assertEquals("proj2", failing_builds[0])

    def test_should_identify_fixed_builds(self):
        old_projects = [
            ProjectBuilder({'name': 'proj1', 'lastBuildStatus': 'Failure', 'activity': 'Sleeping', 'url': 'someurl',
                            'lastBuildTime': '2009-05-29T13:54:07'}).build(),
            ProjectBuilder({'name': 'proj2', 'lastBuildStatus': 'Failure', 'activity': 'Sleeping', 'url': 'someurl',
                            'lastBuildTime': '2009-05-29T13:54:37'}).build()]
        new_projects = [
            ProjectBuilder({'name': 'proj1', 'lastBuildStatus': 'Success', 'activity': 'Sleeping', 'url': 'someurl',
                            'lastBuildTime': '2009-05-29T13:54:07'}).build(),
            ProjectBuilder({'name': 'proj2', 'lastBuildStatus': 'Failure', 'activity': 'Sleeping', 'url': 'someurl',
                            'lastBuildTime': '2009-05-29T13:54:37'}).build()]
        successful_builds = ProjectStatusTest.build(old_projects, new_projects).successful_builds()
        self.assertEquals(1, len(successful_builds))
        self.assertEquals("proj1", successful_builds[0])

    def test_should_identify_still_failing_builds(self):
        old_projects = [
            ProjectBuilder(
                {'name': 'proj1', 'lastBuildStatus': 'Success', 'activity': 'Sleeping', 'url': 'someurl',
                 'lastBuildLabel': '1',
                 'lastBuildTime': '2009-05-29T13:54:07'}).build(),
            ProjectBuilder(
                {'name': 'stillfailingbuild', 'lastBuildStatus': 'Failure', 'activity': 'Sleeping', 'url': 'someurl',
                 'lastBuildLabel': '10', 'lastBuildTime': '2009-05-29T13:54:37'}).build()]
        new_projects = [
            ProjectBuilder(
                {'name': 'proj1', 'lastBuildStatus': 'Success', 'activity': 'Sleeping', 'url': 'someurl',
                 'lastBuildLabel': '1',
                 'lastBuildTime': '2009-05-29T13:54:07'}).build(),
            ProjectBuilder(
                {'name': 'stillfailingbuild', 'lastBuildStatus': 'Failure', 'activity': 'Sleeping', 'url': 'someurl',
                 'lastBuildLabel': '11', 'lastBuildTime': '2009-05-29T13:54:47'}).build()]
        still_failing_builds = ProjectStatusTest.build(old_projects, new_projects).still_failing_builds()
        self.assertEquals(1, len(still_failing_builds))
        self.assertEquals("stillfailingbuild", still_failing_builds[0])

    def test_should_identify_still_successful_builds(self):
        old_projects = [
            ProjectBuilder(
                {'name': 'proj1', 'lastBuildStatus': 'Success', 'activity': 'Sleeping',
                 'url': 'someurl', 'lastBuildLabel': '1',
                 'lastBuildTime': '2009-05-29T13:54:07'}).build(),
            ProjectBuilder(
                {'name': 'Successbuild', 'lastBuildStatus': 'Success', 'activity': 'Sleeping',
                 'url': 'someurl',
                 'lastBuildLabel': '10', 'lastBuildTime': '2009-05-29T13:54:37'}).build()]
        new_projects = [
            ProjectBuilder(
                {'name': 'proj1', 'lastBuildStatus': 'Success', 'activity': 'Sleeping',
                 'url': 'someurl', 'lastBuildLabel': '1',
                 'lastBuildTime': '2009-05-29T13:54:07'}).build(),
            ProjectBuilder(
                {'name': 'Successbuild', 'lastBuildStatus': 'Success', 'activity': 'Sleeping',
                 'url': 'someurl',
                 'lastBuildLabel': '11', 'lastBuildTime': '2009-05-29T13:54:47'}).build()]
        still_successful_builds = ProjectStatusTest.build(old_projects, new_projects).still_successful_builds()
        self.assertEquals(1, len(still_successful_builds))
        self.assertEquals("Successbuild", still_successful_builds[0])

    def test_should_build_tuples_by_server_url_and_name(self):
        project_s1 = ProjectBuilder({'name': 'proj1', 'lastBuildStatus': 'Success', 'activity': 'Sleeping',
                                     'url': 'someurl',
                                     'lastBuildTime': '2009-05-29T13:54:07'}).server('s1').build()
        project_s2 = ProjectBuilder({'name': 'proj1', 'lastBuildStatus': 'Success', 'activity': 'Sleeping',
                                     'url': 'someurl',
                                     'lastBuildTime': '2009-05-29T13:54:07'}).server('s2').build()
        old_projects = [project_s1, project_s2]
        new_projects = [project_s2, project_s1]
        tuple = ProjectStatusTest.build(old_projects, new_projects).tuple_for(project_s2)
        self.assertEquals('s2', tuple.current_project.server_url)
        self.assertEquals('s2', tuple.old_project.server_url)

    def test_should_identify_new_builds(self):
        old_projects = [
            ProjectBuilder(
                {'name': 'proj1', 'lastBuildStatus': 'Success', 'activity': 'Sleeping',
                 'url': 'someurl',
                 'lastBuildTime': '2009-05-29T13:54:07'}).build()]
        new_projects = [
            ProjectBuilder(
                {'name': 'proj1', 'lastBuildStatus': 'Success', 'activity': 'Sleeping',
                 'url': 'someurl',
                 'lastBuildTime': '2009-05-29T13:54:07'}).build(),
            ProjectBuilder(
                {'name': 'Successbuild', 'lastBuildStatus': 'Success',
                 'activity': 'Sleeping', 'url': 'someurl',
                 'lastBuildTime': '2009-05-29T13:54:47'}).build()]
        still_successful_builds = ProjectStatusTest.build(old_projects, new_projects).still_successful_builds()
        self.assertEquals(1, len(still_successful_builds))
        self.assertEquals("Successbuild", still_successful_builds[0])

    def test_should_include_prefix_in_notification(self):
        old_projects = [
            ProjectBuilder(
                {'name': 'proj1', 'lastBuildStatus': 'Success', 'activity': 'Sleeping',
                 'url': 'someurl',
                 'lastBuildTime': '2009-05-29T13:54:07'}).prefix('R1').build()]
        new_projects = [
            ProjectBuilder(
                {'name': 'proj1', 'lastBuildStatus': 'Success', 'activity': 'Sleeping',
                 'url': 'someurl',
                 'lastBuildTime': '2009-05-29T13:54:07'}).prefix('R1').build(),
            ProjectBuilder(
                {'name': 'Successbuild', 'lastBuildStatus': 'Success',
                 'activity': 'Sleeping', 'url': 'someurl',
                 'lastBuildTime': '2009-05-29T13:54:47'}).prefix('R1').build()]
        still_successful_builds = ProjectStatusTest.build(old_projects, new_projects).still_successful_builds()
        self.assertEquals(1, len(still_successful_builds))
        self.assertEquals("[R1] Successbuild", still_successful_builds[0])

    @classmethod
    def build(cls, old_projects, new_projects):
        return ProjectStatus(old_projects, new_projects)


def test_should_return_notifications(mocker):
    old_projects = [ProjectBuilder({'name': 'proj1',
                                    'lastBuildStatus': 'Success',
                                    'activity': 'Sleeping',
                                    'url': 'someurl',
                                    'lastBuildLabel': '1',
                                    'lastBuildTime': '2009-05-29T13:54:07'}).build(),
                    ProjectBuilder({'name': 'Successbuild',
                                    'lastBuildStatus': 'Failure',
                                    'activity': 'Sleeping',
                                    'url': 'someurl',
                                    'lastBuildLabel': '10',
                                    'lastBuildTime': '2009-05-29T13:54:37'}).build()]
    new_projects = [ProjectBuilder({'name': 'proj1',
                                    'lastBuildStatus': 'Failure',
                                    'activity': 'Sleeping',
                                    'url': 'someurl',
                                    'lastBuildLabel': '2',
                                    'lastBuildTime': '2009-05-29T13:54:07'}).build(),
                    ProjectBuilder({'name': 'Successbuild',
                                    'lastBuildStatus': 'Success',
                                    'activity': 'Sleeping',
                                    'url': 'someurl',
                                    'lastBuildLabel': '11',
                                    'lastBuildTime': '2009-05-29T13:54:47'}).build()]
    old = OverallIntegrationStatus([ContinuousIntegrationServer('url', old_projects)])
    new = OverallIntegrationStatus([ContinuousIntegrationServer('url', new_projects)])

    class NotificationFake(object):
        def __init__(self):
            pass

        def show_message(self, **kwargs):
            print kwargs

    m = mocker.patch.object(NotificationFake, 'show_message')

    notification = ProjectStatusNotification(ConfigBuilder().build(), old, new, NotificationFake())
    notification.show_notifications()

    m.assert_any_call('Broken builds', 'proj1')
    m.assert_any_call('Fixed builds', 'Successbuild')


if __name__ == '__main__':
    unittest.main()
