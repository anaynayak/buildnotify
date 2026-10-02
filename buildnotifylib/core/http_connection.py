from typing import Optional, Dict

import requests
from buildnotifylib.serverconfig import ServerConfig
from buildnotifylib.version import VERSION


class HttpConnection(object):
    def __init__(self):
        self.user_agent = "BuildNotify/%s" % VERSION
        self.session = requests.Session()

    def connect(self, server: ServerConfig, timeout: Optional[float], additional_headers: Dict[str, str] = None) -> bytes:
        headers = {'user-agent': self.user_agent}
        headers.update(additional_headers or {})

        auth = (server.username, server.password) if self.uses_basic_auth(server) else None
        response = self.session.get(server.url, verify=not server.skip_ssl_verification, headers=headers, auth=auth,
                                    timeout=timeout)
        response.raise_for_status()
        return response.content

    @staticmethod
    def uses_basic_auth(server: ServerConfig) -> bool:
        return server.authentication_type == ServerConfig.AUTH_USERNAME_PASSWORD and server.has_creds()
