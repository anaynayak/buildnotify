import datetime
import unittest
from datetime import timedelta

from dateutil.tz import tzlocal

from buildnotifylib.core.project import Project


class ProjectTest(unittest.TestCase):
    def test_should_ignore_empty_last_build_time(self):
        project = Project('i', None, 'None', {
            'lastBuildTime': '',
            'name': 'g',
            'lastBuildStatus': 'n',
            'activity': 'o',
            'url': 'r'})
        self.assertEqual(datetime.datetime.now().date(), project.get_last_build_time().date())
        self.assertEqual(tzlocal(), project.get_last_build_time().tzinfo)

    def test_should_correctly_parse_project(self):
        project = Project('url', None, 'None', {
            'name': 'proj1',
            'lastBuildStatus': 'Success',
            'activity': 'Sleeping',
            'url': '1.2.3.4:8080/cc.xml',
            'lastBuildLabel': '120',
            'lastBuildTime': '2009-05-29T13:54:07'
        })

        self.assertEqual('url', project.server_url)
        self.assertEqual('proj1', project.name)
        self.assertEqual('Success', project.status)
        self.assertEqual('http://1.2.3.4:8080/cc.xml', project.url)
        self.assertEqual('Sleeping', project.activity)
        self.assertEqual('2009-05-29T13:54:07', project.last_build_time)
        self.assertEqual('120', project.last_build_label)
        self.assertEqual(datetime.datetime(2009, 5, 29, 13, 54, 7, 0, tzlocal()), project.get_last_build_time())
        self.assertEqual("Success.Sleeping", project.get_build_status())

    def test_should_not_override_existing_url_scheme(self):
        project = Project('url', '', 'tz', {
            'name': 'proj1',
            'lastBuildStatus': 'Success',
            'activity': 'Sleeping',
            'url': 'https://10.0.0.1/project1',
            'lastBuildLabel': '120',
            'lastBuildTime': '2009-05-29T13:54:07'
        })
        self.assertEqual('https://10.0.0.1/project1', project.url)


class ProjectTimezoneTest(unittest.TestCase):
    @classmethod
    def tzproj(cls, time, timezone='None'):
        return Project('url', None, timezone, {
            'name': 'proj1',
            'lastBuildStatus': 'Success',
            'activity': 'Sleeping',
            'url': 'someurl',
            'lastBuildLabel': '120',
            'lastBuildTime': time
        })

    def test_should_retain_original_tz_offset(self):
        project = ProjectTimezoneTest.tzproj('2015-02-14T13:23:20+05:30')
        build_time = project.get_last_build_time()
        self.assertEqual(datetime.datetime(2015, 2, 14, 13, 23, 20, 0, None),
                          build_time.replace(tzinfo=None))
        self.assertEqual(build_time.utcoffset(), timedelta(hours=5, minutes=30))

    def test_should_consider_other_variants1(self):
        project = ProjectTimezoneTest.tzproj('2015-02-14T13:25:53Z')
        build_time = project.get_last_build_time()
        self.assertEqual(datetime.datetime(2015, 2, 14, 13, 25, 53, 0, None),
                          build_time.replace(tzinfo=None))
        self.assertEqual(build_time.utcoffset(), timedelta(hours=0, minutes=0))

    def test_should_consider_other_variants2(self):
        project = ProjectTimezoneTest.tzproj('2015-02-14T13:27:20.000+0000')
        build_time = project.get_last_build_time()
        self.assertEqual(datetime.datetime(2015, 2, 14, 13, 27, 20, 0, None),
                          build_time.replace(tzinfo=None))
        self.assertEqual(build_time.utcoffset(), timedelta(hours=0, minutes=0))

    def test_should_consider_other_variants3(self):
        project = ProjectTimezoneTest.tzproj('2015-02-14T13:23:20+00:00', 'None')
        build_time = project.get_last_build_time()
        self.assertEqual(datetime.datetime(2015, 2, 14, 13, 23, 20, 0, None),
                          build_time.replace(tzinfo=None))
        self.assertEqual(build_time.utcoffset(), timedelta(hours=0, minutes=0))

    def test_should_take_local_timezone_if_unspecified(self):
        project = ProjectTimezoneTest.tzproj('2015-02-14T13:23:20', 'None')
        build_time = project.get_last_build_time()
        self.assertEqual(datetime.datetime(2015, 2, 14, 13, 23, 20, 0, None),
                          build_time.replace(tzinfo=None))
        self.assertEqual(build_time.tzinfo, tzlocal())

    def test_should_override_timezone(self):
        project = ProjectTimezoneTest.tzproj('2015-02-14T13:23:20+05:30', 'Etc/GMT-5')
        build_time = project.get_last_build_time()
        self.assertEqual(datetime.datetime(2015, 2, 14, 13, 23, 20, 0, None),
                          build_time.replace(tzinfo=None))
        self.assertEqual(build_time.utcoffset(), timedelta(hours=5, minutes=0))


if __name__ == '__main__':
    unittest.main()
