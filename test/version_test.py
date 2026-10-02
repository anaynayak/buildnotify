from re import match

from buildnotifylib.version import VERSION


def test_should_be_a_release_version():
    assert match(r"^\d+\.\d+\.\d+$", VERSION)
