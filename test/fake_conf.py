import itertools
from dataclasses import replace
from pathlib import Path

from PySide6 import QtCore

from buildnotifylib.adapters.credentials import Keystore
from buildnotifylib.adapters.settings_store import SettingsStore
from buildnotifylib.core.settings import AppSettings, ServerSettings

SETTINGS_DIR: Path | None = None
counter = itertools.count()


class ConfigBuilder:
    def __init__(self, **overrides):
        defaults = AppSettings(notifications={"lastBuildTimeForProject": False})
        self.settings = replace(defaults, **overrides)

    def server(self, url, **fields):
        self.settings.servers.append(ServerSettings(url, **fields))
        return self

    def build(self) -> SettingsStore:
        assert SETTINGS_DIR is not None, "test/conftest.py sets SETTINGS_DIR to tmp_path"
        path = SETTINGS_DIR / f"settings-{next(counter)}.ini"
        store = SettingsStore(QtCore.QSettings(str(path), QtCore.QSettings.Format.IniFormat), Keystore())
        store.save(self.settings)
        return store
