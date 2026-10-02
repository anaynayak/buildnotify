# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preferences.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QCheckBox,
    QDialog, QDialogButtonBox, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QListView,
    QPushButton, QRadioButton, QSizePolicy, QSpacerItem,
    QSpinBox, QTabWidget, QVBoxLayout, QWidget)

class Ui_Preferences(object):
    def setupUi(self, Preferences):
        if not Preferences.objectName():
            Preferences.setObjectName(u"Preferences")
        Preferences.resize(462, 357)
        Preferences.setSizeGripEnabled(False)
        self.gridLayout = QGridLayout(Preferences)
        self.gridLayout.setObjectName(u"gridLayout")
        self.buttonBox = QDialogButtonBox(Preferences)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.tabWidget = QTabWidget(Preferences)
        self.tabWidget.setObjectName(u"tabWidget")
        self.serversTab = QWidget()
        self.serversTab.setObjectName(u"serversTab")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.serversTab.sizePolicy().hasHeightForWidth())
        self.serversTab.setSizePolicy(sizePolicy)
        self.gridLayout_4 = QGridLayout(self.serversTab)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.groupBox_2 = QGroupBox(self.serversTab)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.gridLayout_3 = QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.cctrayPathList = QListView(self.groupBox_2)
        self.cctrayPathList.setObjectName(u"cctrayPathList")
        self.cctrayPathList.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.gridLayout_3.addWidget(self.cctrayPathList, 0, 0, 1, 7)

        self.configureProjectButton = QPushButton(self.groupBox_2)
        self.configureProjectButton.setObjectName(u"configureProjectButton")
        self.configureProjectButton.setEnabled(False)

        self.gridLayout_3.addWidget(self.configureProjectButton, 1, 2, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer, 1, 1, 1, 1)

        self.addButton = QPushButton(self.groupBox_2)
        self.addButton.setObjectName(u"addButton")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.addButton.sizePolicy().hasHeightForWidth())
        self.addButton.setSizePolicy(sizePolicy1)

        self.gridLayout_3.addWidget(self.addButton, 1, 4, 1, 1)

        self.removeButton = QPushButton(self.groupBox_2)
        self.removeButton.setObjectName(u"removeButton")
        sizePolicy1.setHeightForWidth(self.removeButton.sizePolicy().hasHeightForWidth())
        self.removeButton.setSizePolicy(sizePolicy1)

        self.gridLayout_3.addWidget(self.removeButton, 1, 3, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox_2, 0, 0, 1, 1)

        self.tabWidget.addTab(self.serversTab, "")
        self.notificationsTab = QWidget()
        self.notificationsTab.setObjectName(u"notificationsTab")
        self.verticalLayout = QVBoxLayout(self.notificationsTab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(self.notificationsTab)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setFlat(False)
        self.groupBox.setCheckable(False)
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.successfulBuildsCheckbox = QCheckBox(self.groupBox)
        self.successfulBuildsCheckbox.setObjectName(u"successfulBuildsCheckbox")

        self.gridLayout_2.addWidget(self.successfulBuildsCheckbox, 0, 0, 1, 1)

        self.brokenBuildsCheckbox = QCheckBox(self.groupBox)
        self.brokenBuildsCheckbox.setObjectName(u"brokenBuildsCheckbox")

        self.gridLayout_2.addWidget(self.brokenBuildsCheckbox, 0, 1, 1, 1)

        self.fixedBuildsCheckbox = QCheckBox(self.groupBox)
        self.fixedBuildsCheckbox.setObjectName(u"fixedBuildsCheckbox")

        self.gridLayout_2.addWidget(self.fixedBuildsCheckbox, 1, 0, 1, 1)

        self.stillFailingBuildsCheckbox = QCheckBox(self.groupBox)
        self.stillFailingBuildsCheckbox.setObjectName(u"stillFailingBuildsCheckbox")

        self.gridLayout_2.addWidget(self.stillFailingBuildsCheckbox, 1, 1, 1, 1)

        self.connectivityIssuesCheckbox = QCheckBox(self.groupBox)
        self.connectivityIssuesCheckbox.setObjectName(u"connectivityIssuesCheckbox")
        self.connectivityIssuesCheckbox.setMaximumSize(QSize(200, 16777215))

        self.gridLayout_2.addWidget(self.connectivityIssuesCheckbox, 2, 0, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout_2)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_3 = QGroupBox(self.notificationsTab)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.scriptCheckbox = QCheckBox(self.groupBox_3)
        self.scriptCheckbox.setObjectName(u"scriptCheckbox")

        self.verticalLayout_3.addWidget(self.scriptCheckbox)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.scriptLabel = QLabel(self.groupBox_3)
        self.scriptLabel.setObjectName(u"scriptLabel")

        self.horizontalLayout_3.addWidget(self.scriptLabel)

        self.scriptLineEdit = QLineEdit(self.groupBox_3)
        self.scriptLineEdit.setObjectName(u"scriptLineEdit")
        self.scriptLineEdit.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.scriptLineEdit)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)


        self.verticalLayout.addWidget(self.groupBox_3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.notificationsTab, "")
        self.miscTab = QWidget()
        self.miscTab.setObjectName(u"miscTab")
        self.verticalLayout_5 = QVBoxLayout(self.miscTab)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.pollingIntervalLabel = QLabel(self.miscTab)
        self.pollingIntervalLabel.setObjectName(u"pollingIntervalLabel")

        self.gridLayout_5.addWidget(self.pollingIntervalLabel, 4, 0, 1, 1)

        self.showLastBuildLabelCheckbox = QCheckBox(self.miscTab)
        self.showLastBuildLabelCheckbox.setObjectName(u"showLastBuildLabelCheckbox")

        self.gridLayout_5.addWidget(self.showLastBuildLabelCheckbox, 6, 1, 1, 1)

        self.pollingIntervalSpinBox = QSpinBox(self.miscTab)
        self.pollingIntervalSpinBox.setObjectName(u"pollingIntervalSpinBox")
        self.pollingIntervalSpinBox.setMinimumSize(QSize(130, 0))
        self.pollingIntervalSpinBox.setMaximumSize(QSize(130, 16777215))
        self.pollingIntervalSpinBox.setWrapping(False)
        self.pollingIntervalSpinBox.setMinimum(10)
        self.pollingIntervalSpinBox.setMaximum(3600)
        self.pollingIntervalSpinBox.setSingleStep(1)

        self.gridLayout_5.addWidget(self.pollingIntervalSpinBox, 4, 1, 1, 1)

        self.showLastBuildTimeCheckbox = QCheckBox(self.miscTab)
        self.showLastBuildTimeCheckbox.setObjectName(u"showLastBuildTimeCheckbox")

        self.gridLayout_5.addWidget(self.showLastBuildTimeCheckbox, 5, 1, 1, 1)

        self.symbolicIconsCheckbox = QCheckBox(self.miscTab)
        self.symbolicIconsCheckbox.setObjectName(u"symbolicIconsCheckbox")

        self.gridLayout_5.addWidget(self.symbolicIconsCheckbox, 7, 1, 1, 1)


        self.verticalLayout_5.addLayout(self.gridLayout_5)

        self.groupBox_4 = QGroupBox(self.miscTab)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_4)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.sortBuildByName = QRadioButton(self.groupBox_4)
        self.sortBuildByName.setObjectName(u"sortBuildByName")

        self.verticalLayout_4.addWidget(self.sortBuildByName)

        self.sortBuildByLastBuildTime = QRadioButton(self.groupBox_4)
        self.sortBuildByLastBuildTime.setObjectName(u"sortBuildByLastBuildTime")
        self.sortBuildByLastBuildTime.setChecked(True)

        self.verticalLayout_4.addWidget(self.sortBuildByLastBuildTime)


        self.verticalLayout_5.addWidget(self.groupBox_4)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_2)

        self.tabWidget.addTab(self.miscTab, "")

        self.gridLayout.addWidget(self.tabWidget, 1, 0, 1, 1)

#if QT_CONFIG(shortcut)
        self.scriptLabel.setBuddy(self.scriptLineEdit)
        self.pollingIntervalLabel.setBuddy(self.pollingIntervalSpinBox)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(Preferences)
        self.scriptCheckbox.toggled.connect(self.scriptLineEdit.setEnabled)

        self.tabWidget.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(Preferences)
    # setupUi

    def retranslateUi(self, Preferences):
        Preferences.setWindowTitle(QCoreApplication.translate("Preferences", u"Preferences", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Preferences", u"Monitored servers", None))
        self.configureProjectButton.setText(QCoreApplication.translate("Preferences", u"Configure", None))
#if QT_CONFIG(tooltip)
        self.addButton.setToolTip(QCoreApplication.translate("Preferences", u"Add", None))
#endif // QT_CONFIG(tooltip)
        self.addButton.setText(QCoreApplication.translate("Preferences", u"+", None))
#if QT_CONFIG(tooltip)
        self.removeButton.setToolTip(QCoreApplication.translate("Preferences", u"Remove", None))
#endif // QT_CONFIG(tooltip)
        self.removeButton.setText(QCoreApplication.translate("Preferences", u"-", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.serversTab), QCoreApplication.translate("Preferences", u"Servers", None))
        self.groupBox.setTitle(QCoreApplication.translate("Preferences", u"Notification settings", None))
        self.successfulBuildsCheckbox.setText(QCoreApplication.translate("Preferences", u"successful builds", None))
        self.brokenBuildsCheckbox.setText(QCoreApplication.translate("Preferences", u"broken builds", None))
        self.fixedBuildsCheckbox.setText(QCoreApplication.translate("Preferences", u"fixed builds", None))
        self.stillFailingBuildsCheckbox.setText(QCoreApplication.translate("Preferences", u"still failing builds", None))
        self.connectivityIssuesCheckbox.setText(QCoreApplication.translate("Preferences", u"connectivity issues", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("Preferences", u"Custom notifications", None))
        self.scriptCheckbox.setText(QCoreApplication.translate("Preferences", u"Execute script for notifications", None))
        self.scriptLabel.setText(QCoreApplication.translate("Preferences", u"Script", None))
#if QT_CONFIG(tooltip)
        self.scriptLineEdit.setToolTip(QCoreApplication.translate("Preferences", u"The script gets the build status and projects in the BUILDNOTIFY_STATUS and BUILDNOTIFY_PROJECTS environment variables. #status# and #projects# are also replaced, quoted, except on Windows, where a script using them is not run.", None))
#endif // QT_CONFIG(tooltip)
        self.scriptLineEdit.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.notificationsTab), QCoreApplication.translate("Preferences", u"Notifications", None))
        self.pollingIntervalLabel.setText(QCoreApplication.translate("Preferences", u"Server polling interval", None))
        self.showLastBuildLabelCheckbox.setText(QCoreApplication.translate("Preferences", u"show last build label for each project", None))
        self.pollingIntervalSpinBox.setSuffix(QCoreApplication.translate("Preferences", u" seconds", None))
        self.showLastBuildTimeCheckbox.setText(QCoreApplication.translate("Preferences", u"show last build time for each project", None))
        self.symbolicIconsCheckbox.setText(QCoreApplication.translate("Preferences", u"use symbolic tray icons (shapes instead of coloured squares)", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("Preferences", u"Build Sort order", None))
        self.sortBuildByName.setText(QCoreApplication.translate("Preferences", u"Sort builds by name", None))
        self.sortBuildByLastBuildTime.setText(QCoreApplication.translate("Preferences", u"Sort builds by last build time", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.miscTab), QCoreApplication.translate("Preferences", u"Misc", None))
    # retranslateUi

