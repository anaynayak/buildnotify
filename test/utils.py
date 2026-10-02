import os
import threading


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


class GatedConnection(FakeConnection):
    """Holds fetches of the `slow` URLs until `release` is set, for at most 5s."""

    def __init__(self, body: str, slow: list[str]):
        super().__init__(body)
        self.slow = set(slow)
        self.release = threading.Event()
        self.started: set[str] = set()
        self.done: list[str] = []

    def connect(self, server, timeout, additional_headers=None) -> bytes:
        self.started.add(server.url)
        body = super().connect(server, timeout, additional_headers)
        if server.url in self.slow:
            self.release.wait(5)
        self.done.append(server.url)
        return body
