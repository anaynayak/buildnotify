import os

import pytest
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from mock import ANY

from buildnotifylib.server_configuration_dialog import ServerConfigurationDialog
from test.fake_conf import ConfigBuilder


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_show_configured_urls(qtbot):
    file = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../../data/cctray.xml")
    url = "file://" + file
    conf = ConfigBuilder().server(url).build()
    dialog = ServerConfigurationDialog(url, conf)
    dialog.show()
    qtbot.addWidget(dialog)
    qtbot.mouseClick(dialog.ui.loadUrlButton, QtCore.Qt.LeftButton)

    qtbot.waitUntil(lambda: dialog.ui.projectsList.model() is not None)
    model = dialog.ui.projectsList.model()
    assert model.item(0, 0).hasChildren() == True
    assert model.item(0, 0).child(0, 0).isCheckable() == True
    assert model.item(0, 0).child(0, 0).data(Qt.CheckStateRole) == Qt.Checked
    assert model.item(0, 0).child(0, 0).text() == "cleanup-artifacts-B"

    assert dialog.ui.timezoneList.currentText() == 'None'


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_exclude_projects(qtbot):
    file = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../../data/cctray.xml")
    url = "file://" + file
    conf = ConfigBuilder().server(url).build()
    dialog = ServerConfigurationDialog(url, conf)
    dialog.show()
    qtbot.addWidget(dialog)
    qtbot.mouseClick(dialog.ui.loadUrlButton, QtCore.Qt.LeftButton)

    qtbot.waitUntil(lambda: dialog.ui.projectsList.model() is not None)
    model = dialog.ui.projectsList.model()

    model.item(0, 0).child(0, 0).setCheckState(QtCore.Qt.Unchecked)

    server_config = dialog.get_server_config()
    assert [str(s) for s in server_config.excluded_projects] == ['cleanup-artifacts-B']


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_preload_info(qtbot):
    file = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../../data/cctray.xml")
    url = "file://" + file
    conf = ConfigBuilder().server(url, {
        "excludes/%s" % url: ['cleanup-artifacts-B'],
        "timezone/%s" % url: 'US/Eastern',
    }).build()

    dialog = ServerConfigurationDialog(url, conf)
    dialog.show()
    qtbot.addWidget(dialog)
    qtbot.mouseClick(dialog.ui.loadUrlButton, QtCore.Qt.LeftButton)

    qtbot.waitUntil(lambda: dialog.ui.projectsList.model() is not None)
    model = dialog.ui.projectsList.model()

    assert model.item(0, 0).hasChildren() == True
    assert model.item(0, 0).child(0, 0).isCheckable() == True
    assert model.item(0, 0).child(0, 0).text() == "cleanup-artifacts-B"
    assert model.item(0, 0).child(0, 0).data(Qt.CheckStateRole) == Qt.Unchecked
    def timezone():
        assert dialog.ui.timezoneList.count() > 100
        assert dialog.ui.timezoneList.currentText() == 'US/Eastern'
    qtbot.waitUntil(timezone)


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_fail_for_bad_url(qtbot, mocker):
    url = "file:///badpath"
    conf = ConfigBuilder().server(url).build()
    dialog = ServerConfigurationDialog(url, conf)
    dialog.show()
    qtbot.addWidget(dialog)
    m = mocker.patch.object(QMessageBox, 'critical',
                            return_value=QMessageBox.No)

    qtbot.mouseClick(dialog.ui.loadUrlButton, QtCore.Qt.LeftButton)

    def alert_shown():
        m.assert_called_once_with(dialog, ANY, ANY)

    qtbot.wait_until(alert_shown)
