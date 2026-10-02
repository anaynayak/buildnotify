from dataclasses import dataclass

from PySide6.QtWidgets import QCheckBox, QFormLayout, QRadioButton, QSpinBox, QVBoxLayout, QWidget

from buildnotifylib.core.settings import SortKey
from buildnotifylib.ui.widgets.forms import add_row, section


@dataclass(frozen=True)
class MiscChoices:
    interval_seconds: int
    show_last_build_time: bool
    show_last_build_label: bool
    symbolic_icons: bool
    sort_key: SortKey


class MiscPage(QWidget):
    """The polling interval, what each menu row shows, the tray icon style and the sort order."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.interval = QSpinBox()
        self.interval.setSuffix(self.tr(" seconds"))
        self.interval.setRange(10, 3600)
        self.show_last_build_time = QCheckBox(self.tr("show last build time for each project"))
        self.show_last_build_label = QCheckBox(self.tr("show last build label for each project"))
        self.symbolic_icons = QCheckBox(self.tr("use symbolic tray icons (shapes instead of coloured squares)"))
        self.sort_buttons = {
            SortKey.STATUS: QRadioButton(self.tr("Failing first")),
            SortKey.NAME: QRadioButton(self.tr("Sort builds by name")),
            SortKey.LAST_BUILD_TIME: QRadioButton(self.tr("Sort builds by last build time")),
        }
        self.sort_buttons[SortKey.STATUS].setChecked(True)

        sort_order = QVBoxLayout()
        for button in self.sort_buttons.values():
            sort_order.addWidget(button)
        layout = QVBoxLayout(self)
        layout.addLayout(self.display_form())
        layout.addWidget(section(self.tr("Build Sort order"), sort_order))
        layout.addStretch()

    def display_form(self) -> QFormLayout:
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        add_row(form, self.tr("Server polling interval"), self.interval)
        for checkbox in (self.show_last_build_time, self.show_last_build_label, self.symbolic_icons):
            form.addRow("", checkbox)
        return form

    def set_value(self, choices: MiscChoices) -> None:
        self.interval.setValue(choices.interval_seconds)
        self.show_last_build_time.setChecked(choices.show_last_build_time)
        self.show_last_build_label.setChecked(choices.show_last_build_label)
        self.symbolic_icons.setChecked(choices.symbolic_icons)
        self.sort_buttons[choices.sort_key].setChecked(True)

    def value(self) -> MiscChoices:
        return MiscChoices(
            self.interval.value(),
            self.show_last_build_time.isChecked(),
            self.show_last_build_label.isChecked(),
            self.symbolic_icons.isChecked(),
            next(key for key, button in self.sort_buttons.items() if button.isChecked()),
        )
