import pytest

from buildnotifylib.core.settings import ServerSettings, SortKey
from buildnotifylib.ui.dialogs.preferences.advanced_page import AdvancedChoices, AdvancedPage
from buildnotifylib.ui.dialogs.preferences.menu_page import MenuChoices, MenuPage
from buildnotifylib.ui.dialogs.preferences.notifications_page import NotificationChoices, NotificationsPage
from buildnotifylib.ui.dialogs.preferences.servers_page import ServersPage, row_text
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
def test_menu_page_should_return_the_choices_it_was_given(qtbot, sort_key):
    page = MenuPage()
    qtbot.addWidget(page)
    choices = MenuChoices(False, True, True, sort_key)

    page.set_value(choices)

    assert page.value() == choices


@pytest.mark.functional
def test_advanced_page_should_return_the_choices_it_was_given(qtbot):
    page = AdvancedPage()
    qtbot.addWidget(page)
    choices = AdvancedChoices(45, 25)

    page.set_value(choices)

    assert page.value() == choices


@pytest.mark.functional
def test_notifications_page_should_use_the_event_wording(qtbot):
    page = NotificationsPage()
    qtbot.addWidget(page)

    assert [box.text().replace("&", "") for box in page.events.values()] == [
        "Passes",
        "Fails",
        "Is fixed",
        "Fails again",
        "A server can't be reached",
    ]
    assert page.script_enabled.text().replace("&", "") == "Run a script on each notification"


@pytest.mark.functional
def test_menu_page_should_use_the_sentence_case_wording(qtbot):
    page = MenuPage()
    qtbot.addWidget(page)

    assert page.show_last_build_time.text().replace("&", "") == "Show last build time"
    assert page.show_last_build_label.text().replace("&", "") == "Show build label"
    sort_labels = [button.text().replace("&", "") for button in page.sort_buttons.values()]
    assert sort_labels == ["Failing first", "Name", "Last build time"]
    assert (page.tray_colour.text().replace("&", ""), page.tray_shapes.text().replace("&", "")) == ("Colour", "Shapes")


@pytest.mark.functional
def test_advanced_page_should_label_the_interval_and_timeout(qtbot):
    page = AdvancedPage()
    qtbot.addWidget(page)

    assert [label.replace("&", "") for label in page.form_labels()] == ["Check every:", "Give up after:"]
    assert (page.interval.minimum(), page.interval.maximum()) == (10, 3600)


def test_row_text_for_a_cctray_server_should_show_prefix_kind_host_and_count():
    server = ServerSettings("http://jenkins.example.org:8080/cctray.xml", prefix="jenkins")

    assert row_text(server, 12) == "jenkins - cctray - jenkins.example.org:8080 - 12 projects"


def test_row_text_should_fall_back_to_the_host_and_omit_an_unknown_count():
    assert row_text(ServerSettings("http://ci.example.org/cctray.xml")) == "ci.example.org - cctray - ci.example.org"


def test_row_text_should_use_the_singular_for_one_project():
    assert row_text(ServerSettings("http://ci/cctray.xml"), 1).endswith("- 1 project")


def test_row_text_for_a_github_server_should_show_repository_workflow_and_branch():
    server = ServerSettings("", kind="github", repository="octo-org/hello", workflow="ci.yml", branch="main")

    assert row_text(server, 2) == "github.com - github - octo-org/hello ci.yml@main - 2 projects"


def test_row_text_for_a_github_server_should_omit_an_unset_workflow():
    server = ServerSettings("", kind="github", repository="octo-org/hello")

    assert row_text(server) == "github.com - github - octo-org/hello"


@pytest.mark.functional
def test_servers_page_should_list_a_row_per_server_with_its_project_count(qtbot):
    page = ServersPage(10, FakeConnection(fake_content()), project_counts={"http://one/cctray.xml": 3})
    qtbot.addWidget(page)

    page.set_value([ServerSettings("http://one/cctray.xml", prefix="one"), ServerSettings("http://two/cctray.xml")])

    assert page.server_list.model().stringList() == ["one - cctray - one - 3 projects", "two - cctray - two"]
