import os
import subprocess
import sys

import pytest

from buildnotifylib.adapters.hooks import ShellScriptHook, substitute_placeholders

POPEN = "buildnotifylib.adapters.hooks.subprocess.Popen"
posix_shell = pytest.mark.skipif(sys.platform == "win32", reason="runs printf in a POSIX shell")


def run_and_wait(mocker, script, status, projects):
    processes = []
    real_popen = subprocess.Popen
    mocker.patch(POPEN, side_effect=lambda *a, **kw: processes.append(real_popen(*a, **kw)))
    ShellScriptHook().run(script, status, projects)
    for process in processes:
        process.wait(timeout=10)


def test_should_pass_status_and_projects_as_env_vars(mocker):
    popen = mocker.patch(POPEN)

    ShellScriptHook().run("my-hook", "Broken builds", "proj1")

    env = popen.call_args.kwargs["env"]
    assert env["BUILDNOTIFY_STATUS"] == "Broken builds"
    assert env["BUILDNOTIFY_PROJECTS"] == "proj1"
    assert env["PATH"] == os.environ["PATH"]
    assert popen.call_args.kwargs["shell"] is True


def test_should_quote_legacy_placeholders(mocker):
    popen = mocker.patch(POPEN)

    ShellScriptHook().run("my-hook #status# #projects#", "Broken builds", "it's; rm -rf ~")

    assert popen.call_args.args[0] == "my-hook 'Broken builds' 'it'\"'\"'s; rm -rf ~'"


@posix_shell
@pytest.mark.parametrize("payload", ["$(touch {m})", "`touch {m}`", "x; touch {m}", "x'; touch {m}; '"])
def test_should_not_execute_malicious_project_name(mocker, tmp_path, payload):
    marker = tmp_path / "injected"
    output = tmp_path / "output"
    name = payload.format(m=marker)

    script = f'printf %s #projects# > {output}; printf %s "$BUILDNOTIFY_PROJECTS" >> {output}'
    run_and_wait(mocker, script, "Broken builds", name)

    assert not marker.exists()
    assert output.read_text() == name + name


@posix_shell
@pytest.mark.parametrize("template", ['"#projects#"', "'#projects#'", '"Broken: #projects#"', "'Broken: #projects#'"])
@pytest.mark.parametrize("payload", ["$(touch {m})", "`touch {m}`", 'x"; touch {m}; "', "x'; touch {m}; '"])
def test_should_not_execute_malicious_project_name_in_quoted_placeholder(mocker, tmp_path, template, payload):
    marker = tmp_path / "injected"
    output = tmp_path / "output"
    name = payload.format(m=marker)

    run_and_wait(mocker, f"printf %s {template} > {output}", "Broken builds", name)

    assert not marker.exists()
    assert output.read_text() == template.strip("\"'").replace("#projects#", name)


def test_should_leave_escaped_placeholder_alone():
    assert (
        substitute_placeholders('echo \\#projects# "\\"#projects#"', {"#projects#": "a b"})
        == 'echo \\#projects# "\\""\'a b\'""'
    )
