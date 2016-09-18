from ssl import SSLError

class Response:
    def __init__(self, server, error=None):
        self.server = server
        self.error = error

    def failed(self):
        return self.error is not None

    def ssl_error(self):
        try:
            return self.failed() and type(self.error.reason) is SSLError
        except AttributeError:
            return False