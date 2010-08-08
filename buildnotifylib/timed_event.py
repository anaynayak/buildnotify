from PyQt4 import QtCore

class TimedEvent:
    def __init__(self,parent, event_target):
        self.event_target = event_target
        self.parent = parent
        self.interval = 2000
        
    def start(self):
        self.timer = QtCore.QTimer()
        self.parent.connect(self.timer, QtCore.SIGNAL('timeout()'), self.event_target)
        self.timer.setInterval(self.interval)
        self.timer.setSingleShot(True)
        self.timer.start()
    def set_interval(self, interval):
        self.interval = interval

class RepeatTimedEvent:
    def __init__(self, parent, event_target, repeat_count):
        self.parent = parent
        self.repeat_count = repeat_count
        self.event_target = event_target
        self.event_happened_count = 0

    def start(self):
        self.timed_event = TimedEvent(self.parent, self.on_event)
        self.timed_event.start()

    def on_event(self):
        self.event_target(self.event_happened_count);
        self.event_happened_count = self.event_happened_count + 1
        if (self.event_happened_count != self.repeat_count):
            self.start()
