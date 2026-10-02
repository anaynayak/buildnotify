import logging

from buildnotifylib.core.cctray import CctraySource
from buildnotifylib.core.github import GitHubSource, RateLimits
from buildnotifylib.core.model import ServerSnapshot
from buildnotifylib.core.ports import Connection, Source
from buildnotifylib.core.settings import ServerSettings, SourceKind

log = logging.getLogger(__name__)


class ProjectLoader:
    def __init__(
        self,
        server_config: ServerSettings,
        timeout: float | None,
        connection: Connection,
        apply_excludes: bool = True,
        rate_limits: RateLimits | None = None,
    ):
        self.server_config = server_config
        self.timeout = timeout
        self.connection = connection
        self.apply_excludes = apply_excludes
        self.rate_limits = rate_limits or RateLimits()

    def get_data(self) -> ServerSnapshot:
        log.debug("checking %s", self.server_config.url)
        try:
            projects = self.source().fetch()
        except Exception as ex:
            log.warning("Failed to fetch %s: %s", self.server_config.url, ex)
            return ServerSnapshot(self.server_config.url, error=ex)
        log.debug("processed %s", self.server_config.url)
        return ServerSnapshot(self.server_config.url, tuple(projects))

    def source(self) -> Source:
        if self.server_config.kind is SourceKind.GITHUB:
            return GitHubSource(
                self.server_config, self.timeout, self.connection, self.rate_limits, self.apply_excludes
            )
        return CctraySource(self.server_config, self.timeout, self.connection, self.apply_excludes)
