import keyring
from keyring.backends import fail
from keyring.errors import KeyringLocked

from buildnotifylib.core.keystore import Keystore
from test.fake_keyring import InMemoryKeyring


class LockedKeyring(InMemoryKeyring):
    def set_password(self, servicename, username, password):
        raise KeyringLocked("locked")

    def get_password(self, servicename, username):
        raise KeyringLocked("locked")


def test_should_be_available_with_a_working_backend():
    assert Keystore.is_available()


def test_should_treat_fail_keyring_as_unavailable():
    keyring.set_keyring(fail.Keyring())
    assert not Keystore.is_available()


def test_should_not_raise_when_backend_is_unavailable():
    keyring.set_keyring(fail.Keyring())
    Keystore.save("url", "user", "pass")
    assert Keystore.load("url", "user") is None


def test_should_not_raise_when_backend_raises():
    keyring.set_keyring(LockedKeyring())
    Keystore.save("url", "user", "pass")
    assert Keystore.load("url", "user") is None
