import pytest

from buildnotifylib.core.settings import ServerSettings, SortKey
from buildnotifylib.ui.dialogs.preferences.misc_page import MiscChoices, MiscPage
from buildnotifylib.ui.dialogs.preferences.notifications_page import NotificationChoices, NotificationsPage
from buildnotifylib.ui.dialogs.preferences.servers_page import ServersPage
from test.utils import FakeConnection, fake_content


@pytest.mark.functional
def test_servers_page_should_return_the_servers_it_was_given(qtbot):
    page = ServersPage(10, FakeConnection(fake_content()))
    qtbot.addWidget(page)
    servers = [ServerSettings("http://one/cctray.xml", prefix="one"), ServerSettings("http://two/cctray.xml")]

    page.set_value(servers)

    assert page.value() == servers


@pytest.mark.functional
@pytest.mark.parametrize("enabled", [True, False])
def test_notifications_page_should_return_the_choices_it_was_given(qtbot, enabled):
    page = NotificationsPage()
    qtbot.addWidget(page)
    events = {key: (index % 2 == 0) == enabled for index, key in enumerate(page.events)}
    choices = NotificationChoices(events, "notify-send #status#", enabled)

    page.set_value(choices)

    assert page.value() == choices


@pytest.mark.functional
def test_notifications_page_should_enable_the_script_field_only_while_the_script_is_on(qtbot):
    page = NotificationsPage()
    qtbot.addWidget(page)
    assert not page.script.isEnabled()

    page.script_enabled.setChecked(True)
    assert page.script.isEnabled()

    page.script_enabled.setChecked(False)
    assert not page.script.isEnabled()


@pytest.mark.functional
@pytest.mark.parametrize("sort_key", list(SortKey))
def test_misc_page_should_return_the_choices_it_was_given(qtbot, sort_key):
    page = MiscPage()
    qtbot.addWidget(page)
    choices = MiscChoices(45, False, True, True, sort_key)

    page.set_value(choices)

    assert page.value() == choices
