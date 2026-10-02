import threading
from unittest.mock import ANY

import pytest
import requests_mock
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

from buildnotifylib.adapters.credentials import Keystore
from buildnotifylib.adapters.http import HttpConnection
from buildnotifylib.core.settings import ServerSettings
from buildnotifylib.server_configuration_dialog import ServerConfigurationDialog
from test.utils import FakeConnection, GatedConnection, fake_content

TIMEOUT = 10


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_show_configured_urls(qtbot):
    with requests_mock.Mocker() as m:
        url = "http://localhost:8080/cc.xml"
        m.get(url, text=fake_content())
        dialog = ServerConfigurationDialog(ServerSettings(url), TIMEOUT, HttpConnection())
        dialog.show()
        qtbot.addWidget(dialog)
        qtbot.mouseClick(dialog.ui.loadUrlButton, QtCore.Qt.LeftButton)

        qtbot.waitUntil(lambda: dialog.ui.projectsList.model() is not None)
        model = dialog.ui.projectsList.model()
        assert model.item(0, 0).hasChildren()
        assert model.item(0, 0).child(0, 0).isCheckable()
        assert model.item(0, 0).child(0, 0).data(Qt.CheckStateRole) == Qt.Checked
        assert model.item(0, 0).child(0, 0).text() == "cleanup-artifacts-B"

        assert dialog.ui.timezoneList.currentText() == "None"


@pytest.mark.functional
def test_should_fall_back_to_none_for_unknown_stored_timezone(qtbot):
    url = "http://localhost:8080/cc.xml"
    dialog = ServerConfigurationDialog(ServerSettings(url, timezone="EDT"), TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    assert dialog.ui.timezoneList.currentText() == "None"


@pytest.mark.functional
def test_should_list_zoneinfo_timezones_sorted(qtbot):
    dialog = ServerConfigurationDialog(None, TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)
    zones = [dialog.ui.timezoneList.itemText(i) for i in range(dialog.ui.timezoneList.count())]

    assert zones[0] == "None"
    assert "Asia/Kolkata" in zones
    assert zones[1:] == sorted(zones[1:])


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_save_restore_config(qtbot):
    with requests_mock.Mocker() as m:
        url = "http://localhost:8080/cc.xml"
        m.get(url, text=fake_content())
        dialog = ServerConfigurationDialog(ServerSettings(url), TIMEOUT, HttpConnection())
        dialog.show()
        qtbot.addWidget(dialog)
        qtbot.mouseClick(dialog.ui.loadUrlButton, QtCore.Qt.LeftButton)

        qtbot.waitUntil(lambda: dialog.ui.projectsList.model() is not None)
        server_config = dialog.get_server_config()
        dialog = ServerConfigurationDialog(server_config, TIMEOUT, HttpConnection())
        dialog.show()
        qtbot.addWidget(dialog)


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_exclude_projects(qtbot):
    with requests_mock.Mocker() as m:
        url = "http://localhost:8080/cc.xml"
        m.get(url, text=fake_content())
        dialog = ServerConfigurationDialog(ServerSettings(url), TIMEOUT, HttpConnection())
        dialog.show()
        qtbot.addWidget(dialog)
        qtbot.mouseClick(dialog.ui.loadUrlButton, QtCore.Qt.LeftButton)

        qtbot.waitUntil(lambda: dialog.ui.projectsList.model() is not None)
        model = dialog.ui.projectsList.model()

        model.item(0, 0).child(0, 0).setCheckState(QtCore.Qt.Unchecked)

        server_config = dialog.get_server_config()
        assert [str(s) for s in server_config.excluded_projects] == ["cleanup-artifacts-B"]


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_preload_info(qtbot):
    with requests_mock.Mocker() as m:
        url = "http://localhost:8080/cc.xml"
        m.get(url, text=fake_content())
        server = ServerSettings(url, ["cleanup-artifacts-B"], "US/Eastern")
        dialog = ServerConfigurationDialog(server, TIMEOUT, HttpConnection())
        dialog.show()
        qtbot.addWidget(dialog)
        qtbot.mouseClick(dialog.ui.loadUrlButton, QtCore.Qt.LeftButton)

        qtbot.waitUntil(lambda: dialog.ui.projectsList.model() is not None)
        model = dialog.ui.projectsList.model()

        assert model.item(0, 0).hasChildren()
        assert model.item(0, 0).child(0, 0).isCheckable()
        assert model.item(0, 0).child(0, 0).text() == "cleanup-artifacts-B"
        assert model.item(0, 0).child(0, 0).data(Qt.CheckStateRole) == Qt.Unchecked

        def timezone():
            assert dialog.ui.timezoneList.count() > 100
            assert dialog.ui.timezoneList.currentText() == "US/Eastern"

        qtbot.waitUntil(timezone)


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_fail_for_bad_url(qtbot, mocker):
    url = "file:///badpath"
    dialog = ServerConfigurationDialog(ServerSettings(url), TIMEOUT, HttpConnection())
    dialog.show()
    qtbot.addWidget(dialog)
    m = mocker.patch.object(QMessageBox, "critical", return_value=QMessageBox.No)

    qtbot.mouseClick(dialog.ui.loadUrlButton, QtCore.Qt.LeftButton)

    def alert_shown():
        m.assert_called_once_with(dialog, ANY, ANY)

    qtbot.wait_until(alert_shown)


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_disable_authentication_if_keystore_is_unavailable(qtbot, mocker):
    mocker.patch.object(Keystore, "is_available", return_value=False)
    with requests_mock.Mocker() as r:
        url = "http://localhost:8080/cc.xml"
        r.get(url, text=fake_content())

        dialog = ServerConfigurationDialog(ServerSettings(url), TIMEOUT, HttpConnection())
        dialog.show()
        qtbot.addWidget(dialog)

        def alert_shown():
            assert not dialog.ui.username.isEnabled()
            assert not dialog.ui.password.isEnabled()
            assert dialog.ui.authenticationSettings.title() == "Authentication (keyring dependency missing)"

        qtbot.wait_until(alert_shown)


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_show_error_and_reenable_load_for_non_xml_response(qtbot, mocker):
    with requests_mock.Mocker() as r:
        url = "http://localhost:8080/cc.xml"
        r.get(url, text="<html><body>Please log in</body></html")
        dialog = ServerConfigurationDialog(ServerSettings(url), TIMEOUT, HttpConnection())
        dialog.show()
        qtbot.addWidget(dialog)
        m = mocker.patch.object(QMessageBox, "critical", return_value=QMessageBox.Ok)

        qtbot.mouseClick(dialog.ui.loadUrlButton, QtCore.Qt.LeftButton)

        def alert_shown():
            m.assert_called_once_with(dialog, ANY, ANY)
            assert dialog.ui.loadUrlButton.isEnabled()

        qtbot.wait_until(alert_shown)


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_read_widgets_and_load_results_on_the_gui_thread(qtbot, mocker):
    with requests_mock.Mocker() as r:
        url = "http://localhost:8080/cc.xml"
        r.get(url, text=fake_content())
        loaded = []
        original_load = ServerConfigurationDialog.load_data

        def load_data(dialog, response):
            loaded.append(threading.get_ident())
            original_load(dialog, response)

        mocker.patch.object(ServerConfigurationDialog, "load_data", load_data)
        dialog = ServerConfigurationDialog(ServerSettings(url), TIMEOUT, HttpConnection())
        qtbot.addWidget(dialog)
        threads = []
        original = dialog.get_server_config

        def get_server_config():
            threads.append(threading.get_ident())
            return original()

        mocker.patch.object(dialog, "get_server_config", get_server_config)
        qtbot.mouseClick(dialog.ui.loadUrlButton, QtCore.Qt.LeftButton)

        qtbot.waitUntil(lambda: dialog.ui.projectsList.model() is not None)
        assert dialog.loads.waitForDone(5000)

    assert threads == [threading.get_ident()]
    assert loaded == [threading.get_ident()]


@pytest.mark.functional
def test_should_keep_saved_skip_ssl_verification_when_editing(qtbot):
    url = "https://localhost:8080/cc.xml"
    dialog = ServerConfigurationDialog(ServerSettings(url, skip_ssl_verification=True), TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    assert dialog.get_server_config().skip_ssl_verification is True


@pytest.mark.functional
def test_should_raise_not_implemented_error_for_unknown_authentication_type(qtbot):
    dialog = ServerConfigurationDialog(None, TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    with pytest.raises(NotImplementedError):
        dialog.set_authentication_type(99)


@pytest.mark.functional
def test_should_reject_file_urls_with_a_clear_message(qtbot, mocker):
    url = "file:///tmp/cctray.xml"
    dialog = ServerConfigurationDialog(ServerSettings(url), TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)
    m = mocker.patch.object(QMessageBox, "critical", return_value=QMessageBox.Ok)

    dialog.fetch_data()

    m.assert_called_once_with(dialog, "Invalid input", "Only http:// and https:// URLs are supported.")
    assert dialog.ui.loadUrlButton.isEnabled()
    assert not hasattr(dialog, "project_loader")


@pytest.mark.functional
def test_should_load_projects_through_the_injected_connection(qtbot):
    url = "http://localhost:8080/cc.xml"
    connection = FakeConnection(fake_content())
    dialog = ServerConfigurationDialog(ServerSettings(url), TIMEOUT, connection)
    qtbot.addWidget(dialog)

    dialog.fetch_data()
    qtbot.waitUntil(lambda: dialog.ui.projectsList.model() is not None)

    assert connection.urls == [url]


@pytest.mark.functional
def test_should_give_up_on_a_load_that_misses_the_deadline(qtbot, mocker):
    url = "http://localhost:8080/cc.xml"
    connection = GatedConnection(fake_content(), slow=[url])
    mocker.patch.object(ServerConfigurationDialog, "DEADLINE_GRACE_MS", 50)
    dialog = ServerConfigurationDialog(ServerSettings(url), 0, connection)
    qtbot.addWidget(dialog)
    m = mocker.patch.object(QMessageBox, "critical", return_value=QMessageBox.Ok)

    try:
        dialog.fetch_data()

        def alert_shown():
            m.assert_called_once_with(dialog, "Failed to fetch projects", ANY)
            assert dialog.ui.loadUrlButton.isEnabled()

        qtbot.wait_until(alert_shown, timeout=2000)
    finally:
        connection.release.set()
    assert dialog.loads.waitForDone(5000)
    qtbot.wait(50)

    assert dialog.ui.stackedWidget.currentIndex() == 0
    assert m.call_count == 1
