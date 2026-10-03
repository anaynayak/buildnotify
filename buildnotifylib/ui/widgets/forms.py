"""Helpers for building forms in code: labelled rows, titled sections and an inline message."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QFormLayout, QGroupBox, QLabel, QLayout, QToolButton, QVBoxLayout, QWidget

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


class CollapsibleSection(QWidget):
    """A disclosure button that shows or hides the layout under it."""

    def __init__(self, title: str, content: QLayout, parent: QWidget | None = None):
        super().__init__(parent)
        self.toggle = QToolButton()
        self.toggle.setText(title)
        self.toggle.setCheckable(True)
        self.toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle.setAutoRaise(True)
        self.body = QWidget()
        self.body.setLayout(content)
        self.toggle.toggled.connect(self.set_expanded)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toggle, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.body)
        self.set_expanded(False)

    def is_expanded(self) -> bool:
        return self.toggle.isChecked()

    def set_expanded(self, expanded: bool) -> None:
        self.toggle.setChecked(expanded)
        self.toggle.setArrowType(Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow)
        self.body.setVisible(expanded)


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
