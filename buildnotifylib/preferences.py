from PyQt4 import QtCore
import pytz
from PyQt4 import QtGui
from add_server import AddServerDialog
from preferences_ui import Ui_Preferences

class PreferencesDialog(QtGui.QDialog):
    def __init__(self, conf):
        QtGui.QDialog.__init__(self)
        self.conf = conf
        self.ui = Ui_Preferences()
        self.ui.setupUi(self)
        self.checkboxes = dict(successfulBuild = self.ui.successfulBuildsCheckbox,
            brokenBuild = self.ui.brokenBuildsCheckbox, fixedBuild = self.ui.fixedBuildsCheckbox,
            stillFailingBuild = self.ui.stillFailingBuildsCheckbox, connectivityIssues = self.ui.connectivityIssuesCheckbox,
            lastBuildTimeForProject = self.ui.showLastBuildTimeCheckbox)
        self.set_values_from_config()

        # Connect up the buttons.
        self.connect(self.ui.addButton, QtCore.SIGNAL("clicked()"),
                     self.add_server)
        self.connect(self.ui.removeButton, QtCore.SIGNAL("clicked()"),
                     self.remove_element)
        self.connect(self.ui.buttonBox, QtCore.SIGNAL("accepted()"),
                     QtCore.SLOT("accept()"))

    def set_values_from_config(self):
        self.cctrayUrlsModel = QtGui.QStringListModel(self.conf.get_urls())
        self.ui.cctrayPathList.setModel(self.cctrayUrlsModel)

        timezones = QtCore.QStringList(pytz.all_timezones)
        self.ui.timezoneList.addItems(timezones)

        for key, checkbox in self.checkboxes.iteritems():
            checkbox.setChecked(self.conf.get_value(str(key)))

        self.ui.timezoneList.setCurrentIndex(timezones.indexOf(self.conf.get_timezone()))
        self.ui.browserPath.setText(self.conf.get_browser())


    def add_server(self):
        self.add_server_dialog = AddServerDialog()
        self.add_server_dialog.show()
        if self.add_server_dialog.exec_() != QtGui.QDialog.Accepted:
            return
        str = self.add_server_dialog.get_url()
        if str == "":
            return
        urls = self.ui.cctrayPathList.model().stringList()
        urls.append(str)
        self.cctrayUrlsModel = QtGui.QStringListModel(urls)
        self.ui.cctrayPathList.setModel(self.cctrayUrlsModel)

    def remove_element(self):
        index = self.ui.cctrayPathList.selectionModel().currentIndex()
        urls = self.ui.cctrayPathList.model().stringList()
        urls.removeAt(index.row())
        self.cctrayUrlsModel = QtGui.QStringListModel(urls)
        self.ui.cctrayPathList.setModel(self.cctrayUrlsModel)
    
    def get_urls(self):
        return self.ui.cctrayPathList.model().stringList()

    def get_selections(self):
        return map(lambda (key,checkbox): (key, checkbox.isChecked()), self.checkboxes.items())

    def save(self):
        self.conf.update_urls(self.get_urls())
        self.conf.set_browser(self.ui.browserPath.text())
        self.conf.set_timezone(self.ui.timezoneList.currentText())
        for key,value in self.get_selections():
            self.conf.set_value(key, value)
