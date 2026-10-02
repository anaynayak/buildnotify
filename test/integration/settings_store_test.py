import shutil
import sys
from dataclasses import replace
from datetime import UTC, datetime

import keyring
import pytest
from PySide6 import QtCore

from buildnotifylib.adapters.credentials import Keystore
from buildnotifylib.adapters.settings_store import SettingsStore
from buildnotifylib.core.settings import AppSettings, ServerSettings, SortKey, SourceKind
from test.fake_keyring import InMemoryKeyring


class UntouchableKeyring(InMemoryKeyring):
    def set_password(self, servicename, username, password):
        raise AssertionError("keyring touched")

    def get_password(self, servicename, username):
        raise AssertionError("keyring touched")


@pytest.fixture
def ini(tmp_path):
    return str(tmp_path / "settings.ini")


def reopen(ini) -> SettingsStore:
    return SettingsStore(QtCore.QSettings(ini, QtCore.QSettings.Format.IniFormat), Keystore())


def full_settings() -> AppSettings:
    return AppSettings(
        servers=[
            ServerSettings("https://ci.example.com/go/cctray.xml", ["deploy-prod"], "US/Eastern", "go", "alice", "pw"),
            ServerSettings("http://host:8080", [], "None", "outer", skip_ssl_verification=True, muted=True),
            ServerSettings(
                "http://host:8080/cc.xml",
                ["a", "b :: c"],
                prefix="inner",
                password="token",
                muted_projects=["b :: c"],
                authentication_type=ServerSettings.AUTH_BEARER_TOKEN,
            ),
            ServerSettings(
                "",
                ["CI (main)"],
                prefix="gh",
                password="ghp_token",
                authentication_type=ServerSettings.AUTH_BEARER_TOKEN,
                kind=SourceKind.GITHUB,
                repository="octo-org/hello-world",
                workflow="ci.yml",
                branch="main",
                muted_projects=["CI (main)", "Docs (main)"],
            ),
        ],
        interval_seconds=300,
        timeout_seconds=30,
        custom_script="notify-send #status#",
        custom_script_enabled=True,
        sort_key=SortKey.NAME,
        show_last_build_label=True,
        symbolic_icons=True,
        notifications={"successfulBuild": True, "brokenBuild": False},
        paused_until=datetime(2026, 10, 2, 13, 30, tzinfo=UTC),
    )


def test_should_load_defaults_from_an_empty_file(ini):
    assert reopen(ini).settings == AppSettings()


def test_should_not_write_defaults_on_load(qsettings):
    SettingsStore(qsettings, Keystore())

    assert sorted(qsettings.allKeys()) == ["schema_version", "servers/size"]


def test_should_round_trip_every_value(ini):
    reopen(ini).save(full_settings())

    assert reopen(ini).settings == full_settings()


registry = pytest.mark.skipif(sys.platform == "win32", reason="NativeFormat is the registry on Windows")


@pytest.mark.parametrize(
    "fmt",
    [QtCore.QSettings.Format.IniFormat, pytest.param(QtCore.QSettings.Format.NativeFormat, marks=registry)],
)
def test_should_round_trip_every_value_through_the_file(tmp_path, fmt):
    saved, copy = tmp_path / "saved", tmp_path / "copy"
    SettingsStore(QtCore.QSettings(str(saved), fmt), Keystore()).save(full_settings())
    # A new path skips QSettings' in-process cache, so the values come back parsed from disk.
    shutil.copy(saved, copy)

    assert SettingsStore(QtCore.QSettings(str(copy), fmt), Keystore()).settings == full_settings()


def test_should_keep_the_saved_settings_current(qsettings):
    store = SettingsStore(qsettings, Keystore())

    store.save(full_settings())

    assert store.settings == full_settings()


def test_should_store_servers_as_an_array(qsettings):
    SettingsStore(qsettings, Keystore()).save(full_settings())

    assert qsettings.value("servers/size") == 4
    assert qsettings.value("servers/4/kind") == "github"
    assert qsettings.value("servers/2/url") == "http://host:8080"


def test_should_keep_passwords_out_of_the_settings_file(ini):
    reopen(ini).save(full_settings())

    assert "pw" not in open(ini).read()
    assert keyring.get_password("https://ci.example.com/go/cctray.xml", "alice") == "pw"
    assert keyring.get_password("http://host:8080/cc.xml", "") == "token"
    assert keyring.get_password("https://github.com/octo-org/hello-world", "") == "ghp_token"
    assert "ghp_token" not in open(ini).read()


def test_should_keep_a_server_nested_under_a_removed_one(ini):
    reopen(ini).save(full_settings())
    store = reopen(ini)
    store.save(AppSettings(servers=[s for s in store.settings.servers if s.prefix != "outer"]))

    assert [s.prefix for s in reopen(ini).settings.servers] == ["go", "inner", "gh"]


def test_should_persist_removing_the_last_server(ini):
    reopen(ini).save(full_settings())
    reopen(ini).save(AppSettings())

    assert reopen(ini).settings.servers == []


def test_should_forget_the_password_of_a_removed_server(ini):
    reopen(ini).save(full_settings())

    reopen(ini).save(AppSettings())

    assert keyring.get_password("https://ci.example.com/go/cctray.xml", "alice") is None
    assert keyring.get_password("http://host:8080/cc.xml", "") is None


def test_should_forget_the_password_of_a_renamed_user(ini):
    reopen(ini).save(AppSettings(servers=[ServerSettings("ci", username="alice", password="pw")]))

    reopen(ini).save(AppSettings(servers=[ServerSettings("ci", username="bob", password="pw2")]))

    assert keyring.get_password("http://ci", "alice") is None
    assert keyring.get_password("http://ci", "bob") == "pw2"


def test_should_not_touch_the_keyring_without_credentials(ini):
    keyring.set_keyring(UntouchableKeyring())

    reopen(ini).save(AppSettings(servers=[ServerSettings("ci", prefix="p")]))

    assert reopen(ini).settings.servers[0].password == ""


def test_should_fall_back_to_defaults_for_unreadable_values(qsettings):
    qsettings.setValue("sort_key", "bogus")
    qsettings.setValue("connection/interval_in_seconds", "soon")

    settings = SettingsStore(qsettings, Keystore()).settings

    assert (settings.sort_key, settings.interval_seconds) == (SortKey.LAST_BUILD_TIME, 120)


class DictKeystore:
    def __init__(self) -> None:
        self.passwords: dict[tuple[str, str], str] = {}

    def is_available(self):
        return True

    def save(self, url, username, password):
        self.passwords[(url, username)] = password

    def load(self, url, username):
        return self.passwords.get((url, username))

    def delete(self, url, username):
        self.passwords.pop((url, username), None)


def test_should_keep_passwords_in_the_injected_keystore(qsettings):
    keystore = DictKeystore()
    server = ServerSettings("http://ci/cc.xml", username="alice", password="pw")

    SettingsStore(qsettings, keystore).save(AppSettings(servers=[server]))

    assert keystore.passwords == {("http://ci/cc.xml", "alice"): "pw"}
    assert keyring.get_password("http://ci/cc.xml", "alice") is None
    assert SettingsStore(qsettings, keystore).settings.servers[0].password == "pw"


def test_should_read_a_symbolic_icons_flag_written_as_text(qsettings):
    qsettings.setValue("tray/symbolic_icons", "true")

    assert SettingsStore(qsettings, Keystore()).settings.symbolic_icons


def test_should_resume_notifications_on_save(ini):
    reopen(ini).save(full_settings())
    store = reopen(ini)

    store.save(replace(store.settings, paused_until=None))

    assert reopen(ini).settings.paused_until is None


@pytest.mark.parametrize("value", ["", "soon", "2026-10-02T13:30:00"])
def test_should_ignore_a_pause_without_a_valid_utc_time(qsettings, value):
    qsettings.setValue("notifications/paused_until", value)

    assert SettingsStore(qsettings, Keystore()).settings.paused_until is None
