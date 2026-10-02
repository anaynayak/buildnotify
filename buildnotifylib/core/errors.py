"""Short, credential-free text for the errors a server fetch can end with."""

import re
from urllib.parse import urlsplit

from buildnotifylib.core.ports import CertificateError

MAX_LENGTH = 80
URL = re.compile(r"\b[a-zA-Z][a-zA-Z0-9+.-]*://\S+?(?=[\s,;)\]]|$)")


def summarize(error: Exception) -> str:
    if isinstance(error, CertificateError):
        return "Certificate not trusted"
    lines = [line.strip() for line in str(error).splitlines() if line.strip()]
    text = URL.sub(lambda match: host(match.group()), lines[0]) if lines else type(error).__name__
    return text if len(text) <= MAX_LENGTH else text[: MAX_LENGTH - 3] + "..."


def server_label(url: str) -> str:
    parts = urlsplit(url)
    return (host(url) + parts.path) or "server"


def host(url: str) -> str:
    return urlsplit(url).netloc.rpartition("@")[2]
