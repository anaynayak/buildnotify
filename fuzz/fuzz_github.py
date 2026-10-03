"""Atheris target for the GitHub workflow runs parser. Only GitHubError is expected; anything else is a finding."""

import contextlib
import sys

try:
    import atheris

    instrument = atheris.instrument_imports
except ImportError:  # the smoke test runs without atheris
    atheris = None
    instrument = contextlib.nullcontext

with instrument():
    from buildnotifylib.core.github import GitHubError, read_runs


def test_one_input(data: bytes) -> None:
    try:
        read_runs(data)
    except GitHubError:
        pass


if __name__ == "__main__":
    assert atheris is not None, "install atheris to fuzz"
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()
