from dataclasses import dataclass

from PySide6.QtWidgets import QGroupBox, QLineEdit, QWidget

from buildnotifylib.ui.widgets.forms import add_message, add_row, form_layout


@dataclass(frozen=True)
class GithubSource:
    repository: str = ""
    workflow: str = ""
    branch: str = ""


class GithubForm(QGroupBox):
    """The repository, workflow and branch of a GitHub Actions source."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setTitle(self.tr("GitHub repository"))
        self.repository = self.line_edit(self.tr("owner/name"))
        self.workflow = self.line_edit(self.tr("All workflows, or a file such as ci.yml"))
        self.branch = self.line_edit(self.tr("All branches"))
        layout = form_layout()
        add_row(layout, self.tr("Repository"), self.repository)
        self.message = add_message(layout)
        add_row(layout, self.tr("Workflow"), self.workflow)
        add_row(layout, self.tr("Branch"), self.branch)
        self.setLayout(layout)

    @staticmethod
    def line_edit(placeholder: str) -> QLineEdit:
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        return field

    def set_value(self, source: GithubSource) -> None:
        self.repository.setText(source.repository)
        self.workflow.setText(source.workflow)
        self.branch.setText(source.branch)

    def value(self) -> GithubSource:
        return GithubSource(self.repository.text().strip(), self.workflow.text().strip(), self.branch.text().strip())
