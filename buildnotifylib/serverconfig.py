from buildnotifylib.core.model import normalise_url


class ServerConfig:
    AUTH_USERNAME_PASSWORD = 0
    AUTH_BEARER_TOKEN = 1

    def __init__(
        self,
        url: str,
        excluded_projects: list[str],
        timezone: str,
        prefix: str,
        username: str,
        password: str,
        skip_ssl_verification=False,
        authentication_type=AUTH_USERNAME_PASSWORD,
    ):
        self.url = self.cleanup(url)
        self.excluded_projects = excluded_projects
        self.timezone = timezone
        self.prefix = prefix
        self.authentication_type = authentication_type
        self.username = username
        self.password = password
        self.skip_ssl_verification = skip_ssl_verification

    def has_creds(self) -> bool:
        return self.username != "" and self.username is not None

    @staticmethod
    def cleanup(url: str) -> str:
        return normalise_url(url)
