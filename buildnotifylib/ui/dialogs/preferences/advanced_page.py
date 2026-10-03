from dataclasses import dataclass

from PySide6.QtWidgets import QFormLayout, QSpinBox, QVBoxLayout, QWidget

from buildnotifylib.ui.widgets.forms import add_row


@dataclass(frozen=True)
class AdvancedChoices:
    interval_seconds: int
    timeout_seconds: int


class AdvancedPage(QWidget):
    """How often servers are polled and how long a request may take."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.interval = QSpinBox()
        self.interval.setSuffix(self.tr(" seconds"))
        self.interval.setRange(10, 3600)
        self.timeout = QSpinBox()
        self.timeout.setSuffix(self.tr(" seconds"))
        self.timeout.setRange(1, 300)

        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.labels = [
            add_row(form, self.tr("&Check every:"), self.interval),
            add_row(form, self.tr("&Give up after:"), self.timeout),
        ]
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addStretch()

    def form_labels(self) -> list[str]:
        return [label.text() for label in self.labels]

    def set_value(self, choices: AdvancedChoices) -> None:
        self.interval.setValue(choices.interval_seconds)
        self.timeout.setValue(choices.timeout_seconds)

    def value(self) -> AdvancedChoices:
        return AdvancedChoices(self.interval.value(), self.timeout.value())
