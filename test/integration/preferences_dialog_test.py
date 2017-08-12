import os

import pytest
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QItemSelectionModel, Qt

from buildnotifylib.preferences import PreferencesDialog
from test.fake_conf import ConfigBuilder


@pytest.mark.functional
def test_should_show_configured_urls(qtbot):
    file = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../../data/cctray.xml")
    conf = ConfigBuilder().server("file://" + file).build()
    dialog = PreferencesDialog(conf)
    qtbot.addWidget(dialog)
    assert [str(s) for s in dialog.ui.cctrayPathList.model().stringList()] == ["file://" + file]


@pytest.mark.functional
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

    qtbot.mouseClick(dialog.ui.successfulBuildsCheckbox, Qt.LeftButton)
    dialog.save()

    qtbot.waitUntil(lambda: conf.get_value("successfulBuild"))


@pytest.mark.functional
def test_should_prefill_server_config(qtbot):
    file = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../../data/cctray.xml")
    conf = ConfigBuilder().server("file://" + file).build()
    dialog = PreferencesDialog(conf)
    qtbot.addWidget(dialog)
    dialog.show()

    index = dialog.ui.cctrayPathList.model().index(0, 0)
    dialog.ui.cctrayPathList.selectionModel().select(index, QItemSelectionModel.Select)
    dialog.ui.cctrayPathList.setCurrentIndex(index)
    dialog.item_selection_changed(True)

    def close_dialog():
        dialog.server_configuration_dialog.close()

    QtCore.QTimer.singleShot(500, close_dialog)

    qtbot.mouseClick(dialog.ui.configureProjectButton, Qt.LeftButton)

    assert dialog.server_configuration_dialog.ui.addServerUrl.text() == "file://" + file


@pytest.mark.functional
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


