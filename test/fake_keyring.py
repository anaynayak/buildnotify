import keyring


class InMemoryKeyring(keyring.backend.KeyringBackend):
    priority = 1

    def __init__(self):
        super().__init__()
        self.passwords = {}

    def set_password(self, servicename, username, password):
        self.passwords[(servicename, username)] = password

    def get_password(self, servicename, username):
        return self.passwords.get((servicename, username))

    def delete_password(self, servicename, username):
        self.passwords.pop((servicename, username), None)
