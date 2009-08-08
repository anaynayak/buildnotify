import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
from config import Config

class PreferencesDialog:
    def __init__(self, config):
        self.gladefile = 'preferences.glade'
        self.config = config 
    def show(self):
        self.wTree = gtk.glade.XML(self.gladefile)
    	self.serverList = self.wTree.get_widget("serverList")
    	self.preferencesDialog = self.wTree.get_widget("preferencesDialog")
    	column = gtk.TreeViewColumn("Server")
        column.set_resizable(True)		
        cellRenderer = gtk.CellRendererText()
        column.pack_start(cellRenderer)
        column.add_attribute(cellRenderer, 'text', 0)
        self.serverList.append_column(column)
    	self.serverListModel = gtk.ListStore(str)
    	self.selectedRow = None
    	self.serverList.set_model(self.serverListModel)
    	for url in self.config.get_urls():
        	self.serverListModel.append([url])
        dic = {"on_mainWindow_destroy" : gtk.main_quit, 
        "on_addButton_clicked" : self.on_addButton_clicked,
        "on_removeButton_clicked": self.on_removeButton_clicked}
        self.wTree.signal_autoconnect(dic)
        selection = self.serverList.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        selection.connect('changed', self.rowSelected)
        self.preferencesDialog.run()
        
    def rowSelected(self, treeSelection):
        model, treeIter = treeSelection.get_selected()
        self.selectedRow = treeIter
    def on_addButton_clicked(self, widget):
        addServerDialog = AddServerDialog()
        result, server = addServerDialog.run()
        if (result == 0):
            self.serverListModel.append([server])        
            self.updateUrls()
    def on_removeButton_clicked(self, widget):
        if self.selectedRow != None: 
            self.serverListModel.remove(self.selectedRow)
            self.selectedRow = None
            self.updateUrls()
    def updateUrls(self):
        values = [r[0] for r in self.serverListModel]
        self.config.update_urls(values)
        
            
class AddServerDialog:
    def __init__(self):
        self.gladefile = "add_server.glade"
        self.server = ""
    def run(self):
        self.addServerDialogXml = gtk.glade.XML(self.gladefile)
        self.addServerDialog = self.addServerDialogXml.get_widget("addServerDialog")
        self.addServerText= self.addServerDialogXml.get_widget("addServerText")
        self.result = self.addServerDialog.run()
        self.server = self.addServerText.get_text()
        self.addServerDialog.destroy()
        return self.result, self.server    

if __name__ == "__main__":
    preferencesDialog = PreferencesDialog(Config())
    
