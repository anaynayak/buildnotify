import keyring

keyring.get_keyring()

class Keystore(object):
    @staticmethod
    def isAvailable():
        return True

    @staticmethod
    def save(url, username, password):
        keyring.set_password(url, username, password)

    @staticmethod
    def load(url, username):
        return keyring.get_password(url, username)
