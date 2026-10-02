import os


def fake_content():
    path = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "/../data/cctray.xml")
    return open(path, encoding="utf-8").read()


class FakeConnection:
    def __init__(self, body: str):
        self.body = body.encode("utf-8")
        self.urls: list[str] = []

    def connect(self, server, timeout, additional_headers=None) -> bytes:
        self.urls.append(server.url)
        return self.body
