import os

import pytest
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from mock import ANY

from buildnotifylib.server_configuration_dialog import ServerConfigurationDialog
from test.fake_conf import ConfigBuilder


@pytest.mark.functional
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

@pytest.mark.functional
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

    dialog.save()
    config = conf.get_server_config(url)
    assert [str(s) for s in config.excluded_projects] == ['cleanup-artifacts-B']



@pytest.mark.functional
def test_should_preload_info(qtbot):
    file = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../../data/cctray.xml")
    url = "file://" + file
    conf = ConfigBuilder().server(url, {"excludes/%s" % url: ['cleanup-artifacts-B']}).build()
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


@pytest.mark.functional
def test_should_fail_for_bad_url(qtbot, mocker):
    url = "file:///badpath"
    conf = ConfigBuilder().server(url).build()
    dialog = ServerConfigurationDialog(url, conf)
    dialog.show()
    qtbot.addWidget(dialog)
    m = mocker.patch.object(QtGui.QMessageBox, 'critical',
                            return_value=QtGui.QMessageBox.No)

    qtbot.mouseClick(dialog.ui.loadUrlButton, QtCore.Qt.LeftButton)

    def alert_shown():
        m.assert_called_once_with(dialog, ANY, ANY)

    qtbot.wait_until(alert_shown)
