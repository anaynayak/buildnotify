import os

import pytest
from PySide6 import QtCore
from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtWidgets import QDialog, QDialogButtonBox

from buildnotifylib.core.settings import DEFAULT_NOTIFICATIONS, AppSettings, ServerSettings, SortKey
from buildnotifylib.ui.dialogs.preferences import PreferencesDialog
from buildnotifylib.ui.dialogs.server_configuration_dialog import ServerConfigurationDialog
from test.fake_conf import ConfigBuilder
from test.utils import FakeConnection, fake_content


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_show_configured_urls(qtbot):
    file_path = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../../data/cctray.xml")
    conf = ConfigBuilder().server("file://" + file_path).build()
    dialog = PreferencesDialog(conf.settings, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    assert [str(s) for s in dialog.ui.cctrayPathList.model().stringList()] == ["file://" + file_path]


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_show_configure_notifications(qtbot):
    file_path = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../../data/cctray.xml")
    conf = ConfigBuilder().server("file://" + file_path).build()
    dialog = PreferencesDialog(conf.settings, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    dialog.show()
    dialog.ui.tabWidget.setCurrentIndex(1)
    assert dialog.ui.connectivityIssuesCheckbox.isChecked()
    assert dialog.ui.fixedBuildsCheckbox.isChecked()
    assert dialog.ui.brokenBuildsCheckbox.isChecked()
    assert not dialog.ui.successfulBuildsCheckbox.isChecked()
    assert not dialog.ui.scriptCheckbox.isChecked()
    assert dialog.ui.scriptLineEdit.text() == "echo #status# #projects# >> /tmp/buildnotify.log"


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_return_preferences_on_accept(qtbot):
    conf = ConfigBuilder().build()
    dialog = PreferencesDialog(conf.settings, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)

    def close_dialog():
        button = dialog.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok)
        qtbot.mouseClick(button, QtCore.Qt.MouseButton.LeftButton)

    QtCore.QTimer.singleShot(100, close_dialog)
    preferences = dialog.open()

    qtbot.waitUntil(lambda: preferences is not None)


@pytest.mark.functional
def test_should_prefill_server_config(qtbot, mocker):
    file_path = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../../data/cctray.xml")
    conf = ConfigBuilder().server("file://" + file_path).build()
    dialog = PreferencesDialog(conf.settings, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    dialog.show()

    index = dialog.ui.cctrayPathList.model().index(0, 0)
    dialog.ui.cctrayPathList.selectionModel().select(index, QItemSelectionModel.SelectionFlag.Select)
    dialog.ui.cctrayPathList.setCurrentIndex(index)

    m = mocker.patch.object(ServerConfigurationDialog, "open")

    qtbot.mouseClick(dialog.ui.configureProjectButton, Qt.MouseButton.LeftButton)

    qtbot.waitUntil(lambda: m.assert_any_call())


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_remove_configured_servers(qtbot):
    file_path = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../../data/cctray.xml")
    conf = ConfigBuilder().server("file://" + file_path).build()
    dialog = PreferencesDialog(conf.settings, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    dialog.show()

    index = dialog.ui.cctrayPathList.model().index(0, 0)
    dialog.ui.cctrayPathList.selectionModel().select(index, QItemSelectionModel.SelectionFlag.Select)
    dialog.ui.cctrayPathList.setCurrentIndex(index)

    qtbot.mouseClick(dialog.ui.removeButton, Qt.MouseButton.LeftButton)

    assert [str(s) for s in dialog.ui.cctrayPathList.model().stringList()] == []


@pytest.mark.functional
def test_should_not_remove_anything_without_a_selection(qtbot):
    conf = ConfigBuilder().server("http://one/cctray.xml").server("http://two/cctray.xml").build()
    dialog = PreferencesDialog(conf.settings, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)

    dialog.remove_element()

    assert dialog.get_urls() == ["http://one/cctray.xml", "http://two/cctray.xml"]


def select_row(dialog, row):
    index = dialog.ui.cctrayPathList.model().index(row, 0)
    dialog.ui.cctrayPathList.setCurrentIndex(index)


@pytest.mark.functional
def test_should_replace_the_row_when_a_server_url_is_edited(qtbot, mocker):
    conf = ConfigBuilder().server("http://one/cctray.xml").server("http://two/cctray.xml").build()
    dialog = PreferencesDialog(conf.settings, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    select_row(dialog, 0)
    mocker.patch.object(ServerConfigurationDialog, "open", return_value=ServerSettings("http://new/cctray.xml"))

    dialog.configure_projects()

    assert dialog.get_urls() == ["http://new/cctray.xml", "http://two/cctray.xml"]


def stub_server_dialog(mocker, url):
    mocker.patch.object(ServerConfigurationDialog, "open", return_value=ServerSettings(url, prefix="prefix"))


@pytest.mark.functional
def test_should_not_save_an_added_server_until_ok(qtbot, mocker):
    conf = ConfigBuilder().build()
    dialog = PreferencesDialog(conf.settings, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    stub_server_dialog(mocker, "http://new/cctray.xml")
    mocker.patch.object(dialog, "exec", return_value=QDialog.DialogCode.Rejected)

    dialog.add_server()
    preferences = dialog.open()

    assert preferences is None
    assert dialog.get_urls() == ["http://new/cctray.xml"]
    assert conf.settings.servers == []


@pytest.mark.functional
def test_should_return_an_added_server_on_ok(qtbot, mocker):
    conf = ConfigBuilder().build()
    dialog = PreferencesDialog(conf.settings, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    stub_server_dialog(mocker, "http://new/cctray.xml")
    mocker.patch.object(dialog, "exec", return_value=QDialog.DialogCode.Accepted)

    dialog.add_server()
    preferences = dialog.open()

    assert [server.url for server in preferences.servers] == ["http://new/cctray.xml"]
    assert preferences.servers[0].prefix == "prefix"


@pytest.mark.functional
def test_should_not_return_an_added_server_removed_before_ok(qtbot, mocker):
    conf = ConfigBuilder().build()
    dialog = PreferencesDialog(conf.settings, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    stub_server_dialog(mocker, "http://new/cctray.xml")
    mocker.patch.object(dialog, "exec", return_value=QDialog.DialogCode.Accepted)

    dialog.add_server()
    select_row(dialog, 0)
    dialog.remove_element()

    assert dialog.open().servers == []


@pytest.mark.functional
def test_should_reject_a_duplicate_server(qtbot, mocker):
    conf = ConfigBuilder().server("http://one/cctray.xml").build()
    dialog = PreferencesDialog(conf.settings, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    stub_server_dialog(mocker, "http://one/cctray.xml")

    dialog.add_server()

    assert dialog.get_urls() == ["http://one/cctray.xml"]


@pytest.mark.functional
def test_should_keep_edits_to_an_added_server(qtbot, mocker):
    conf = ConfigBuilder().build()
    dialog = PreferencesDialog(conf.settings, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    stub_server_dialog(mocker, "http://new/cctray.xml")
    mocker.patch.object(dialog, "exec", return_value=QDialog.DialogCode.Accepted)
    dialog.add_server()
    select_row(dialog, 0)
    mocker.patch.object(
        ServerConfigurationDialog,
        "open",
        return_value=ServerSettings("http://new/cctray.xml", prefix="edited"),
    )

    dialog.configure_projects()

    assert dialog.open().servers[0].prefix == "edited"


@pytest.mark.functional
def test_should_delete_server_dialogs_after_use(qtbot, mocker):
    conf = ConfigBuilder().server("http://one/cctray.xml").build()
    dialog = PreferencesDialog(conf.settings, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    mocker.patch.object(ServerConfigurationDialog, "open", return_value=None)
    delete_later = mocker.patch.object(ServerConfigurationDialog, "deleteLater")

    dialog.add_server()
    select_row(dialog, 0)
    dialog.configure_projects()

    assert delete_later.call_count == 2


@pytest.mark.functional
def test_should_not_save_an_edited_server_until_ok(qtbot, mocker):
    conf = ConfigBuilder().server("http://one/cctray.xml").build()
    dialog = PreferencesDialog(conf.settings, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    select_row(dialog, 0)
    stub_server_dialog(mocker, "http://one/cctray.xml")
    mocker.patch.object(dialog, "exec", return_value=QDialog.DialogCode.Rejected)

    dialog.configure_projects()

    assert dialog.open() is None
    assert conf.settings.servers[0].prefix == ""


@pytest.mark.functional
def test_should_return_an_edited_server_on_ok(qtbot, mocker):
    conf = ConfigBuilder().server("http://one/cctray.xml").build()
    dialog = PreferencesDialog(conf.settings, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    select_row(dialog, 0)
    stub_server_dialog(mocker, "http://one/cctray.xml")
    mocker.patch.object(dialog, "exec", return_value=QDialog.DialogCode.Accepted)

    dialog.configure_projects()

    assert dialog.open().servers[0].prefix == "prefix"


@pytest.mark.functional
def test_should_return_every_unchanged_setting_on_ok(qtbot, mocker):
    notifications = {key: key != "brokenBuild" for key in DEFAULT_NOTIFICATIONS}
    builder = ConfigBuilder(
        interval_seconds=45,
        custom_script="notify-send #status#",
        custom_script_enabled=True,
        sort_key=SortKey.NAME,
        show_last_build_label=True,
        symbolic_icons=True,
        notifications=notifications,
    )
    conf = builder.server("http://one/cctray.xml", username="alice", password="pw").server("http://two").build()
    dialog = PreferencesDialog(conf.settings, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    mocker.patch.object(dialog, "exec", return_value=QDialog.DialogCode.Accepted)

    assert dialog.open() == conf.settings


def test_should_open_the_server_dialog_with_the_injected_connection(qtbot, mocker):
    conf = ConfigBuilder().build()
    connection = FakeConnection(fake_content())
    dialog = PreferencesDialog(conf.settings, connection)
    qtbot.addWidget(dialog)
    server_dialog = mocker.patch("buildnotifylib.ui.dialogs.preferences.ServerConfigurationDialog")
    server_dialog.return_value.open.return_value = None

    dialog.add_server()

    server_dialog.assert_called_once_with(
        None, conf.settings.timeout_seconds, connection, dialog, keystore_available=True
    )


def test_should_pass_keystore_availability_to_the_server_dialog(qtbot, mocker):
    conf = ConfigBuilder().build()
    dialog = PreferencesDialog(conf.settings, FakeConnection(fake_content()), keystore_available=False)
    qtbot.addWidget(dialog)
    server_dialog = mocker.patch("buildnotifylib.ui.dialogs.preferences.ServerConfigurationDialog")
    server_dialog.return_value.open.return_value = None

    dialog.add_server()

    assert server_dialog.call_args.kwargs == {"keystore_available": False}


@pytest.mark.functional
def test_should_reject_editing_a_server_url_to_another_servers_url(qtbot, mocker):
    conf = ConfigBuilder().server("http://one/cctray.xml").server("http://two/cctray.xml", username="bob").build()
    dialog = PreferencesDialog(conf.settings, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    select_row(dialog, 0)
    stub_server_dialog(mocker, "http://two/cctray.xml")
    mocker.patch.object(dialog, "exec", return_value=QDialog.DialogCode.Accepted)

    dialog.configure_projects()

    assert dialog.get_urls() == ["http://one/cctray.xml", "http://two/cctray.xml"]
    assert dialog.open().servers == conf.settings.servers


@pytest.mark.functional
def test_should_return_the_symbolic_icons_choice(qtbot, mocker):
    dialog = PreferencesDialog(ConfigBuilder().build().settings, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    assert not dialog.ui.symbolicIconsCheckbox.isChecked()
    mocker.patch.object(dialog, "exec", return_value=QDialog.DialogCode.Accepted)

    dialog.ui.symbolicIconsCheckbox.setChecked(True)

    assert dialog.open().symbolic_icons


@pytest.mark.functional
def test_should_keep_the_default_polling_interval(qtbot):
    dialog = PreferencesDialog(AppSettings(interval_seconds=120), FakeConnection(fake_content()))
    qtbot.addWidget(dialog)

    assert dialog.edited_settings().interval_seconds == 120


@pytest.mark.functional
def test_should_offer_polling_intervals_from_10_seconds_to_an_hour(qtbot):
    dialog = PreferencesDialog(AppSettings(), FakeConnection(fake_content()))
    qtbot.addWidget(dialog)

    spin_box = dialog.ui.pollingIntervalSpinBox
    assert (spin_box.minimum(), spin_box.maximum()) == (10, 3600)


@pytest.mark.functional
def test_should_clamp_a_stored_polling_interval_above_an_hour(qtbot):
    dialog = PreferencesDialog(AppSettings(interval_seconds=5000), FakeConnection(fake_content()))
    qtbot.addWidget(dialog)

    assert dialog.edited_settings().interval_seconds == 3600


@pytest.mark.functional
def test_should_enable_configure_when_a_server_is_selected_without_a_click(qtbot):
    conf = ConfigBuilder().server("http://one/cctray.xml").server("http://two/cctray.xml").build()
    dialog = PreferencesDialog(conf.settings, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    assert not dialog.ui.configureProjectButton.isEnabled()

    select_row(dialog, 1)

    assert dialog.ui.configureProjectButton.isEnabled()


@pytest.mark.functional
def test_should_disable_configure_once_the_selected_server_is_removed(qtbot):
    conf = ConfigBuilder().server("http://one/cctray.xml").build()
    dialog = PreferencesDialog(conf.settings, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    select_row(dialog, 0)

    dialog.remove_element()

    assert not dialog.ui.configureProjectButton.isEnabled()


@pytest.mark.functional
@pytest.mark.parametrize("key", [Qt.Key.Key_Return, Qt.Key.Key_Enter])
def test_should_configure_the_selected_server_on_enter(qtbot, mocker, key):
    conf = ConfigBuilder().server("http://one/cctray.xml").build()
    dialog = PreferencesDialog(conf.settings, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    dialog.show()
    select_row(dialog, 0)
    dialog.ui.cctrayPathList.setFocus()
    edit = mocker.patch.object(ServerConfigurationDialog, "open", return_value=None)

    qtbot.keyClick(dialog.ui.cctrayPathList, key)

    edit.assert_called_once()
    assert dialog.isVisible()
