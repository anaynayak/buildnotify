# Local setup

* Install [uv](https://docs.astral.sh/uv/).
* `uv sync` creates `.venv` with the app and the dev dependency group from `uv.lock`.
* `QT_QPA_PLATFORM=offscreen uv run pytest -q` runs the tests.
* `uv run buildnotify` launches the app.
* `uv build` builds the sdist and wheel into `dist/`.

## Editing the UI

To edit the dialog windows, you should use [Qt Designer](https://doc.qt.io/qt-6/qtdesigner-manual.html).
Once you're done, invoke the following command to regenerate its Python implementation:

```shell
uv run pyside6-uic --from-imports -o buildnotifylib/generated/<file>_ui.py data/<file>.ui
```

Regenerate the icon resources after changing `icons/` with:

```shell
uv run pyside6-rcc icons/icons.qrc -o buildnotifylib/generated/icons_rc.py
```
