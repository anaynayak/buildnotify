import pytest
import requests_mock
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
from mock import ANY

from buildnotifylib.server_configuration_dialog import ServerConfigurationDialog
from buildnotifylib.core.keystore import Keystore
from test.fake_conf import ConfigBuilder
from test.utils import fake_content


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_show_configured_urls(qtbot):
    with requests_mock.Mocker() as m:
        url = 'http://localhost:8080/cc.xml'
        m.get(url, text=fake_content())
        conf = ConfigBuilder().server(url).build()
        dialog = ServerConfigurationDialog(url, conf)
        dialog.show()
        qtbot.addWidget(dialog)
        qtbot.mouseClick(dialog.ui.loadUrlButton, QtCore.Qt.LeftButton)

        qtbot.waitUntil(lambda: dialog.ui.projectsList.model() is not None)
        model = dialog.ui.projectsList.model()
        assert model.item(0, 0).hasChildren()
        assert model.item(0, 0).child(0, 0).isCheckable()
        assert model.item(0, 0).child(0, 0).data(Qt.CheckStateRole) == Qt.Checked
        assert model.item(0, 0).child(0, 0).text() == "cleanup-artifacts-B"

        assert dialog.ui.timezoneList.currentText() == 'None'


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_exclude_projects(qtbot):
    with requests_mock.Mocker() as m:
        url = 'http://localhost:8080/cc.xml'
        m.get(url, text=fake_content())
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
    with requests_mock.Mocker() as m:
        url = 'http://localhost:8080/cc.xml'
        m.get(url, text=fake_content())
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

        assert model.item(0, 0).hasChildren()
        assert model.item(0, 0).child(0, 0).isCheckable()
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


@pytest.mark.functional
@pytest.mark.requireshead
def test_should_disable_authentication_if_keystore_is_unavailable(qtbot, mocker):
    m = mocker.patch.object(Keystore, 'isAvailable',
                            return_value=False)
    with requests_mock.Mocker() as r:
        url = 'http://localhost:8080/cc.xml'
        r.get(url, text=fake_content())

        conf = ConfigBuilder().server(url).build()
        dialog = ServerConfigurationDialog(url, conf)
        dialog.show()
        qtbot.addWidget(dialog)

        def alert_shown():
            assert not dialog.ui.username.isEnabled()
            assert not dialog.ui.password.isEnabled()
            assert dialog.ui.authenticationSettings.title() == 'Authentication (keyring dependency missing)'

        qtbot.wait_until(alert_shown)
