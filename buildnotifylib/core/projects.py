import logging

from buildnotifylib.core import cctray
from buildnotifylib.core.model import Project, ServerSnapshot
from buildnotifylib.core.ports import Connection
from buildnotifylib.core.settings import ServerSettings

log = logging.getLogger(__name__)


class ProjectLoader:
    def __init__(
        self,
        server_config: ServerSettings,
        timeout: float | None,
        connection: Connection,
        apply_excludes: bool = True,
    ):
        self.server_config = server_config
        self.timeout = timeout
        self.connection = connection
        self.apply_excludes = apply_excludes

    def get_data(self) -> ServerSnapshot:
        log.debug("checking %s", self.server_config.url)
        try:
            headers = {}
            if self.server_config.authentication_type == ServerSettings.AUTH_BEARER_TOKEN:
                headers["Authorization"] = f"Bearer {self.server_config.password}"

            data = self.connection.connect(self.server_config, self.timeout, headers)
            projects = self.parse(data)
        except Exception as ex:
            log.warning("Failed to fetch %s: %s", self.server_config.url, ex)
            return ServerSnapshot(self.server_config.url, error=ex)
        log.debug("processed %s", self.server_config.url)
        return ServerSnapshot(self.server_config.url, tuple(projects))

    def parse(self, data: bytes) -> list[Project]:
        return cctray.parse(data, self.server_config, apply_excludes=self.apply_excludes)
