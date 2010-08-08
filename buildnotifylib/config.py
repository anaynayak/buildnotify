from PyQt4 import QtCore
class Config:
    default_options = dict(successfulBuild = False,
        brokenBuild = True, fixedBuild = True,
        stillFailingBuild = True, connectivityIssues = True,
        lastBuildTimeForProject = True)

    def __init__(self):
        self.settings = QtCore.QSettings("BuildNotify", "BuildNotify")
        self.timeout = self.get_with_default("connection/timeout", 10).toDouble()[0]
        self.interval = self.get_with_default("connection/interval_in_minutes", 2).toInt()[0]

    def get_with_default(self, key, default):
        if (str(self.settings.value(key, "notset").toString()) == "notset"):
            self.settings.setValue(key, default)
        return self.settings.value(key)

        
    def update_urls(self, urls):
        self.settings.setValue("connection/urls", urls)

    def get_urls(self):
        return self.settings.value("connection/urls", QtCore.QStringList()).toStringList()

    def set_interval(self, interval):
        self.interval = interval
        self.settings.setValue("connection/interval", interval)
    
    def get_interval(self):
        return self.interval
    
    def get_interval_in_millis(self):
        return self.get_interval() * 1000 * 60
        
    def get_value(self, key):
        return self.get_with_default("values/%s" % key , self.default_options[key]).toBool()

    def set_value(self, key, value):
        return self.settings.setValue("values/%s" % key, value)

    def get_timezone(self):
        return str(self.get_with_default("misc/timezone", "US/Central").toString())

    def set_timezone(self, timezone):
        self.settings.setValue("misc/timezone",timezone)
