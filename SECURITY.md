# Security policy

## Supported versions

1. 3.x: supported, and receives security fixes.
2. 2.x and older: not supported. Upgrade to 3.x.

## Reporting a vulnerability

Report it privately through GitHub: https://github.com/anaynayak/buildnotify/security/advisories/new

Please don't open a public issue or pull request for a vulnerability. Include the version, the platform, and steps or a sample feed that reproduce it.

## Scope

In scope:

1. Credential handling: passwords, tokens and the keyring or settings storage.
2. The custom script hook, including the `#status#` and `#projects#` substitution and the `BUILDNOTIFY_*` environment variables.
3. Feed parsing: cctray XML and GitHub Actions responses from a hostile or compromised server.
4. The release supply chain: the build workflows, published wheels and sdists, and their attestations.

Out of scope: problems that need an attacker who already controls the user's account or settings file, and bugs in the CI servers BuildNotify talks to.

## Disclosure timeline

1. We acknowledge a report within 7 days.
2. We ship a fix, or share a plan with a date, within 30 days.
3. We disclose in coordination with the reporter, after a fix is released. We credit the reporter unless they ask us not to.

## Verifying releases

Release wheels and sdists carry build provenance and PyPI attestations. Check one with:

```sh
gh attestation verify buildnotify-3.0.0-py3-none-any.whl --repo anaynayak/buildnotify
```

Each release and nightly also has a `buildnotify-<version>.intoto.jsonl` asset. See [DEVELOPMENT.md](DEVELOPMENT.md#verifying-a-release) for the SBOM check and how to reproduce a build.
