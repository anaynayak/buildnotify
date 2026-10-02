import pytest
from PySide6.QtWidgets import QLineEdit, QWidget

from buildnotifylib.ui.widgets.forms import ERROR_COLOUR, add_message, add_row, form_layout, section


@pytest.mark.functional
def test_should_label_a_row_with_its_field_as_buddy(qtbot):
    layout = form_layout()
    field = QLineEdit()

    label = add_row(layout, "Repository", field)

    assert label.text() == "Repository"
    assert label.buddy() is field
    assert layout.rowCount() == 1


@pytest.mark.functional
def test_should_title_a_section(qtbot):
    box = section("Misc", form_layout())
    qtbot.addWidget(box)

    assert box.title() == "Misc"


@pytest.mark.functional
def test_should_hide_the_message_until_there_is_something_to_say(qtbot):
    host = QWidget()
    layout = form_layout()
    host.setLayout(layout)
    qtbot.addWidget(host)
    message = add_message(layout)

    assert message.isHidden()

    message.show_error("Enter the repository as owner/name.")
    assert not message.isHidden()
    assert message.error
    assert message.palette().color(message.foregroundRole()) == ERROR_COLOUR

    message.show_hint("Usually ends in cctray.xml")
    assert not message.error
    assert message.text() == "Usually ends in cctray.xml"

    message.clear_message()
    assert message.isHidden()
    assert message.text() == ""
