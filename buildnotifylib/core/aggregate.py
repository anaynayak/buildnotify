from collections import defaultdict
from collections.abc import Sequence
from dataclasses import replace

from buildnotifylib.core.errors import server_name
from buildnotifylib.core.model import Activity, Project, ServerSnapshot, Status
from buildnotifylib.core.mute import Mutes


def rank(project: Project) -> tuple[Status, Activity]:
    if project.activity is Activity.UNKNOWN:
        return Status.UNKNOWN, Activity.UNKNOWN
    return project.status, project.activity


SUMMARY_NAMES = 5
NO_MUTES = Mutes()


def disambiguated(servers: Sequence[ServerSnapshot]) -> list[ServerSnapshot]:
    """Display only: name the server on unprefixed rows whose label also appears on another server."""
    homes: dict[str, set[str]] = defaultdict(set)
    for server in servers:
        for project in server.projects:
            homes[project.label()].add(server.url)
    return [replace(server, projects=tuple(named(project, homes) for project in server.projects)) for server in servers]


def named(project: Project, homes: dict[str, set[str]]) -> Project:
    if project.prefix or len(homes[project.label()]) < 2:
        return project
    return replace(project, prefix=server_name(project.server_url))


class OverallIntegrationStatus:
    def __init__(self, servers: Sequence[ServerSnapshot]):
        self.servers = disambiguated(servers)

    def counted(self, mutes: Mutes) -> list[Project]:
        """The projects that set the icon and the failing count: everything not muted."""
        return [project for project in self.get_projects() if not mutes.mutes(project)]

    def muted_count(self, mutes: Mutes) -> int:
        return len(self.get_projects()) - len(self.counted(mutes))

    def get_build_status(self, mutes: Mutes = NO_MUTES) -> str | None:
        ranks = [rank(project) for project in self.counted(mutes)]
        if not ranks:
            return None
        status, activity = min(ranks, key=lambda pair: (pair[0].priority, pair[1].priority))
        return f"{status}.{activity}"

    def get_failing_builds(self, mutes: Mutes = NO_MUTES) -> list[Project]:
        return [project for project in self.counted(mutes) if project.status is Status.FAILURE]

    def failing_summary(self, mutes: Mutes = NO_MUTES) -> str:
        names = [project.label() for project in self.get_failing_builds(mutes)]
        if not names:
            return "No failing builds"
        listed = ", ".join(names[:SUMMARY_NAMES])
        more = f" and {len(names) - SUMMARY_NAMES} more" if len(names) > SUMMARY_NAMES else ""
        return f"{len(names)} failing: {listed}{more}"

    def get_projects(self) -> list[Project]:
        return [project for server in self.servers for project in server.projects]

    def unavailable_servers(self) -> list[ServerSnapshot]:
        return [server for server in self.servers if server.unavailable]

    def unreachable(self) -> bool:
        """Every server is down and none has projects cached from an earlier fetch."""
        return bool(self.servers) and all(server.unavailable and not server.projects for server in self.servers)
