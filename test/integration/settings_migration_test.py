import shutil
from pathlib import Path

import keyring
import pytest
from PySide6 import QtCore

from buildnotifylib.adapters.credentials import Keystore
from buildnotifylib.adapters.settings_store import SettingsStore, migrate
from buildnotifylib.core.settings import SCHEMA_VERSION, AppSettings, ServerSettings, SortKey, SourceKind

FIXTURES = Path(__file__).parent.parent / "fixtures" / "settings"
LEGACY_GROUPS = ("excludes", "timezone", "username", "skip_ssl_verification", "authorization_type", "display_prefix")

V21_SETTINGS = AppSettings(
    servers=[
        ServerSettings(
            "https://ci.example.com/go/cctray.xml", ["deploy-prod"], "US/Eastern", "go", "alice", "s3cret", True
        ),
        ServerSettings(
            "http://jenkins.local:8080/cc.xml",
            ["nightly", "flaky :: tests"],
            password="tok",
            authentication_type=ServerSettings.AUTH_BEARER_TOKEN,
        ),
        ServerSettings("http://jenkins.local:8080", prefix="root"),
    ],
    interval_seconds=300,
    timeout_seconds=10,
    custom_script="notify-send #status#",
    custom_script_enabled=True,
    sort_key=SortKey.NAME,
    notifications={
        "successfulBuild": True,
        "brokenBuild": True,
        "fixedBuild": False,
        "stillFailingBuild": True,
        "connectivityIssues": False,
        "lastBuildTimeForProject": True,
    },
)

SINGLE_SERVER_SETTINGS = AppSettings(
    servers=[
        ServerSettings(
            "https://gitlab.example.com/group/app/-/cctray.xml",
            ["pages"],
            "Europe/Berlin",
            "app",
            "bob@example.com",
            "hunter2",
            True,
        )
    ],
    interval_seconds=45,
    timeout_seconds=20,
    show_last_build_label=True,
    notifications={"successfulBuild": True},
)


class FailingSettings(QtCore.QSettings):
    def __init__(self, path, failing_key):
        super().__init__(path, QtCore.QSettings.Format.IniFormat)
        self.failing_key = failing_key

    def setValue(self, key, value):
        if key == self.failing_key:
            raise OSError("disk full")
        super().setValue(key, value)


@pytest.fixture
def v21(tmp_path, in_memory_keyring):
    keyring.set_password("https://ci.example.com/go/cctray.xml", "alice", "s3cret")
    # 3.0 and earlier stored tokens under an empty username; keyring warns when one is written.
    in_memory_keyring.passwords[("http://jenkins.local:8080/cc.xml", "")] = "tok"
    return str(shutil.copy(FIXTURES / "buildnotify-2.1.conf", tmp_path / "BuildNotify.conf"))


@pytest.fixture
def single_server(tmp_path):
    keyring.set_password("https://gitlab.example.com/group/app/-/cctray.xml", "bob@example.com", "hunter2")
    return str(shutil.copy(FIXTURES / "single-server-2.x.conf", tmp_path / "BuildNotify.conf"))


def open_ini(path) -> QtCore.QSettings:
    return QtCore.QSettings(path, QtCore.QSettings.Format.IniFormat)


def legacy_keys(qsettings: QtCore.QSettings) -> list[str]:
    return [key for key in qsettings.allKeys() if key.split("/")[0] in LEGACY_GROUPS or key == "connection/urls"]


def test_should_migrate_every_2_1_value(v21):
    assert SettingsStore(open_ini(v21), Keystore()).settings == V21_SETTINGS


def test_should_migrate_one_item_lists_and_bool_strings(single_server):
    assert SettingsStore(open_ini(single_server), Keystore()).settings == SINGLE_SERVER_SETTINGS


@pytest.mark.parametrize("fixture, expected", [("v21", V21_SETTINGS), ("single_server", SINGLE_SERVER_SETTINGS)])
def test_should_round_trip_migrated_settings(request, fixture, expected):
    path = request.getfixturevalue(fixture)
    SettingsStore(open_ini(path), Keystore()).save(SettingsStore(open_ini(path), Keystore()).settings)

    assert SettingsStore(open_ini(path), Keystore()).settings == expected


def test_should_replace_the_2x_layout(v21):
    SettingsStore(open_ini(v21), Keystore())

    qsettings = open_ini(v21)
    assert legacy_keys(qsettings) == []
    assert int(qsettings.value("schema_version")) == SCHEMA_VERSION
    assert int(qsettings.value("servers/size")) == 3


def test_should_be_idempotent(v21):
    migrate(open_ini(v21))
    migrated = Path(v21).read_text()

    migrate(open_ini(v21))

    assert Path(v21).read_text() == migrated
    assert SettingsStore(open_ini(v21), Keystore()).settings == V21_SETTINGS


@pytest.mark.parametrize("failing_key", ["url", "schema_version"])
def test_should_keep_the_2x_keys_until_the_new_ones_are_written(v21, failing_key):
    before = legacy_keys(open_ini(v21))

    with pytest.raises(OSError):
        migrate(FailingSettings(v21, failing_key))

    assert legacy_keys(open_ini(v21)) == before
    assert SettingsStore(open_ini(v21), Keystore()).settings == V21_SETTINGS


def test_should_leave_current_settings_alone(tmp_path):
    path = str(tmp_path / "settings.ini")
    SettingsStore(open_ini(path), Keystore()).save(V21_SETTINGS)
    saved = Path(path).read_text()

    migrate(open_ini(path))

    assert Path(path).read_text() == saved


@pytest.fixture
def v30(tmp_path):
    keyring.set_password("https://ci.example.com/go/cctray.xml", "alice", "s3cret")
    return str(shutil.copy(FIXTURES / "buildnotify-3.0.conf", tmp_path / "BuildNotify.conf"))


def test_should_keep_3_0_servers_as_cctray_feeds(v30):
    servers = SettingsStore(open_ini(v30), Keystore()).settings.servers

    assert [(s.url, s.kind) for s in servers] == [
        ("https://ci.example.com/go/cctray.xml", SourceKind.CCTRAY),
        ("http://jenkins.local:8080/cc.xml", SourceKind.CCTRAY),
    ]
    url = "https://ci.example.com/go/cctray.xml"
    assert servers[0] == ServerSettings(url, ["deploy-prod"], "US/Eastern", "go", "alice", "s3cret")


def test_should_write_the_kind_of_each_3_0_server(v30):
    migrate(open_ini(v30))

    qsettings = open_ini(v30)
    assert int(qsettings.value("schema_version")) == SCHEMA_VERSION
    assert [qsettings.value(f"servers/{i}/kind") for i in (1, 2)] == ["cctray", "cctray"]
    assert int(qsettings.value("servers/size")) == 2


def test_should_write_unmuted_3_0_servers(v30):
    migrate(open_ini(v30))

    qsettings = open_ini(v30)
    assert [str(qsettings.value(f"servers/{i}/muted")).lower() for i in (1, 2)] == ["false", "false"]


@pytest.fixture
def v4(tmp_path):
    return str(shutil.copy(FIXTURES / "buildnotify-4.conf", tmp_path / "BuildNotify.conf"))


def test_should_unmute_every_server_from_before_mutes(v4):
    migrate(open_ini(v4))

    qsettings = open_ini(v4)
    assert int(qsettings.value("schema_version")) == SCHEMA_VERSION
    assert [str(qsettings.value(f"servers/{i}/muted")).lower() for i in (1, 2)] == ["false", "false"]
    assert [qsettings.value(f"servers/{i}/kind") for i in (1, 2)] == ["cctray", "github"]
    assert int(qsettings.value("servers/size")) == 2


def test_should_load_servers_from_before_mutes_with_nothing_muted(v4):
    settings = SettingsStore(open_ini(v4), Keystore()).settings

    assert [(s.muted, s.muted_projects) for s in settings.servers] == [(False, []), (False, [])]
    assert settings.paused_until is None
