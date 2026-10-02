import keyring
import pytest
from PyQt5 import QtCore

from test import fake_conf
from test.fake_keyring import InMemoryKeyring


@pytest.fixture(autouse=True)
def in_memory_keyring():
    previous = keyring.get_keyring()
    backend = InMemoryKeyring()
    keyring.set_keyring(backend)
    yield backend
    keyring.set_keyring(previous)


@pytest.fixture
def qsettings(tmp_path):
    return QtCore.QSettings(str(tmp_path / "settings.ini"), QtCore.QSettings.IniFormat)


@pytest.fixture(autouse=True)
def builder_settings_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(fake_conf, "SETTINGS_DIR", tmp_path)
