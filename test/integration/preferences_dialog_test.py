import os

import pytest
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtCore import QItemSelectionModel, Qt

from buildnotifylib.preferences import PreferencesDialog
from buildnotifylib.server_configuration_dialog import ServerConfigurationDialog
from test.fake_conf import ConfigBuilder


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_show_configured_urls(qtbot):
    file = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../../data/cctray.xml")
    conf = ConfigBuilder().server("file://" + file).build()
    dialog = PreferencesDialog(conf)
    qtbot.addWidget(dialog)
    assert [str(s) for s in dialog.ui.cctrayPathList.model().stringList()] == ["file://" + file]


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_show_configure_notifications(qtbot):
    file = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../../data/cctray.xml")
    conf = ConfigBuilder().server("file://" + file).build()
    dialog = PreferencesDialog(conf)
    qtbot.addWidget(dialog)
    dialog.show()
    dialog.ui.tabWidget.setCurrentIndex(1)
    assert dialog.ui.connectivityIssuesCheckbox.isChecked() == True
    assert dialog.ui.fixedBuildsCheckbox.isChecked() == True
    assert dialog.ui.brokenBuildsCheckbox.isChecked() == True
    assert dialog.ui.successfulBuildsCheckbox.isChecked() == False
    assert dialog.ui.scriptCheckbox.isChecked() == False
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
    file = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../../data/cctray.xml")
    conf = ConfigBuilder().server("file://" + file).build()
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
    file = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../../data/cctray.xml")
    conf = ConfigBuilder().server("file://" + file).build()
    dialog = PreferencesDialog(conf)
    qtbot.addWidget(dialog)
    dialog.show()

    index = dialog.ui.cctrayPathList.model().index(0, 0)
    dialog.ui.cctrayPathList.selectionModel().select(index, QItemSelectionModel.Select)
    dialog.ui.cctrayPathList.setCurrentIndex(index)
    dialog.item_selection_changed(True)

    qtbot.mouseClick(dialog.ui.removeButton, Qt.LeftButton)

    assert [str(s) for s in dialog.ui.cctrayPathList.model().stringList()] == []
