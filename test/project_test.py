import datetime
import unittest
from datetime import timedelta

from buildnotifylib.core.project import Project


class ProjectTest(unittest.TestCase):
    def test_should_ignore_empty_last_build_time(self):
        project = Project(
            "i", None, "None", {"lastBuildTime": "", "name": "g", "lastBuildStatus": "n", "activity": "o", "url": "r"}
        )
        self.assertIsNone(project.get_last_build_time())

    def test_should_correctly_parse_project(self):
        project = Project(
            "url",
            None,
            "None",
            {
                "name": "proj1",
                "lastBuildStatus": "Success",
                "activity": "Sleeping",
                "url": "1.2.3.4:8080/cc.xml",
                "lastBuildLabel": "120",
                "lastBuildTime": "2009-05-29T13:54:07",
            },
        )

        self.assertEqual("url", project.server_url)
        self.assertEqual("proj1", project.name)
        self.assertEqual("Success", project.status)
        self.assertEqual("http://1.2.3.4:8080/cc.xml", project.url)
        self.assertEqual("Sleeping", project.activity)
        self.assertEqual("2009-05-29T13:54:07", project.last_build_time)
        self.assertEqual("120", project.last_build_label)
        self.assertEqual(datetime.datetime(2009, 5, 29, 13, 54, 7).astimezone(), project.get_last_build_time())
        self.assertEqual("Success.Sleeping", project.get_build_status())

    def test_should_report_exception_as_failure_build_status(self):
        project = Project(
            "url",
            None,
            "None",
            {
                "name": "proj1",
                "lastBuildStatus": "Exception",
                "activity": "Building",
                "url": "someurl",
                "lastBuildTime": "",
            },
        )
        self.assertEqual("Exception", project.status)
        self.assertEqual("Failure.Building", project.get_build_status())

    def test_should_display_last_build_label_on_demand(self):
        project = Project(
            "url",
            None,
            "None",
            {
                "name": "proj1",
                "lastBuildStatus": "Success",
                "activity": "Sleeping",
                "url": "1.2.3.4:8080/cc.xml",
                "lastBuildLabel": "master",
                "lastBuildTime": "2009-05-29T13:54:07",
            },
        )

        self.assertEqual("proj1", project.label())
        self.assertEqual("proj1 (master)", project.label(True))

    def test_should_not_override_existing_url_scheme(self):
        project = Project(
            "url",
            "",
            "tz",
            {
                "name": "proj1",
                "lastBuildStatus": "Success",
                "activity": "Sleeping",
                "url": "https://10.0.0.1/project1",
                "lastBuildLabel": "120",
                "lastBuildTime": "2009-05-29T13:54:07",
            },
        )
        self.assertEqual("https://10.0.0.1/project1", project.url)


class ProjectTimezoneTest(unittest.TestCase):
    @classmethod
    def tzproj(cls, time, timezone="None"):
        return Project(
            "url",
            None,
            timezone,
            {
                "name": "proj1",
                "lastBuildStatus": "Success",
                "activity": "Sleeping",
                "url": "someurl",
                "lastBuildLabel": "120",
                "lastBuildTime": time,
            },
        )

    def test_should_retain_original_tz_offset(self):
        project = ProjectTimezoneTest.tzproj("2015-02-14T13:23:20+05:30")
        build_time = project.get_last_build_time()
        self.assertEqual(datetime.datetime(2015, 2, 14, 13, 23, 20, 0, None), build_time.replace(tzinfo=None))
        self.assertEqual(build_time.utcoffset(), timedelta(hours=5, minutes=30))

    def test_should_consider_other_variants1(self):
        project = ProjectTimezoneTest.tzproj("2015-02-14T13:25:53Z")
        build_time = project.get_last_build_time()
        self.assertEqual(datetime.datetime(2015, 2, 14, 13, 25, 53, 0, None), build_time.replace(tzinfo=None))
        self.assertEqual(build_time.utcoffset(), timedelta(hours=0, minutes=0))

    def test_should_consider_other_variants2(self):
        project = ProjectTimezoneTest.tzproj("2015-02-14T13:27:20.000+0000")
        build_time = project.get_last_build_time()
        self.assertEqual(datetime.datetime(2015, 2, 14, 13, 27, 20, 0, None), build_time.replace(tzinfo=None))
        self.assertEqual(build_time.utcoffset(), timedelta(hours=0, minutes=0))

    def test_should_consider_other_variants3(self):
        project = ProjectTimezoneTest.tzproj("2015-02-14T13:23:20+00:00", "None")
        build_time = project.get_last_build_time()
        self.assertEqual(datetime.datetime(2015, 2, 14, 13, 23, 20, 0, None), build_time.replace(tzinfo=None))
        self.assertEqual(build_time.utcoffset(), timedelta(hours=0, minutes=0))

    def test_should_take_local_timezone_if_unspecified(self):
        project = ProjectTimezoneTest.tzproj("2015-02-14T13:23:20", "None")
        build_time = project.get_last_build_time()
        self.assertEqual(datetime.datetime(2015, 2, 14, 13, 23, 20, 0, None), build_time.replace(tzinfo=None))
        self.assertEqual(build_time, datetime.datetime(2015, 2, 14, 13, 23, 20).astimezone())

    def test_should_keep_explicit_offset_when_server_timezone_is_set(self):
        project = ProjectTimezoneTest.tzproj("2015-02-14T13:23:20+05:30", "Etc/GMT-5")
        build_time = project.get_last_build_time()
        self.assertEqual(datetime.datetime(2015, 2, 14, 13, 23, 20, 0, None), build_time.replace(tzinfo=None))
        self.assertEqual(build_time.utcoffset(), timedelta(hours=5, minutes=30))

    def test_should_keep_z_suffix_when_server_timezone_is_set(self):
        project = ProjectTimezoneTest.tzproj("2015-02-14T13:25:53Z", "Asia/Kolkata")
        self.assertEqual(project.get_last_build_time().utcoffset(), timedelta(0))

    def test_should_apply_server_timezone_to_naive_time(self):
        project = ProjectTimezoneTest.tzproj("2015-02-14T13:23:20", "Asia/Kolkata")
        build_time = project.get_last_build_time()
        self.assertEqual(datetime.datetime(2015, 2, 14, 13, 23, 20, 0, None), build_time.replace(tzinfo=None))
        self.assertEqual(build_time.utcoffset(), timedelta(hours=5, minutes=30))

    def test_should_apply_dst_aware_server_timezone(self):
        project = ProjectTimezoneTest.tzproj("2015-07-14T13:23:20", "America/New_York")
        self.assertEqual(project.get_last_build_time().utcoffset(), timedelta(hours=-4))

    def test_should_return_none_for_garbage_time(self):
        project = ProjectTimezoneTest.tzproj("not a date", "Asia/Kolkata")
        self.assertIsNone(project.get_last_build_time())

    def test_should_fall_back_to_local_time_for_unknown_timezone(self):
        project = ProjectTimezoneTest.tzproj("2015-02-14T13:23:20", "EDT")
        build_time = project.get_last_build_time()
        self.assertEqual(datetime.datetime(2015, 2, 14, 13, 23, 20).astimezone(), build_time)


def build(label, build_time):
    return Project(
        "url",
        None,
        "None",
        {
            "name": "proj1",
            "lastBuildStatus": "Success",
            "activity": "Sleeping",
            "url": "u",
            "lastBuildLabel": label,
            "lastBuildTime": build_time,
        },
    )


class DifferentBuildsTest(unittest.TestCase):
    def test_should_treat_same_label_and_time_as_same_build(self):
        self.assertFalse(build("1", "2009-05-29T13:54:07").different_builds(build("1", "2009-05-29T13:54:07")))

    def test_should_detect_new_label(self):
        self.assertTrue(build("2", "2009-05-29T13:54:07").different_builds(build("1", "2009-05-29T13:54:07")))

    def test_should_detect_new_build_time_with_same_label(self):
        self.assertTrue(build("", "2009-05-29T14:00:00").different_builds(build("", "2009-05-29T13:54:07")))


if __name__ == "__main__":
    unittest.main()
