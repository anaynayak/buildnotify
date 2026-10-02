# Local setup

* Install [uv](https://docs.astral.sh/uv/).
* `uv sync` creates `.venv` with the app and the dev dependency group from `uv.lock`.
* `QT_QPA_PLATFORM=offscreen uv run pytest -q` runs the tests.
* `uv run buildnotify` launches the app.
* `uv build` builds the sdist and wheel into `dist/`.

## Editing the UI

To edit the dialog windows, you should use [Qt Designer](https://doc.qt.io/qt-6/qtdesigner-manual.html).
Once you're done, regenerate its Python implementation in `buildnotifylib/generated` with:

```shell
just ui
```

The status icons are plain SVG files in `buildnotifylib/resources/icons` and ship as package data.
