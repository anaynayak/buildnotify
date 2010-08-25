# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data/project_configuration.ui'
#
# Created: Tue Aug 24 21:40:59 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_projectConfigurationDialog(object):
    def setupUi(self, projectConfigurationDialog):
        projectConfigurationDialog.setObjectName("projectConfigurationDialog")
        projectConfigurationDialog.resize(435, 319)
        self.buttonBox = QtGui.QDialogButtonBox(projectConfigurationDialog)
        self.buttonBox.setGeometry(QtCore.QRect(240, 280, 191, 31))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.excludedProjectList = QtGui.QListView(projectConfigurationDialog)
        self.excludedProjectList.setGeometry(QtCore.QRect(20, 60, 401, 211))
        self.excludedProjectList.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.excludedProjectList.setObjectName("excludedProjectList")
        self.serverConfigurationLabel = QtGui.QLabel(projectConfigurationDialog)
        self.serverConfigurationLabel.setGeometry(QtCore.QRect(20, 10, 141, 20))
        self.serverConfigurationLabel.setObjectName("serverConfigurationLabel")
        self.label = QtGui.QLabel(projectConfigurationDialog)
        self.label.setGeometry(QtCore.QRect(20, 40, 391, 20))
        self.label.setObjectName("label")

        self.retranslateUi(projectConfigurationDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), projectConfigurationDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), projectConfigurationDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(projectConfigurationDialog)

    def retranslateUi(self, projectConfigurationDialog):
        projectConfigurationDialog.setWindowTitle(QtGui.QApplication.translate("projectConfigurationDialog", "Project Configuration", None, QtGui.QApplication.UnicodeUTF8))
        self.serverConfigurationLabel.setText(QtGui.QApplication.translate("projectConfigurationDialog", "Server", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("projectConfigurationDialog", "Select projects to exclude from BuildNotify", None, QtGui.QApplication.UnicodeUTF8))

