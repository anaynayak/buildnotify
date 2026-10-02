import os

import pytest
from PyQt5 import QtCore
from PyQt5.QtCore import QItemSelectionModel, Qt
from PyQt5.QtWidgets import QDialog, QDialogButtonBox

from buildnotifylib.preferences import PreferencesDialog
from buildnotifylib.server_configuration_dialog import ServerConfigurationDialog
from buildnotifylib.serverconfig import ServerConfig
from test.fake_conf import ConfigBuilder


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_show_configured_urls(qtbot):
    file_path = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../../data/cctray.xml")
    conf = ConfigBuilder().server("file://" + file_path).build()
    dialog = PreferencesDialog(conf)
    qtbot.addWidget(dialog)
    assert [str(s) for s in dialog.ui.cctrayPathList.model().stringList()] == ["file://" + file_path]


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_show_configure_notifications(qtbot):
    file_path = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../../data/cctray.xml")
    conf = ConfigBuilder().server("file://" + file_path).build()
    dialog = PreferencesDialog(conf)
    qtbot.addWidget(dialog)
    dialog.show()
    dialog.ui.tabWidget.setCurrentIndex(1)
    assert dialog.ui.connectivityIssuesCheckbox.isChecked()
    assert dialog.ui.fixedBuildsCheckbox.isChecked()
    assert dialog.ui.brokenBuildsCheckbox.isChecked()
    assert not dialog.ui.successfulBuildsCheckbox.isChecked()
    assert not dialog.ui.scriptCheckbox.isChecked()
    assert dialog.ui.scriptLineEdit.text() == 'echo #status# #projects# >> /tmp/buildnotify.log'


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_return_preferences_on_accept(qtbot):
    conf = ConfigBuilder().build()
    dialog = PreferencesDialog(conf)
    qtbot.addWidget(dialog)

    def close_dialog():
        button = dialog.ui.buttonBox.button(QDialogButtonBox.Ok)
        qtbot.mouseClick(button, QtCore.Qt.LeftButton)

    QtCore.QTimer.singleShot(100, close_dialog)
    preferences = dialog.open()

    qtbot.waitUntil(lambda: preferences is not None)


@pytest.mark.functional
def test_should_prefill_server_config(qtbot, mocker):
    file_path = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../../data/cctray.xml")
    conf = ConfigBuilder().server("file://" + file_path).build()
    dialog = PreferencesDialog(conf)
    qtbot.addWidget(dialog)
    dialog.show()

    index = dialog.ui.cctrayPathList.model().index(0, 0)
    dialog.ui.cctrayPathList.selectionModel().select(index, QItemSelectionModel.Select)
    dialog.ui.cctrayPathList.setCurrentIndex(index)
    dialog.item_selection_changed(True)

    m = mocker.patch.object(ServerConfigurationDialog, 'open')

    qtbot.mouseClick(dialog.ui.configureProjectButton, Qt.LeftButton)

    qtbot.waitUntil(lambda: m.assert_any_call())


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_remove_configured_servers(qtbot):
    file_path = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../../data/cctray.xml")
    conf = ConfigBuilder().server("file://" + file_path).build()
    dialog = PreferencesDialog(conf)
    qtbot.addWidget(dialog)
    dialog.show()

    index = dialog.ui.cctrayPathList.model().index(0, 0)
    dialog.ui.cctrayPathList.selectionModel().select(index, QItemSelectionModel.Select)
    dialog.ui.cctrayPathList.setCurrentIndex(index)
    dialog.item_selection_changed(True)

    qtbot.mouseClick(dialog.ui.removeButton, Qt.LeftButton)

    assert [str(s) for s in dialog.ui.cctrayPathList.model().stringList()] == []


@pytest.mark.functional
def test_should_not_remove_anything_without_a_selection(qtbot):
    conf = ConfigBuilder().server("http://one/cctray.xml").server("http://two/cctray.xml").build()
    dialog = PreferencesDialog(conf)
    qtbot.addWidget(dialog)

    dialog.remove_element()

    assert dialog.get_urls() == ["http://one/cctray.xml", "http://two/cctray.xml"]


def select_row(dialog, row):
    index = dialog.ui.cctrayPathList.model().index(row, 0)
    dialog.ui.cctrayPathList.setCurrentIndex(index)


@pytest.mark.functional
def test_should_replace_the_row_when_a_server_url_is_edited(qtbot, mocker):
    conf = ConfigBuilder().server("http://one/cctray.xml").server("http://two/cctray.xml").build()
    dialog = PreferencesDialog(conf)
    qtbot.addWidget(dialog)
    select_row(dialog, 0)
    mocker.patch.object(ServerConfigurationDialog, 'open',
                        return_value=ServerConfig("http://new/cctray.xml", [], 'None', '', '', ''))

    dialog.configure_projects()

    assert dialog.get_urls() == ["http://new/cctray.xml", "http://two/cctray.xml"]


def stub_server_dialog(mocker, url):
    mocker.patch.object(ServerConfigurationDialog, 'open',
                        return_value=ServerConfig(url, [], 'None', 'prefix', '', ''))


@pytest.mark.functional
def test_should_not_save_an_added_server_until_ok(qtbot, mocker):
    conf = ConfigBuilder().build()
    dialog = PreferencesDialog(conf)
    qtbot.addWidget(dialog)
    stub_server_dialog(mocker, "http://new/cctray.xml")
    mocker.patch.object(dialog, 'exec_', return_value=QDialog.Rejected)

    dialog.add_server()
    preferences = dialog.open()

    assert preferences is None
    assert dialog.get_urls() == ["http://new/cctray.xml"]
    assert conf.get_urls() == []


@pytest.mark.functional
def test_should_save_an_added_server_on_ok(qtbot, mocker):
    conf = ConfigBuilder().build()
    dialog = PreferencesDialog(conf)
    qtbot.addWidget(dialog)
    stub_server_dialog(mocker, "http://new/cctray.xml")
    mocker.patch.object(dialog, 'exec_', return_value=QDialog.Accepted)

    dialog.add_server()
    preferences = dialog.open()

    assert preferences.urls == ["http://new/cctray.xml"]
    assert conf.get_display_prefix("http://new/cctray.xml") == 'prefix'


@pytest.mark.functional
def test_should_not_save_an_added_server_removed_before_ok(qtbot, mocker):
    conf = ConfigBuilder().build()
    dialog = PreferencesDialog(conf)
    qtbot.addWidget(dialog)
    stub_server_dialog(mocker, "http://new/cctray.xml")
    mocker.patch.object(dialog, 'exec_', return_value=QDialog.Accepted)

    dialog.add_server()
    select_row(dialog, 0)
    dialog.remove_element()
    dialog.open()

    assert conf.get_display_prefix("http://new/cctray.xml") is None


@pytest.mark.functional
def test_should_reject_a_duplicate_server(qtbot, mocker):
    conf = ConfigBuilder().server("http://one/cctray.xml").build()
    dialog = PreferencesDialog(conf)
    qtbot.addWidget(dialog)
    stub_server_dialog(mocker, "http://one/cctray.xml")

    dialog.add_server()

    assert dialog.get_urls() == ["http://one/cctray.xml"]


@pytest.mark.functional
def test_should_keep_edits_to_an_added_server(qtbot, mocker):
    conf = ConfigBuilder().build()
    dialog = PreferencesDialog(conf)
    qtbot.addWidget(dialog)
    stub_server_dialog(mocker, "http://new/cctray.xml")
    mocker.patch.object(dialog, 'exec_', return_value=QDialog.Accepted)
    dialog.add_server()
    select_row(dialog, 0)
    mocker.patch.object(ServerConfigurationDialog, 'open',
                        return_value=ServerConfig("http://new/cctray.xml", [], 'None', 'edited', '', ''))

    dialog.configure_projects()
    dialog.open()

    assert conf.get_display_prefix("http://new/cctray.xml") == 'edited'


@pytest.mark.functional
def test_should_delete_server_dialogs_after_use(qtbot, mocker):
    conf = ConfigBuilder().server("http://one/cctray.xml").build()
    dialog = PreferencesDialog(conf)
    qtbot.addWidget(dialog)
    mocker.patch.object(ServerConfigurationDialog, 'open', return_value=None)
    delete_later = mocker.patch.object(ServerConfigurationDialog, 'deleteLater')

    dialog.add_server()
    select_row(dialog, 0)
    dialog.configure_projects()

    assert delete_later.call_count == 2
