from re import match

from buildnotifylib import version


def test_should_append_build_label_as_dev_suffix(monkeypatch):
    monkeypatch.delenv('BUILD_LABEL', raising=False)
    assert match(r'^\d+\.\d+\.\d+$', version.version())
    monkeypatch.setenv('BUILD_LABEL', '23')
    assert match(r'^\d+\.\d+\.\d+\.dev23$', version.version())
