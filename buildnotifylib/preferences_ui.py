# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'preferences.ui'
#
# Created: Tue Feb  9 21:27:48 2010
#      by: PyQt4 UI code generator 4.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Preferences(object):
    def setupUi(self, Preferences):
        Preferences.setObjectName("Preferences")
        Preferences.resize(442, 303)
        self.gridLayoutWidget = QtGui.QWidget(Preferences)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 423, 281))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.cctrayPathList = QtGui.QListView(self.gridLayoutWidget)
        self.cctrayPathList.setObjectName("cctrayPathList")
        self.gridLayout.addWidget(self.cctrayPathList, 2, 0, 1, 1)
        self.cctrayPath = QtGui.QLineEdit(self.gridLayoutWidget)
        self.cctrayPath.setObjectName("cctrayPath")
        self.gridLayout.addWidget(self.cctrayPath, 1, 0, 1, 1)
        self.cctrayPathLabel = QtGui.QLabel(self.gridLayoutWidget)
        self.cctrayPathLabel.setObjectName("cctrayPathLabel")
        self.gridLayout.addWidget(self.cctrayPathLabel, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self.gridLayoutWidget)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 1)

        self.retranslateUi(Preferences)
        QtCore.QMetaObject.connectSlotsByName(Preferences)

    def retranslateUi(self, Preferences):
        Preferences.setWindowTitle(QtGui.QApplication.translate("Preferences", "Preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.cctrayPathLabel.setText(QtGui.QApplication.translate("Preferences", "Path to cctray.xml", None, QtGui.QApplication.UnicodeUTF8))

