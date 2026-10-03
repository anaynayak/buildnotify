import threading
from pathlib import Path
from unittest.mock import ANY

import pytest
import requests
import requests_mock
from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QMessageBox

from buildnotifylib.adapters.http import HttpConnection
from buildnotifylib.core.ports import Response
from buildnotifylib.core.settings import ServerSettings, SourceKind
from buildnotifylib.ui.dialogs.server.auth_form import NONE, PASSWORD, TOKEN, AuthForm, Credentials
from buildnotifylib.ui.dialogs.server.cctray_form import CctrayForm
from buildnotifylib.ui.dialogs.server.dialog import ServerConfigurationDialog
from buildnotifylib.ui.dialogs.server.github_form import GithubForm, GithubSource
from buildnotifylib.ui.poller import Deadline
from test.utils import FakeConnection, GatedConnection, fake_content

TIMEOUT = 10
QWIDGETSIZE_MAX = 16777215
FEED_OFFSET = "Use the feed's offset"


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_show_configured_urls(qtbot):
    with requests_mock.Mocker() as m:
        url = "http://localhost:8080/cc.xml"
        m.get(url, text=fake_content())
        dialog = ServerConfigurationDialog(ServerSettings(url), TIMEOUT, HttpConnection())
        dialog.show()
        qtbot.addWidget(dialog)
        qtbot.mouseClick(dialog.test_button, QtCore.Qt.MouseButton.LeftButton)

        qtbot.waitUntil(lambda: dialog.projects_view.model() is not None)
        model = dialog.projects_view.model()
        assert model.item(0, 0).hasChildren()
        assert model.item(0, 0).child(0, 0).isCheckable()
        assert model.item(0, 0).child(0, 0).checkState() == Qt.CheckState.Checked
        assert model.item(0, 0).child(0, 0).text() == "cleanup-artifacts-B"

        assert dialog.timezone.currentText() == FEED_OFFSET


@pytest.mark.functional
def test_should_fall_back_to_none_for_unknown_stored_timezone(qtbot):
    url = "http://localhost:8080/cc.xml"
    dialog = ServerConfigurationDialog(ServerSettings(url, timezone="EDT"), TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    assert dialog.timezone.currentText() == FEED_OFFSET


@pytest.mark.functional
def test_should_list_zoneinfo_timezones_sorted(qtbot):
    dialog = ServerConfigurationDialog(None, TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)
    zones = [dialog.timezone.itemText(i) for i in range(dialog.timezone.count())]

    assert zones[0] == FEED_OFFSET
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
        qtbot.mouseClick(dialog.test_button, QtCore.Qt.MouseButton.LeftButton)

        qtbot.waitUntil(lambda: dialog.projects_view.model() is not None)
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
        qtbot.mouseClick(dialog.test_button, QtCore.Qt.MouseButton.LeftButton)

        qtbot.waitUntil(lambda: dialog.projects_view.model() is not None)
        model = dialog.projects_view.model()

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
        qtbot.mouseClick(dialog.test_button, QtCore.Qt.MouseButton.LeftButton)

        qtbot.waitUntil(lambda: dialog.projects_view.model() is not None)
        model = dialog.projects_view.model()

        assert model.item(0, 0).hasChildren()
        assert model.item(0, 0).child(0, 0).isCheckable()
        assert model.item(0, 0).child(0, 0).text() == "cleanup-artifacts-B"
        assert model.item(0, 0).child(0, 0).checkState() == Qt.CheckState.Unchecked

        def timezone():
            assert dialog.timezone.count() > 100
            assert dialog.timezone.currentText() == "US/Eastern"

        qtbot.waitUntil(timezone)


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
            assert not dialog.auth.username.isEnabled()
            assert not dialog.auth.password.isEnabled()
            assert dialog.auth.title() == "Authentication (keyring dependency missing)"

        qtbot.wait_until(alert_shown)


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_show_an_inline_error_and_reenable_test_for_non_xml_response(qtbot, mocker):
    with requests_mock.Mocker() as r:
        url = "http://localhost:8080/cc.xml"
        r.get(url, text="<html><body>Please log in</body></html")
        dialog = ServerConfigurationDialog(ServerSettings(url), TIMEOUT, HttpConnection())
        dialog.show()
        qtbot.addWidget(dialog)
        m = mocker.patch.object(QMessageBox, "critical")

        qtbot.mouseClick(dialog.test_button, QtCore.Qt.MouseButton.LeftButton)

        def error_shown():
            assert dialog.test_status.error
            assert dialog.test_button.isEnabled()

        qtbot.wait_until(error_shown)
        m.assert_not_called()
        assert dialog.cctray.url.text() == url


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
        qtbot.mouseClick(dialog.test_button, QtCore.Qt.MouseButton.LeftButton)

        qtbot.waitUntil(lambda: dialog.projects_view.model() is not None)
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
        dialog.auth.set_authentication_type(99)


@pytest.mark.functional
def test_should_reject_file_urls_with_a_clear_message(qtbot, mocker):
    url = "file:///tmp/cctray.xml"
    dialog = ServerConfigurationDialog(ServerSettings(url), TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)
    m = mocker.patch.object(QMessageBox, "critical")

    dialog.fetch_data()

    m.assert_not_called()
    assert dialog.cctray.message.error
    assert dialog.cctray.message.text() == "Only http:// and https:// URLs are supported."
    assert dialog.test_button.isEnabled()
    assert not hasattr(dialog, "project_loader")


@pytest.mark.functional
def test_should_load_projects_through_the_injected_connection(qtbot):
    url = "http://localhost:8080/cc.xml"
    connection = FakeConnection(fake_content())
    dialog = ServerConfigurationDialog(ServerSettings(url), TIMEOUT, connection)
    qtbot.addWidget(dialog)

    dialog.fetch_data()
    qtbot.waitUntil(lambda: dialog.projects_view.model() is not None)

    assert connection.urls == [url]


@pytest.mark.functional
def test_should_give_up_on_a_test_that_misses_the_deadline(qtbot, mocker):
    url = "http://localhost:8080/cc.xml"
    connection = GatedConnection(fake_content(), slow=[url])
    mocker.patch.object(Deadline, "GRACE_MS", 50)
    dialog = ServerConfigurationDialog(ServerSettings(url), 0, connection)
    qtbot.addWidget(dialog)
    try:
        dialog.fetch_data()

        def error_shown():
            assert dialog.test_status.error
            assert dialog.test_button.isEnabled()

        qtbot.wait_until(error_shown, timeout=2000)
    finally:
        connection.release.set()
    assert dialog.loads.waitForDone(5000)
    qtbot.wait(50)

    assert dialog.test_status.text() == "no response before the load deadline"
    assert not dialog.projects_loaded


@pytest.mark.functional
def test_should_offer_to_retry_without_verification_after_an_ssl_error(qtbot, mocker):
    url = "https://localhost:8080/cc.xml"
    with requests_mock.Mocker() as m:
        m.get(url, [{"exc": requests.exceptions.SSLError("bad-certificate")}, {"text": fake_content()}])
        dialog = ServerConfigurationDialog(ServerSettings(url), TIMEOUT, HttpConnection())
        qtbot.addWidget(dialog)
        question = mocker.patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes)

        dialog.fetch_data()
        qtbot.waitUntil(lambda: dialog.projects_loaded)

    yes, no = QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No
    question.assert_called_once_with(dialog, "Failed to fetch projects", ANY, yes | no, no)
    assert "bad-certificate" in question.call_args.args[2]
    assert dialog.get_server_config().skip_ssl_verification is True
    assert [r.verify for r in m.request_history] == [True, False]


@pytest.mark.functional
def test_should_turn_certificate_checks_back_on_when_the_host_changes(qtbot, mocker):
    url = "https://localhost:8080/cc.xml"
    with requests_mock.Mocker() as m:
        m.get(url, [{"exc": requests.exceptions.SSLError("bad-certificate")}, {"text": fake_content()}])
        dialog = ServerConfigurationDialog(ServerSettings(url), TIMEOUT, HttpConnection())
        qtbot.addWidget(dialog)
        mocker.patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes)
        dialog.fetch_data()
        qtbot.waitUntil(lambda: dialog.projects_loaded)

    dialog.cctray.url.setText("https://ci.example.com/cc.xml")
    assert dialog.get_server_config().skip_ssl_verification is False

    dialog.cctray.url.setText("https://localhost:8080/other.xml")
    assert dialog.get_server_config().skip_ssl_verification is True


@pytest.mark.functional
def test_should_keep_a_stored_certificate_skip_only_for_its_host(qtbot):
    url = "https://localhost:8080/cc.xml"
    dialog = ServerConfigurationDialog(ServerSettings(url, skip_ssl_verification=True), TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    dialog.cctray.url.setText("https://ci.example.com/cc.xml")
    assert dialog.get_server_config().skip_ssl_verification is False

    dialog.cctray.url.setText("https://localhost:8080/cc.xml")
    assert dialog.get_server_config().skip_ssl_verification is True


URL_JENKINS = "http://jenkins.local:8080/cc.xml"
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

    assert dialog.source_kind.currentText() == "cctray feed"
    assert dialog.github.isHidden()
    assert not dialog.cctray.isHidden()
    assert not dialog.auth.authentication_type.isHidden()


@pytest.mark.functional
def test_should_show_github_fields_when_github_is_selected(qtbot):
    dialog = ServerConfigurationDialog(None, TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    dialog.source_kind.setCurrentIndex(1)

    assert not dialog.github.isHidden()
    assert dialog.cctray.isHidden()
    assert dialog.auth.authentication_type.isHidden()
    assert dialog.auth.username.isHidden()
    assert dialog.timezone.isHidden()
    assert dialog.auth.password_label.text().replace("&", "") == "Token"

    dialog.source_kind.setCurrentIndex(0)

    assert dialog.github.isHidden()
    assert not dialog.auth.authentication_type.isHidden()


@pytest.mark.functional
def test_should_round_trip_a_github_server(qtbot):
    server = github_server(workflow="ci.yml", branch="main", prefix="gh")
    dialog = ServerConfigurationDialog(server, TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    assert dialog.source_kind.currentText() == "GitHub Actions"
    assert dialog.github.repository.text() == "octo-org/hello-world"
    assert dialog.get_server_config() == server


@pytest.mark.functional
@pytest.mark.parametrize("repository", ["", "hello-world", "octo-org/hello/world", "https://gitlab.com/a/b"])
def test_should_ask_for_an_owner_and_name(qtbot, mocker, repository):
    dialog = ServerConfigurationDialog(None, TIMEOUT, FakeApi())
    qtbot.addWidget(dialog)
    dialog.source_kind.setCurrentIndex(1)
    dialog.github.repository.setText(repository)
    m = mocker.patch.object(QMessageBox, "critical")

    dialog.fetch_data()

    m.assert_not_called()
    assert dialog.github.message.error
    assert dialog.github.message.text() == "Enter the repository as owner/name."


@pytest.mark.functional
def test_should_load_github_workflows_to_choose_from(qtbot):
    api = FakeApi()
    dialog = ServerConfigurationDialog(github_server(branch="main"), TIMEOUT, api)
    qtbot.addWidget(dialog)

    dialog.fetch_data()
    qtbot.waitUntil(lambda: dialog.projects_view.model() is not None)

    names = [dialog.projects_list.child(i).text() for i in range(dialog.projects_list.rowCount())]
    assert names[0] == "CI (main)"
    assert api.requested == ["https://api.github.com/repos/octo-org/hello-world/actions/runs?per_page=100&branch=main"]


@pytest.mark.functional
def test_should_not_carry_a_cctray_token_over_to_github(qtbot):
    server = ServerSettings(URL_JENKINS, password="jenkins-token", authentication_type=ServerSettings.AUTH_BEARER_TOKEN)
    dialog = ServerConfigurationDialog(server, TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    dialog.source_kind.setCurrentIndex(1)

    assert dialog.auth.password.text() == ""


@pytest.mark.functional
def test_should_restore_the_cctray_authentication_type_after_switching_back(qtbot):
    dialog = ServerConfigurationDialog(ServerSettings(URL_JENKINS, username="alice"), TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    dialog.source_kind.setCurrentIndex(1)
    dialog.source_kind.setCurrentIndex(0)

    assert dialog.auth.authentication_type.currentIndex() == PASSWORD
    assert not dialog.auth.username.isHidden()
    assert dialog.auth.password_label.text().replace("&", "") == "Password"


@pytest.mark.functional
@pytest.mark.parametrize("kind", [SourceKind.CCTRAY, SourceKind.GITHUB])
def test_should_keep_the_mutes_of_an_edited_server(qtbot, kind):
    server = ServerSettings("http://ci/cc.xml", kind=kind, repository="o/r", muted=True, muted_projects=["api"])
    dialog = ServerConfigurationDialog(server, TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    edited = dialog.get_server_config()

    assert (edited.muted, edited.muted_projects) == (True, ["api"])


@pytest.mark.functional
def test_should_round_trip_each_source_form(qtbot):
    cctray, github, auth = CctrayForm(), GithubForm(), AuthForm()
    for form in (cctray, github, auth):
        qtbot.addWidget(form)
    credentials = Credentials(ServerSettings.AUTH_USERNAME_PASSWORD, "alice", "secret")

    cctray.set_value(URL_JENKINS)
    github.set_value(GithubSource(" octo-org/hello-world ", "ci.yml", "main"))
    auth.set_value(credentials)

    assert cctray.value() == URL_JENKINS
    assert github.value() == GithubSource("octo-org/hello-world", "ci.yml", "main")
    assert auth.value() == credentials


@pytest.mark.functional
def test_should_hide_the_username_label_with_its_field(qtbot):
    auth = AuthForm()
    qtbot.addWidget(auth)

    auth.set_value(Credentials(ServerSettings.AUTH_BEARER_TOKEN, "", "token"))

    assert auth.username.isHidden()
    assert auth.username_label.isHidden()


@pytest.mark.functional
def test_should_not_cap_the_dialog_size(qtbot):
    dialog = ServerConfigurationDialog(None, TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    assert dialog.maximumSize() == QtCore.QSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)


@pytest.mark.functional
@pytest.mark.parametrize(
    ("server", "title"),
    [
        (None, "Add server"),
        (ServerSettings(URL_JENKINS, prefix="jenkins"), "Edit server - jenkins"),
        (ServerSettings(URL_JENKINS), "Edit server - jenkins.local:8080"),
        (github_server(), "Edit server - octo-org/hello-world"),
    ],
)
def test_should_title_the_dialog_for_adding_or_editing(qtbot, server, title):
    dialog = ServerConfigurationDialog(server, TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == title


@pytest.mark.functional
@pytest.mark.parametrize(
    ("typed", "url"),
    [
        ("ci.example.org/cc.xml", "https://ci.example.org/cc.xml"),
        (" ci.example.org:8153/go/cctray.xml ", "https://ci.example.org:8153/go/cctray.xml"),
        ("http://ci.example.org/cc.xml", "http://ci.example.org/cc.xml"),
    ],
)
def test_should_default_a_url_without_a_scheme_to_https(qtbot, typed, url):
    connection = FakeConnection(fake_content())
    dialog = ServerConfigurationDialog(None, TIMEOUT, connection)
    qtbot.addWidget(dialog)

    dialog.cctray.url.setText(typed)
    dialog.cctray.url.editingFinished.emit()
    dialog.fetch_data()
    qtbot.waitUntil(lambda: connection.urls != [])

    assert dialog.cctray.url.text() == url
    assert dialog.get_server_config().url == url
    assert connection.urls == [url]


@pytest.mark.functional
def test_should_show_an_error_under_an_empty_url_when_it_loses_focus(qtbot):
    dialog = ServerConfigurationDialog(None, TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    dialog.cctray.url.editingFinished.emit()

    assert not dialog.cctray.message.isHidden()
    assert dialog.cctray.message.text() == "Enter the feed URL."


@pytest.mark.functional
def test_should_clear_the_url_error_once_the_url_is_valid(qtbot):
    dialog = ServerConfigurationDialog(None, TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)
    dialog.cctray.url.editingFinished.emit()

    dialog.cctray.url.setText("ci.example.org/cc.xml")

    assert dialog.cctray.message.isHidden()


@pytest.mark.functional
def test_should_save_a_new_server_without_testing_it_with_all_projects(qtbot):
    connection = FakeConnection(fake_content())
    dialog = ServerConfigurationDialog(None, TIMEOUT, connection)
    qtbot.addWidget(dialog)

    dialog.cctray.url.setText("ci.example.org/cc.xml")
    qtbot.mouseClick(dialog.save_button, QtCore.Qt.MouseButton.LeftButton)

    assert dialog.result() == QDialog.DialogCode.Accepted
    saved = dialog.get_server_config()
    assert (saved.url, saved.excluded_projects) == ("https://ci.example.org/cc.xml", [])
    assert connection.urls == []


@pytest.mark.functional
def test_should_keep_the_exclusions_of_an_edited_server_saved_without_testing(qtbot):
    server = ServerSettings(URL_JENKINS, ["cleanup-artifacts-B"])
    dialog = ServerConfigurationDialog(server, TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    dialog.save_button.click()

    assert dialog.result() == QDialog.DialogCode.Accepted
    assert dialog.get_server_config().excluded_projects == ["cleanup-artifacts-B"]


@pytest.mark.functional
@pytest.mark.parametrize("url", ["", "file:///tmp/cctray.xml"])
def test_should_disable_save_while_the_url_is_invalid(qtbot, url):
    dialog = ServerConfigurationDialog(None, TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    dialog.cctray.url.setText(url)
    assert not dialog.save_button.isEnabled()

    dialog.cctray.url.setText("http://ci/cc.xml")
    assert dialog.save_button.isEnabled()


@pytest.mark.functional
def test_should_enable_save_for_a_github_server_with_a_valid_repository(qtbot):
    dialog = ServerConfigurationDialog(None, TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)
    dialog.source_kind.setCurrentIndex(1)
    assert not dialog.save_button.isEnabled()

    dialog.github.repository.setText("octo-org/hello-world")

    assert dialog.save_button.isEnabled()


@pytest.mark.functional
def test_should_cancel_without_saving(qtbot):
    dialog = ServerConfigurationDialog(ServerSettings(URL_JENKINS), TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    dialog.cancel_button.click()

    assert dialog.result() == QDialog.DialogCode.Rejected


@pytest.mark.functional
def test_should_report_the_project_count_after_a_successful_test(qtbot):
    dialog = ServerConfigurationDialog(ServerSettings(URL_JENKINS), TIMEOUT, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)

    dialog.fetch_data()
    qtbot.waitUntil(lambda: dialog.projects_loaded)

    count = dialog.projects_list.rowCount()
    assert dialog.test_status.text() == f"OK - {count} projects found"
    assert not dialog.test_status.error
    assert not dialog.projects_view.isHidden()


@pytest.mark.functional
def test_should_keep_typed_values_after_a_failed_test(qtbot, mocker):
    connection = FakeConnection("")
    mocker.patch.object(connection, "connect", side_effect=ConnectionError("Could not connect to ci"))
    dialog = ServerConfigurationDialog(None, TIMEOUT, connection)
    qtbot.addWidget(dialog)
    dialog.cctray.url.setText("https://ci/cc.xml")
    dialog.prefix.setText("ci")

    dialog.fetch_data()
    qtbot.waitUntil(lambda: dialog.test_status.error)

    assert dialog.test_status.text() == "Could not connect to ci"
    assert (dialog.cctray.url.text(), dialog.prefix.text()) == ("https://ci/cc.xml", "ci")
    assert dialog.save_button.isEnabled()


@pytest.mark.functional
def test_should_show_a_certificate_error_inline_when_retry_is_declined(qtbot, mocker):
    url = "https://localhost:8080/cc.xml"
    with requests_mock.Mocker() as m:
        m.get(url, exc=requests.exceptions.SSLError("bad-certificate"))
        dialog = ServerConfigurationDialog(ServerSettings(url), TIMEOUT, HttpConnection())
        qtbot.addWidget(dialog)
        mocker.patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.No)

        dialog.fetch_data()
        qtbot.waitUntil(lambda: dialog.test_status.error)

    assert dialog.test_status.text() == "Certificate not trusted"
    assert dialog.get_server_config().skip_ssl_verification is False
    assert m.call_count == 1


def loaded_dialog(qtbot, server):
    dialog = ServerConfigurationDialog(server, TIMEOUT, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    dialog.fetch_data()
    qtbot.waitUntil(lambda: dialog.projects_loaded)
    dialog.projects_list.child(1).setCheckState(Qt.CheckState.Unchecked)
    return dialog


@pytest.mark.functional
@pytest.mark.parametrize(
    "change",
    [
        lambda dialog: dialog.cctray.url.setText("https://other.example.org/cc.xml"),
        lambda dialog: dialog.source_kind.setCurrentIndex(1),
    ],
)
def test_should_forget_a_test_once_the_source_changes(qtbot, change):
    dialog = loaded_dialog(qtbot, ServerSettings(URL_JENKINS, ["cleanup-artifacts-B"]))

    change(dialog)

    assert dialog.test_status.isHidden()
    assert dialog.projects_view.isHidden()
    assert not dialog.projects_hint.isHidden()
    assert dialog.get_server_config().excluded_projects == ["cleanup-artifacts-B"]


@pytest.mark.functional
def test_should_drop_a_running_test_once_the_url_changes(qtbot):
    url = "http://localhost:8080/cc.xml"
    connection = GatedConnection(fake_content(), slow=[url])
    dialog = ServerConfigurationDialog(ServerSettings(url), TIMEOUT, connection)
    qtbot.addWidget(dialog)

    dialog.fetch_data()
    dialog.cctray.url.setText("http://other/cc.xml")
    connection.release.set()
    assert dialog.loads.waitForDone(5000)
    qtbot.wait(50)

    assert not dialog.projects_loaded
    assert dialog.test_button.isEnabled()


@pytest.mark.functional
def test_should_drop_a_running_test_once_the_dialog_closes(qtbot):
    url = "http://localhost:8080/cc.xml"
    connection = GatedConnection(fake_content(), slow=[url])
    dialog = ServerConfigurationDialog(ServerSettings(url), TIMEOUT, connection)
    qtbot.addWidget(dialog)

    dialog.fetch_data()
    dialog.cancel_button.click()
    connection.release.set()
    assert dialog.loads.waitForDone(5000)
    qtbot.wait(50)

    assert not dialog.projects_loaded


def picker_dialog(qtbot, excluded=()):
    server = ServerSettings(URL_JENKINS, list(excluded))
    dialog = ServerConfigurationDialog(server, TIMEOUT, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    dialog.fetch_data()
    qtbot.waitUntil(lambda: dialog.projects_loaded)
    return dialog


def child_states(dialog):
    root = dialog.projects_list
    return [root.child(i).checkState() for i in range(root.rowCount())]


@pytest.mark.functional
def test_should_reflect_the_children_in_the_all_box(qtbot):
    dialog = picker_dialog(qtbot)
    assert dialog.projects_list.checkState() == Qt.CheckState.Checked

    dialog.projects_list.child(1).setCheckState(Qt.CheckState.Unchecked)
    assert dialog.projects_list.checkState() == Qt.CheckState.PartiallyChecked

    for i in range(dialog.projects_list.rowCount()):
        dialog.projects_list.child(i).setCheckState(Qt.CheckState.Unchecked)
    assert dialog.projects_list.checkState() == Qt.CheckState.Unchecked


@pytest.mark.functional
def test_should_start_partially_checked_when_some_are_excluded(qtbot):
    dialog = picker_dialog(qtbot, ["orbit-I"])

    assert dialog.projects_list.checkState() == Qt.CheckState.PartiallyChecked


@pytest.mark.functional
def test_should_set_every_child_when_all_is_toggled(qtbot):
    dialog = picker_dialog(qtbot, ["orbit-I"])

    dialog.projects_list.setCheckState(Qt.CheckState.Checked)
    assert set(child_states(dialog)) == {Qt.CheckState.Checked}
    assert dialog.excluded_projects() == []

    dialog.projects_list.setCheckState(Qt.CheckState.Unchecked)
    assert set(child_states(dialog)) == {Qt.CheckState.Unchecked}
    assert len(dialog.excluded_projects()) == 7


def visible_names(dialog):
    root = dialog.projects_list
    view = dialog.projects_view
    return [root.child(i).text() for i in range(root.rowCount()) if not view.isRowHidden(i, root.index())]


@pytest.mark.functional
def test_should_narrow_the_list_by_substring(qtbot):
    dialog = picker_dialog(qtbot)

    dialog.projects_filter.setText("ORBIT")
    assert visible_names(dialog) == ["orbit-I", "orbit-M", "orbit-R", "orbit-S"]

    dialog.projects_filter.setText("")
    assert len(visible_names(dialog)) == 7


@pytest.mark.functional
def test_should_toggle_only_the_visible_projects(qtbot):
    dialog = picker_dialog(qtbot)
    dialog.projects_filter.setText("orbit")

    dialog.projects_list.setCheckState(Qt.CheckState.Unchecked)

    assert dialog.excluded_projects() == ["orbit-I", "orbit-M", "orbit-R", "orbit-S"]
    assert dialog.projects_list.checkState() == Qt.CheckState.PartiallyChecked


@pytest.mark.functional
def test_should_count_the_included_projects_in_the_header(qtbot):
    dialog = picker_dialog(qtbot, ["orbit-I", "orbit-M"])
    assert dialog.projects_list.text() == "All (5 of 7)"

    dialog.projects_list.setCheckState(Qt.CheckState.Checked)
    assert dialog.projects_list.text() == "All (7 of 7)"


@pytest.mark.functional
def test_should_say_that_new_projects_are_included(qtbot):
    dialog = picker_dialog(qtbot)

    assert not dialog.projects_note.isHidden()
    assert "new projects" in dialog.projects_note.text().lower()


@pytest.mark.functional
def test_should_show_the_full_name_as_a_tooltip(qtbot):
    dialog = picker_dialog(qtbot)

    assert dialog.projects_list.child(2).toolTip() == "ganymaticPack»R3.0-I"
    assert dialog.projects_view.textElideMode() == Qt.TextElideMode.ElideMiddle


def test_should_offer_none_password_and_token_sign_in(qtbot):
    auth = AuthForm()
    qtbot.addWidget(auth)
    items = [auth.authentication_type.itemText(i) for i in range(auth.authentication_type.count())]
    assert items == ["None", "Username and password", "Token"]


def test_should_hide_both_fields_and_save_blank_credentials_for_none(qtbot):
    auth = AuthForm()
    qtbot.addWidget(auth)
    auth.set_value(Credentials(ServerSettings.AUTH_USERNAME_PASSWORD, "alice", "secret"))

    auth.authentication_type.setCurrentIndex(NONE)

    assert auth.username.isHidden() and auth.password.isHidden()
    assert auth.value() == Credentials(ServerSettings.AUTH_USERNAME_PASSWORD, "", "")


def test_should_start_a_new_server_with_no_sign_in(qtbot):
    dialog = ServerConfigurationDialog(None, TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    assert dialog.auth.authentication_type.currentIndex() == NONE
    assert dialog.auth.username.isHidden() and dialog.auth.password.isHidden()


def test_should_show_username_and_password_fields_for_password_sign_in(qtbot):
    auth = AuthForm()
    qtbot.addWidget(auth)
    auth.set_value(Credentials(ServerSettings.AUTH_USERNAME_PASSWORD, "alice", "secret"))

    assert auth.authentication_type.currentIndex() == PASSWORD
    assert not auth.username.isHidden() and not auth.password.isHidden()
    assert auth.password_label.text().replace("&", "") == "Password"


def test_should_label_a_stored_bearer_token_as_a_token(qtbot):
    auth = AuthForm()
    qtbot.addWidget(auth)
    credentials = Credentials(ServerSettings.AUTH_BEARER_TOKEN, "", "tok")

    auth.set_value(credentials)

    assert auth.authentication_type.currentIndex() == TOKEN
    assert auth.username.isHidden() and not auth.password.isHidden()
    assert auth.password_label.text().replace("&", "") == "Bearer token"
    assert auth.password.placeholderText() != ""
    assert auth.value() == credentials


def test_should_name_the_package_to_install_when_there_is_no_keyring(qtbot):
    dialog = ServerConfigurationDialog(None, TIMEOUT, HttpConnection(), keystore_available=False)
    qtbot.addWidget(dialog)
    dialog.show()

    assert dialog.auth.message.isVisible()
    assert "can't be stored" in dialog.auth.message.text()
    assert "'keyring'" in dialog.auth.message.text()


def accepted_certificate_dialog(qtbot, mocker, m, url="https://localhost:8080/cc.xml"):
    m.get(url, [{"exc": requests.exceptions.SSLError("bad-certificate")}, {"text": fake_content()}])
    dialog = ServerConfigurationDialog(ServerSettings(url), TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)
    question = mocker.patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes)
    dialog.fetch_data()
    qtbot.waitUntil(lambda: dialog.projects_loaded)
    return dialog, question


@pytest.mark.functional
def test_should_word_the_certificate_prompt_for_the_host(qtbot, mocker):
    with requests_mock.Mocker() as m:
        _, question = accepted_certificate_dialog(qtbot, mocker, m)

    text = question.call_args.args[2]
    assert "certificate for localhost:8080 isn't trusted" in text
    assert "Connect anyway?" in text
    assert "turns off certificate checks for this server" in text


@pytest.mark.functional
def test_should_show_that_certificate_checks_are_off_after_accepting(qtbot, mocker):
    with requests_mock.Mocker() as m:
        dialog, _ = accepted_certificate_dialog(qtbot, mocker, m)

    assert not dialog.certificate_status.isHidden()
    assert dialog.certificate_status.text() == "Certificate checks off for localhost:8080"
    assert not dialog.certificate_undo.isHidden()


@pytest.mark.functional
def test_should_hide_the_certificate_indicator_when_checks_are_on(qtbot):
    dialog = ServerConfigurationDialog(None, TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    assert dialog.certificate_status.isHidden()
    assert dialog.certificate_undo.isHidden()


@pytest.mark.functional
def test_should_undo_the_certificate_skip_from_the_indicator(qtbot, mocker):
    with requests_mock.Mocker() as m:
        dialog, _ = accepted_certificate_dialog(qtbot, mocker, m)

    dialog.certificate_undo.click()

    assert dialog.get_server_config().skip_ssl_verification is False
    assert dialog.certificate_status.isHidden()
    assert dialog.certificate_undo.isHidden()


@pytest.mark.functional
def test_should_show_the_indicator_for_a_stored_certificate_skip(qtbot):
    url = "https://localhost:8080/cc.xml"
    dialog = ServerConfigurationDialog(ServerSettings(url, skip_ssl_verification=True), TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)

    assert not dialog.certificate_status.isHidden()
    dialog.cctray.url.setText("https://other.example.org/cc.xml")
    assert dialog.certificate_status.isHidden()


@pytest.mark.parametrize(
    "pasted",
    [
        "https://github.com/octo-org/hello-world",
        "https://github.com/octo-org/hello-world/",
        "https://github.com/octo-org/hello-world.git",
        "http://www.github.com/octo-org/hello-world/actions/workflows/ci.yml",
        "github.com/octo-org/hello-world?tab=readme",
        " octo-org/hello-world ",
    ],
)
def test_should_accept_a_pasted_github_url_as_the_repository(qtbot, pasted):
    form = GithubForm()
    qtbot.addWidget(form)

    form.repository.setText(pasted)

    assert form.value().repository == "octo-org/hello-world"
    form.repository.editingFinished.emit()
    assert form.repository.text() == "octo-org/hello-world"


@pytest.mark.functional
def test_should_save_a_github_server_from_a_pasted_url(qtbot):
    dialog = ServerConfigurationDialog(None, TIMEOUT, FakeApi())
    qtbot.addWidget(dialog)
    dialog.source_kind.setCurrentIndex(1)

    dialog.github.repository.setText("https://github.com/octo-org/hello-world")

    assert dialog.save_button.isEnabled()
    assert dialog.get_server_config().repository == "octo-org/hello-world"


@pytest.mark.functional
def test_should_guide_the_user_to_create_a_github_token(qtbot):
    dialog = ServerConfigurationDialog(None, TIMEOUT, FakeApi())
    qtbot.addWidget(dialog)
    dialog.source_kind.setCurrentIndex(1)

    text = dialog.auth.token_help.text()
    assert not dialog.auth.token_help.isHidden()
    assert 'href="https://github.com/settings/personal-access-tokens/new"' in text
    assert "Actions: read" in text
    assert "60 requests an hour" in text

    dialog.source_kind.setCurrentIndex(0)
    assert dialog.auth.token_help.isHidden()


def open_dialog(qtbot, server=None):
    dialog = ServerConfigurationDialog(server, TIMEOUT, HttpConnection())
    qtbot.addWidget(dialog)
    dialog.show()
    return dialog


def test_should_collapse_advanced_when_everything_is_default(qtbot):
    dialog = open_dialog(qtbot, ServerSettings("http://localhost:8080/cc.xml"))

    assert dialog.advanced.toggle.text() == "&Advanced"
    assert not dialog.advanced.is_expanded()
    assert not dialog.timezone.isVisible()


def test_should_expand_advanced_when_the_time_zone_is_not_the_default(qtbot):
    dialog = open_dialog(qtbot, ServerSettings("http://localhost:8080/cc.xml", timezone="Asia/Kolkata"))

    assert dialog.advanced.is_expanded()
    assert dialog.timezone.isVisible()


def test_should_expand_advanced_when_certificate_checks_are_off(qtbot):
    url = "https://localhost:8080/cc.xml"
    dialog = open_dialog(qtbot, ServerSettings(url, skip_ssl_verification=True))

    assert dialog.advanced.is_expanded()
    assert dialog.certificate_undo.isVisible()


def test_should_expand_advanced_when_a_retry_without_verification_is_accepted(qtbot, mocker):
    url = "https://localhost:8080/cc.xml"
    with requests_mock.Mocker() as m:
        m.get(url, [{"exc": requests.exceptions.SSLError("bad")}, {"text": fake_content()}])
        dialog = open_dialog(qtbot, ServerSettings(url))
        mocker.patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes)
        dialog.fetch_data()
        qtbot.waitUntil(lambda: dialog.projects_loaded)

    assert dialog.advanced.is_expanded()


def test_should_label_the_time_zone_field_for_feed_times(qtbot):
    dialog = open_dialog(qtbot, None)

    assert dialog.timezone_form.labelForField(dialog.timezone).text() == "Time &zone for feed times"


def test_should_keep_none_as_the_stored_value_of_the_default_entry(qtbot):
    dialog = open_dialog(qtbot, ServerSettings("http://localhost:8080/cc.xml", timezone="Asia/Kolkata"))
    dialog.timezone.setCurrentIndex(0)

    assert dialog.timezone.currentText() == FEED_OFFSET
    assert dialog.get_server_config().timezone == "None"


def completions(dialog, text):
    completer = dialog.timezone.completer()
    completer.setCompletionPrefix(text)
    return [completer.completionModel().index(i, 0).data() for i in range(completer.completionCount())]


def test_should_complete_time_zones_by_substring(qtbot):
    dialog = open_dialog(qtbot, None)

    assert dialog.timezone.isEditable()
    assert "Asia/Kolkata" in completions(dialog, "Kolkata")


def test_should_ignore_case_when_completing_time_zones(qtbot):
    dialog = open_dialog(qtbot, None)

    assert "Asia/Kolkata" in completions(dialog, "kolkata")


def test_should_save_a_typed_time_zone(qtbot):
    dialog = open_dialog(qtbot, ServerSettings("http://localhost:8080/cc.xml"))
    dialog.timezone.setEditText("Asia/Kolkata")

    assert dialog.get_server_config().timezone == "Asia/Kolkata"


def test_should_save_a_time_zone_picked_from_the_list(qtbot):
    dialog = open_dialog(qtbot, ServerSettings("http://localhost:8080/cc.xml"))
    dialog.timezone.setCurrentIndex(dialog.timezone.findText("Europe/Paris"))

    assert dialog.get_server_config().timezone == "Europe/Paris"


def test_should_save_the_default_when_typed_text_is_not_a_time_zone(qtbot):
    dialog = open_dialog(qtbot, ServerSettings("http://localhost:8080/cc.xml", timezone="Asia/Kolkata"))
    dialog.timezone.setEditText("Kolka")

    assert dialog.get_server_config().timezone == "None"
