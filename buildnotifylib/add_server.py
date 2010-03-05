from add_server_ui import Ui_AddServerDialog
from PyQt4 import QtCore, QtGui

class AddServerDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)

        self.ui = Ui_AddServerDialog()
        self.ui.setupUi(self)
        self.connect(self.ui.buttonBox, QtCore.SIGNAL("accepted()"),
                     QtCore.SLOT("accept()"))

    def get_url(self):
        return self.ui.url.text()