# File: config.py
# Class: Config

import sys, os
import ConfigParser

class Config:
    def __init__(self):
        config = ConfigParser.SafeConfigParser()
        urls = self.from_properties(config, "connection","urls", "file:///home/anay/appl2/cctray.xml")
        self.urls = urls.split(",")
        self.timeout = float(self.from_properties(config, "connection","timeout", 10))
        self.check_interval = int(self.from_properties(config, "connection", "interval", 60))
        self.browser = self.from_properties(config, "misc", "browser", "firefox")
        self.icon_dir = self.from_properties(config, "misc", "icons", "/usr/share/buildnotify/pixmaps/")
    
    def from_properties(self, config, category, prop, val):
        if len(config.read([os.path.expanduser('~/.buildnotify')]))>0:
            if config.has_option(category,prop):
                return config.get(category,prop)
        return val
