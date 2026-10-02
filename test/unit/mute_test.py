from datetime import UTC, datetime, timedelta

from buildnotifylib.core.diff import Change, Event
from buildnotifylib.core.model import Activity, Project, Status
from buildnotifylib.core.mute import (
    PAUSE,
    Mutes,
    audible,
    audible_servers,
    pause,
    resume,
    toggle_project,
    toggle_server,
)
from buildnotifylib.core.settings import AppSettings, ServerSettings

NOW = datetime(2026, 10, 2, 12, 0, tzinfo=UTC)
CI = "http://ci/cc.xml"
OTHER = "http://other/cc.xml"


def project(name: str, server_url: str = CI) -> Project:
    return Project(server_url, name, Status.FAILURE, Activity.SLEEPING, "url")


def broken(name: str, server_url: str = CI) -> Event:
    return Event(Change.BROKEN, project(name, server_url))


def settings(*servers: ServerSettings, paused_until: datetime | None = None) -> AppSettings:
    return AppSettings(servers=list(servers), paused_until=paused_until)


def test_should_keep_every_event_when_nothing_is_muted():
    events = [broken("api"), broken("web", OTHER)]

    assert audible(events, Mutes.from_settings(settings(ServerSettings(CI))), NOW) == events


def test_should_drop_events_for_a_muted_project():
    mutes = Mutes.from_settings(settings(ServerSettings(CI, muted_projects=["api"])))

    assert audible([broken("api"), broken("web"), broken("api", OTHER)], mutes, NOW) == [
        broken("web"),
        broken("api", OTHER),
    ]


def test_should_drop_events_for_every_project_of_a_muted_server():
    mutes = Mutes.from_settings(settings(ServerSettings(CI, muted=True), ServerSettings(OTHER)))

    assert audible([broken("api"), broken("web", OTHER)], mutes, NOW) == [broken("web", OTHER)]


def test_should_drop_every_event_while_paused():
    mutes = Mutes.from_settings(settings(paused_until=NOW + timedelta(minutes=1)))

    assert audible([broken("api")], mutes, NOW) == []
    assert mutes.paused(NOW)


def test_should_notify_again_once_the_pause_expires():
    mutes = Mutes.from_settings(settings(paused_until=NOW))

    assert audible([broken("api")], mutes, NOW) == [broken("api")]
    assert not mutes.paused(NOW)


def test_should_drop_muted_and_paused_servers_from_connectivity_issues():
    mutes = Mutes.from_settings(settings(ServerSettings(CI, muted=True)))

    assert audible_servers([CI, OTHER], mutes, NOW) == [OTHER]
    assert audible_servers([OTHER], Mutes(paused_until=NOW + PAUSE), NOW) == []


def test_should_tell_whether_a_project_is_muted():
    mutes = Mutes.from_settings(settings(ServerSettings(CI, muted_projects=["api"]), ServerSettings(OTHER, muted=True)))

    assert [mutes.mutes(p) for p in (project("api"), project("web"), project("web", OTHER))] == [True, False, True]


def test_should_pause_for_an_hour_from_now():
    assert pause(settings(), NOW).paused_until == NOW + timedelta(hours=1)


def test_should_resume_notifications():
    assert resume(settings(paused_until=NOW)).paused_until is None


def test_should_toggle_a_server_mute():
    muted = toggle_server(settings(ServerSettings(CI), ServerSettings(OTHER)), CI)

    assert [server.muted for server in muted.servers] == [True, False]
    assert [server.muted for server in toggle_server(muted, CI).servers] == [False, False]


def test_should_toggle_a_project_mute():
    muted = toggle_project(settings(ServerSettings(CI), ServerSettings(OTHER)), project("api"))

    assert [server.muted_projects for server in muted.servers] == [["api"], []]
    assert toggle_project(muted, project("api")).servers[0].muted_projects == []


def test_should_leave_the_original_settings_alone_when_toggling():
    original = settings(ServerSettings(CI))

    toggle_project(toggle_server(original, CI), project("api"))

    assert original.servers[0] == ServerSettings(CI)
