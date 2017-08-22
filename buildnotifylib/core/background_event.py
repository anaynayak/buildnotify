from PyQt5.QtCore import QThread, pyqtSignal


class BackgroundEvent(QThread):
    completed = pyqtSignal('PyQt_PyObject')

    def __init__(self, task, parent=None):
        QThread.__init__(self, parent)
        self.task = task

    def run(self):
        data = self.task()
        self.completed.emit(data)
