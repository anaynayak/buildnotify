from collections.abc import Sequence

from buildnotifylib.core.model import Activity, Project, ServerSnapshot, Status


def rank(project: Project) -> tuple[Status, Activity]:
    if project.activity is Activity.UNKNOWN:
        return Status.UNKNOWN, Activity.UNKNOWN
    return project.status, project.activity


SUMMARY_NAMES = 5


class OverallIntegrationStatus:
    def __init__(self, servers: Sequence[ServerSnapshot]):
        self.servers = list(servers)

    def get_build_status(self) -> str | None:
        ranks = [rank(project) for project in self.get_projects()]
        if not ranks:
            return None
        status, activity = min(ranks, key=lambda pair: (pair[0].priority, pair[1].priority))
        return f"{status}.{activity}"

    def get_failing_builds(self) -> list[Project]:
        return [project for project in self.get_projects() if project.status is Status.FAILURE]

    def failing_summary(self) -> str:
        names = [project.label() for project in self.get_failing_builds()]
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
