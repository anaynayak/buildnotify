from buildnotifylib.core.timed_event import TimedEvent


class RepeatTimedEvent(object):
    def __init__(self, parent, event_target, repeat_count, interval=2000):
        self.parent = parent
        self.repeat_count = repeat_count
        self.event_target = event_target
        self.event_happened_count = 0
        self.interval = interval
        self.timed_event = TimedEvent(self.parent, self.on_event, self.interval)

    def start(self):
        self.timed_event.start()

    def on_event(self):
        self.event_target(self.event_happened_count)
        self.event_happened_count += 1
        if self.event_happened_count != self.repeat_count:
            self.start()
