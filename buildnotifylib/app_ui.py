import gtk
import pygtk
from time import strftime
import build_icons
from app_menu import AppMenu

pygtk.require("2.0")
class AppUi:
    def __init__(self, tray, conf):
        self.eventbox = gtk.EventBox()
        self.hb = gtk.HBox(False, 0)
        self.tray = tray
        self.conf = conf
        self.tooltip = gtk.Tooltips()
        self.imageicon = gtk.Image()
        self.failing_build_count = gtk.Label()
        self.build_icons = build_icons.BuildIcons(self.conf.icon_dir)
        self.imageicon.set_from_file(self.build_icons.for_status(""))
        self.eventbox.add(self.hb)
        self.tray.add(self.eventbox)
        self.menu = AppMenu(self.conf, self.build_icons, self.imageicon)
        self.eventbox.connect("button_press_event", self.button_pressed, None)
        self.hb.add(self.imageicon)
        self.hb.add(self.failing_build_count)
        self.tray.show_all()

    def button_pressed(self, signal, event, n):
        self.menu.update(self.projects.all_projects)
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            self.menu.show(event);

    def update_projects(self,updated_projects):
        self.imageicon.set_from_file(self.build_icons.for_status(updated_projects.get_build_status()))
        count = str(len(updated_projects.get_failing_builds()))
        if count is "0":
            count = ""
        self.failing_build_count.set_label(count)
        self.lastcheck = "Last checked: " + strftime("%Y-%m-%d %H:%M:%S")
        self.tooltip.set_tip(self.tray, self.lastcheck)
        self.projects = updated_projects
