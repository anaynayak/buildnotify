from PyQt4 import QtCore


class Config:
    default_options = dict(successfulBuild=False, brokenBuild=True, fixedBuild=True, stillFailingBuild=True, connectivityIssues=True, lastBuildTimeForProject=True)

    default_script = "echo #status# #projects# >> /tmp/buildnotify.log"
    CUSTOM_SCRIPT = "notifications/custom_script"
    SCRIPT_ENABLED = "notifications/custom_script_enabled"
    INTERVAL_IN_MINUTES = "connection/interval_in_minutes"
    CONNECTION_URLS = "connection/urls"
    EXCLUDES = "excludes/%s"
    TIMEZONE = "timezone/%s"
    VALUES = "values/%s"

    def __init__(self):
        self.settings = QtCore.QSettings("BuildNotify", "BuildNotify")
        self.timeout = self.get_with_default("connection/timeout", 10).toDouble()[0]
        self.interval = self.get_with_default(self.INTERVAL_IN_MINUTES, 2).toInt()[0]

    def get_with_default(self, key, default):
        if str(self.settings.value(key, "notset").toString()) == "notset":
            self.settings.setValue(key, default)
        return self.settings.value(key)

    def add_server_url(self, url):
        urls = self.get_urls()
        urls.append(url)
        self.update_urls(urls)

    def update_urls(self, urls):
        self.settings.setValue(self.CONNECTION_URLS, urls)

    def get_urls(self):
        return self.settings.value(self.CONNECTION_URLS, QtCore.QStringList()).toStringList()

    def set_interval(self, interval):
        self.settings.setValue(self.INTERVAL_IN_MINUTES, interval)

    def get_interval(self):
        return self.get_with_default(self.INTERVAL_IN_MINUTES, 2).toInt()[0]

    def get_interval_in_millis(self):
        return self.get_interval() * 1000 * 60

    def get_value(self, key):
        return self.get_with_default(self.VALUES % key, self.default_options[key]).toBool()

    def set_value(self, key, value):
        return self.settings.setValue(self.VALUES % key, value)

    def get_timezone(self, url):
        return str(self.get_with_default(self.TIMEZONE % url, "US/Central").toString())

    def get_project_timezone(self, url, server_url):
        # project level time zones can not be edited, so ditch the value
        # and just return the server's time zone
        return self.get_timezone(server_url)

    def set_project_timezone(self, url, timezone):
        self.settings.setValue(self.TIMEZONE % url, timezone)

    def set_project_excludes(self, url, excluded_project_names):
        self.settings.setValue(self.EXCLUDES % url, excluded_project_names)

    def get_project_excludes(self, url):
        return self.settings.value(self.EXCLUDES % url, QtCore.QStringList()).toStringList()

    def set_custom_script(self, user_script, status):
        script = user_script if status else self.default_script
        self.settings.setValue(self.CUSTOM_SCRIPT, script)

    def set_custom_script_enabled(self, status):
        self.settings.setValue(self.SCRIPT_ENABLED, status)

    def get_custom_script(self):
        return str(self.settings.value(self.CUSTOM_SCRIPT, self.default_script).toString())

    def get_custom_script_enabled(self):
        return self.settings.value(self.SCRIPT_ENABLED, False).toBool()
