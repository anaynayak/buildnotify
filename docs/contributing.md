---
description: Set up a local BuildNotify checkout, run the tests and linters, and send a pull request.
---

# Contributing

Bug reports and pull requests are welcome at [github.com/anaynayak/buildnotify](https://github.com/anaynayak/buildnotify). Report a security problem privately, as described in [Security and privacy](security.md#reporting-a-vulnerability). The project follows the [code of conduct](https://github.com/anaynayak/buildnotify/blob/main/CODE_OF_CONDUCT.md).

## Local setup

1. Install [uv](https://docs.astral.sh/uv/) and [just](https://just.systems/).
2. `uv sync --locked` creates `.venv` with the app and the dev dependency group from `uv.lock`.
3. `pre-commit install` enables the ruff, ruff-format and uv-lock hooks.

## Commands

```commandline
just test          # full suite with QT_QPA_PLATFORM=offscreen; pass pytest args, e.g. just test -k config
just lint          # ruff check + ruff format --check
just fmt           # ruff fixes + formatting
just types         # mypy
just build         # sdist + wheel into dist/
just repro         # build twice from the same commit and compare sha256
just sbom          # CycloneDX SBOM of the runtime dependencies into sbom.cdx.json
just demo          # run the app against local fixture feeds; pass app args, e.g. just demo --debug
just screenshots   # render docs/images offscreen from fixture data
just docs          # build this site into site/ and fail on any warning
```

Run the tests outside `just` with `QT_QPA_PLATFORM=offscreen uv run pytest -q`.

## Running the app

`just demo` serves the cctray fixtures in `test/fixtures/cctray` from 127.0.0.1, writes a temp settings file with two feeds and one unreachable server, and starts the app with a null keyring. It never reads or writes your real settings or keychain, and it deletes the temp files when the app exits.

`uv run buildnotify --settings /tmp/buildnotify.ini --debug` launches the app against a throwaway settings file and logs every fetch. Don't leave out `--settings` for a test run, because on macOS HOME and XDG overrides don't isolate Qt's settings.

## Pull requests

`main` is protected, so changes arrive through a pull request.

1. Branch from `main` and keep the branch short-lived.
2. Make small commits with short imperative subjects, such as "Fix ...", "Add ..." or "Remove ...". Each commit does one thing.
3. Put the tests in the same commit as the change. Every commit should pass the checks.
4. For a bug, write a failing regression test first, then the fix.
5. Tests must be hermetic. They never touch the real keychain or your settings.
6. Open the pull request. It needs the `lint`, `reproducible`, `analyze` and `test (...)` checks green and up to date with `main`. No approval is needed.
7. Spotted another bug? Open an issue for it rather than fixing it in an unrelated commit.

## Editing the UI

The dialogs are built in Python code, not Qt Designer files. Each one is a package under `buildnotifylib/ui/dialogs` made of page or form widgets with `set_value()` and `value()`. `buildnotifylib/ui/widgets/forms.py` has helpers for labelled rows, titled sections and inline messages. Don't give widgets fixed sizes, so the dialogs grow with large fonts.

`just screenshots` renders the tray menu, each Preferences tab, the server dialog and the tray icon states into `docs/images`. Rerun it after a UI change and commit the images.

## Continuous integration and releases

CI runs lint, format and mypy, then the tests on Python 3.11 to 3.14 on Ubuntu and on Python 3.14 on macOS and Windows.

1. Every push to `main` replaces the rolling `dev` pre-release with a wheel, an sdist and a Flatpak bundle. The wheel gets a `.devN` version. Nothing from `main` goes to PyPI.
2. Pushing a `v*` tag builds the sdist and wheel and publishes them to PyPI with trusted publishing, after approval on the `pypi` environment. The tag must match `VERSION` in `buildnotifylib/version.py`.
3. The tag also gets a GitHub Release, with that version's section of the changelog as its notes, the wheel, the sdist, the SBOM and the Flatpak bundle.
4. Release builds are reproducible: `SOURCE_DATE_EPOCH` is the commit time, and `just repro` builds twice and compares the hashes. Provenance and the SBOM are attested. See [Security and privacy](security.md#verifying-a-release).

## Flatpak

The manifest is `packaging/flatpak/io.github.anaynayak.BuildNotify.yml`. It builds on the KDE runtime with PySide6 from `io.qt.PySide.BaseApp`. Regenerate the Python dependency list after a dependency change:

```commandline
uv run --with packaging python packaging/flatpak/generate-requirements.py
```

Build and run it on Linux with:

```commandline
flatpak-builder --user --install --force-clean --install-deps-from=flathub build-dir packaging/flatpak/io.github.anaynayak.BuildNotify.yml
flatpak run io.github.anaynayak.BuildNotify
```

CI builds the Flatpak on every pull request and runs `flatpak-builder-lint` on it. The full notes, including the lint commands, are in [DEVELOPMENT.md](https://github.com/anaynayak/buildnotify/blob/main/DEVELOPMENT.md).
