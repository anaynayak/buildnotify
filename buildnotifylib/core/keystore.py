class FakeKeyring:
    def set_password(self, url, username, password):
        pass

    def get_password(self, url, username):
        pass


try:
    import keyring
except ImportError:
    keyring = FakeKeyring()


class Keystore(object):
    @staticmethod
    def is_available() -> bool:
        return not isinstance(keyring, FakeKeyring)

    @staticmethod
    def save(url: str, username: str, password: str):
        keyring.set_password(url, username, password)

    @staticmethod
    def load(url: str, username: str) -> str:
        return keyring.get_password(url, username)
