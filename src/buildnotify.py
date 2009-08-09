#!/usr/bin/env python

import pygtk, gtk, gobject
import sys, os, time, warnings, string
import pytrayicon
import pynotify
from time import strftime
from config import Config
from app_menu import AppMenu
from app_menu import OtherMenu
from project_status_notification import ProjectStatusNotification
import projects
import build_icons
import projects
pygtk.require("2.0")

class BuildNotify:
    exposed_signal_id = 0   #For the notifications.
    lastcheck = None        #Time of last  check.
    maintimer = None        #Main check timer.   

    def __init__(self, tray):
        self.conf = Config()
        self.projects_populator = projects.ProjectsPopulator(self.conf)
        self.projects = None
        self.build_icons = build_icons.BuildIcons(self.conf.icon_dir)
        self.tray = tray
        self.eventbox = gtk.EventBox()
        self.hb = gtk.HBox(False, 0)
        self.tooltip = gtk.Tooltips()
        self.imageicon = gtk.Image()
        self.failing_build_count = gtk.Label()
        self.imageicon.set_from_file(self.build_icons.for_status(""))
        self.eventbox.add(self.hb)
        self.tray.add(self.eventbox)
        self.menu = AppMenu(self.conf, self.build_icons, self.imageicon)
        self.other_menu = OtherMenu(self.conf, self.imageicon)
        self.hb.add(self.imageicon)
        self.hb.add(self.failing_build_count)
        if not pynotify.init(" buildnotify "):
            sys.exit(1)
        self.notification = pynotify.Notification("buildnotify", "buildnotify", None, self.eventbox)
        self.notification.update("buildnotify", "Cruise applet has started...")
        self.eventbox.connect("button_press_event", self.button_pressed, self.notification)
        self.exposed_signal_id = self.eventbox.connect("expose_event", self.exposed_cb, self.notification)
        self.tray.show_all()
        self.check_nodes()
        self.events_pending()
        self.notification.update("Build failed", "message", None)
   
    def check_nodes(self):
        self.maintimer = gobject.timeout_add(self.conf.check_interval * 1000, self.check_nodes)
        self.projects_populator.load_from_server(self.conf, self.update_with_response)
        
    def update_with_response(self, updated_projects):
        self.imageicon.set_from_file(self.build_icons.for_status(updated_projects.get_build_status()))
        count = str(len(updated_projects.get_failing_builds()))
        if count is "0":
            count = ""
        self.failing_build_count.set_label(count)
        self.lastcheck = "Last checked: " + strftime("%Y-%m-%d %H:%M:%S")
        self.tooltip.set_tip(self.tray, self.lastcheck)        
        self.events_pending()
        self.menu.update(updated_projects.all_projects)
        if self.projects is not None :
            ProjectStatusNotification(self.projects, updated_projects, self.notification).show_notifications()
        self.projects = updated_projects
        
    def button_pressed(self, signal, event, n):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 2:
            sys.exit()
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.other_menu.show(event)
        else:
            self.menu.show(event);
    
    #For pynotify 
    def exposed_cb(self, obj, event, n):
        obj.disconnect(self.exposed_signal_id)

    def events_pending(self):
        while gtk.events_pending():
            gtk.main_iteration(True)

    def main(self):
        gtk.main()

if __name__ == "__main__":
    warnings.filterwarnings(action = "ignore", category = DeprecationWarning)
    buildnotify = BuildNotify(pytrayicon.TrayIcon("buildnotify"))
    buildnotify.main()
