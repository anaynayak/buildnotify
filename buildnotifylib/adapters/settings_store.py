from collections.abc import Callable
from datetime import datetime
from typing import Any

from PySide6.QtCore import QSettings

from buildnotifylib.core.ports import CredentialStore
from buildnotifylib.core.settings import (
    DEFAULT_NOTIFICATIONS,
    SCHEMA_VERSION,
    AppSettings,
    ServerSettings,
    SortKey,
    SourceKind,
)

DEFAULTS = AppSettings()
SERVERS = "servers"
GLOBAL_KEYS = {
    "interval_seconds": "connection/interval_in_seconds",
    "timeout_seconds": "connection/timeout",
    "custom_script": "notifications/custom_script",
    "custom_script_enabled": "notifications/custom_script_enabled",
    "show_last_build_label": "show_last_build_label",
    "symbolic_icons": "tray/symbolic_icons",
}
SORT_KEY = "sort_key"
PAUSED_UNTIL = "notifications/paused_until"
NOTIFICATION = "values/%s"
SERVER_KEYS = {
    "url": "url",
    "excluded_projects": "excludes",
    "timezone": "timezone",
    "prefix": "display_prefix",
    "username": "username",
    "skip_ssl_verification": "skip_ssl_verification",
    "authentication_type": "authorization_type",
    "kind": "kind",
    "repository": "repository",
    "workflow": "workflow",
    "branch": "branch",
    "muted": "muted",
    "muted_projects": "muted_projects",
}

VERSION = "schema_version"
LEGACY_URLS = "connection/urls"
LEGACY_SERVER_GROUPS = [
    "excludes",
    "timezone",
    "display_prefix",
    "username",
    "skip_ssl_verification",
    "authorization_type",
]
FIRST_ARRAY_VERSION = 3
SERVER_KEYS_ADDED: dict[int, dict[str, Any]] = {4: {"kind": SourceKind.CCTRAY.value}, 5: {"muted": False}}

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
            paused_until=paused_until(self.qsettings.value(PAUSED_UNTIL)),
            **values,
        )

    def save(self, settings: AppSettings) -> None:
        for field, key in GLOBAL_KEYS.items():
            self.qsettings.setValue(key, getattr(settings, field))
        self.qsettings.setValue(SORT_KEY, settings.sort_key.value)
        self.qsettings.setValue(PAUSED_UNTIL, settings.paused_until.isoformat() if settings.paused_until else "")
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
    version = as_int(qsettings.value(VERSION), 2)
    if version < FIRST_ARRAY_VERSION:
        urls = coerce(qsettings.value(LEGACY_URLS), [])
        write_servers(qsettings, [read_server(legacy_value(qsettings, url)) for url in urls])
    elif version < SCHEMA_VERSION:
        add_server_keys(qsettings, version)
    if version < SCHEMA_VERSION:
        qsettings.setValue(VERSION, SCHEMA_VERSION)
        qsettings.sync()
    if qsettings.status() == QSettings.Status.NoError and qsettings.contains(LEGACY_URLS):
        remove_legacy_keys(qsettings)


def add_server_keys(qsettings: QSettings, version: int) -> None:
    """Give each server the keys added since its schema version: 3.0 servers are cctray feeds, and none is muted."""
    added = {key: value for since, keys in SERVER_KEYS_ADDED.items() if since > version for key, value in keys.items()}
    size = qsettings.beginReadArray(SERVERS)
    qsettings.endArray()
    qsettings.beginWriteArray(SERVERS, size)
    for index in range(size):
        qsettings.setArrayIndex(index)
        for key, value in added.items():
            if not qsettings.contains(key):
                qsettings.setValue(key, value)
    qsettings.endArray()


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
            value = getattr(server, field)
            qsettings.setValue(key, value.value if isinstance(value, SourceKind) else value)
    qsettings.endArray()


def keyring_entries(servers: list[ServerSettings]) -> dict[tuple[str, str], str]:
    """Keyring entries by (url, username). A token server with no token has none, so no empty entry is written."""
    return {
        (server.url, server.username): server.password
        for server in servers
        if server.uses_keyring() and (server.username or server.password)
    }


def paused_until(value: Any) -> datetime | None:
    try:
        until = datetime.fromisoformat(str(value))
    except ValueError:
        return None
    return until if until.tzinfo is not None else None


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
