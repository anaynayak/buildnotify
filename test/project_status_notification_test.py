import unittest
from dataclasses import replace

from buildnotifylib.app_notification import AppNotification
from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.model import ServerSnapshot
from buildnotifylib.project_status_notification import ProjectStatusNotification
from test.fake_conf import ConfigBuilder
from test.project_builder import ProjectBuilder


def test_should_return_notifications(mocker):
    old_projects = [
        ProjectBuilder(
            {
                "name": "proj1",
                "lastBuildStatus": "Success",
                "activity": "Sleeping",
                "url": "someurl",
                "lastBuildLabel": "1",
                "lastBuildTime": "2009-05-29T13:54:07",
            }
        ).build(),
        ProjectBuilder(
            {
                "name": "Successbuild",
                "lastBuildStatus": "Failure",
                "activity": "Sleeping",
                "url": "someurl",
                "lastBuildLabel": "10",
                "lastBuildTime": "2009-05-29T13:54:37",
            }
        ).build(),
    ]
    new_projects = [
        ProjectBuilder(
            {
                "name": "proj1",
                "lastBuildStatus": "Failure",
                "activity": "Sleeping",
                "url": "someurl",
                "lastBuildLabel": "2",
                "lastBuildTime": "2009-05-29T13:54:07",
            }
        ).build(),
        ProjectBuilder(
            {
                "name": "Successbuild",
                "lastBuildStatus": "Success",
                "activity": "Sleeping",
                "url": "someurl",
                "lastBuildLabel": "11",
                "lastBuildTime": "2009-05-29T13:54:47",
            }
        ).build(),
    ]
    old = OverallIntegrationStatus([ServerSnapshot("url", tuple(old_projects))])
    new = OverallIntegrationStatus([ServerSnapshot("url", tuple(new_projects))])

    class NotificationFake:
        def __init__(self):
            pass

        def show_message(self, **kwargs):
            print(kwargs)

    m = mocker.patch.object(NotificationFake, "show_message")

    notification = ProjectStatusNotification(ConfigBuilder().build().settings, old, new, NotificationFake())
    notification.show_notifications()

    m.assert_any_call("Broken builds", "proj1")
    m.assert_any_call("Fixed builds", "Successbuild")


class _SilentNotification:
    def show_message(self, title, message):
        pass


def _broken_build_notification(script, project_name, hook):
    old = OverallIntegrationStatus(
        [
            ServerSnapshot(
                "url",
                (
                    ProjectBuilder(
                        {
                            "name": project_name,
                            "lastBuildStatus": "Success",
                            "activity": "Sleeping",
                            "url": "someurl",
                            "lastBuildLabel": "1",
                            "lastBuildTime": "2009-05-29T13:54:07",
                        }
                    ).build(),
                ),
            )
        ]
    )
    new = OverallIntegrationStatus(
        [
            ServerSnapshot(
                "url",
                (
                    ProjectBuilder(
                        {
                            "name": project_name,
                            "lastBuildStatus": "Failure",
                            "activity": "Sleeping",
                            "url": "someurl",
                            "lastBuildLabel": "2",
                            "lastBuildTime": "2009-05-29T13:54:07",
                        }
                    ).build(),
                ),
            )
        ]
    )
    config = ConfigBuilder(custom_script=script, custom_script_enabled=True).build()
    return ProjectStatusNotification(config.settings, old, new, _SilentNotification(), hook=hook)


class RecordingHook:
    def __init__(self):
        self.calls = []

    def run(self, script, status, projects):
        self.calls.append((script, status, projects))


def test_should_run_custom_script_hook_with_status_and_projects():
    hook = RecordingHook()

    _broken_build_notification("my-hook #status#", "proj1", hook).show_notifications()

    assert hook.calls == [("my-hook #status#", "Broken builds", "proj1")]


def test_should_not_run_hook_when_custom_script_is_disabled():
    hook = RecordingHook()
    notification = _broken_build_notification("my-hook", "proj1", hook)
    notification.settings = replace(notification.settings, custom_script_enabled=False)

    notification.show_notifications()

    assert hook.calls == []


if __name__ == "__main__":
    unittest.main()


def _unavailable_status():
    return OverallIntegrationStatus([ServerSnapshot("url", error=OSError("down"))])


def test_should_keep_back_off_across_polls(mocker):
    app_notification = AppNotification(ConfigBuilder().build(), None)
    show = mocker.patch.object(app_notification.notification, "show_message")

    for _ in range(5):
        app_notification.update_projects(_unavailable_status())

    assert show.call_count == 3
