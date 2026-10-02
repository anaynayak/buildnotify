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
just ui            # regenerate buildnotifylib/generated from data/*.ui
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

To edit the dialog windows, you should use [Qt Designer](https://doc.qt.io/qt-6/qtdesigner-manual.html) (`uv run pyside6-designer`) on `data/*.ui`.
Once you're done, regenerate its Python implementation in `buildnotifylib/generated` with:

```shell
just ui
```

Commit the regenerated modules with the `.ui` change. CI runs `just ui` and fails if the output differs.

The status icons are plain SVG files in `buildnotifylib/resources/icons` and ship as package data.

## CI and releases

CI runs lint, format, mypy and the generated UI check, then the tests on Python 3.11 to 3.14 on Ubuntu and on Python 3.14 on macOS and Windows. On Linux it also builds the wheel and installs it into a clean venv.

Pushing a `v*` tag builds the sdist and wheel and publishes them to PyPI with trusted publishing.

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
