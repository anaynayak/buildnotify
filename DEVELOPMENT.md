# Local setup

1. Install [uv](https://docs.astral.sh/uv/) and [just](https://just.systems/).
2. `uv sync --locked` creates `.venv` with the app and the dev dependency group from `uv.lock`.
3. `pre-commit install` enables the ruff, ruff-format and uv-lock hooks.

## Commands

```shell
just test          # full suite with QT_QPA_PLATFORM=offscreen; pass pytest args, e.g. just test -k config
just lint          # ruff check + ruff format --check
just fmt           # ruff fixes + formatting
just types         # mypy
just build         # sdist + wheel into dist/
just repro         # build twice from the same commit and compare sha256
just sbom          # CycloneDX SBOM of the runtime dependencies into sbom.cdx.json
just demo          # run the app against local fixture feeds; pass app args, e.g. just demo --debug
just screenshots   # render docs/images offscreen from fixture data
```

Run the tests outside `just` with `QT_QPA_PLATFORM=offscreen uv run pytest -q`.

## Running the app

`just demo` serves the cctray fixtures in `test/fixtures/cctray` from 127.0.0.1, writes a temp settings file with two feeds and one unreachable server, and starts the app with the null keyring. It never reads or writes your real settings or keychain, and it deletes the temp files when the app exits or you press Ctrl-C.

`uv run buildnotify --settings /tmp/buildnotify.ini --debug` launches the app against a throwaway settings file and logs every fetch. Leave out `--settings` to use your real settings.

## Screenshots

`just screenshots` renders the tray menu, each preferences tab, the server dialog (cctray and GitHub) and the tray icon states into `docs/images`. It uses the offscreen platform, the cctray fixtures and a fixed clock, so a rerun gives the same files. The offscreen platform has no native style, so the widgets use Fusion and the dialogs have no title bar. Rerun it after a UI change and commit the images.

## Editing the UI

The dialogs are built in Python code, not Qt Designer files. Each one is a package under `buildnotifylib/ui/dialogs` made of page or form widgets with `set_value()` and `value()`, and `buildnotifylib/ui/widgets/forms.py` has helpers for labelled rows, titled sections and inline messages. Don't give widgets fixed sizes, so the dialogs grow with large fonts. Rerun `just screenshots` after a change.

The status icons are plain SVG files in `buildnotifylib/resources/icons` and ship as package data.

## CI and releases

CI runs lint, format and mypy, then the tests on Python 3.11 to 3.14 on Ubuntu and on Python 3.14 on macOS and Windows. On Linux it also builds the wheel, installs it into a clean venv and checks that every tray icon loads.

Pushing a `v*` tag builds the sdist and wheel and publishes them to PyPI with trusted publishing. The tag must match `VERSION` in `buildnotifylib/version.py`, so `VERSION = "3.0.0"` is released by the tag `v3.0.0`. A mismatch fails the release before anything is built.

The release build also:

1. Sets `SOURCE_DATE_EPOCH` to the commit time (`git log -1 --format=%ct`), so the same commit gives the same sdist and wheel. CI runs `scripts/repro-check.sh` (`just repro`) to build twice and compare sha256.
2. Writes a CycloneDX SBOM of the runtime dependencies from `uv.lock` with `uv export --format cyclonedx1.5`, and uploads it as the `sbom` artifact.
3. Attests build provenance for `dist/*` with `actions/attest-build-provenance`, and attests the SBOM against the same files with `actions/attest-sbom`.
4. Publishes to PyPI with PEP 740 attestations through `pypa/gh-action-pypi-publish`.

Every action in `.github/workflows` is pinned to a full commit SHA with the version in a trailing comment. Dependabot's `github-actions` entry proposes updates to both.

### Verifying a release

Download the wheel or sdist from PyPI or the GitHub release, then:

```shell
gh attestation verify buildnotify-3.0.0-py3-none-any.whl --repo anaynayak/buildnotify
gh attestation verify buildnotify-3.0.0-py3-none-any.whl --repo anaynayak/buildnotify \
  --predicate-type https://cyclonedx.org/bom
```

The first command checks the build provenance, the second the SBOM attestation. PyPI also shows the PEP 740 attestation on each file's page under "Provenance". To check a build yourself, check out the tag, run `just repro` and compare the hashes with the ones on PyPI.

## Flatpak

The Flatpak manifest is `packaging/flatpak/io.github.anaynayak.BuildNotify.yml`. It builds on the KDE runtime with PySide6 from `io.qt.PySide.BaseApp`. The other Python deps are in `python3-requirements.json`, generated from `uv.lock`. Regenerate it after a dependency change:

```shell
uv run --with packaging python packaging/flatpak/generate-requirements.py
```

Build and run it on Linux with:

```shell
flatpak-builder --user --install --force-clean --install-deps-from=flathub build-dir packaging/flatpak/io.github.anaynayak.BuildNotify.yml
flatpak run io.github.anaynayak.BuildNotify
```

The desktop file, icon and AppStream metainfo at the repo root are named after the app id and ship in the wheel under `share/`. Check them with `desktop-file-validate` and `appstreamcli validate`.
