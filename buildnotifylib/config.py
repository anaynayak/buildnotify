from PyQt4 import QtCore
class Config:
    def __init__(self):
        self.settings = QtCore.QSettings("BuildNotify", "BuildNotify")
        self.timeout = self.settings.value("connection/timeout",2).toDouble()[0]
        self.check_interval = self.settings.value("connection/interval", "15").toInt()[0]
        self.browser = self.settings.value("connection/browser", "firefox")

    def update_urls(self, urls):
        self.settings.setValue("connection/urls", urls)

    def get_urls(self):
        return self.settings.value("connection/urls", QtCore.QStringList()).toStringList()
