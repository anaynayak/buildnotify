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
```

Run the tests outside `just` with `QT_QPA_PLATFORM=offscreen uv run pytest -q`.

## Running the app

`uv run buildnotify --settings /tmp/buildnotify.ini --debug` launches the app against a throwaway settings file and logs every fetch. Leave out `--settings` to use your real settings.

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
