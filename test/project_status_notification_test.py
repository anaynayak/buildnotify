from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.model import ServerSnapshot
from buildnotifylib.ui.app_notification import AppNotification
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

    app_notification = AppNotification(ConfigBuilder().build(), None, RecordingHook())
    m = mocker.patch.object(app_notification.notification, "show_message")

    app_notification.update_projects(old)
    app_notification.update_projects(new)

    m.assert_any_call("Broken builds", "proj1")
    m.assert_any_call("Fixed builds", "Successbuild")


def _notify_broken_build(mocker, script, project_name, hook, enabled=True):
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
    store = ConfigBuilder(custom_script=script, custom_script_enabled=enabled).build()
    app_notification = AppNotification(store, None, hook)
    mocker.patch.object(app_notification.notification, "show_message")
    app_notification.update_projects(old)
    app_notification.update_projects(new)


class RecordingHook:
    def __init__(self):
        self.calls = []

    def run(self, script, status, projects):
        self.calls.append((script, status, projects))


def test_should_run_custom_script_hook_with_status_and_projects(mocker):
    hook = RecordingHook()

    _notify_broken_build(mocker, "my-hook #status#", "proj1", hook)

    assert hook.calls == [("my-hook #status#", "Broken builds", "proj1")]


def test_should_not_run_hook_when_custom_script_is_disabled(mocker):
    hook = RecordingHook()

    _notify_broken_build(mocker, "my-hook", "proj1", hook, enabled=False)

    assert hook.calls == []


def _unavailable_status():
    return OverallIntegrationStatus([ServerSnapshot("url", error=OSError("down"))])


def test_should_keep_back_off_across_polls(mocker):
    app_notification = AppNotification(ConfigBuilder().build(), None, RecordingHook())
    show = mocker.patch.object(app_notification.notification, "show_message")

    for _ in range(5):
        app_notification.update_projects(_unavailable_status())

    assert show.call_count == 3


def test_should_run_the_injected_hook_from_the_app_notification(mocker):
    hook = RecordingHook()
    store = ConfigBuilder(custom_script="my-hook", custom_script_enabled=True).build()
    app_notification = AppNotification(store, None, hook)
    mocker.patch.object(app_notification.notification, "show_message")

    app_notification.update_projects(_unavailable_status())
    app_notification.update_projects(_unavailable_status())

    assert hook.calls == [("my-hook", "Connectivity issues", "url")]
