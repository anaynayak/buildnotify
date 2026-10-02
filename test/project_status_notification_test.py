import os
import subprocess
import unittest

import pytest

from buildnotifylib.app_notification import AppNotification
from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.model import ServerSnapshot
from buildnotifylib.project_status_notification import (
    ProjectStatusNotification,
    substitute_placeholders,
)
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

    notification = ProjectStatusNotification(ConfigBuilder().build(), old, new, NotificationFake())
    notification.show_notifications()

    m.assert_any_call("Broken builds", "proj1")
    m.assert_any_call("Fixed builds", "Successbuild")


class _SilentNotification:
    def show_message(self, title, message):
        pass


def _broken_build_notification(script, project_name):
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
    config = ConfigBuilder({"notifications/custom_script": script, "notifications/custom_script_enabled": True}).build()
    return ProjectStatusNotification(config, old, new, _SilentNotification())


def test_should_pass_status_and_projects_as_env_vars(mocker):
    popen = mocker.patch("buildnotifylib.project_status_notification.subprocess.Popen")

    _broken_build_notification("my-hook", "proj1").show_notifications()

    env = popen.call_args.kwargs["env"]
    assert env["BUILDNOTIFY_STATUS"] == "Broken builds"
    assert env["BUILDNOTIFY_PROJECTS"] == "proj1"
    assert env["PATH"] == os.environ["PATH"]


def test_should_quote_legacy_placeholders(mocker):
    popen = mocker.patch("buildnotifylib.project_status_notification.subprocess.Popen")

    _broken_build_notification("my-hook #status# #projects#", "it's; rm -rf ~").show_notifications()

    assert popen.call_args.args[0] == "my-hook 'Broken builds' 'it'\"'\"'s; rm -rf ~'"


@pytest.mark.parametrize("payload", ["$(touch {m})", "`touch {m}`", "x; touch {m}", "x'; touch {m}; '"])
def test_should_not_execute_malicious_project_name(mocker, tmp_path, payload):
    marker = tmp_path / "injected"
    output = tmp_path / "output"
    name = payload.format(m=marker)
    processes = []
    real_popen = subprocess.Popen
    mocker.patch(
        "buildnotifylib.project_status_notification.subprocess.Popen",
        side_effect=lambda *a, **kw: processes.append(real_popen(*a, **kw)),
    )

    script = f'printf %s #projects# > {output}; printf %s "$BUILDNOTIFY_PROJECTS" >> {output}'
    _broken_build_notification(script, name).show_notifications()
    for process in processes:
        process.wait(timeout=10)

    assert not marker.exists()
    assert output.read_text() == name + name


@pytest.mark.parametrize("template", ['"#projects#"', "'#projects#'", '"Broken: #projects#"', "'Broken: #projects#'"])
@pytest.mark.parametrize("payload", ["$(touch {m})", "`touch {m}`", 'x"; touch {m}; "', "x'; touch {m}; '"])
def test_should_not_execute_malicious_project_name_in_quoted_placeholder(mocker, tmp_path, template, payload):
    marker = tmp_path / "injected"
    output = tmp_path / "output"
    name = payload.format(m=marker)
    processes = []
    real_popen = subprocess.Popen
    mocker.patch(
        "buildnotifylib.project_status_notification.subprocess.Popen",
        side_effect=lambda *a, **kw: processes.append(real_popen(*a, **kw)),
    )

    _broken_build_notification(f"printf %s {template} > {output}", name).show_notifications()
    for process in processes:
        process.wait(timeout=10)

    assert not marker.exists()
    assert output.read_text() == template.strip("\"'").replace("#projects#", name)


def test_should_leave_escaped_placeholder_alone():
    assert (
        substitute_placeholders('echo \\#projects# "\\"#projects#"', {"#projects#": "a b"})
        == 'echo \\#projects# "\\""\'a b\'""'
    )


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
