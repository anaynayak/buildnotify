import pytest

from buildnotifylib.core.cctray import FeedError
from buildnotifylib.core.errors import server_label, summarize
from buildnotifylib.core.ports import CertificateError, FetchError


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
