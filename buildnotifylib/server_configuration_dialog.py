from PyQt4 import QtCore
import pytz
from PyQt4.QtCore import Qt
from PyQt4 import QtGui
from server_configuration_ui import Ui_serverConfigurationDialog
from timed_event import BackgroundEvent
from projects import ProjectLoader

class ServerConfigurationDialog(QtGui.QDialog):

    def __init__(self, editable, url, conf, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_serverConfigurationDialog()
        self.ui.setupUi(self)
        self.editable = editable
        self.ui.addServerUrl.setText(url)
        self.conf = conf
        if not editable:
            self.auto_load()
        self.connect(self.ui.loadUrlButton, QtCore.SIGNAL("clicked()"),
                     self.fetch_data)

    def auto_load(self):
        self.ui.addServerUrl.setReadOnly(True)
        self.ui.loadUrlButton.setEnabled(False)
        self.fetch_data()
    
    def fetch_data(self):
        self.ui.loadUrlButton.setEnabled(False)
        self.event = BackgroundEvent(self.load_projects, self)
        self.connect(self.event, QtCore.SIGNAL('complete'), lambda data: self.load_data(data))
        self.event.start()

    def load_projects(self):
        self.project_loader = ProjectLoader(self.server_url(), self.conf.timeout)
        return self.project_loader.get_data()

    def load_data(self, server):
        self.ui.loadUrlButton.setEnabled(self.editable)
        projects = [project.name for project in server.projects]
        excluded_projects = self.conf.get_project_excludes(self.server_url())

        projectsModel = QtGui.QStandardItemModel()
        for project in server.projects:
            item = QtGui.QStandardItem(project.name)
            item.setCheckable(True)
            check = Qt.Unchecked if project.name in excluded_projects else Qt.Checked
            item.setCheckState(check)
            projectsModel.appendRow(item)
        self.ui.projectsList.setModel(projectsModel)
    
    def server_url(self):
        return str(self.ui.addServerUrl.text())
    
    def save(self):
        projectsModel = self.ui.projectsList.model()
        if projectsModel is None:
            return
        excluded_projects = [str(projectsModel.index(index, 0).data().toString()) for index in range(projectsModel.rowCount()) if projectsModel.index(index, 0).data(Qt.CheckStateRole)==Qt.Unchecked]
        self.conf.set_project_excludes(self.server_url(), excluded_projects)
        return self.server_url()
    
