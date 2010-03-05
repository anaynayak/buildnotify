# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'add_server.ui'
#
# Created: Sat Feb 27 20:43:30 2010
#      by: PyQt4 UI code generator 4.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_AddServerDialog(object):
    def setupUi(self, AddServerDialog):
        AddServerDialog.setObjectName("AddServerDialog")
        AddServerDialog.resize(572, 88)
        self.buttonBox = QtGui.QDialogButtonBox(AddServerDialog)
        self.buttonBox.setGeometry(QtCore.QRect(470, 40, 81, 31))
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.url = QtGui.QLineEdit(AddServerDialog)
        self.url.setGeometry(QtCore.QRect(10, 40, 431, 31))
        self.url.setObjectName("url")
        self.label = QtGui.QLabel(AddServerDialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 171, 21))
        self.label.setObjectName("label")
        self.label.setBuddy(self.url)

        self.retranslateUi(AddServerDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), AddServerDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), AddServerDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AddServerDialog)

    def retranslateUi(self, AddServerDialog):
        AddServerDialog.setWindowTitle(QtGui.QApplication.translate("AddServerDialog", "Add Server", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("AddServerDialog", "Path to cctray.xml", None, QtGui.QApplication.UnicodeUTF8))

