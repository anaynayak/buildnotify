from typing import Callable, Any

from PyQt5.QtCore import QThread, pyqtSignal, QObject


class BackgroundEvent(QThread):
    completed = pyqtSignal('PyQt_PyObject')

    def __init__(self, task: Callable[[], Any], parent: QObject = None):
        QThread.__init__(self, parent)
        self.task = task

    def run(self):
        data = self.task()
        self.completed.emit(data)
