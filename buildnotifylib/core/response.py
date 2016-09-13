class Response:
    def __init__(self, server, error=None):
        self.server = server
        self.error = error

    def failed(self):
        return self.error is not None
