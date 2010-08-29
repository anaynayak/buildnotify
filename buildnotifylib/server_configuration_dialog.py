from PyQt4 import QtCore
import pytz
from PyQt4.QtCore import Qt
from PyQt4 import QtGui
from server_configuration_ui import Ui_serverConfigurationDialog
from timed_event import TimedEvent
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
                     self.load_data)

    def auto_load(self):
        self.ui.addServerUrl.setReadOnly(True)
        self.ui.loadUrlButton.setEnabled(False)
        self.event = TimedEvent(self, self.load_data, 100);
        self.event.start()
        
    def load_data(self):
        self.project_loader = ProjectLoader(self.server_url(), self.conf.timeout)
        server = self.project_loader.get_data()
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
        excluded_projects = [str(projectsModel.index(index, 0).data().toString()) for index in range(projectsModel.rowCount()) if projectsModel.index(index, 0).data(Qt.CheckStateRole)==Qt.Unchecked]
        self.conf.set_project_excludes(self.server_url(), excluded_projects)
    
    def add_server(self):
        self.conf.add_server_url(self.server_url())
        self.save()