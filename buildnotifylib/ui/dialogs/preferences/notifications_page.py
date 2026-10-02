from dataclasses import dataclass

from PySide6.QtWidgets import QCheckBox, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from buildnotifylib.ui.widgets.forms import section


@dataclass(frozen=True)
class NotificationChoices:
    events: dict[str, bool]
    script: str
    script_enabled: bool


class NotificationsPage(QWidget):
    """Which build events notify, and the custom notification script."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.successful_builds = QCheckBox(self.tr("successful builds"))
        self.broken_builds = QCheckBox(self.tr("broken builds"))
        self.fixed_builds = QCheckBox(self.tr("fixed builds"))
        self.still_failing_builds = QCheckBox(self.tr("still failing builds"))
        self.connectivity_issues = QCheckBox(self.tr("connectivity issues"))
        self.events = dict(
            successfulBuild=self.successful_builds,
            brokenBuild=self.broken_builds,
            fixedBuild=self.fixed_builds,
            stillFailingBuild=self.still_failing_builds,
            connectivityIssues=self.connectivity_issues,
        )
        self.script_enabled = QCheckBox(self.tr("Execute script for notifications"))
        self.script = QLineEdit()
        self.script.setEnabled(False)
        self.script.setToolTip(
            self.tr(
                "The script gets the build status and projects in the BUILDNOTIFY_STATUS and BUILDNOTIFY_PROJECTS"
                " environment variables. #status# and #projects# are also replaced, quoted, except on Windows,"
                " where a script using them is not run."
            )
        )
        self.script_enabled.toggled.connect(self.script.setEnabled)

        layout = QVBoxLayout(self)
        layout.addWidget(section(self.tr("Notification settings"), self.events_grid()))
        layout.addWidget(section(self.tr("Custom notifications"), self.script_layout()))
        layout.addStretch()

    def events_grid(self) -> QGridLayout:
        grid = QGridLayout()
        for position, checkbox in enumerate(self.events.values()):
            grid.addWidget(checkbox, position // 2, position % 2)
        return grid

    def script_layout(self) -> QVBoxLayout:
        label = QLabel(self.tr("Script"))
        label.setBuddy(self.script)
        row = QHBoxLayout()
        row.addWidget(label)
        row.addWidget(self.script)
        layout = QVBoxLayout()
        layout.addWidget(self.script_enabled)
        layout.addLayout(row)
        return layout

    def set_value(self, choices: NotificationChoices) -> None:
        for key, checkbox in self.events.items():
            checkbox.setChecked(choices.events[key])
        self.script_enabled.setChecked(choices.script_enabled)
        self.script.setText(choices.script)

    def value(self) -> NotificationChoices:
        events = {key: checkbox.isChecked() for key, checkbox in self.events.items()}
        return NotificationChoices(events, self.script.text(), self.script_enabled.isChecked())
