"""Run BuildNotify against local fixture feeds, with throwaway settings and no keychain.

The feeds are served from 127.0.0.1 on a free port. One server points at a port nothing
listens on, so the menu shows an error row. The temp directory goes when the app exits.
"""

import functools
import os
import signal
import socket
import subprocess
import sys
import tempfile
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PySide6.QtCore import QSettings

from buildnotifylib.adapters.settings_store import SettingsStore
from buildnotifylib.core.settings import AppSettings, ServerSettings

ROOT = Path(__file__).resolve().parent.parent
FEEDS = ROOT / "test" / "fixtures" / "cctray"
NULL_KEYRING = "keyring.backends.null.Keyring"
INTERVAL_SECONDS = 10


class NoKeystore:
    """The demo settings hold no credentials, so nothing ever reaches a keyring."""

    def is_available(self) -> bool:
        return True

    def save(self, url: str, username: str, password: str) -> None:
        pass

    def load(self, url: str, username: str) -> str | None:
        return None

    def delete(self, url: str, username: str) -> None:
        pass


def demo_settings(port: int, dead_port: int) -> AppSettings:
    feed = f"http://127.0.0.1:{port}"
    return AppSettings(
        servers=[
            ServerSettings(f"{feed}/jenkins.xml", prefix="jenkins"),
            ServerSettings(f"{feed}/gocd.xml", prefix="gocd"),
            ServerSettings(f"http://127.0.0.1:{dead_port}/cctray.xml"),
        ],
        interval_seconds=INTERVAL_SECONDS,
        timeout_seconds=3,
    )


def write_settings(directory: Path, settings: AppSettings) -> Path:
    path = directory / "buildnotify-demo.ini"
    SettingsStore(QSettings(str(path), QSettings.Format.IniFormat), NoKeystore()).save(settings)
    return path


def free_port() -> int:
    """A port that was free a moment ago and has nothing listening on it now."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@contextmanager
def serve(directory: Path) -> Iterator[int]:
    handler = functools.partial(QuietHandler, directory=str(directory))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield int(server.server_address[1])
    finally:
        server.shutdown()
        server.server_close()


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass


def child_env(environ: dict[str, str]) -> dict[str, str]:
    """The just recipes export QT_QPA_PLATFORM=offscreen, which would hide the tray icon."""
    env = {key: value for key, value in environ.items() if key != "QT_QPA_PLATFORM"}
    env["PYTHON_KEYRING_BACKEND"] = NULL_KEYRING
    return env


def run(args: list[str]) -> int:
    with tempfile.TemporaryDirectory(prefix="buildnotify-demo-") as tmp, serve(FEEDS) as port:
        settings = write_settings(Path(tmp), demo_settings(port, free_port()))
        print(f"Serving {FEEDS} on http://127.0.0.1:{port}, settings in {settings}. Ctrl-C to stop.")
        command = [sys.executable, "-m", "buildnotifylib", "--settings", str(settings), *args]
        child = subprocess.Popen(command, env=child_env(dict(os.environ)))
        try:
            return child.wait()
        except KeyboardInterrupt:
            return 130
        finally:
            stop(child)


def stop(child: subprocess.Popen[bytes]) -> None:
    if child.poll() is None:
        child.terminate()
        child.wait()


def interrupt(signum: int, frame: object) -> None:
    raise KeyboardInterrupt


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, interrupt)
    sys.exit(run(sys.argv[1:]))
