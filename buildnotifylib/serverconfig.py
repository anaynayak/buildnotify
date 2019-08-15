from urllib.parse import urlparse


class ServerConfig(object):
    VALID_SCHEMES = ('http', 'https', 'file')

    def __init__(self, url, excluded_projects, timezone, prefix, username,
                 password, skip_ssl_verification=False):
        self.url = self.cleanup(url)
        self.excluded_projects = excluded_projects
        self.timezone = timezone
        self.prefix = prefix
        self.username = username
        self.password = password
        self.skip_ssl_verification = skip_ssl_verification

    def has_creds(self):
        return self.username != '' and self.username is not None

    @staticmethod
    def cleanup(url):
        parsed = urlparse(url)
        if parsed.scheme not in ServerConfig.VALID_SCHEMES:
            return 'http://' + url
        return parsed.geturl()
