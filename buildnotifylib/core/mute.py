"""Muted servers and projects, and the timed pause, as filters over what would be notified."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass, replace
from datetime import datetime, timedelta

from buildnotifylib.core.diff import Event, Key, key
from buildnotifylib.core.model import Project
from buildnotifylib.core.settings import AppSettings, ServerSettings

PAUSE = timedelta(hours=1)


@dataclass(frozen=True)
class Mutes:
    servers: frozenset[str] = frozenset()
    projects: frozenset[Key] = frozenset()
    paused_until: datetime | None = None

    @classmethod
    def from_settings(cls, settings: AppSettings) -> "Mutes":
        servers = frozenset(server.url for server in settings.servers if server.muted)
        projects = frozenset((server.url, name) for server in settings.servers for name in server.muted_projects)
        return cls(servers, projects, settings.paused_until)

    def paused(self, now: datetime) -> bool:
        return self.paused_until is not None and now < self.paused_until

    def mutes(self, project: Project) -> bool:
        return project.server_url in self.servers or key(project) in self.projects


def audible(events: Iterable[Event], mutes: Mutes, now: datetime) -> list[Event]:
    if mutes.paused(now):
        return []
    return [event for event in events if not mutes.mutes(event.project)]


def audible_servers(urls: Iterable[str], mutes: Mutes, now: datetime) -> list[str]:
    if mutes.paused(now):
        return []
    return [url for url in urls if url not in mutes.servers]


def pause(settings: AppSettings, now: datetime) -> AppSettings:
    return replace(settings, paused_until=now + PAUSE)


def resume(settings: AppSettings) -> AppSettings:
    return replace(settings, paused_until=None)


def toggle_server(settings: AppSettings, url: str) -> AppSettings:
    return with_server(settings, url, lambda server: replace(server, muted=not server.muted))


def toggle_project(settings: AppSettings, project: Project) -> AppSettings:
    def toggle(server: ServerSettings) -> ServerSettings:
        names = server.muted_projects
        toggled = [n for n in names if n != project.name] if project.name in names else [*names, project.name]
        return replace(server, muted_projects=toggled)

    return with_server(settings, project.server_url, toggle)


def with_server(settings: AppSettings, url: str, change: Callable[[ServerSettings], ServerSettings]) -> AppSettings:
    servers = [change(server) if server.url == url else server for server in settings.servers]
    return replace(settings, servers=servers)
