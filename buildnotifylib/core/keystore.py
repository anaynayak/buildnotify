import keyring


class Keystore:
    def save(self, url, username, password):
        keyring.set_password(url, username, password)

    def load(self, url, username):
        return keyring.get_password(url, username)
