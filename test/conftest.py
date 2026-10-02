import keyring
import pytest
from PyQt5 import QtCore

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
