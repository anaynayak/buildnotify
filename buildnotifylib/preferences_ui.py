# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'preferences.ui'
#
# Created: Fri Feb 12 23:09:09 2010
#      by: PyQt4 UI code generator 4.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Preferences(object):
    def setupUi(self, Preferences):
        Preferences.setObjectName("Preferences")
        Preferences.resize(441, 300)
        self.gridLayoutWidget = QtGui.QWidget(Preferences)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 423, 281))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.cctrayPathList = QtGui.QListView(self.gridLayoutWidget)
        self.cctrayPathList.setObjectName("cctrayPathList")
        self.gridLayout.addWidget(self.cctrayPathList, 2, 0, 1, 1)
        self.cctrayPathLabel = QtGui.QLabel(self.gridLayoutWidget)
        self.cctrayPathLabel.setObjectName("cctrayPathLabel")
        self.gridLayout.addWidget(self.cctrayPathLabel, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self.gridLayoutWidget)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.cctrayPath = QtGui.QLineEdit(self.gridLayoutWidget)
        self.cctrayPath.setObjectName("cctrayPath")
        self.horizontalLayout_2.addWidget(self.cctrayPath)
        self.addButton = QtGui.QPushButton(self.gridLayoutWidget)
        self.addButton.setObjectName("addButton")
        self.horizontalLayout_2.addWidget(self.addButton)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)

        self.removeButton = QtGui.QPushButton("&Remove");
        self.buttonBox.addButton(self.removeButton, QtGui.QDialogButtonBox.ActionRole)

        self.retranslateUi(Preferences)
        QtCore.QObject.connect(self.cctrayPath, QtCore.SIGNAL("returnPressed()"), self.addButton.animateClick)
        QtCore.QMetaObject.connectSlotsByName(Preferences)

    def retranslateUi(self, Preferences):
        Preferences.setWindowTitle(QtGui.QApplication.translate("Preferences", "Preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.cctrayPathLabel.setText(QtGui.QApplication.translate("Preferences", "Path to cctray.xml", None, QtGui.QApplication.UnicodeUTF8))
        self.addButton.setText(QtGui.QApplication.translate("Preferences", "&Add", None, QtGui.QApplication.UnicodeUTF8))

