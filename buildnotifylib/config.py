from PyQt4 import QtCore
class Config:
    default_options = dict(successfulBuild = False,
        brokenBuild = True, fixedBuild = True,
        stillFailingBuild = True, connectivityIssues = True,
        lastBuildTimeForProject = True)

    def __init__(self):
        self.settings = QtCore.QSettings("BuildNotify", "BuildNotify")
        if (str(self.settings.value("misc/settings", "notset").toString()) == "notset"):
            self.set_defaults()
            
        self.timeout = self.settings.value("connection/timeout").toDouble()[0]
        self.check_interval = self.settings.value("connection/interval").toInt()[0]

    def set_defaults(self):
        self.settings.setValue("misc/settings", "0.1")
        self.settings.setValue("connection/timeout",10)
        self.settings.setValue("connection/interval", 30)
        self.settings.setValue("misc/timezone", "US/Central")
        for key,value in self.default_options.items():
            self.settings.setValue("values/%s" % key, value)
        
    def update_urls(self, urls):
        self.settings.setValue("connection/urls", urls)

    def get_urls(self):
        return self.settings.value("connection/urls", QtCore.QStringList()).toStringList()

    def get_value(self, key):
        return self.settings.value("values/%s" % key).toBool()

    def set_value(self, key, value):
        return self.settings.setValue("values/%s" % key, value)

    def get_timezone(self):
        return str(self.settings.value("misc/timezone").toString())

    def set_timezone(self, timezone):
        self.settings.setValue("misc/timezone",timezone)
