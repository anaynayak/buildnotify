from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QDialog

from buildnotifylib.generated.preferences_ui import Ui_Preferences
from buildnotifylib.server_configuration_dialog import ServerConfigurationDialog


class PreferencesDialog(QDialog):
    addServerTemplateText = "http://[host]:[port]/dashboard/cctray.xml"

    def __init__(self, conf, parent=None):
        QDialog.__init__(self, parent)
        self.conf = conf
        self.ui = Ui_Preferences()
        self.ui.setupUi(self)
        self.checkboxes = dict(successfulBuild=self.ui.successfulBuildsCheckbox,
                               brokenBuild=self.ui.brokenBuildsCheckbox, fixedBuild=self.ui.fixedBuildsCheckbox,
                               stillFailingBuild=self.ui.stillFailingBuildsCheckbox,
                               connectivityIssues=self.ui.connectivityIssuesCheckbox,
                               lastBuildTimeForProject=self.ui.showLastBuildTimeCheckbox)
        self.set_values_from_config()

        # Connect up the buttons.
        self.ui.addButton.clicked.connect(self.add_server)
        self.ui.removeButton.clicked.connect(self.remove_element)
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.configureProjectButton.clicked.connect(self.configure_projects)

    def set_values_from_config(self):
        self.ui.cctrayPathList.setModel(QStringListModel(self.conf.get_urls()))

        self.ui.cctrayPathList.clicked.connect(lambda x: self.item_selection_changed(True))
        self.ui.removeButton.clicked.connect(lambda x: self.item_selection_changed(False))

        for key, checkbox in self.checkboxes.items():
            checkbox.setChecked(self.conf.get_value(str(key)))

        self.ui.pollingIntervalSpinBox.setValue(self.conf.get_interval_in_seconds())
        self.ui.scriptCheckbox.setChecked(self.conf.get_custom_script_enabled())
        self.ui.scriptLineEdit.setText(self.conf.get_custom_script())
        self.ui.sortBuildByLastBuildTime.setChecked(self.conf.get_sort_by_last_build_time())
        self.ui.sortBuildByName.setChecked(self.conf.get_sort_by_name())

    def item_selection_changed(self, status):
        self.ui.configureProjectButton.setEnabled(status)

    def add_server(self):
        server_config = ServerConfigurationDialog(self.addServerTemplateText, self.conf, self).open()
        if server_config is not None:
            self.conf.save_server_config(server_config)
            urls = self.ui.cctrayPathList.model().stringList()
            urls.append(server_config.url)
            self.ui.cctrayPathList.setModel(QStringListModel(urls))

    def remove_element(self):
        index = self.ui.cctrayPathList.selectionModel().currentIndex()
        urls = self.ui.cctrayPathList.model().stringList()
        urls.pop(index.row())
        self.ui.cctrayPathList.setModel(QStringListModel(urls))

    def configure_projects(self):
        url = self.ui.cctrayPathList.selectionModel().currentIndex().data()
        if not url:
            return
        server_config = ServerConfigurationDialog(url, self.conf, self).open()
        if server_config is not None:
            self.conf.save_server_config(server_config)

    def get_urls(self):
        return [str(url) for url in self.ui.cctrayPathList.model().stringList()]

    def get_interval_in_seconds(self):
        return self.ui.pollingIntervalSpinBox.value()

    def get_selections(self):
        return [(key, checkbox.isChecked()) for (key, checkbox) in self.checkboxes.items()]

    def open(self):
        if self.exec_() == QDialog.Accepted:
            return Preferences(
                urls=self.get_urls(),
                interval=self.get_interval_in_seconds(),
                custom_script_text=self.ui.scriptLineEdit.text(),
                custom_script_checked=self.ui.scriptCheckbox.isChecked(),
                sort_by_build_time=self.ui.sortBuildByLastBuildTime.isChecked(),
                sort_by_name=self.ui.sortBuildByName.isChecked(),
                selections=self.get_selections()
            )


class Preferences(object):
    def __init__(self, urls, interval, custom_script_text, custom_script_checked,
                 sort_by_build_time, sort_by_name, selections):
        self.urls = urls
        self.interval = interval
        self.custom_script_text = custom_script_text
        self.trigger_custom_script = custom_script_checked
        self.sort_by_build_time = sort_by_build_time
        self.sort_by_name = sort_by_name
        self.selections = selections
