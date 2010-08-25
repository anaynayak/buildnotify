from PyQt4 import QtCore
import pytz
from PyQt4 import QtGui
from project_configuration_ui import Ui_projectConfigurationDialog
from timed_event import TimedEvent
from projects import ProjectLoader

class ProjectConfigurationDialog(QtGui.QDialog):

    def __init__(self, url, conf, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_projectConfigurationDialog()
        self.ui.setupUi(self)
        self.url = url
        self.conf = conf
        self.event = TimedEvent(self, self.load_data, 100);
        self.event.start()
    
    def load_data(self):
        self.project_loader = ProjectLoader(self.url, self.conf.timeout)
        server = self.project_loader.get_data()
        urls = [project.name for project in server.projects]
        self.projectsModel = QtGui.QStringListModel(urls)
        self.ui.excludedProjectList.setModel(self.projectsModel)
        excluded_projects = self.conf.get_project_excludes(self.url)
        excluded_projects_indices = [self.projectsModel.stringList().indexOf(project) for project in excluded_projects]
        selectionModel = self.ui.excludedProjectList.selectionModel()
        for index in excluded_projects_indices:
            qmodelIndex = self.projectsModel.index(index,0, QtCore.QModelIndex())
            selectionModel.select(qmodelIndex, QtGui.QItemSelectionModel.Select)
        self.setWindowTitle("Configure %s" % self.url)
    
    def save(self):
        self.conf.set_project_excludes(self.url, [str(qModelIndex.data().toString()) for qModelIndex in self.ui.excludedProjectList.selectionModel().selectedRows()])