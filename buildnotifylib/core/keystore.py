import keyring


class Keystore(object):
    def __init__(self):
        pass

    @staticmethod
    def save(url, username, password):
        keyring.set_password(url, username, password)

    @staticmethod
    def load(url, username):
        return keyring.get_password(url, username)
