import pytest

from buildnotifylib.core.settings import SCHEMA_VERSION, AppSettings, ServerSettings, SortKey, SourceKind


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


def test_should_default_to_the_2x_behaviour():
    settings = AppSettings()

    assert settings.servers == []
    assert (settings.interval_seconds, settings.timeout_seconds) == (120, 10)
    assert settings.custom_script == ""
    assert not settings.custom_script_enabled
    assert settings.sort_key is SortKey.STATUS
    assert not settings.show_last_build_label
    assert not settings.symbolic_icons


def test_should_default_notifications_per_event():
    settings = AppSettings()

    assert settings.notify("brokenBuild")
    assert not settings.notify("successfulBuild")


def test_should_prefer_a_configured_notification():
    assert AppSettings(notifications={"successfulBuild": True}).notify("successfulBuild")


def test_should_store_sort_keys_with_their_2x_names():
    assert [SortKey.LAST_BUILD_TIME.value, SortKey.NAME.value] == ["sort_build_time", "sort_name"]
    assert SortKey.STATUS.value == "sort_status"


def test_should_be_on_the_layout_with_mutes():
    assert SCHEMA_VERSION == 5


def test_should_default_a_server_to_a_cctray_feed():
    assert ServerSettings("http://ci/cc.xml").kind is SourceKind.CCTRAY


@pytest.mark.parametrize(
    "value, kind", [("github", SourceKind.GITHUB), ("cctray", SourceKind.CCTRAY), ("", SourceKind.CCTRAY)]
)
def test_should_parse_the_stored_kind(value, kind):
    assert ServerSettings("http://ci/cc.xml", kind=value).kind is kind


def test_should_point_a_github_server_at_its_repository():
    server = ServerSettings("", kind=SourceKind.GITHUB, repository="octo-org/hello-world")
    assert server.url == "https://github.com/octo-org/hello-world"
