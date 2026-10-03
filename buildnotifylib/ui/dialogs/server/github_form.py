import re
from dataclasses import dataclass

from PySide6.QtWidgets import QGroupBox, QLineEdit, QWidget

from buildnotifylib.ui.widgets.forms import add_message, add_row, form_layout

GITHUB_URL = re.compile(
    r"(?:https?://)?(?:www\.)?github\.com/([\w.-]+)/([\w.-]+?)(?:\.git)?(?:[/?#].*)?",
    re.IGNORECASE,
)


def repository_name(text: str) -> str:
    """owner/name from a pasted GitHub URL, or the text unchanged."""
    match = GITHUB_URL.fullmatch(text.strip())
    return f"{match.group(1)}/{match.group(2)}" if match else text.strip()


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
        self.repository = self.line_edit(self.tr("owner/name or a github.com URL"))
        self.workflow = self.line_edit(self.tr("All workflows, or a file such as ci.yml"))
        self.branch = self.line_edit(self.tr("All branches"))
        layout = form_layout()
        add_row(layout, self.tr("&Repository"), self.repository)
        self.message = add_message(layout)
        add_row(layout, self.tr("&Workflow"), self.workflow)
        add_row(layout, self.tr("&Branch"), self.branch)
        self.setLayout(layout)
        self.repository.editingFinished.connect(self.tidy_repository)

    @staticmethod
    def line_edit(placeholder: str) -> QLineEdit:
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        return field

    def tidy_repository(self) -> None:
        self.repository.setText(repository_name(self.repository.text()))

    def set_value(self, source: GithubSource) -> None:
        self.repository.setText(source.repository)
        self.workflow.setText(source.workflow)
        self.branch.setText(source.branch)

    def value(self) -> GithubSource:
        repository = repository_name(self.repository.text())
        return GithubSource(repository, self.workflow.text().strip(), self.branch.text().strip())
