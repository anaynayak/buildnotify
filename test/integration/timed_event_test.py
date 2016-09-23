from PyQt4.QtGui import QWidget
import pytest

from  buildnotifylib.core.timed_event import TimedEvent, RepeatTimedEvent


class TargetTimedEvent:
    def method(self, **kwargs):
        pass

@pytest.mark.functional
def test_should_trigger_event_on_timeout(qtbot, mocker):
    m = mocker.patch.object(TargetTimedEvent, 'method')
    widget = QWidget()
    qtbot.addWidget(widget)
    event = TimedEvent(widget, TargetTimedEvent().method, 20)
    event.start()

    qtbot.waitUntil(lambda: m.assert_any_call())

@pytest.mark.functional
def test_should_repeat_trigger_event(qtbot, mocker):
    m = mocker.patch.object(TargetTimedEvent, 'method')
    widget = QWidget()
    qtbot.addWidget(widget)
    target = TargetTimedEvent()
    event = RepeatTimedEvent(widget, target.method, 3, 10)
    event.start()

    qtbot.waitUntil(lambda: m.assert_any_call(0))
    qtbot.waitUntil(lambda: m.assert_any_call(1))
    qtbot.waitUntil(lambda: m.assert_any_call(2))
