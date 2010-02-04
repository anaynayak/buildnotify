import os
import gtk
from preferences import PreferencesDialog
from distance_of_time import DistanceOfTime
from dateutil.parser import parse

class AppMenu:
    def __init__(self, conf, build_icons, imageicon):
        self.menu = gtk.Menu()
        self.conf = conf
        self.build_icons = build_icons
        self.imageicon = imageicon
            
    def show(self, event):
        self.menu.popup(None, None, None, event.button,event.time)
    
    def update(self, projects):
        self.menu = gtk.Menu() 
        for project in projects:
            self.menu.append(self.create_menu_item(project.name, self.build_icons.for_status(project.get_build_status()), project.url, parse(project.lastBuildTime)));
        self.create_default_menu_items()
        self.menu.show_all()
            
    def create_default_menu_items(self):
    	self.about_dialog = AboutBuildNotifyDialog(self.imageicon)
        menu_item_separator = gtk.SeparatorMenuItem()
        menu_item_about = gtk.ImageMenuItem('gtk-about',None)
        menu_item_about.connect('activate',self.about_clicked)
        menu_item_preferences = gtk.ImageMenuItem('gtk-preferences', None)
        menu_item_preferences.connect('activate', self.preferences_clicked)
        self.menu.add(menu_item_separator)
        self.menu.add(menu_item_preferences)
        self.menu.add(menu_item_about)

    def about_clicked(self,widget):
	    self.about_dialog.create()     
                 
    def preferences_clicked(self, widget):
        self.preferences_dialog = PreferencesDialog(self.conf)
        self.preferences_dialog.show()
    
    def exit(self,widget):
        gtk.main_quit()   

    def create_menu_item(self, label, iconName, url, lastBuildTime):
        menu_item = gtk.ImageMenuItem(label + ", " + DistanceOfTime(lastBuildTime).age() + " ago", None);
        image = gtk.Image()
        image.set_from_file(iconName)
        menu_item.set_image(image)
        menu_item.set_use_underline(False)
        menu_item.connect("activate", self.menu_item_selected, url)
        return menu_item

    def menu_item_selected(self,menu_item, param) :
        self.launch_browser(param)
   
    def launch_browser(self, url):
        os.system(self.conf.browser + " " + url + " &")

class AboutBuildNotifyDialog:
    def __init__(self, imageicon):
        self.imageicon = imageicon
    
    def create(self):
        dialog = gtk.AboutDialog()
        dialog.set_name('BuildNotify')
        dialog.set_version('0.0.1')
        dialog.set_comments('CruiseControl build tray notification')
        dialog.set_logo(gtk.gdk.pixbuf_new_from_file_at_size('/usr/share/icons/gnome/scalable/status/stock_dialog-info.svg', 64, 64))
        dialog.run()
        dialog.destroy()

    def close(self):
        self.window.destroy()        
        

