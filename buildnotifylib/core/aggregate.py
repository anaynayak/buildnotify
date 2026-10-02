from collections.abc import Iterable, Sequence

from buildnotifylib.core.model import Activity, Project, ServerSnapshot, Status


def rank(project: Project) -> tuple[Status, Activity]:
    if project.activity is Activity.UNKNOWN:
        return Status.UNKNOWN, Activity.UNKNOWN
    return project.status, project.activity


def overall_status(projects: Iterable[Project]) -> str | None:
    ranks = [rank(project) for project in projects]
    if not ranks:
        return None
    status, activity = min(ranks, key=lambda pair: (pair[0].priority, pair[1].priority))
    return f"{status}.{activity}"


def failing(projects: Iterable[Project]) -> list[Project]:
    return [project for project in projects if project.status is Status.FAILURE]


class OverallIntegrationStatus:
    def __init__(self, servers: Sequence[ServerSnapshot]):
        self.servers = list(servers)

    def get_build_status(self) -> str | None:
        return overall_status(self.get_projects())

    def get_failing_builds(self) -> list[Project]:
        return failing(self.get_projects())

    def get_projects(self) -> list[Project]:
        return [project for server in self.servers for project in server.projects]

    def unavailable_servers(self) -> list[ServerSnapshot]:
        return [server for server in self.servers if server.unavailable]
