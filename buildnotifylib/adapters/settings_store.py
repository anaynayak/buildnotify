from collections.abc import Callable
from typing import Any

from PyQt5.QtCore import QSettings

from buildnotifylib.core.ports import CredentialStore
from buildnotifylib.core.settings import (
    DEFAULT_NOTIFICATIONS,
    SCHEMA_VERSION,
    AppSettings,
    ServerSettings,
    SortKey,
)

DEFAULTS = AppSettings()
SERVERS = "servers"
GLOBAL_KEYS = {
    "interval_seconds": "connection/interval_in_seconds",
    "timeout_seconds": "connection/timeout",
    "custom_script": "notifications/custom_script",
    "custom_script_enabled": "notifications/custom_script_enabled",
    "show_last_build_label": "show_last_build_label",
}
SORT_KEY = "sort_key"
NOTIFICATION = "values/%s"
SERVER_KEYS = {
    "url": "url",
    "excluded_projects": "excludes",
    "timezone": "timezone",
    "prefix": "display_prefix",
    "username": "username",
    "skip_ssl_verification": "skip_ssl_verification",
    "authentication_type": "authorization_type",
}

VERSION = "schema_version"
LEGACY_URLS = "connection/urls"
LEGACY_SERVER_GROUPS = [key for key in SERVER_KEYS.values() if key != "url"]

ValueReader = Callable[[str], Any]


class SettingsStore:
    def __init__(self, qsettings: QSettings, keystore: CredentialStore):
        self.qsettings = qsettings
        self.keystore = keystore
        migrate(qsettings)
        self.settings = self.load()

    def load(self) -> AppSettings:
        values = {field: self.read(key, getattr(DEFAULTS, field)) for field, key in GLOBAL_KEYS.items()}
        return AppSettings(
            servers=[self.with_password(server) for server in self.read_servers()],
            sort_key=sort_key(self.qsettings.value(SORT_KEY)),
            notifications=self.read_notifications(),
            **values,
        )

    def save(self, settings: AppSettings) -> None:
        for field, key in GLOBAL_KEYS.items():
            self.qsettings.setValue(key, getattr(settings, field))
        self.qsettings.setValue(SORT_KEY, settings.sort_key.value)
        for event, enabled in settings.notifications.items():
            self.qsettings.setValue(NOTIFICATION % event, enabled)
        write_servers(self.qsettings, settings.servers)
        self.qsettings.sync()
        self.save_passwords(self.settings.servers, settings.servers)
        self.settings = settings

    def read_notifications(self) -> dict[str, bool]:
        stored = [event for event in DEFAULT_NOTIFICATIONS if self.qsettings.contains(NOTIFICATION % event)]
        return {event: self.read(NOTIFICATION % event, DEFAULT_NOTIFICATIONS[event]) for event in stored}

    def read(self, key: str, default: Any) -> Any:
        return coerce(self.qsettings.value(key), default)

    def read_servers(self) -> list[ServerSettings]:
        size = self.qsettings.beginReadArray(SERVERS)
        servers = []
        for index in range(size):
            self.qsettings.setArrayIndex(index)
            servers.append(read_server(self.qsettings.value))
        self.qsettings.endArray()
        return servers

    def with_password(self, server: ServerSettings) -> ServerSettings:
        if server.uses_keyring():
            server.password = self.keystore.load(server.url, server.username) or ""
        return server

    def save_passwords(self, old: list[ServerSettings], new: list[ServerSettings]) -> None:
        old_entries, new_entries = keyring_entries(old), keyring_entries(new)
        for url, username in old_entries.keys() - new_entries.keys():
            self.keystore.delete(url, username)
        for (url, username), password in new_entries.items():
            if old_entries.get((url, username)) != password:
                self.keystore.save(url, username, password)


def migrate(qsettings: QSettings) -> None:
    """Move 2.x per-URL keys into the servers array; the old keys go only once the new ones are on disk."""
    if as_int(qsettings.value(VERSION), 2) < SCHEMA_VERSION:
        urls = coerce(qsettings.value(LEGACY_URLS), [])
        write_servers(qsettings, [read_server(legacy_value(qsettings, url)) for url in urls])
        qsettings.setValue(VERSION, SCHEMA_VERSION)
        qsettings.sync()
    if qsettings.status() == QSettings.NoError and qsettings.contains(LEGACY_URLS):
        remove_legacy_keys(qsettings)


def legacy_value(qsettings: QSettings, url: str) -> ValueReader:
    return lambda key: url if key == "url" else qsettings.value(f"{key}/{url}")


def remove_legacy_keys(qsettings: QSettings) -> None:
    for group in LEGACY_SERVER_GROUPS:
        qsettings.remove(group)
    qsettings.remove(LEGACY_URLS)
    qsettings.sync()


def read_server(value: ValueReader) -> ServerSettings:
    defaults = ServerSettings("")
    fields = {field: coerce(value(key), getattr(defaults, field)) for field, key in SERVER_KEYS.items()}
    return ServerSettings(**fields)


def write_servers(qsettings: QSettings, servers: list[ServerSettings]) -> None:
    qsettings.remove(SERVERS)
    qsettings.beginWriteArray(SERVERS, len(servers))
    for index, server in enumerate(servers):
        qsettings.setArrayIndex(index)
        for field, key in SERVER_KEYS.items():
            qsettings.setValue(key, getattr(server, field))
    qsettings.endArray()


def keyring_entries(servers: list[ServerSettings]) -> dict[tuple[str, str], str]:
    return {(server.url, server.username): server.password for server in servers if server.uses_keyring()}


def sort_key(value: Any) -> SortKey:
    try:
        return SortKey(value)
    except ValueError:
        return DEFAULTS.sort_key


def coerce(value: Any, default: Any) -> Any:
    """Read a QSettings value as the type of its default; INI files hand back strings."""
    if value is None:
        return default
    if isinstance(default, bool):
        return value if isinstance(value, bool) else str(value).lower() == "true"
    if isinstance(default, int):
        return as_int(value, default)
    if isinstance(default, list):
        return [str(item) for item in ([value] if isinstance(value, str) else value) if item != ""]
    return str(value)


def as_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
