import subprocess
import sys

import keyring

from test.fake_keyring import InMemoryKeyring


def test_should_use_in_memory_keyring():
    assert isinstance(keyring.get_keyring(), InMemoryKeyring)


def test_should_not_leak_passwords_between_tests_part_one():
    keyring.set_password("svc", "user", "secret")


def test_should_not_leak_passwords_between_tests_part_two():
    assert keyring.get_password("svc", "user") is None


def test_should_not_open_real_qsettings_on_import():
    script = (
        "from PyQt5 import QtCore\n"
        "calls = []\n"
        "class Spy(QtCore.QSettings):\n"
        "    def __init__(self, *args):\n"
        "        calls.append(args)\n"
        "        super().__init__(*args)\n"
        "QtCore.QSettings = Spy\n"
        "import buildnotifylib.buildnotify\n"
        "import buildnotifylib.__main__\n"
        "assert not calls, calls\n"
    )
    subprocess.run([sys.executable, "-c", script], check=True)
