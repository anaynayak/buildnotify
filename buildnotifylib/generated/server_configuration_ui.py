# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'server_configuration.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QDialog,
    QFormLayout, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QStackedWidget, QTreeView, QVBoxLayout,
    QWidget)

class Ui_serverConfigurationDialog(object):
    def setupUi(self, serverConfigurationDialog):
        if not serverConfigurationDialog.objectName():
            serverConfigurationDialog.setObjectName(u"serverConfigurationDialog")
        serverConfigurationDialog.resize(458, 384)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(serverConfigurationDialog.sizePolicy().hasHeightForWidth())
        serverConfigurationDialog.setSizePolicy(sizePolicy)
        serverConfigurationDialog.setMaximumSize(QSize(458, 384))
        self.verticalLayout = QVBoxLayout(serverConfigurationDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.stackedWidget = QStackedWidget(serverConfigurationDialog)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.verticalLayout_2 = QVBoxLayout(self.page)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.cctrayUrlLabel = QLabel(self.page)
        self.cctrayUrlLabel.setObjectName(u"cctrayUrlLabel")

        self.verticalLayout_2.addWidget(self.cctrayUrlLabel)

        self.addServerUrl = QLineEdit(self.page)
        self.addServerUrl.setObjectName(u"addServerUrl")
        self.addServerUrl.setPlaceholderText(u"http://[host]:[port]/dashboard/cctray.xml")

        self.verticalLayout_2.addWidget(self.addServerUrl)

        self.authenticationSettings = QGroupBox(self.page)
        self.authenticationSettings.setObjectName(u"authenticationSettings")
        self.verticalLayout_3 = QVBoxLayout(self.authenticationSettings)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.usernameLabel = QLabel(self.authenticationSettings)
        self.usernameLabel.setObjectName(u"usernameLabel")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.usernameLabel)

        self.username = QLineEdit(self.authenticationSettings)
        self.username.setObjectName(u"username")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.username)

        self.passwordLabel = QLabel(self.authenticationSettings)
        self.passwordLabel.setObjectName(u"passwordLabel")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.passwordLabel)

        self.password = QLineEdit(self.authenticationSettings)
        self.password.setObjectName(u"password")
        self.password.setEchoMode(QLineEdit.Password)

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.password)

        self.authentication_type_label = QLabel(self.authenticationSettings)
        self.authentication_type_label.setObjectName(u"authentication_type_label")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.authentication_type_label)

        self.authentication_type = QComboBox(self.authenticationSettings)
        self.authentication_type.addItem("")
        self.authentication_type.addItem("")
        self.authentication_type.setObjectName(u"authentication_type")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.authentication_type)


        self.verticalLayout_3.addLayout(self.formLayout_2)


        self.verticalLayout_2.addWidget(self.authenticationSettings)

        self.groupBox_2 = QGroupBox(self.page)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.formLayout_3 = QFormLayout()
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.timezoneLabel = QLabel(self.groupBox_2)
        self.timezoneLabel.setObjectName(u"timezoneLabel")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.timezoneLabel.sizePolicy().hasHeightForWidth())
        self.timezoneLabel.setSizePolicy(sizePolicy1)
        self.timezoneLabel.setMinimumSize(QSize(180, 0))
        self.timezoneLabel.setMaximumSize(QSize(180, 16777215))

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.timezoneLabel)

        self.timezoneList = QComboBox(self.groupBox_2)
        self.timezoneList.setObjectName(u"timezoneList")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.timezoneList.sizePolicy().hasHeightForWidth())
        self.timezoneList.setSizePolicy(sizePolicy2)
        self.timezoneList.setMinimumSize(QSize(210, 0))
        self.timezoneList.setMaximumSize(QSize(200, 16777215))

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.FieldRole, self.timezoneList)

        self.displayPrefixLabel = QLabel(self.groupBox_2)
        self.displayPrefixLabel.setObjectName(u"displayPrefixLabel")
        sizePolicy1.setHeightForWidth(self.displayPrefixLabel.sizePolicy().hasHeightForWidth())
        self.displayPrefixLabel.setSizePolicy(sizePolicy1)
        self.displayPrefixLabel.setMinimumSize(QSize(180, 0))
        self.displayPrefixLabel.setMaximumSize(QSize(180, 16777215))

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.displayPrefixLabel)

        self.displayPrefix = QLineEdit(self.groupBox_2)
        self.displayPrefix.setObjectName(u"displayPrefix")
        self.displayPrefix.setMinimumSize(QSize(210, 0))

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.FieldRole, self.displayPrefix)


        self.verticalLayout_4.addLayout(self.formLayout_3)


        self.verticalLayout_2.addWidget(self.groupBox_2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.loadUrlButton = QPushButton(self.page)
        self.loadUrlButton.setObjectName(u"loadUrlButton")
        self.loadUrlButton.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.loadUrlButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.verticalLayout_5 = QVBoxLayout(self.page_2)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.chooseProjectsLabel = QLabel(self.page_2)
        self.chooseProjectsLabel.setObjectName(u"chooseProjectsLabel")

        self.verticalLayout_5.addWidget(self.chooseProjectsLabel)

        self.projectsList = QTreeView(self.page_2)
        self.projectsList.setObjectName(u"projectsList")
        self.projectsList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.projectsList.setSelectionMode(QAbstractItemView.NoSelection)

        self.verticalLayout_5.addWidget(self.projectsList)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.backButton = QPushButton(self.page_2)
        self.backButton.setObjectName(u"backButton")
        self.backButton.setAutoDefault(False)

        self.horizontalLayout_2.addWidget(self.backButton)

        self.submitButton = QPushButton(self.page_2)
        self.submitButton.setObjectName(u"submitButton")
        self.submitButton.setAutoDefault(False)

        self.horizontalLayout_2.addWidget(self.submitButton)


        self.verticalLayout_5.addLayout(self.horizontalLayout_2)

        self.stackedWidget.addWidget(self.page_2)

        self.verticalLayout.addWidget(self.stackedWidget)

#if QT_CONFIG(shortcut)
        self.cctrayUrlLabel.setBuddy(self.addServerUrl)
        self.timezoneLabel.setBuddy(self.timezoneList)
        self.displayPrefixLabel.setBuddy(self.timezoneList)
        self.chooseProjectsLabel.setBuddy(self.addServerUrl)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.addServerUrl, self.projectsList)

        self.retranslateUi(serverConfigurationDialog)
        self.addServerUrl.returnPressed.connect(self.loadUrlButton.click)
        self.submitButton.clicked.connect(serverConfigurationDialog.accept)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(serverConfigurationDialog)
    # setupUi

    def retranslateUi(self, serverConfigurationDialog):
        serverConfigurationDialog.setWindowTitle(QCoreApplication.translate("serverConfigurationDialog", u"Add Server", None))
        self.cctrayUrlLabel.setText(QCoreApplication.translate("serverConfigurationDialog", u"Path to cctray.xml", None))
        self.authenticationSettings.setTitle(QCoreApplication.translate("serverConfigurationDialog", u"Authentication", None))
        self.usernameLabel.setText(QCoreApplication.translate("serverConfigurationDialog", u"Username", None))
        self.passwordLabel.setText(QCoreApplication.translate("serverConfigurationDialog", u"Password", None))
        self.authentication_type_label.setText(QCoreApplication.translate("serverConfigurationDialog", u"Authentication type", None))
        self.authentication_type.setItemText(0, QCoreApplication.translate("serverConfigurationDialog", u"Username/password", None))
        self.authentication_type.setItemText(1, QCoreApplication.translate("serverConfigurationDialog", u"Authentication Bearer token", None))

        self.groupBox_2.setTitle(QCoreApplication.translate("serverConfigurationDialog", u"Misc", None))
        self.timezoneLabel.setText(QCoreApplication.translate("serverConfigurationDialog", u"Server timezone", None))
        self.displayPrefixLabel.setText(QCoreApplication.translate("serverConfigurationDialog", u"Display prefix", None))
        self.displayPrefix.setPlaceholderText(QCoreApplication.translate("serverConfigurationDialog", u"e.g. branch/release", None))
        self.loadUrlButton.setText(QCoreApplication.translate("serverConfigurationDialog", u"Load", None))
        self.chooseProjectsLabel.setText(QCoreApplication.translate("serverConfigurationDialog", u"Choose projects", None))
        self.backButton.setText(QCoreApplication.translate("serverConfigurationDialog", u"Back", None))
        self.submitButton.setText(QCoreApplication.translate("serverConfigurationDialog", u"OK", None))
    # retranslateUi

