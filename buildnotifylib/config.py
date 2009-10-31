# File: config.py
# Class: Config

import sys, os
import ConfigParser

class Config:
    def __init__(self):
        self.config = ConfigParser.SafeConfigParser()
        self.glade_root = "/usr/local/share/buildnotify/"
        self.config.read([os.path.expanduser('~/.buildnotify')])
        urls = self.from_properties( "connection","urls", "file:///tmp/cctray.xml")
        self.urls = urls.split(",")
        self.timeout = float(self.from_properties("connection","timeout", "2"))
        self.check_interval = int(self.from_properties("connection", "interval", "5"))
        self.browser = self.from_properties("misc", "browser", "firefox")
        self.icon_dir = self.from_properties("misc", "icons", "/usr/local/share/buildnotify/pixmaps/")
    
    def from_properties(self, category, prop, val):
        if not self.config.has_option(category, prop):
            if not self.config.has_section(category):
                self.config.add_section(category)
            self.config.set(category, prop, val)
        return self.config.get(category,prop)
    
    def update_urls(self, urls):
        self.urls = urls
        self.config.set("connection","urls", ",".join(urls))
        self.config.write(open(os.path.expanduser('~/.buildnotify'), "w"))

    def get_urls(self):
        return self.urls
        
    def preferences_glade(self):
        return os.path.join(self.glade_root, 'preferences.glade')
    def add_server_glade(self):
        return os.path.join(self.glade_root, 'add_server.glade')

