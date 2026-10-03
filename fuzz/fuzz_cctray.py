"""Atheris target for the cctray parser. Only FeedError is expected; anything else is a finding."""

import contextlib
import sys

try:
    import atheris

    instrument = atheris.instrument_imports
except ImportError:  # the smoke test runs without atheris
    atheris = None
    instrument = contextlib.nullcontext

with instrument():
    from buildnotifylib.core.cctray import FeedError, parse
    from buildnotifylib.core.settings import ServerSettings

SERVER = ServerSettings("https://ci.example.com/cctray.xml")


def test_one_input(data: bytes) -> None:
    try:
        parse(data, SERVER)
    except FeedError:
        pass


if __name__ == "__main__":
    assert atheris is not None, "install atheris to fuzz"
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()
