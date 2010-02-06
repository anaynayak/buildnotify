from app_ui import AppUi
from app_notification import AppNotification
from config import Config
from projects import ProjectsPopulator
import gobject
from PyQt4 import QtGui
import sys
import gtk

class BuildNotify:
    def __init__(self):
        self.conf = Config()
        self.projects_populator = ProjectsPopulator(self.conf)
        self.app = QtGui.QApplication(sys.argv)
        self.app_ui = AppUi(self.conf)
        self.app_notification = AppNotification()
        self.projects_populator.add_listener(self.app_notification)
        self.projects_populator.add_listener(self.app_ui)
        self.check_nodes()
        
    def check_nodes(self):
        self.maintimer = gobject.timeout_add(self.conf.check_interval * 1000, self.check_nodes)
        self.projects_populator.load_from_server(self.conf)

BuildNotify()
gtk.main()
sys.exit()