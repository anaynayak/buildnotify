import keyring


class FakeKeyring(keyring.backend.KeyringBackend):
    priority = 1

    def set_password(self, servicename, username, password):
        pass

    def get_password(self, servicename, username):
        return "pass"

    def delete_password(self, servicename, username, password):
        pass
