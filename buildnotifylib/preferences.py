from PyQt4 import QtCore, QtGui
from preferences_ui import Ui_Preferences

class PreferencesDialog(QtGui.QDialog):
    def __init__(self, config=None):
        QtGui.QDialog.__init__(self)

        self.ui = Ui_Preferences()
        self.ui.setupUi(self)
        self.config = config
        self.cctrayUrlsModel = QtGui.QStringListModel()
        self.cctrayUrls = QtCore.QStringList()
        urls = self.config.get_urls()
        print urls
        for url in urls:
            self.cctrayUrls.append(url)
        self.ui.cctrayPathList.setModel(self.cctrayUrlsModel)
        self.cctrayUrlsModel.setStringList(self.cctrayUrls)

        # Connect up the buttons.
        self.connect(self.ui.addButton, QtCore.SIGNAL("returnPressed()"),
                     self.return_pressed)
        self.connect(self.ui.removeButton, QtCore.SIGNAL("clicked()"),
                     self.remove_element)
        self.connect(self.ui.buttonBox, QtCore.SIGNAL("accepted()"),
                     self.save_changes)
        self.connect(self.ui.buttonBox, QtCore.SIGNAL("accepted()"),
                     QtCore.SLOT("accept()"))

    def return_pressed(self):
        str = self.ui.cctrayPath.text()
        self.ui.cctrayPath.clear()
        self.cctrayUrls.append(str);
        self.cctrayUrlsModel.setStringList(self.cctrayUrls)

    def remove_element(self):
        index = self.ui.cctrayPathList.selectionModel().currentIndex()
        self.ui.cctrayPathList.model().removeRow(index.row(), index.parent())

    def save_changes(self):
        cctrayPaths = self.ui.cctrayPathList.model().stringList()
        self.config.update_urls(cctrayPaths.join(","))
