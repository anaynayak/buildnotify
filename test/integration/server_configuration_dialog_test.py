import threading
from pathlib import Path
from unittest.mock import ANY

import pytest
import requests
import requests_mock
from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from buildnotifylib.adapters.http import HttpConnection
from buildnotifylib.core.ports import Response
from buildnotifylib.core.settings import ServerSettings, SourceKind
from buildnotifylib.ui.dialogs.server_configuration_dialog import ServerConfigurationDialog
from buildnotifylib.ui.poller import Deadline
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
        qtbot.mouseClick(dialog.ui.loadUrlButton, QtCore.Qt.MouseButton.LeftButton)

        qtbot.waitUntil(lambda: dialog.ui.projectsList.model() is not None)
        model = dialog.ui.projectsList.model()
        assert model.item(0, 0).hasChildren()
        assert model.item(0, 0).child(0, 0).isCheckable()
        assert model.item(0, 0).child(0, 0).checkState() == Qt.CheckState.Checked
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
        qtbot.mouseClick(dialog.ui.loadUrlButton, QtCore.Qt.MouseButton.LeftButton)

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
        qtbot.mouseClick(dialog.ui.loadUrlButton, QtCore.Qt.MouseButton.LeftButton)

        qtbot.waitUntil(lambda: dialog.ui.projectsList.model() is not None)
        model = dialog.ui.projectsList.model()

        model.item(0, 0).child(0, 0).setCheckState(QtCore.Qt.CheckState.Unchecked)

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
        qtbot.mouseClick(dialog.ui.loadUrlButton, QtCore.Qt.MouseButton.LeftButton)

        qtbot.waitUntil(lambda: dialog.ui.projectsList.model() is not None)
        model = dialog.ui.projectsList.model()

        assert model.item(0, 0).hasChildren()
        assert model.item(0, 0).child(0, 0).isCheckable()
        assert model.item(0, 0).child(0, 0).text() == "cleanup-artifacts-B"
        assert model.item(0, 0).child(0, 0).checkState() == Qt.CheckState.Unchecked

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
    m = mocker.patch.object(QMessageBox, "critical", return_value=QMessageBox.StandardButton.No)

    qtbot.mouseClick(dialog.ui.loadUrlButton, QtCore.Qt.MouseButton.LeftButton)

    def alert_shown():
        m.assert_called_once_with(dialog, ANY, ANY)

    qtbot.wait_until(alert_shown)


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_disable_authentication_if_keystore_is_unavailable(qtbot):
    with requests_mock.Mocker() as r:
        url = "http://localhost:8080/cc.xml"
        r.get(url, text=fake_content())

        dialog = ServerConfigurationDialog(ServerSettings(url), TIMEOUT, HttpConnection(), keystore_available=False)
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
        m = mocker.patch.object(QMessageBox, "critical", return_value=QMessageBox.StandardButton.Ok)

        qtbot.mouseClick(dialog.ui.loadUrlButton, QtCore.Qt.MouseButton.LeftButton)

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
        qtbot.mouseClick(dialog.ui.loadUrlButton, QtCore.Qt.MouseButton.LeftButton)

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
    m = mocker.patch.object(QMessageBox, "critical", return_value=QMessageBox.StandardButton.Ok)

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
    mocker.patch.object(Deadline, "GRACE_MS", 50)
    dialog = ServerConfigurationDialog(ServerSettings(url), 0, connection)
    qtbot.addWidget(dialog)
    m = mocker.patch.object(QMessageBox, "critical", return_value=QMessageBox.StandardButton.Ok)

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


@pytest.mark.functional
def test_should_offer_to_retry_without_verification_after_an_ssl_error(qtbot, mocker):
    url = "https://localhost:8080/cc.xml"
    with requests_mock.Mocker() as m:
        m.get(url, [{"exc": requests.exceptions.SSLError("bad-certificate")}, {"text": fake_content()}])
        dialog = ServerConfigurationDialog(ServerSettings(url), TIMEOUT, HttpConnection())
        qtbot.addWidget(dialog)
        question = mocker.patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes)

        dialog.fetch_data()
        qtbot.waitUntil(lambda: dialog.ui.stackedWidget.currentIndex() == 1)

    yes, no = QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No
    question.assert_called_once_with(dialog, "Failed to fetch projects", ANY, yes | no, no)
    assert "bad-certificate" in question.call_args.args[2]
    assert dialog.get_server_config().skip_ssl_verification is True
    assert [r.verify for r in m.request_history] == [True, False]


GITHUB_RUNS = Path(__file__).parent.parent / "fixtures" / "github" / "runs.json"


class FakeApi(FakeConnection):
    def __init__(self):
        super().__init__("")
        self.requested: list[str] = []

    def request(self, url, timeout, headers, verify=True):
        self.requested.append(url)
        return Response(200, {}, GITHUB_RUNS.read_bytes())


def github_server(**fields):
    return ServerSettings(
        "",
        kind=SourceKind.GITHUB,
        repository="octo-org/hello-world",
        password="ghp_token",
        authentication_type=ServerSettings.AUTH_BEARER_TOKEN,
        **fields,
    )


@pytest.mark.functional
def test_should_show_cctray_fields_for_a_new_server(qtbot):
    dialog = ServerConfigurationDialog(None, TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    assert dialog.ui.sourceKind.currentText() == "cctray feed"
    assert dialog.ui.githubSettings.isHidden()
    assert not dialog.ui.addServerUrl.isHidden()
    assert not dialog.ui.authentication_type.isHidden()


@pytest.mark.functional
def test_should_show_github_fields_when_github_is_selected(qtbot):
    dialog = ServerConfigurationDialog(None, TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    dialog.ui.sourceKind.setCurrentIndex(1)

    assert not dialog.ui.githubSettings.isHidden()
    assert dialog.ui.addServerUrl.isHidden()
    assert dialog.ui.authentication_type.isHidden()
    assert dialog.ui.username.isHidden()
    assert dialog.ui.timezoneList.isHidden()
    assert dialog.ui.passwordLabel.text() == "Token"

    dialog.ui.sourceKind.setCurrentIndex(0)

    assert dialog.ui.githubSettings.isHidden()
    assert not dialog.ui.authentication_type.isHidden()


@pytest.mark.functional
def test_should_round_trip_a_github_server(qtbot):
    server = github_server(workflow="ci.yml", branch="main", prefix="gh")
    dialog = ServerConfigurationDialog(server, TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    assert dialog.ui.sourceKind.currentText() == "GitHub Actions"
    assert dialog.ui.repository.text() == "octo-org/hello-world"
    assert dialog.get_server_config() == server


@pytest.mark.functional
@pytest.mark.parametrize("repository", ["", "hello-world", "octo-org/hello/world", "https://github.com/a/b"])
def test_should_ask_for_an_owner_and_name(qtbot, mocker, repository):
    dialog = ServerConfigurationDialog(None, TIMEOUT, FakeApi())
    qtbot.addWidget(dialog)
    dialog.ui.sourceKind.setCurrentIndex(1)
    dialog.ui.repository.setText(repository)
    m = mocker.patch.object(QMessageBox, "critical", return_value=QMessageBox.StandardButton.Ok)

    dialog.fetch_data()

    m.assert_called_once_with(dialog, "Invalid input", "Enter the repository as owner/name.")


@pytest.mark.functional
def test_should_load_github_workflows_to_choose_from(qtbot):
    api = FakeApi()
    dialog = ServerConfigurationDialog(github_server(branch="main"), TIMEOUT, api)
    qtbot.addWidget(dialog)

    dialog.fetch_data()
    qtbot.waitUntil(lambda: dialog.ui.projectsList.model() is not None)

    names = [dialog.projects_list.child(i).text() for i in range(dialog.projects_list.rowCount())]
    assert names[0] == "CI (main)"
    assert api.requested == ["https://api.github.com/repos/octo-org/hello-world/actions/runs?per_page=100&branch=main"]
