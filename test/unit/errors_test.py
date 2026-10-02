from datetime import UTC, datetime

import pytest

from buildnotifylib.core.cctray import FeedError
from buildnotifylib.core.errors import DETAILS_LENGTH, MAX_LENGTH, details, phrase, server_label, summarize
from buildnotifylib.core.github import GitHubError, RateLimited
from buildnotifylib.core.ports import CannotConnect, CertificateError, FetchError, FetchTimeout, HostNotFound


@pytest.mark.parametrize(
    "error, summary",
    [
        (FetchError("HTTP 503 Service Unavailable"), "HTTP 503 Service Unavailable"),
        (TimeoutError("no response before the poll deadline"), "no response before the poll deadline"),
        (FeedError("Not a cctray feed"), "Not a cctray feed"),
        (CertificateError("[SSL: CERTIFICATE_VERIFY_FAILED] verify failed"), "Certificate not trusted"),
        (OSError(), "OSError"),
        (ValueError("\n  first line\nTraceback (most recent call last):\n  File x"), "first line"),
    ],
)
def test_should_summarise_an_error_in_one_short_line(error, summary):
    assert summarize(error) == summary


def test_should_truncate_a_long_error():
    summary = summarize(ValueError("x" * 200))
    assert len(summary) == 80 and summary.endswith("...")


def test_should_reduce_urls_in_an_error_to_their_host():
    error = ValueError("failed for https://user:hunter2@ci.example.com/cc.xml?token=s3cret, giving up")
    assert summarize(error) == "failed for ci.example.com, giving up"


@pytest.mark.parametrize(
    "url, label",
    [
        ("https://ci.example.com/cc.xml", "ci.example.com/cc.xml"),
        ("http://user:hunter2@localhost:8080/cc.xml?token=s3cret#x", "localhost:8080/cc.xml"),
        ("not a url", "not a url"),
        ("", "server"),
    ],
)
def test_should_label_a_server_without_credentials(url, label):
    assert server_label(url) == label


RESET = datetime(2026, 10, 2, 10, 30, tzinfo=UTC)


@pytest.mark.parametrize(
    "error, short",
    [
        (CannotConnect("Could not connect to ci.example.com"), "can't connect"),
        (HostNotFound("Could not connect to ci.example.com"), "server not found"),
        (FetchTimeout("Timed out"), "timed out"),
        (TimeoutError("no response before the poll deadline"), "timed out"),
        (FetchError("HTTP 401 Unauthorized", 401), "sign-in failed"),
        (FetchError("The token can't read this repository (HTTP 403)", 403), "sign-in failed"),
        (FetchError("HTTP 404 Not Found", 404), "not found"),
        (FetchError("HTTP 503 Service Unavailable", 503), "HTTP 503"),
        (FeedError("Not a cctray feed: expected <Projects> as the root element, got <html>"), "not a cctray feed"),
        (GitHubError("Not a GitHub workflow runs response"), "unexpected response"),
        (CertificateError("[SSL: CERTIFICATE_VERIFY_FAILED] verify failed"), "certificate not trusted"),
        (RateLimited(RESET), "GitHub rate limit reached"),
        (FetchError("Request failed (TooManyRedirects)"), "request failed"),
        (RuntimeError("boom"), "request failed"),
    ],
)
def test_should_map_an_error_to_a_short_phrase(error, short):
    assert phrase(error) == short


@pytest.mark.parametrize(
    "error, hint",
    [
        (FetchError("HTTP 401 Unauthorized", 401), "Sign-in failed - check the username and token"),
        (FeedError("Not a cctray feed"), "That URL didn't return a cctray feed"),
        (RateLimited(RESET), "GitHub rate limit reached - add a token"),
        (CertificateError("verify failed"), "Edit the server to connect anyway"),
        (HostNotFound("Could not connect to ci.example.com"), "Check the server address"),
    ],
)
def test_should_follow_the_full_message_with_a_hint(error, hint):
    assert details(error) == [summarize(error, DETAILS_LENGTH), hint]


def test_should_give_the_full_message_alone_without_a_hint():
    assert details(CannotConnect("Could not connect to ci.example.com")) == ["Could not connect to ci.example.com"]


def test_should_keep_credentials_out_of_the_details():
    error = ValueError("failed for https://user:hunter2@ci.example.com/cc.xml?token=s3cret " + "x" * 100)
    [message] = details(error)
    assert "hunter2" not in message and "s3cret" not in message and "/cc.xml" not in message
    assert len(message) > MAX_LENGTH
