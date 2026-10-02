from collections.abc import Callable
from typing import Any

from PyQt5.QtCore import QObject, QThread, pyqtSignal


class BackgroundEvent(QThread):
    completed = pyqtSignal('PyQt_PyObject')

    def __init__(self, task: Callable[[], Any], parent: QObject = None):
        QThread.__init__(self, parent)
        self.task = task

    def run(self):
        data = self.task()
        self.completed.emit(data)
