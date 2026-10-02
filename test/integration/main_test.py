import logging
import subprocess
import sys
import tomllib
from pathlib import Path

from PySide6.QtCore import QSettings

from buildnotifylib import __main__ as entry
from buildnotifylib.adapters.credentials import Keystore
from buildnotifylib.adapters.hooks import ShellScriptHook
from buildnotifylib.adapters.http import HttpConnection

PYPROJECT = Path(__file__).parents[2] / "pyproject.toml"


def fake_run(mocker, exit_code=0, workers_done=True):
    calls = mocker.MagicMock()
    calls.app.exec.return_value = exit_code
    calls.wait_for_workers.return_value = workers_done
    application = mocker.patch("buildnotifylib.__main__.QApplication", return_value=calls.app)
    buildnotify = mocker.MagicMock(wait_for_workers=calls.wait_for_workers)
    build = mocker.patch("buildnotifylib.__main__.build", return_value=buildnotify)
    mocker.patch("buildnotifylib.__main__.logging.basicConfig")
    return calls, application, build


def test_should_wait_for_workers_after_the_event_loop_ends(mocker):
    calls, _, _ = fake_run(mocker, exit_code=3)
    sys_exit = mocker.patch("sys.exit")

    entry.main(["buildnotify"])

    assert calls.mock_calls[-2:] == [mocker.call.app.exec(), mocker.call.wait_for_workers()]
    sys_exit.assert_called_once_with(3)


def test_should_exit_without_cleanup_when_a_fetch_is_stuck(mocker):
    fake_run(mocker, workers_done=False)
    hard_exit = mocker.patch("os._exit")
    sys_exit = mocker.patch("sys.exit")

    entry.main(["buildnotify"])

    hard_exit.assert_called_once_with(0)
    sys_exit.assert_not_called()


def test_should_build_the_app_from_the_application(mocker):
    calls, application, build = fake_run(mocker)
    mocker.patch("sys.exit")

    entry.main(["buildnotify"])

    calls.app.setQuitOnLastWindowClosed.assert_called_once_with(False)
    build.assert_called_once_with(calls.app, None)


def test_should_pass_the_settings_path_to_build(mocker, tmp_path):
    calls, application, build = fake_run(mocker)
    mocker.patch("sys.exit")
    path = str(tmp_path / "settings.ini")

    entry.main(["buildnotify", "--settings", path, "-style", "fusion"])

    build.assert_called_once_with(calls.app, path)
    application.assert_called_once_with(["buildnotify", "-style", "fusion"])


def test_should_log_warnings_by_default(mocker):
    fake_run(mocker)
    mocker.patch("sys.exit")

    entry.main(["buildnotify"])

    assert entry.logging.basicConfig.call_args.kwargs["level"] == logging.WARNING


def test_should_log_debug_with_the_debug_flag(mocker):
    _, application, _ = fake_run(mocker)
    mocker.patch("sys.exit")

    entry.main(["buildnotify", "--debug"])

    assert entry.logging.basicConfig.call_args.kwargs["level"] == logging.DEBUG
    application.assert_called_once_with(["buildnotify"])


def test_should_hand_unknown_arguments_to_qt(mocker):
    _, application, _ = fake_run(mocker)
    mocker.patch("sys.exit")

    entry.main(["buildnotify", "-style", "fusion", "--debug"])

    application.assert_called_once_with(["buildnotify", "-style", "fusion"])


def test_should_inject_the_real_adapters(qapp, qsettings, mocker):
    mocker.patch("buildnotifylib.__main__.QSettings", return_value=qsettings)

    buildnotify = entry.build(qapp)
    buildnotify.tray_timer.stop()

    assert buildnotify.store.qsettings is qsettings
    assert isinstance(buildnotify.store.keystore, Keystore)
    assert isinstance(buildnotify.connection, HttpConnection)
    assert isinstance(buildnotify.hook, ShellScriptHook)


def test_should_open_an_ini_settings_file_when_given_a_path(qapp, tmp_path):
    path = str(tmp_path / "settings.ini")

    buildnotify = entry.build(qapp, path)
    buildnotify.tray_timer.stop()

    assert Path(buildnotify.store.qsettings.fileName()) == Path(path)
    assert buildnotify.store.qsettings.format() == QSettings.Format.IniFormat


def test_should_run_as_a_module():
    result = subprocess.run(
        [sys.executable, "-m", "buildnotifylib", "--help"], capture_output=True, text=True, check=True
    )
    assert "--debug" in result.stdout
    assert "--settings" in result.stdout


def test_should_point_the_gui_script_at_main():
    scripts = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]["gui-scripts"]
    assert scripts == {"buildnotify": "buildnotifylib.__main__:main"}
