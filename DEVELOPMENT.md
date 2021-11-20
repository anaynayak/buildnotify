# Local setup

* `pyenv virtualenv 3.8.5 buildnotify`
* `pyenv activate buildnotify`
* `pip install -r test-requirements.txt`
* `tox` for running tests
* `pip install -e .` for installing locally. Use `python buildnotifyapplet.py` to launch
* `paver mk_resources` is used to regenerate source files corresponding to icons/dialogs.

Paver commands can be viewed by running `paver -h`. Run `pip install paver` if not installed.

## Editing the UI

To edit the dialog windows, you should use [Qt Designer](https://doc.qt.io/qt-5/qtdesigner-manual.html).
Once you're done, invoke the following command to regenerate its Python implementation:

```shell
pyuic5 -x data/<file>.ui -o buildnotifylib/generated/<file>_ui.py
```

## Packaging

Dependencies for creating a pip/deb package (use virtualenv)

```shell
pip install paver
pip install stdeb
pip install twine
pip install keyrings.alt
apt-get install debhelper dput
```
