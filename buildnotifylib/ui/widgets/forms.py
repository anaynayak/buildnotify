"""Helpers for building forms in code: labelled rows, titled sections and an inline message."""

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QFormLayout, QGroupBox, QLabel, QLayout, QWidget

ERROR_COLOUR = QColor("#c62828")


def form_layout() -> QFormLayout:
    layout = QFormLayout()
    layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
    return layout


def add_row(layout: QFormLayout, text: str, field: QWidget) -> QLabel:
    label = QLabel(text)
    label.setBuddy(field)
    layout.addRow(label, field)
    return label


def add_message(layout: QFormLayout) -> "MessageLabel":
    message = MessageLabel()
    layout.addRow("", message)
    return message


def section(title: str, layout: QLayout) -> QGroupBox:
    box = QGroupBox(title)
    box.setLayout(layout)
    return box


class MessageLabel(QLabel):
    """A hint or error shown under a field, hidden while there is nothing to say."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWordWrap(True)
        self.error = False
        self.hide()

    def show_hint(self, text: str) -> None:
        self.show_message(text, error=False)

    def show_error(self, text: str) -> None:
        self.show_message(text, error=True)

    def clear_message(self) -> None:
        self.error = False
        self.setText("")
        self.hide()

    def show_message(self, text: str, error: bool) -> None:
        self.error = error
        palette = self.palette()
        colour = ERROR_COLOUR if error else palette.color(QPalette.ColorRole.PlaceholderText)
        palette.setColor(QPalette.ColorRole.WindowText, colour)
        self.setPalette(palette)
        self.setText(text)
        self.show()
