

class FakeKeyring:
    def set_password(self, url, username, password):
        pass

    def get_password(self, url, username):
        pass

    def delete_password(self, url, username):
        pass


class KeyringError(Exception):
    pass


try:
    import keyring
    from keyring.backends import fail
    from keyring.errors import KeyringError  # noqa: F811
except ImportError:
    keyring = FakeKeyring()


class Keystore:
    @staticmethod
    def is_available() -> bool:
        if isinstance(keyring, FakeKeyring):
            return False
        return not isinstance(keyring.get_keyring(), fail.Keyring)

    @staticmethod
    def save(url: str, username: str, password: str):
        try:
            keyring.set_password(url, username, password)
        except KeyringError:
            pass

    @staticmethod
    def load(url: str, username: str) -> str | None:
        try:
            return keyring.get_password(url, username)
        except KeyringError:
            return None

    @staticmethod
    def delete(url: str, username: str):
        try:
            keyring.delete_password(url, username)
        except KeyringError:
            pass
