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
    def isAvailable():
        return not isinstance(keyring, FakeKeyring)

    @staticmethod
    def save(url, username, password):
        keyring.set_password(url, username, password)

    @staticmethod
    def load(url, username):
        return keyring.get_password(url, username)
