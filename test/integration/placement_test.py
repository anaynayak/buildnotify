from PySide6.QtCore import QPoint, QRect
from PySide6.QtWidgets import QWidget

from buildnotifylib.ui.widgets import placement


class FakeScreen:
    def __init__(self, available: QRect):
        self.available = available

    def availableGeometry(self) -> QRect:
        return self.available


def sized_widget(qtbot, width=200, height=100) -> QWidget:
    widget = QWidget()
    qtbot.addWidget(widget)
    widget.setFixedSize(width, height)
    return widget


def patch(mocker, under_cursor, primary):
    mocker.patch.object(placement.QCursor, "pos", return_value=QPoint(2500, 300))
    mocker.patch.object(placement.QGuiApplication, "screenAt", return_value=under_cursor)
    mocker.patch.object(placement.QGuiApplication, "primaryScreen", return_value=primary)


def test_should_centre_on_the_screen_under_the_cursor(qtbot, mocker):
    other = FakeScreen(QRect(1920, 0, 1000, 800))
    patch(mocker, other, FakeScreen(QRect(0, 0, 1920, 1080)))
    widget = sized_widget(qtbot)

    placement.centre_on_cursor_screen(widget)

    assert widget.pos() == QPoint(1920 + 400, 350)


def test_should_fall_back_to_the_primary_screen(qtbot, mocker):
    patch(mocker, None, FakeScreen(QRect(0, 0, 1000, 800)))
    widget = sized_widget(qtbot)

    placement.centre_on_cursor_screen(widget)

    assert widget.pos() == QPoint(400, 350)


def test_should_stay_inside_the_available_area(qtbot, mocker):
    patch(mocker, FakeScreen(QRect(0, 25, 300, 275)), None)
    widget = sized_widget(qtbot, 400, 500)

    placement.centre_on_cursor_screen(widget)

    assert widget.pos() == QPoint(0, 25)


def test_should_do_nothing_without_any_screen(qtbot, mocker):
    patch(mocker, None, None)
    widget = sized_widget(qtbot)
    before = widget.pos()

    placement.centre_on_cursor_screen(widget)

    assert widget.pos() == before
