from PyQt5 import QtCore


class TimedEvent(object):
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
