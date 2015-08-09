# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data/server_configuration.ui'
#
# Created: Sun Aug  9 15:48:59 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_serverConfigurationDialog(object):
    def setupUi(self, serverConfigurationDialog):
        serverConfigurationDialog.setObjectName(_fromUtf8("serverConfigurationDialog"))
        serverConfigurationDialog.resize(439, 397)
        self.projectsList = QtGui.QTreeView(serverConfigurationDialog)
        self.projectsList.setGeometry(QtCore.QRect(20, 70, 401, 191))
        self.projectsList.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.projectsList.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.projectsList.setObjectName(_fromUtf8("projectsList"))
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
        self.submitButton.setGeometry(QtCore.QRect(340, 350, 81, 31))
        self.submitButton.setAutoDefault(False)
        self.submitButton.setObjectName(_fromUtf8("submitButton"))
        self.layoutWidget = QtGui.QWidget(serverConfigurationDialog)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 270, 401, 41))
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
        self.layoutWidget_2 = QtGui.QWidget(serverConfigurationDialog)
        self.layoutWidget_2.setGeometry(QtCore.QRect(20, 310, 401, 41))
        self.layoutWidget_2.setObjectName(_fromUtf8("layoutWidget_2"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.layoutWidget_2)
        self.horizontalLayout_3.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.horizontalLayout_3.setMargin(0)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.displayPrefixLabel = QtGui.QLabel(self.layoutWidget_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.displayPrefixLabel.sizePolicy().hasHeightForWidth())
        self.displayPrefixLabel.setSizePolicy(sizePolicy)
        self.displayPrefixLabel.setMinimumSize(QtCore.QSize(180, 0))
        self.displayPrefixLabel.setMaximumSize(QtCore.QSize(180, 16777215))
        self.displayPrefixLabel.setObjectName(_fromUtf8("displayPrefixLabel"))
        self.horizontalLayout_3.addWidget(self.displayPrefixLabel)
        self.displayPrefix = QtGui.QLineEdit(self.layoutWidget_2)
        self.displayPrefix.setMinimumSize(QtCore.QSize(210, 0))
        self.displayPrefix.setObjectName(_fromUtf8("displayPrefix"))
        self.horizontalLayout_3.addWidget(self.displayPrefix)
        self.cctrayUrlLabel.setBuddy(self.addServerUrl)
        self.timezoneLabel.setBuddy(self.timezoneList)
        self.displayPrefixLabel.setBuddy(self.timezoneList)

        self.retranslateUi(serverConfigurationDialog)
        QtCore.QObject.connect(self.addServerUrl, QtCore.SIGNAL(_fromUtf8("returnPressed()")), self.loadUrlButton.click)
        QtCore.QObject.connect(self.submitButton, QtCore.SIGNAL(_fromUtf8("clicked()")), serverConfigurationDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(serverConfigurationDialog)
        serverConfigurationDialog.setTabOrder(self.addServerUrl, self.loadUrlButton)
        serverConfigurationDialog.setTabOrder(self.loadUrlButton, self.submitButton)
        serverConfigurationDialog.setTabOrder(self.submitButton, self.projectsList)

    def retranslateUi(self, serverConfigurationDialog):
        serverConfigurationDialog.setWindowTitle(_translate("serverConfigurationDialog", "Add Server", None))
        self.cctrayUrlLabel.setText(_translate("serverConfigurationDialog", "Path to cctray.xml", None))
        self.loadUrlButton.setText(_translate("serverConfigurationDialog", "Load", None))
        self.submitButton.setText(_translate("serverConfigurationDialog", "OK", None))
        self.timezoneLabel.setText(_translate("serverConfigurationDialog", "Server timezone", None))
        self.displayPrefixLabel.setText(_translate("serverConfigurationDialog", "Display prefix", None))
        self.displayPrefix.setPlaceholderText(_translate("serverConfigurationDialog", "e.g. branch/release", None))

