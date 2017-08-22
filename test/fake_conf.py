from buildnotifylib.config import Config


class FakeSettings(object):
    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        self.settings = settings

    def setValue(self, key, val):
        self.settings[key] = val

    def value(self, key, fallback=None, type=None):
        return self.settings.get(key, fallback)


class ConfigBuilder(object):
    def __init__(self, overrides=None):
        if overrides is None:
            overrides = {}
        self.conf = {
            'sort_by_name': True,
            'values/lastBuildTimeForProject': False
        }
        self._merge(overrides)

    def server(self, url, overrides=None):
        if overrides is None:
            overrides = {}
        urls = self.conf.get('connection/urls', [])
        urls.append(url)
        self._merge({'connection/urls': urls})
        self._merge({'display_prefix/%s' % url: ""})
        self._merge(overrides)
        return self

    def build(self):
        return Config(FakeSettings(self.conf))

    def _merge(self, overrides):
        self.conf = dict(self.conf, **overrides)
