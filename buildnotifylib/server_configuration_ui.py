# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data/server_configuration.ui'
#
# Created: Tue Aug 31 17:06:09 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_serverConfigurationDialog(object):
    def setupUi(self, serverConfigurationDialog):
        serverConfigurationDialog.setObjectName("serverConfigurationDialog")
        serverConfigurationDialog.resize(435, 319)
        self.projectsList = QtGui.QListView(serverConfigurationDialog)
        self.projectsList.setGeometry(QtCore.QRect(20, 80, 401, 191))
        self.projectsList.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.projectsList.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.projectsList.setObjectName("projectsList")
        self.label = QtGui.QLabel(serverConfigurationDialog)
        self.label.setGeometry(QtCore.QRect(20, 60, 391, 20))
        self.label.setObjectName("label")
        self.cctrayUrlLabel = QtGui.QLabel(serverConfigurationDialog)
        self.cctrayUrlLabel.setGeometry(QtCore.QRect(20, 0, 161, 41))
        self.cctrayUrlLabel.setObjectName("cctrayUrlLabel")
        self.addServerUrl = QtGui.QLineEdit(serverConfigurationDialog)
        self.addServerUrl.setGeometry(QtCore.QRect(20, 30, 311, 30))
        self.addServerUrl.setObjectName("addServerUrl")
        self.loadUrlButton = QtGui.QPushButton(serverConfigurationDialog)
        self.loadUrlButton.setGeometry(QtCore.QRect(340, 30, 81, 31))
        self.loadUrlButton.setAutoDefault(False)
        self.loadUrlButton.setObjectName("loadUrlButton")
        self.submitButton = QtGui.QPushButton(serverConfigurationDialog)
        self.submitButton.setGeometry(QtCore.QRect(340, 280, 81, 31))
        self.submitButton.setAutoDefault(False)
        self.submitButton.setObjectName("submitButton")
        self.label.setBuddy(self.projectsList)
        self.cctrayUrlLabel.setBuddy(self.addServerUrl)

        self.retranslateUi(serverConfigurationDialog)
        QtCore.QObject.connect(self.addServerUrl, QtCore.SIGNAL("returnPressed()"), self.loadUrlButton.click)
        QtCore.QObject.connect(self.submitButton, QtCore.SIGNAL("clicked()"), serverConfigurationDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(serverConfigurationDialog)
        serverConfigurationDialog.setTabOrder(self.addServerUrl, self.loadUrlButton)
        serverConfigurationDialog.setTabOrder(self.loadUrlButton, self.submitButton)
        serverConfigurationDialog.setTabOrder(self.submitButton, self.projectsList)

    def retranslateUi(self, serverConfigurationDialog):
        serverConfigurationDialog.setWindowTitle(QtGui.QApplication.translate("serverConfigurationDialog", "Add Server", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("serverConfigurationDialog", "Select projects", None, QtGui.QApplication.UnicodeUTF8))
        self.cctrayUrlLabel.setText(QtGui.QApplication.translate("serverConfigurationDialog", "Path to cctray.xml", None, QtGui.QApplication.UnicodeUTF8))
        self.loadUrlButton.setText(QtGui.QApplication.translate("serverConfigurationDialog", "Load", None, QtGui.QApplication.UnicodeUTF8))
        self.submitButton.setText(QtGui.QApplication.translate("serverConfigurationDialog", "OK", None, QtGui.QApplication.UnicodeUTF8))

