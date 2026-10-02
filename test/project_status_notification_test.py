import os
import subprocess
import unittest

import pytest

from buildnotifylib.core.continous_integration_server import ContinuousIntegrationServer
from buildnotifylib.core.projects import OverallIntegrationStatus
from buildnotifylib.app_notification import AppNotification
from buildnotifylib.project_status_notification import substitute_placeholders, ProjectStatus, ProjectStatusNotification, TimedProjectFilter
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
        self.assertEqual(1, len(failing_builds))
        self.assertEqual("proj2", failing_builds[0])

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
        self.assertEqual(1, len(successful_builds))
        self.assertEqual("proj1", successful_builds[0])

    def test_should_treat_exception_as_failure(self):
        def project(status, label):
            return ProjectBuilder({'name': 'proj1', 'lastBuildStatus': status, 'activity': 'Sleeping',
                                   'url': 'someurl', 'lastBuildLabel': label,
                                   'lastBuildTime': '2009-05-29T13:54:07'}).build()

        self.assertEqual(["proj1"], ProjectStatusTest.build([project('Success', '1')],
                                                            [project('Exception', '2')]).failing_builds())
        self.assertEqual(["proj1"], ProjectStatusTest.build([project('Exception', '1')],
                                                            [project('Success', '2')]).successful_builds())
        self.assertEqual(["proj1"], ProjectStatusTest.build([project('Failure', '1')],
                                                            [project('Exception', '2')]).still_failing_builds())

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
        self.assertEqual(1, len(still_failing_builds))
        self.assertEqual("stillfailingbuild", still_failing_builds[0])

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
        self.assertEqual(1, len(still_successful_builds))
        self.assertEqual("Successbuild", still_successful_builds[0])

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
        self.assertEqual('s2', tuple.current_project.server_url)
        self.assertEqual('s2', tuple.old_project.server_url)

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
        self.assertEqual(1, len(still_successful_builds))
        self.assertEqual("Successbuild", still_successful_builds[0])

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
        self.assertEqual(1, len(still_successful_builds))
        self.assertEqual("[R1] Successbuild", still_successful_builds[0])

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
            print(kwargs)

    m = mocker.patch.object(NotificationFake, 'show_message')

    notification = ProjectStatusNotification(ConfigBuilder().build(), old, new, NotificationFake())
    notification.show_notifications()

    m.assert_any_call('Broken builds', 'proj1')
    m.assert_any_call('Fixed builds', 'Successbuild')



class _SilentNotification(object):
    def show_message(self, title, message):
        pass


def _broken_build_notification(script, project_name):
    old = OverallIntegrationStatus([ContinuousIntegrationServer('url', [ProjectBuilder(
        {'name': project_name, 'lastBuildStatus': 'Success', 'activity': 'Sleeping', 'url': 'someurl',
         'lastBuildLabel': '1', 'lastBuildTime': '2009-05-29T13:54:07'}).build()])])
    new = OverallIntegrationStatus([ContinuousIntegrationServer('url', [ProjectBuilder(
        {'name': project_name, 'lastBuildStatus': 'Failure', 'activity': 'Sleeping', 'url': 'someurl',
         'lastBuildLabel': '2', 'lastBuildTime': '2009-05-29T13:54:07'}).build()])])
    config = ConfigBuilder({'notifications/custom_script': script,
                            'notifications/custom_script_enabled': True}).build()
    return ProjectStatusNotification(config, old, new, _SilentNotification())


def test_should_pass_status_and_projects_as_env_vars(mocker):
    popen = mocker.patch('buildnotifylib.project_status_notification.subprocess.Popen')

    _broken_build_notification('my-hook', 'proj1').show_notifications()

    env = popen.call_args.kwargs['env']
    assert env['BUILDNOTIFY_STATUS'] == 'Broken builds'
    assert env['BUILDNOTIFY_PROJECTS'] == 'proj1'
    assert env['PATH'] == os.environ['PATH']


def test_should_quote_legacy_placeholders(mocker):
    popen = mocker.patch('buildnotifylib.project_status_notification.subprocess.Popen')

    _broken_build_notification('my-hook #status# #projects#', "it's; rm -rf ~").show_notifications()

    assert popen.call_args.args[0] == "my-hook 'Broken builds' 'it'\"'\"'s; rm -rf ~'"


@pytest.mark.parametrize('payload', ['$(touch {m})', '`touch {m}`', 'x; touch {m}', "x'; touch {m}; '"])
def test_should_not_execute_malicious_project_name(mocker, tmp_path, payload):
    marker = tmp_path / 'injected'
    output = tmp_path / 'output'
    name = payload.format(m=marker)
    processes = []
    real_popen = subprocess.Popen
    mocker.patch('buildnotifylib.project_status_notification.subprocess.Popen',
                 side_effect=lambda *a, **kw: processes.append(real_popen(*a, **kw)))

    script = 'printf %s #projects# > {out}; printf %s "$BUILDNOTIFY_PROJECTS" >> {out}'.format(out=output)
    _broken_build_notification(script, name).show_notifications()
    for process in processes:
        process.wait(timeout=10)

    assert not marker.exists()
    assert output.read_text() == name + name


@pytest.mark.parametrize('template', ['"#projects#"', "'#projects#'", '"Broken: #projects#"', "'Broken: #projects#'"])
@pytest.mark.parametrize('payload', ['$(touch {m})', '`touch {m}`', 'x"; touch {m}; "', "x'; touch {m}; '"])
def test_should_not_execute_malicious_project_name_in_quoted_placeholder(mocker, tmp_path, template, payload):
    marker = tmp_path / 'injected'
    output = tmp_path / 'output'
    name = payload.format(m=marker)
    processes = []
    real_popen = subprocess.Popen
    mocker.patch('buildnotifylib.project_status_notification.subprocess.Popen',
                 side_effect=lambda *a, **kw: processes.append(real_popen(*a, **kw)))

    _broken_build_notification('printf %s {t} > {out}'.format(t=template, out=output), name).show_notifications()
    for process in processes:
        process.wait(timeout=10)

    assert not marker.exists()
    assert output.read_text() == template.strip('"\'').replace('#projects#', name)


def test_should_leave_escaped_placeholder_alone():
    assert substitute_placeholders('echo \\#projects# "\\"#projects#"', {'#projects#': 'a b'}) == \
        'echo \\#projects# "\\""\'a b\'""'


if __name__ == '__main__':
    unittest.main()


def test_should_back_off_repeated_connectivity_notifications():
    timed_filter = TimedProjectFilter()

    shown = [timed_filter.filter(['url']) == ['url'] for _ in range(8)]

    assert shown == [True, True, True, False, True, False, False, True]


def test_should_not_share_back_off_state_between_filters():
    TimedProjectFilter().filter(['url'])

    assert TimedProjectFilter().map == {}


def test_should_reset_back_off_when_server_recovers():
    timed_filter = TimedProjectFilter()
    for _ in range(3):
        timed_filter.filter(['url'])

    timed_filter.filter([])

    assert timed_filter.filter(['url']) == ['url']


def _unavailable_status():
    return OverallIntegrationStatus([ContinuousIntegrationServer('url', [], True)])


def test_should_keep_back_off_across_polls(mocker):
    app_notification = AppNotification(ConfigBuilder().build(), None)
    show = mocker.patch.object(app_notification.notification, 'show_message')

    for _ in range(5):
        app_notification.update_projects(_unavailable_status())

    assert show.call_count == 3
