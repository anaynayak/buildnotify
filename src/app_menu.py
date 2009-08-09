import os
import gtk
from preferences import PreferencesDialog
class AppMenu:
    def __init__(self, conf, build_icons, imageicon):
        self.menu = gtk.Menu()
        self.conf = conf
        self.build_icons = build_icons
        self.imageicon = imageicon
            
    def show(self, event):
        self.menu.popup(None, None, self.func, event.button,event.time)
    
    def update(self, projects):
        self.menu = gtk.Menu() 
        for project in projects:
            self.menu.append(self.create_menu_item(project.name, self.build_icons.for_status(project.get_build_status()), project.url));
        self.menu.show_all()
            
    def create_menu_item(self, label, iconName, url):
        menu_item = gtk.ImageMenuItem(label, None);
        image = gtk.Image()
        image.set_from_file(iconName)
        menu_item.set_image(image)
        menu_item.connect("activate", self.menu_item_selected, url)
        return menu_item

    def menu_item_selected(self,menu_item, param) :
        self.launch_browser(param)
   
    def func(menu, user_data):
        coordinates=menu.imageicon.window.get_origin()
        return (coordinates[0],coordinates[1], True)
    def launch_browser(self, url):
        os.system(self.conf.browser + " " + url + " &")

class OtherMenu:
    def __init__(self, conf, imageicon):
    	self.about_dialog = about_dialog(imageicon)
    	self.window = gtk.Menu()    
    	self.conf = conf
        self.imageicon = imageicon
        menu_item_separator = gtk.SeparatorMenuItem()
        menu_item_about = gtk.ImageMenuItem('gtk-about',None)
        menu_item_about.connect('activate',self.about_clicked)
        menu_item_quit = gtk.ImageMenuItem('gtk-quit',None)
        menu_item_quit.connect('activate',self.exit)
        menu_item_preferences = gtk.ImageMenuItem('gtk-preferences', None)
        menu_item_preferences.connect('activate', self.preferences_clicked)
        self.window.add(menu_item_about)
        self.window.add(menu_item_preferences)
        self.window.add(menu_item_separator)
        self.window.add(menu_item_quit)
        self.window.show_all()         

    def show(self,event):
        self.window.popup(None, None, self.func, event.button,event.time)

    def about_clicked(self,widget):
	    self.about_dialog.create()     
                 
    def preferences_clicked(self, widget):
        self.preferences_dialog = PreferencesDialog(self.conf)
        self.preferences_dialog.show()
    
    def func(menu, user_data):
        coordinates=menu.imageicon.window.get_origin()
        return (coordinates[0],coordinates[1], True)
    def exit(self,widget):
        gtk.main_quit()   

class about_dialog:
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
        

