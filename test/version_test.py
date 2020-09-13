from os import environ
from re import match

from buildnotifylib import version


def test_should_cleanup_url():
    assert match('^\d*.\d*.\d*$', version.version())
    environ['BUILD_LABEL'] = '23'
    assert match('^\d*.\d*.\d*.dev23$', version.version())
