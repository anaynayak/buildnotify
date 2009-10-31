#!/usr/bin/env python

import gtk
import gnomeapplet as applet
import buildnotifylib
import sys

def buildnotify_factory(applet, iid):
    buildnotify = buildnotifylib.BuildNotify(applet)
    return True

def main():
    win = gtk.Window(gtk.WINDOW_TOPLEVEL)
    app = applet.Applet()
    buildnotify_factory(app, None)
    app.reparent(win)
    win.show_all()
    gtk.main()
    sys.exit()

if len(sys.argv) > 1 and sys.argv[1] == 'win':
    main()
else:
    applet.bonobo_factory("OAFIID:GNOME_BuildNotifyApplet_Factory", 
            applet.Applet.__gtype__, "BuildNotify", "0", 
            buildnotify_factory)
