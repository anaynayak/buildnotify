"""Short, credential-free text for the errors a server fetch can end with."""

import re
from urllib.parse import urlsplit

from buildnotifylib.core.cctray import FeedError
from buildnotifylib.core.github import GitHubError, RateLimited
from buildnotifylib.core.ports import CannotConnect, CertificateError, FetchError, FetchTimeout, HostNotFound

MAX_LENGTH = 80
DETAILS_LENGTH = 200
URL = re.compile(r"\b[a-zA-Z][a-zA-Z0-9+.-]*://\S+?(?=[\s,;)\]]|$)")
SIGN_IN = (401, 403)
PHRASES: list[tuple[type[Exception], str]] = [
    (CertificateError, "certificate not trusted"),
    (RateLimited, "GitHub rate limit reached"),
    (HostNotFound, "server not found"),
    (CannotConnect, "can't connect"),
    (FetchTimeout, "timed out"),
    (TimeoutError, "timed out"),
    (FeedError, "not a cctray feed"),
    (GitHubError, "unexpected response"),
]
HINTS: list[tuple[type[Exception], str]] = [
    (CertificateError, "Edit the server to connect anyway"),
    (RateLimited, "GitHub rate limit reached - add a token"),
    (HostNotFound, "Check the server address"),
    (FeedError, "That URL didn't return a cctray feed"),
]


def summarize(error: Exception, max_length: int = MAX_LENGTH) -> str:
    if isinstance(error, CertificateError):
        return "Certificate not trusted"
    lines = [line.strip() for line in str(error).splitlines() if line.strip()]
    text = URL.sub(lambda match: host(match.group()), lines[0]) if lines else type(error).__name__
    return text if len(text) <= max_length else text[: max_length - 3] + "..."


def phrase(error: Exception) -> str:
    """A few words for the menu row, such as "can't connect"."""
    status = error.status if isinstance(error, FetchError) else None
    if status in SIGN_IN:
        return "sign-in failed"
    if status == 404:
        return "not found"
    found = next((text for kind, text in PHRASES if isinstance(error, kind)), None)
    return found or (f"HTTP {status}" if status else "request failed")


def details(error: Exception) -> list[str]:
    """The full message, still free of credentials, and what to do about it if that is known."""
    return [summarize(error, DETAILS_LENGTH), *([hint] if (hint := hint_for(error)) else [])]


def hint_for(error: Exception) -> str | None:
    if isinstance(error, FetchError) and error.status in SIGN_IN:
        return "Sign-in failed - check the username and token"
    return next((text for kind, text in HINTS if isinstance(error, kind)), None)


def server_label(url: str) -> str:
    parts = urlsplit(url)
    return (host(url) + parts.path) or "server"


def server_name(url: str, prefix: str = "") -> str:
    """What the menu and notifications call a server: its menu prefix, else its host."""
    return prefix or host(url) or "server"


def host(url: str) -> str:
    return urlsplit(url).netloc.rpartition("@")[2]
