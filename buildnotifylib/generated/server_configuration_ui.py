# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data/server_configuration.ui'
#
# Created: Tue Mar 18 20:49:08 2014
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_serverConfigurationDialog(object):
    def setupUi(self, serverConfigurationDialog):
        serverConfigurationDialog.setObjectName(_fromUtf8("serverConfigurationDialog"))
        serverConfigurationDialog.resize(440, 381)
        self.projectsList = QtGui.QListView(serverConfigurationDialog)
        self.projectsList.setGeometry(QtCore.QRect(20, 80, 401, 191))
        self.projectsList.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.projectsList.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.projectsList.setObjectName(_fromUtf8("projectsList"))
        self.label = QtGui.QLabel(serverConfigurationDialog)
        self.label.setGeometry(QtCore.QRect(20, 60, 391, 20))
        self.label.setObjectName(_fromUtf8("label"))
        self.cctrayUrlLabel = QtGui.QLabel(serverConfigurationDialog)
        self.cctrayUrlLabel.setGeometry(QtCore.QRect(20, 0, 161, 41))
        self.cctrayUrlLabel.setObjectName(_fromUtf8("cctrayUrlLabel"))
        self.addServerUrl = QtGui.QLineEdit(serverConfigurationDialog)
        self.addServerUrl.setGeometry(QtCore.QRect(20, 30, 311, 30))
        self.addServerUrl.setObjectName(_fromUtf8("addServerUrl"))
        self.loadUrlButton = QtGui.QPushButton(serverConfigurationDialog)
        self.loadUrlButton.setGeometry(QtCore.QRect(340, 30, 81, 31))
        self.loadUrlButton.setAutoDefault(False)
        self.loadUrlButton.setObjectName(_fromUtf8("loadUrlButton"))
        self.submitButton = QtGui.QPushButton(serverConfigurationDialog)
        self.submitButton.setGeometry(QtCore.QRect(340, 340, 81, 31))
        self.submitButton.setAutoDefault(False)
        self.submitButton.setObjectName(_fromUtf8("submitButton"))
        self.layoutWidget = QtGui.QWidget(serverConfigurationDialog)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 280, 401, 41))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.timezoneLabel = QtGui.QLabel(self.layoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.timezoneLabel.sizePolicy().hasHeightForWidth())
        self.timezoneLabel.setSizePolicy(sizePolicy)
        self.timezoneLabel.setMinimumSize(QtCore.QSize(180, 0))
        self.timezoneLabel.setMaximumSize(QtCore.QSize(180, 16777215))
        self.timezoneLabel.setObjectName(_fromUtf8("timezoneLabel"))
        self.horizontalLayout.addWidget(self.timezoneLabel)
        self.timezoneList = QtGui.QComboBox(self.layoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.timezoneList.sizePolicy().hasHeightForWidth())
        self.timezoneList.setSizePolicy(sizePolicy)
        self.timezoneList.setMinimumSize(QtCore.QSize(210, 0))
        self.timezoneList.setMaximumSize(QtCore.QSize(200, 16777215))
        self.timezoneList.setObjectName(_fromUtf8("timezoneList"))
        self.horizontalLayout.addWidget(self.timezoneList)
        self.label.setBuddy(self.projectsList)
        self.cctrayUrlLabel.setBuddy(self.addServerUrl)
        self.timezoneLabel.setBuddy(self.timezoneList)

        self.retranslateUi(serverConfigurationDialog)
        QtCore.QObject.connect(self.addServerUrl, QtCore.SIGNAL(_fromUtf8("returnPressed()")), self.loadUrlButton.click)
        QtCore.QObject.connect(self.submitButton, QtCore.SIGNAL(_fromUtf8("clicked()")), serverConfigurationDialog.accept)
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
        self.timezoneLabel.setText(QtGui.QApplication.translate("serverConfigurationDialog", "Server timezone", None, QtGui.QApplication.UnicodeUTF8))

