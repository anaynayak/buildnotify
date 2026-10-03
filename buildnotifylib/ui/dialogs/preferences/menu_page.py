from dataclasses import dataclass

from PySide6.QtWidgets import QCheckBox, QFormLayout, QHBoxLayout, QLabel, QRadioButton, QVBoxLayout, QWidget

from buildnotifylib.core.settings import SortKey
from buildnotifylib.ui.widgets.forms import section


@dataclass(frozen=True)
class MenuChoices:
    show_last_build_time: bool
    show_last_build_label: bool
    symbolic_icons: bool
    sort_key: SortKey


class MenuPage(QWidget):
    """What each menu row shows, the tray icon style and the sort order."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.show_last_build_time = QCheckBox(self.tr("Show last build &time"))
        self.show_last_build_label = QCheckBox(self.tr("Show build &label"))
        self.tray_colour = QRadioButton(self.tr("&Colour"))
        self.tray_shapes = QRadioButton(self.tr("S&hapes"))
        self.tray_colour.setChecked(True)
        self.sort_buttons = {
            SortKey.STATUS: QRadioButton(self.tr("&Failing first")),
            SortKey.NAME: QRadioButton(self.tr("Nam&e")),
            SortKey.LAST_BUILD_TIME: QRadioButton(self.tr("Last &build time")),
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
        for checkbox in (self.show_last_build_time, self.show_last_build_label):
            form.addRow("", checkbox)
        tray = QHBoxLayout()
        tray.addWidget(self.tray_colour)
        tray.addWidget(self.tray_shapes)
        tray.addStretch()
        tray_label = QLabel(self.tr("Tra&y icon:"))
        tray_label.setBuddy(self.tray_colour)
        form.addRow(tray_label, tray)
        return form

    def set_value(self, choices: MenuChoices) -> None:
        self.show_last_build_time.setChecked(choices.show_last_build_time)
        self.show_last_build_label.setChecked(choices.show_last_build_label)
        self.tray_shapes.setChecked(choices.symbolic_icons)
        self.tray_colour.setChecked(not choices.symbolic_icons)
        self.sort_buttons[choices.sort_key].setChecked(True)

    def value(self) -> MenuChoices:
        return MenuChoices(
            self.show_last_build_time.isChecked(),
            self.show_last_build_label.isChecked(),
            self.tray_shapes.isChecked(),
            next(key for key, button in self.sort_buttons.items() if button.isChecked()),
        )
