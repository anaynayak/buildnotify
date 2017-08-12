from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal

class TimedEvent:
    def __init__(self, parent, event_target, interval=2000):
        self.event_target = event_target
        self.parent = parent
        self.interval = interval

    def start(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.event_target)
        self.timer.setInterval(self.interval)
        self.timer.setSingleShot(True)
        self.timer.start()

    def set_interval(self, interval):
        self.interval = interval


class RepeatTimedEvent:
    def __init__(self, parent, event_target, repeat_count, interval=2000):
        self.parent = parent
        self.repeat_count = repeat_count
        self.event_target = event_target
        self.event_happened_count = 0
        self.interval = interval

    def start(self):
        self.timed_event = TimedEvent(self.parent, self.on_event, self.interval)
        self.timed_event.start()

    def on_event(self):
        self.event_target(self.event_happened_count)
        self.event_happened_count += 1
        if self.event_happened_count != self.repeat_count:
            self.start()


class BackgroundEvent(QThread):
    completed = pyqtSignal('PyQt_PyObject')

    def __init__(self, task, parent=None):
        QThread.__init__(self, parent)
        self.task = task

    def run(self):
        data = self.task()
        self.completed.emit(data)
