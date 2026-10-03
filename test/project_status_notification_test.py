from datetime import UTC, datetime, timedelta

import pytest

from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.model import ServerSnapshot
from buildnotifylib.core.settings import ServerSettings
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
    m = mocker.patch.object(app_notification.notification, "show")

    app_notification.update_projects(old)
    app_notification.update_projects(new)

    assert titles(m) == ["Build fixed: Successbuild", "Build failed: proj1"]


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
    mocker.patch.object(app_notification.notification, "show")
    app_notification.update_projects(old)
    app_notification.update_projects(new)


def titles(show):
    return [call.args[0].title for call in show.call_args_list]


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
    show = mocker.patch.object(app_notification.notification, "show")

    for _ in range(5):
        app_notification.update_projects(_unavailable_status())

    assert show.call_count == 3


def test_should_run_the_injected_hook_from_the_app_notification(mocker):
    hook = RecordingHook()
    store = ConfigBuilder(custom_script="my-hook", custom_script_enabled=True).build()
    app_notification = AppNotification(store, None, hook)
    mocker.patch.object(app_notification.notification, "show")

    app_notification.update_projects(_unavailable_status())
    app_notification.update_projects(_unavailable_status())

    assert hook.calls == [("my-hook", "Connectivity issues", "url")]


CI = "http://ci/cc.xml"
NOW = datetime(2026, 10, 2, 12, 0, tzinfo=UTC)


def _status(status, label, server_url=CI, name="proj1"):
    attrs = {
        "name": name,
        "lastBuildStatus": status,
        "activity": "Sleeping",
        "url": "someurl",
        "lastBuildLabel": label,
        "lastBuildTime": "2009-05-29T13:54:07",
    }
    return ProjectBuilder(attrs).server(server_url).build()


def _break_builds(mocker, store, clock=lambda: NOW, names=("proj1",)):
    hook = RecordingHook()
    app_notification = AppNotification(store, None, hook, clock)
    show = mocker.patch.object(app_notification.notification, "show")
    old = [_status("Success", "1", name=name) for name in names]
    new = [_status("Failure", "2", name=name) for name in names]
    app_notification.update_projects(OverallIntegrationStatus([ServerSnapshot(CI, tuple(old))]))
    app_notification.update_projects(OverallIntegrationStatus([ServerSnapshot(CI, tuple(new))]))
    return show, hook


def _scripted(**fields):
    return ConfigBuilder(custom_script="my-hook", custom_script_enabled=True, **fields)


@pytest.mark.parametrize("server", [ServerSettings(CI, muted=True), ServerSettings(CI, muted_projects=["proj1"])])
def test_should_neither_notify_nor_run_the_script_for_a_muted_project(mocker, server):
    show, hook = _break_builds(mocker, _scripted(servers=[server]).build())

    assert (show.call_count, hook.calls) == (0, [])


def test_should_still_notify_the_projects_that_are_not_muted(mocker):
    store = _scripted(servers=[ServerSettings(CI, muted_projects=["proj1"])]).build()

    show, hook = _break_builds(mocker, store, names=("proj1", "proj2"))

    assert titles(show) == ["Build failed: proj2"]
    assert hook.calls == [("my-hook", "Broken builds", "proj2")]


def test_should_stay_quiet_while_paused(mocker):
    store = _scripted(servers=[ServerSettings(CI)], paused_until=NOW + timedelta(minutes=5)).build()

    show, hook = _break_builds(mocker, store)

    assert (show.call_count, hook.calls) == (0, [])


def test_should_notify_once_the_pause_has_expired(mocker):
    store = _scripted(servers=[ServerSettings(CI)], paused_until=NOW).build()

    show, hook = _break_builds(mocker, store, clock=lambda: NOW + timedelta(seconds=1))

    assert titles(show) == ["Build failed: proj1"]


def test_should_not_report_connectivity_issues_for_a_muted_server(mocker):
    store = _scripted(servers=[ServerSettings(CI, muted=True)]).build()
    hook = RecordingHook()
    app_notification = AppNotification(store, None, hook, lambda: NOW)
    show = mocker.patch.object(app_notification.notification, "show")

    for _ in range(2):
        app_notification.update_projects(OverallIntegrationStatus([ServerSnapshot(CI, error=OSError("down"))]))

    assert (show.call_count, hook.calls) == (0, [])


def _down(url=CI):
    return OverallIntegrationStatus([ServerSnapshot(url, error=OSError("down"))])


def _up(url=CI):
    return OverallIntegrationStatus([ServerSnapshot(url, (_status("Success", "1", server_url=url),))])


def _poll(mocker, store, *statuses):
    hook = RecordingHook()
    app_notification = AppNotification(store, None, hook, lambda: NOW)
    show = mocker.patch.object(app_notification.notification, "show")
    for status in statuses:
        app_notification.update_projects(status)
    return show, hook


def test_should_say_a_server_is_reachable_again_after_a_connectivity_toast(mocker):
    store = _scripted(servers=[ServerSettings(CI, prefix="jenkins")]).build()

    show, hook = _poll(mocker, store, _up(), _down(), _up())

    assert titles(show) == ["Can't reach jenkins", "jenkins is reachable again"]
    assert hook.calls == [("my-hook", "Connectivity issues", CI), ("my-hook", "Connectivity restored", CI)]


def test_should_say_reachable_again_only_once(mocker):
    show, _ = _poll(mocker, ConfigBuilder(servers=[ServerSettings(CI)]).build(), _up(), _down(), _up(), _up())

    assert titles(show) == ["Can't reach ci", "ci is reachable again"]


def test_should_not_say_reachable_again_without_a_connectivity_toast(mocker):
    show, _ = _poll(mocker, ConfigBuilder(servers=[ServerSettings(CI)]).build(), _up(), _up())

    assert show.call_count == 0


def test_should_not_say_reachable_again_when_connectivity_toasts_are_off(mocker):
    store = ConfigBuilder(servers=[ServerSettings(CI)], notifications={"connectivityIssues": False}).build()

    show, _ = _poll(mocker, store, _up(), _down(), _up())

    assert show.call_count == 0


def test_should_not_say_reachable_again_for_a_server_muted_while_it_was_down(mocker):
    store = ConfigBuilder(servers=[ServerSettings(CI)]).build()
    hook = RecordingHook()
    app_notification = AppNotification(store, None, hook, lambda: NOW)
    show = mocker.patch.object(app_notification.notification, "show")
    for status in (_up(), _down()):
        app_notification.update_projects(status)
    store.save(_scripted(servers=[ServerSettings(CI, muted=True)]).settings)

    app_notification.update_projects(_up())

    assert (titles(show), hook.calls) == (["Can't reach ci"], [])


def test_should_not_say_reachable_again_for_a_removed_server(mocker):
    other = "http://other/cc.xml"
    store = ConfigBuilder(servers=[ServerSettings(CI), ServerSettings(other)]).build()

    show, _ = _poll(mocker, store, _up(), _down(), _up(other))

    assert titles(show) == ["Can't reach ci"]


def test_should_warn_about_broken_builds(mocker):
    show, _ = _break_builds(mocker, ConfigBuilder(servers=[ServerSettings(CI)]).build())

    assert [call.args[0].warning for call in show.call_args_list] == [True]


def test_should_use_the_disambiguated_label_in_notifications_and_the_tooltip_summary(mocker):
    other = "http://other/cc.xml"
    store = ConfigBuilder(servers=[ServerSettings(CI), ServerSettings(other)]).build()
    app_notification = AppNotification(store, None, RecordingHook(), lambda: NOW)
    show = mocker.patch.object(app_notification.notification, "show")
    passing = [ServerSnapshot(CI, (_status("Success", "1"),)), ServerSnapshot(other, (_status("Success", "1", other),))]
    failing = [ServerSnapshot(CI, (_status("Failure", "2"),)), ServerSnapshot(other, (_status("Success", "1", other),))]

    app_notification.update_projects(OverallIntegrationStatus(passing))
    app_notification.update_projects(OverallIntegrationStatus(failing))

    assert titles(show) == ["Build failed: [ci] proj1"]
    assert OverallIntegrationStatus(failing).failing_summary() == "1 failing: [ci] proj1"
