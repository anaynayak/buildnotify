import pytest

from buildnotifylib.core.settings import ServerSettings


@pytest.mark.parametrize(
    "url, expected",
    [
        ("http://url.com:9800/cc.xml", "http://url.com:9800/cc.xml"),
        ("url.com:9800/cc.xml", "http://url.com:9800/cc.xml"),
        ("url.com/cc.xml", "http://url.com/cc.xml"),
        ("localhost:8080/cc.xml", "http://localhost:8080/cc.xml"),
        ("https://localhost:8080/cc.xml", "https://localhost:8080/cc.xml"),
        ("file://localhost:8080/cc.xml", "file://localhost:8080/cc.xml"),
    ],
)
def test_should_normalise_the_server_url(url, expected):
    assert ServerSettings(url).url == expected


def test_should_default_to_no_credentials():
    server = ServerSettings("http://ci/cc.xml")

    assert (server.username, server.password, server.timezone) == ("", "", "None")
    assert not server.has_creds()
    assert not server.uses_keyring()


def test_should_use_the_keyring_for_a_username_or_a_bearer_token():
    assert ServerSettings("ci", username="alice").uses_keyring()
    assert ServerSettings("ci", authentication_type=ServerSettings.AUTH_BEARER_TOKEN).uses_keyring()
