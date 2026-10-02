from dataclasses import dataclass

from PySide6.QtWidgets import QCheckBox, QFormLayout, QHBoxLayout, QLabel, QRadioButton, QSpinBox, QVBoxLayout, QWidget

from buildnotifylib.core.settings import SortKey
from buildnotifylib.ui.widgets.forms import add_row, section


@dataclass(frozen=True)
class MiscChoices:
    interval_seconds: int
    show_last_build_time: bool
    show_last_build_label: bool
    symbolic_icons: bool
    sort_key: SortKey
    timeout_seconds: int


class MiscPage(QWidget):
    """The polling interval, what each menu row shows, the tray icon style and the sort order."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.interval = QSpinBox()
        self.interval.setSuffix(self.tr(" seconds"))
        self.interval.setRange(10, 3600)
        self.timeout = QSpinBox()
        self.timeout.setSuffix(self.tr(" seconds"))
        self.timeout.setRange(1, 300)
        self.show_last_build_time = QCheckBox(self.tr("Show last build time"))
        self.show_last_build_label = QCheckBox(self.tr("Show build label"))
        self.tray_colour = QRadioButton(self.tr("Colour"))
        self.tray_shapes = QRadioButton(self.tr("Shapes"))
        self.tray_colour.setChecked(True)
        self.sort_buttons = {
            SortKey.STATUS: QRadioButton(self.tr("Failing first")),
            SortKey.NAME: QRadioButton(self.tr("Name")),
            SortKey.LAST_BUILD_TIME: QRadioButton(self.tr("Last build time")),
        }
        self.sort_buttons[SortKey.STATUS].setChecked(True)

        sort_order = QVBoxLayout()
        for button in self.sort_buttons.values():
            sort_order.addWidget(button)
        layout = QVBoxLayout(self)
        layout.addLayout(self.display_form())
        layout.addWidget(section(self.tr("Sort projects"), sort_order))
        layout.addStretch()

    def display_form(self) -> QFormLayout:
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.labels = [
            add_row(form, self.tr("Check every:"), self.interval),
            add_row(form, self.tr("Give up after:"), self.timeout),
        ]
        for checkbox in (self.show_last_build_time, self.show_last_build_label):
            form.addRow("", checkbox)
        tray = QHBoxLayout()
        tray.addWidget(self.tray_colour)
        tray.addWidget(self.tray_shapes)
        tray.addStretch()
        tray_label = QLabel(self.tr("Tray icon:"))
        tray_label.setBuddy(self.tray_colour)
        form.addRow(tray_label, tray)
        return form

    def form_labels(self) -> list[str]:
        return [label.text() for label in self.labels]

    def set_value(self, choices: MiscChoices) -> None:
        self.interval.setValue(choices.interval_seconds)
        self.timeout.setValue(choices.timeout_seconds)
        self.show_last_build_time.setChecked(choices.show_last_build_time)
        self.show_last_build_label.setChecked(choices.show_last_build_label)
        self.tray_shapes.setChecked(choices.symbolic_icons)
        self.tray_colour.setChecked(not choices.symbolic_icons)
        self.sort_buttons[choices.sort_key].setChecked(True)

    def value(self) -> MiscChoices:
        return MiscChoices(
            self.interval.value(),
            self.show_last_build_time.isChecked(),
            self.show_last_build_label.isChecked(),
            self.tray_shapes.isChecked(),
            next(key for key, button in self.sort_buttons.items() if button.isChecked()),
            self.timeout.value(),
        )
