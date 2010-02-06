from app_ui import AppUi
from app_notification import AppNotification
from config import Config
from projects import ProjectsPopulator
import gobject

class BuildNotify:
    def __init__(self, tray):
        self.conf = Config()
        self.projects_populator = ProjectsPopulator(self.conf)
        self.app_ui = AppUi(tray, self.conf)
        self.app_notification = AppNotification()
        self.projects_populator.add_listener(self.app_notification)
        self.projects_populator.add_listener(self.app_ui)
        self.check_nodes()
   
    def check_nodes(self):
        self.maintimer = gobject.timeout_add(self.conf.check_interval * 1000, self.check_nodes)
        self.projects_populator.load_from_server(self.conf)
        
    def button_pressed(self, signal, event, n):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            self.menu.show(event);
    
    def main(self):
        gtk.main()
