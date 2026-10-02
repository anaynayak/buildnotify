import tempfile
import urllib.request
from pathlib import Path

from PySide6.QtCore import QSettings

from scripts import demo


def test_demo_settings_live_under_the_temp_directory():
    with tempfile.TemporaryDirectory(prefix="buildnotify-demo-") as tmp:
        path = demo.write_settings(Path(tmp), demo.demo_settings(8000, 8001))

        assert path.resolve().is_relative_to(Path(tempfile.gettempdir()).resolve())
        assert path.is_file()


def test_demo_settings_point_at_the_local_feeds_and_a_dead_port():
    with tempfile.TemporaryDirectory() as tmp:
        path = demo.write_settings(Path(tmp), demo.demo_settings(8000, 8001))
        qsettings = QSettings(str(path), QSettings.Format.IniFormat)

        urls = [qsettings.value(f"servers/{index}/url") for index in range(1, 4)]

    assert urls == [
        "http://127.0.0.1:8000/jenkins.xml",
        "http://127.0.0.1:8000/gocd.xml",
        "http://127.0.0.1:8001/cctray.xml",
    ]


def test_demo_child_uses_the_null_keyring_and_a_real_display():
    env = demo.child_env({"QT_QPA_PLATFORM": "offscreen", "HOME": "/home/me"})

    assert env == {"HOME": "/home/me", "PYTHON_KEYRING_BACKEND": "keyring.backends.null.Keyring"}


def test_demo_serves_the_fixture_feeds():
    with demo.serve(demo.FEEDS) as port:
        body = urllib.request.urlopen(f"http://127.0.0.1:{port}/jenkins.xml", timeout=5).read()

    assert b"payments-api" in body
