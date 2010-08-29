# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data/server_configuration.ui'
#
# Created: Sun Aug 29 13:54:10 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_serverConfigurationDialog(object):
    def setupUi(self, serverConfigurationDialog):
        serverConfigurationDialog.setObjectName("serverConfigurationDialog")
        serverConfigurationDialog.resize(435, 319)
        self.buttonBox = QtGui.QDialogButtonBox(serverConfigurationDialog)
        self.buttonBox.setGeometry(QtCore.QRect(240, 280, 191, 31))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.projectsList = QtGui.QListView(serverConfigurationDialog)
        self.projectsList.setGeometry(QtCore.QRect(20, 80, 401, 191))
        self.projectsList.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.projectsList.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.projectsList.setObjectName("projectsList")
        self.label = QtGui.QLabel(serverConfigurationDialog)
        self.label.setGeometry(QtCore.QRect(20, 60, 391, 20))
        self.label.setObjectName("label")
        self.horizontalLayoutWidget = QtGui.QWidget(serverConfigurationDialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(20, 10, 401, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.cctrayUrlLabel = QtGui.QLabel(self.horizontalLayoutWidget)
        self.cctrayUrlLabel.setObjectName("cctrayUrlLabel")
        self.horizontalLayout.addWidget(self.cctrayUrlLabel)
        self.addServerUrl = QtGui.QLineEdit(self.horizontalLayoutWidget)
        self.addServerUrl.setObjectName("addServerUrl")
        self.horizontalLayout.addWidget(self.addServerUrl)
        self.loadUrlButton = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.loadUrlButton.setObjectName("loadUrlButton")
        self.horizontalLayout.addWidget(self.loadUrlButton)
        self.label.setBuddy(self.projectsList)
        self.cctrayUrlLabel.setBuddy(self.addServerUrl)

        self.retranslateUi(serverConfigurationDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), serverConfigurationDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), serverConfigurationDialog.reject)
        QtCore.QObject.connect(self.addServerUrl, QtCore.SIGNAL("returnPressed()"), self.loadUrlButton.click)
        QtCore.QMetaObject.connectSlotsByName(serverConfigurationDialog)
        serverConfigurationDialog.setTabOrder(self.addServerUrl, self.loadUrlButton)
        serverConfigurationDialog.setTabOrder(self.loadUrlButton, self.projectsList)
        serverConfigurationDialog.setTabOrder(self.projectsList, self.buttonBox)

    def retranslateUi(self, serverConfigurationDialog):
        serverConfigurationDialog.setWindowTitle(QtGui.QApplication.translate("serverConfigurationDialog", "Add Server", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("serverConfigurationDialog", "Select projects", None, QtGui.QApplication.UnicodeUTF8))
        self.cctrayUrlLabel.setText(QtGui.QApplication.translate("serverConfigurationDialog", "cctray.xml", None, QtGui.QApplication.UnicodeUTF8))
        self.loadUrlButton.setText(QtGui.QApplication.translate("serverConfigurationDialog", "Load", None, QtGui.QApplication.UnicodeUTF8))

