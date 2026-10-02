"""Composition root: builds the adapters once and injects them into the app."""

import argparse
import logging
import os
import sys

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from buildnotifylib.adapters.credentials import Keystore
from buildnotifylib.adapters.hooks import ShellScriptHook
from buildnotifylib.adapters.http import HttpConnection
from buildnotifylib.adapters.settings_store import SettingsStore
from buildnotifylib.ui.buildnotify import BuildNotify

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def parse_args(args: list[str]) -> tuple[argparse.Namespace, list[str]]:
    """Return our options and the arguments left over for Qt."""
    parser = argparse.ArgumentParser(prog="buildnotify", allow_abbrev=False)
    parser.add_argument("--debug", action="store_true", help="log every fetch")
    parser.add_argument("--settings", metavar="PATH", help="read and write settings in this INI file")
    return parser.parse_known_args(args)


def open_settings(path: str | None) -> QSettings:
    if path is None:
        return QSettings("BuildNotify", "BuildNotify")
    return QSettings(path, QSettings.Format.IniFormat)


def build(app: QApplication, settings_path: str | None = None) -> BuildNotify:
    store = SettingsStore(open_settings(settings_path), Keystore())
    return BuildNotify(app, store, HttpConnection(), ShellScriptHook())


def main(argv: list[str] | None = None) -> None:
    argv = sys.argv if argv is None else argv
    options, qt_args = parse_args(argv[1:])
    logging.basicConfig(level=logging.DEBUG if options.debug else logging.WARNING, format=LOG_FORMAT)
    app = QApplication([argv[0], *qt_args])
    app.setQuitOnLastWindowClosed(False)
    buildnotify = build(app, options.settings)
    exit_code = app.exec()
    if not buildnotify.wait_for_workers():
        logging.shutdown()
        sys.stdout.flush()
        os._exit(exit_code)
    else:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
