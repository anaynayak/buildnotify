from PyQt4 import QtCore, QtGui
from preferences_ui import Ui_Preferences

class PreferencesDialog(QtGui.QDialog):
    def __init__(self, cctrayUrls=[]):
        QtGui.QDialog.__init__(self)

        self.ui = Ui_Preferences()
        self.ui.setupUi(self)
        self.cctrayUrlsModel = QtGui.QStringListModel(cctrayUrls)
        self.ui.cctrayPathList.setModel(self.cctrayUrlsModel)

        # Connect up the buttons.
        self.connect(self.ui.addButton, QtCore.SIGNAL("clicked()"),
                     self.return_pressed)
        self.connect(self.ui.removeButton, QtCore.SIGNAL("clicked()"),
                     self.remove_element)
        self.connect(self.ui.buttonBox, QtCore.SIGNAL("accepted()"),
                     QtCore.SLOT("accept()"))

    def return_pressed(self):
        str = self.ui.cctrayPath.text()
        self.ui.cctrayPath.clear()
        urls = self.ui.cctrayPathList.model().stringList()
        urls.append(str)
        self.ui.cctrayPathList.model().setStringList(urls)
        return

    def remove_element(self):
        index = self.ui.cctrayPathList.selectionModel().currentIndex()
        urls = self.ui.cctrayPathList.model().stringList()
        urls.removeAt(index.row())
        self.ui.cctrayPathList.model().setStringList(urls)
        return
    
    def get_urls(self):
        return self.ui.cctrayPathList.model().stringList()

