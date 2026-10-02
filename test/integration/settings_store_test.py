import keyring
import pytest
from PySide6 import QtCore

from buildnotifylib.adapters.credentials import Keystore
from buildnotifylib.adapters.settings_store import SettingsStore
from buildnotifylib.core.settings import AppSettings, ServerSettings, SortKey
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
            ServerSettings("http://host:8080", [], "None", "outer", skip_ssl_verification=True),
            ServerSettings(
                "http://host:8080/cc.xml",
                ["a", "b :: c"],
                prefix="inner",
                password="token",
                authentication_type=ServerSettings.AUTH_BEARER_TOKEN,
            ),
        ],
        interval_seconds=300,
        timeout_seconds=30,
        custom_script="notify-send #status#",
        custom_script_enabled=True,
        sort_key=SortKey.NAME,
        show_last_build_label=True,
        notifications={"successfulBuild": True, "brokenBuild": False},
    )


def test_should_load_defaults_from_an_empty_file(ini):
    assert reopen(ini).settings == AppSettings()


def test_should_not_write_defaults_on_load(qsettings):
    SettingsStore(qsettings, Keystore())

    assert sorted(qsettings.allKeys()) == ["schema_version", "servers/size"]


def test_should_round_trip_every_value(ini):
    reopen(ini).save(full_settings())

    assert reopen(ini).settings == full_settings()


def test_should_keep_the_saved_settings_current(qsettings):
    store = SettingsStore(qsettings, Keystore())

    store.save(full_settings())

    assert store.settings == full_settings()


def test_should_store_servers_as_an_array(qsettings):
    SettingsStore(qsettings, Keystore()).save(full_settings())

    assert qsettings.value("servers/size") == 3
    assert qsettings.value("servers/2/url") == "http://host:8080"


def test_should_keep_passwords_out_of_the_settings_file(ini):
    reopen(ini).save(full_settings())

    assert "pw" not in open(ini).read()
    assert keyring.get_password("https://ci.example.com/go/cctray.xml", "alice") == "pw"
    assert keyring.get_password("http://host:8080/cc.xml", "") == "token"


def test_should_keep_a_server_nested_under_a_removed_one(ini):
    reopen(ini).save(full_settings())
    store = reopen(ini)
    store.save(AppSettings(servers=[s for s in store.settings.servers if s.prefix != "outer"]))

    assert [s.prefix for s in reopen(ini).settings.servers] == ["go", "inner"]


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
