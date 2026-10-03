---
description: How BuildNotify stores credentials in the system keyring, what it sends over the network, and how to report a vulnerability.
---

# Security and privacy

## Where credentials are stored

Passwords and tokens go in the system keyring (Keychain on macOS, Credential Manager on Windows, a Secret Service provider such as GNOME Keyring or KWallet on Linux), through the `keyring` package. Each server has one entry. The service name is the server URL, and the user name is the one you typed, or `token` for a Bearer token.

The settings file never holds a password or token. It holds the server URL, your user name, the project filters and the other options listed in the [Reference](reference.md#settings-file-location). It also records whether certificate checks are off for a server.

Without a working keyring the server dialog disables the sign-in fields and says so. See [Troubleshooting](troubleshooting.md#the-keyring-is-missing-or-locked).

## What goes over the network

The only HTTP client is `requests`, used in `buildnotifylib/adapters/http.py`. It sends GET requests to two kinds of address:

1. The feed URL of each cctray server you configured.
2. `https://api.github.com/repos/<owner>/<name>/actions/runs` for each GitHub Actions server, and the next-page link GitHub returns, which `buildnotifylib/core/github.py` follows only when it points at `https://api.github.com/`.

Every request has the header `User-Agent: BuildNotify/<version>`, with no operating system details. A GitHub token is sent as an `Authorization: Bearer` header to `api.github.com` only. A cctray user name and password go to the feed URL you entered as HTTP basic auth, and a cctray token goes there as an `Authorization: Bearer` header. `requests` follows HTTP redirects, and the code doesn't turn that off. On a redirect to another host, `requests` drops the `Authorization` header.

BuildNotify makes no other network requests:

1. No update check, telemetry or analytics. `buildnotifylib/` and `scripts/` use no `urllib`, `http.client` or `smtplib` request code. The only related imports are URL parsing, `socket` in `buildnotifylib/adapters/http.py`, used only to recognise a DNS lookup error, and `socket` in `scripts/demo.py`, which serves local fixtures for `just demo`.
2. No Qt network code. Nothing imports `QtNetwork` or `QtWebEngine`.
3. `webbrowser.open` in `buildnotifylib/ui/app_menu.py` and `buildnotifylib/ui/notifications.py` hands a project URL to your browser when you click a project or a notification. BuildNotify itself makes no request to that URL. The About box and the GitHub token help in the server dialog contain links that your browser opens when you click them.

The custom script is yours. BuildNotify runs it with your privileges, and BuildNotify has no control over what it does.

## Certificate checks

Certificates are checked by default. If a server's certificate isn't trusted, the server dialog asks whether to connect anyway. Accepting turns checks off for that server only, shows `Certificate checks off for <host>` in the dialog, and offers a button to turn them back on. See [Troubleshooting](troubleshooting.md#certificate-not-trusted).

## Verifying a release

Releases are built by GitHub Actions from a tag and published to PyPI with trusted publishing. The wheel and sdist carry build provenance and PyPI attestations. Download a file from PyPI or the GitHub release and check it with the [GitHub CLI](https://cli.github.com/):

```commandline
gh attestation verify buildnotify-3.0.0-py3-none-any.whl --repo anaynayak/buildnotify
```

Releases also carry an SBOM attestation:

```commandline
gh attestation verify buildnotify-3.0.0-py3-none-any.whl --repo anaynayak/buildnotify \
  --predicate-type https://cyclonedx.org/bom
```

1. PyPI shows the PEP 740 attestation of each file under "Provenance" on the file's page.
2. Each release and development build has a `buildnotify-<version>.intoto.jsonl` asset with the provenance bundle, one JSON bundle per line.
3. Development build wheels and sdists have build provenance, so the first command works for them. They have no SBOM.
4. Builds are reproducible. Check out the tag, run `just repro` and compare the hashes with the ones on PyPI. See [Contributing](contributing.md).

## Reporting a vulnerability

Report it privately through [GitHub security advisories](https://github.com/anaynayak/buildnotify/security/advisories/new). Don't open a public issue or pull request. Include the version, the platform, and steps or a sample feed that reproduce it.

1. Version 3.x is supported and gets security fixes. 2.x and older are not supported.
2. A report is acknowledged within 7 days.
3. A fix, or a plan with a date, follows within 30 days.
4. Disclosure is coordinated with you after a fix is released, and you are credited unless you ask otherwise.

In scope are credential handling, the custom script hook, parsing of hostile feeds and the release supply chain. The full policy is in [SECURITY.md](https://github.com/anaynayak/buildnotify/blob/main/SECURITY.md).
