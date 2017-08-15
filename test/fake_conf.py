from buildnotifylib.config import Config


class FakeSettings:
    def __init__(self, hash={}):
        self.hash = hash

    def setValue(self, key, val):
        self.hash[key] = val

    def value(self, key, fallback=None, type=None):
        return self.hash.get(key, fallback)


class ConfigBuilder:
    def __init__(self, overrides={}):
        self.conf = {
            'sort_by_name': True,
            'values/lastBuildTimeForProject': False
        }
        self._merge(overrides)

    def server(self, url, overrides={}):
        urls = self.conf.get('connection/urls', [])
        urls.append(url)
        self._merge({'connection/urls': urls})
        self._merge({'display_prefix/%s' % url: ""})
        self._merge(overrides)
        return self

    def build(self):
        return Config(FakeSettings(self.conf))

    def _merge(self, overrides):
        self.conf = dict(self.conf.items() + overrides.items())
