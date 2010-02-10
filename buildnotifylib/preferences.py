from PyQt4 import QtCore, QtGui
from preferences_ui import Ui_Preferences
import sys

class PreferencesDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)

        self.ui = Ui_Preferences()
        self.ui.setupUi(self)

        self.cctrayUrlsModel = QtGui.QStringListModel()
        self.cctrayUrls = QtCore.QStringList()
        self.ui.cctrayPathList.setModel(self.cctrayUrlsModel)

        # Connect up the buttons.
#        self.connect(self.ui.buttonBox, QtCore.SIGNAL("accepted()"),
#                     self, QtCore.SLOT("accept()"))
        self.connect(self.ui.cctrayPath, QtCore.SIGNAL("returnPressed()"),
                     self.return_pressed)
        self.connect(self.ui.cctrayPathList, QtCore.SIGNAL("doubleClicked()"),
                     self.remove_element)
    def return_pressed(self):
        str = self.ui.cctrayPath.text()
        self.ui.cctrayPath.clear()
        self.cctrayUrls.append(str);
        self.cctrayUrlsModel.setStringList(self.cctrayUrls)



if __name__== '__main__':
    app = QtGui.QApplication(sys.argv)
    ui = PreferencesDialog()
    ui.show()
    sys.exit(app.exec_())