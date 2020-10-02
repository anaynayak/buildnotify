import platform
from typing import Optional, Dict

import requests
from buildnotifylib.serverconfig import ServerConfig


class HttpConnection(object):
    def __init__(self):
        self.user_agent = "%s-%s" % ("BuildNotify", platform.platform())

    def connect(self, server: ServerConfig, timeout: Optional[float], additional_headers: Dict[str, str] = None) -> str:
        headers = {'user-agent': self.user_agent}
        headers.update(additional_headers or {})

        auth = (server.username, server.password) if server.has_creds() else None
        response = requests.get(server.url, verify=not server.skip_ssl_verification, headers=headers, auth=auth,
                                timeout=timeout)
        response.encoding = 'utf-8'
        response.raise_for_status()
        return response.text
