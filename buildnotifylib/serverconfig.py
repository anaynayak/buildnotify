from typing import List
from urllib.parse import urlparse


class ServerConfig(object):
    VALID_SCHEMES = ('http', 'https', 'file')
    AUTH_USERNAME_PASSWORD = 0
    AUTH_BEARER_TOKEN = 1

    def __init__(self, url: str, excluded_projects: List[str], timezone: str, prefix: str, username: str,
                 password: str, skip_ssl_verification=False, authentication_type=AUTH_USERNAME_PASSWORD):
        self.url = self.cleanup(url)
        self.excluded_projects = excluded_projects
        self.timezone = timezone
        self.prefix = prefix
        self.authentication_type = authentication_type
        self.username = username
        self.password = password
        self.skip_ssl_verification = skip_ssl_verification

    def has_creds(self) -> bool:
        return self.username != '' and self.username is not None

    @staticmethod
    def cleanup(url: str) -> str:
        parsed = urlparse(url)
        if parsed.scheme not in ServerConfig.VALID_SCHEMES:
            return 'http://' + url
        return parsed.geturl()
