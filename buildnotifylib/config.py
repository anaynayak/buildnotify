from PyQt5 import QtCore
from serverconfig import ServerConfig
from core.keystore import Keystore

class Config:
    default_options = dict(successfulBuild=False, brokenBuild=True, fixedBuild=True, stillFailingBuild=True, connectivityIssues=True, lastBuildTimeForProject=True)

    default_script = "echo #status# #projects# >> /tmp/buildnotify.log"
    CUSTOM_SCRIPT = "notifications/custom_script"
    SCRIPT_ENABLED = "notifications/custom_script_enabled"
    SORT_KEY = "sort_key"
    INTERVAL_IN_SECONDS = "connection/interval_in_seconds"
    CONNECTION_URLS = "connection/urls"
    EXCLUDES = "excludes/%s"
    TIMEZONE = "timezone/%s"
    USERNAME = "username/%s"
    PASSWORD = "password/%s"
    SKIP_SSL_VERIFICATION = "skip_ssl_verification/%s"
    DISPLAY_PREFIX = "display_prefix/%s"
    VALUES = "values/%s"
    NONE_TIMEZONE = "None"

    SORT_BY_LAST_BUILD_TIME = "sort_build_time"
    SORT_BY_NAME = "sort_name"

    def __init__(self, settings = QtCore.QSettings("BuildNotify", "BuildNotify")):
        self.settings = settings
        self.keystore = Keystore()
        self.timeout = self.get_with_default("connection/timeout", 10, int)
        self.interval = self.get_with_default(self.INTERVAL_IN_SECONDS, 2 * 60, int)

    def get_with_default(self, key, default, usertype):
        if self.settings.value(key, "notset") == "notset":
            self.settings.setValue(key, default)
        return self.settings.value(key, type=usertype)

    def add_server_url(self, url):
        urls = self.get_urls()
        if url in urls:
            return
        urls.append(url)
        self.update_urls(urls)

    def update_urls(self, urls):
        if urls:
            self.settings.setValue(self.CONNECTION_URLS, urls)

    def get_urls(self):
        return [str(url) for url in self.settings.value(self.CONNECTION_URLS, [])]

    def set_interval_in_seconds(self, interval):
        self.settings.setValue(self.INTERVAL_IN_SECONDS, interval)

    def get_interval_in_seconds(self):
        default = self.get_with_default(self.INTERVAL_IN_SECONDS, 2 * 60, int)
        return default

    def get_interval_in_millis(self):
        return self.get_interval_in_seconds() * 1000

    def get_value(self, key):
        return self.get_with_default(self.VALUES % key, self.default_options[key], bool)

    def set_value(self, key, value):
        return self.settings.setValue(self.VALUES % key, value)

    def get_timezone(self, url):
        return self.get_with_default(self.TIMEZONE % url, "None", str)

    def set_timezone(self, url, timezone):
        self.settings.setValue(self.TIMEZONE % url, timezone)

    def set_display_prefix(self, url, prefix):
        self.settings.setValue(self.DISPLAY_PREFIX % url, prefix)

    def get_display_prefix(self, url):
        return self.settings.value(self.DISPLAY_PREFIX % url)

    def set_project_excludes(self, url, excluded_project_names):
        self.settings.setValue(self.EXCLUDES % url, excluded_project_names)

    def get_project_excludes(self, url):
        return self.settings.value(self.EXCLUDES % url, [])

    def set_custom_script(self, user_script, status):
        script = user_script if status else self.default_script
        self.settings.setValue(self.CUSTOM_SCRIPT, script)

    def set_custom_script_enabled(self, status):
        self.settings.setValue(self.SCRIPT_ENABLED, status)

    def get_custom_script(self):
        return self.settings.value(self.CUSTOM_SCRIPT, self.default_script)

    def get_custom_script_enabled(self):
        return self.settings.value(self.SCRIPT_ENABLED, False, bool)

    def get_sort_by_last_build_time(self):
        return self.settings.value(self.SORT_KEY, self.SORT_BY_LAST_BUILD_TIME) == self.SORT_BY_LAST_BUILD_TIME

    def get_sort_by_name(self):
        return self.settings.value(self.SORT_KEY, self.SORT_BY_LAST_BUILD_TIME) == self.SORT_BY_NAME

    def set_sort_by_last_build_time(self):
        self.settings.setValue(self.SORT_KEY, self.SORT_BY_LAST_BUILD_TIME)

    def set_sort_by_name(self):
        self.settings.setValue(self.SORT_KEY, self.SORT_BY_NAME)

    def set_username(self, url, username):
        self.settings.setValue(self.USERNAME % url, username)

    def get_username(self, url):
        return self.settings.value(self.USERNAME % url, '')

    def set_password(self, url, username, password):
        self.keystore.save(url, username, password)

    def get_password(self, url, username):
        return self.keystore.load(url, username) or ''

    def set_skip_ssl_verification(self, url, skip_ssl_verification):
        self.settings.setValue(self.SKIP_SSL_VERIFICATION % url, skip_ssl_verification)

    def get_skip_ssl_verification(self, url):
        return self.settings.value(self.SKIP_SSL_VERIFICATION % url, False, bool)

    def save_server_config(self, server_config):
        self.add_server_url(server_config.url)
        self.set_project_excludes(server_config.url, server_config.excluded_projects)
        self.set_timezone(server_config.url, server_config.timezone)
        self.set_display_prefix(server_config.url, server_config.prefix)
        self.set_username(server_config.url, server_config.username)
        self.set_password(server_config.url, server_config.username, server_config.password)
        self.set_skip_ssl_verification(server_config.url, server_config.skip_ssl_verification)

    def get_server_config(self, url):
        username = self.get_username(url)
        return ServerConfig(url, self.get_project_excludes(url), self.get_timezone(url),
                            self.get_display_prefix(url), username, self.get_password(url, username),
                            self.get_skip_ssl_verification(url))

    def get_server_configs(self):
        return [self.get_server_config(url) for url in self.get_urls()]

    def update_preferences(self, preferences):
        self.update_urls(preferences.urls)
        self.set_interval_in_seconds(preferences.interval)
        self.set_custom_script(preferences.custom_script_text, preferences.trigger_custom_script)
        self.set_custom_script_enabled(preferences.trigger_custom_script)
        if preferences.sort_by_build_time:
            self.set_sort_by_last_build_time()
        if preferences.sort_by_name:
            self.set_sort_by_name()
        for key, value in preferences.selections:
            self.set_value(key, value)
