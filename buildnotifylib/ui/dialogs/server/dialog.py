import re
from dataclasses import replace
from zoneinfo import available_timezones

from PySide6 import QtGui
from PySide6.QtCore import Qt, QThreadPool, Signal
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from buildnotifylib.core.model import NONE_TIMEZONE, ServerSnapshot
from buildnotifylib.core.ports import CertificateError, Connection
from buildnotifylib.core.projects import ProjectLoader
from buildnotifylib.core.settings import ServerSettings, SourceKind
from buildnotifylib.ui.dialogs.server.auth_form import AuthForm, Credentials
from buildnotifylib.ui.dialogs.server.cctray_form import CctrayForm
from buildnotifylib.ui.dialogs.server.github_form import GithubForm, GithubSource
from buildnotifylib.ui.poller import Deadline, Fetch
from buildnotifylib.ui.widgets.forms import add_row, form_layout, section

KINDS = [SourceKind.CCTRAY, SourceKind.GITHUB]
REPOSITORY = re.compile(r"[\w.-]+/[\w.-]+")


def button_row(*buttons: QPushButton) -> QHBoxLayout:
    row = QHBoxLayout()
    row.addStretch()
    for button in buttons:
        button.setAutoDefault(False)
        row.addWidget(button)
    return row


class ServerConfigurationDialog(QDialog):
    loaded = Signal(int, ServerSnapshot)

    def __init__(
        self,
        server: ServerSettings | None,
        timeout: int,
        connection: Connection,
        parent: QWidget | None = None,
        keystore_available: bool = True,
    ):
        super().__init__(parent)
        self.connection = connection
        self.setWindowTitle(self.tr("Add Server"))
        self.pages = QStackedWidget()
        self.pages.addWidget(self.source_page())
        self.pages.addWidget(self.projects_page())
        QVBoxLayout(self).addWidget(self.pages)

        self.timeout = timeout
        self.projects_list = QtGui.QStandardItem(self.tr("All"))
        self.timezone.addItems([NONE_TIMEZONE, *sorted(available_timezones())])

        if server is not None:
            self.server = server
            self.set_value(server)
        else:
            self.server = ServerSettings("", timezone="")

        self.load_button.clicked.connect(self.fetch_data)
        self.loads = QThreadPool.globalInstance()
        self.loaded.connect(self.on_loaded)
        self.deadline = Deadline(self, self.expire)

        if not keystore_available:
            self.auth.disable_keyring()

        self.auth.authentication_type.currentIndexChanged.connect(self.auth.set_authentication_type)
        self.cctray_authentication_type = ServerSettings.AUTH_USERNAME_PASSWORD
        self.source_kind.currentIndexChanged.connect(self.switch_kind)
        self.show_kind(self.source_kind.currentIndex())
        self.back_button.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        self.skip_ssl_verification = bool(self.server.skip_ssl_verification)

    def source_page(self) -> QWidget:
        self.source_kind = QComboBox()
        self.source_kind.addItems([self.tr("cctray feed"), self.tr("GitHub Actions")])
        kind_row = form_layout()
        add_row(kind_row, self.tr("Source"), self.source_kind)
        self.github = GithubForm()
        self.cctray = CctrayForm()
        self.auth = AuthForm()
        self.timezone = QComboBox()
        self.prefix = QLineEdit()
        self.prefix.setPlaceholderText(self.tr("e.g. branch/release"))
        self.misc = form_layout()
        add_row(self.misc, self.tr("Server timezone"), self.timezone)
        add_row(self.misc, self.tr("Display prefix"), self.prefix)
        self.load_button = QPushButton(self.tr("Load"))
        self.cctray.url.returnPressed.connect(self.load_button.click)

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addLayout(kind_row)
        for widget in (self.github, self.cctray, self.auth, section(self.tr("Misc"), self.misc)):
            layout.addWidget(widget)
        layout.addStretch()
        layout.addLayout(button_row(self.load_button))
        return page

    def projects_page(self) -> QWidget:
        self.projects_view = QTreeView()
        self.projects_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.projects_view.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        label = QLabel(self.tr("Choose projects"))
        label.setBuddy(self.projects_view)
        self.back_button = QPushButton(self.tr("Back"))
        self.submit_button = QPushButton(self.tr("OK"))
        self.submit_button.clicked.connect(self.accept)

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(label)
        layout.addWidget(self.projects_view)
        layout.addLayout(button_row(self.back_button, self.submit_button))
        return page

    def set_value(self, server: ServerSettings) -> None:
        self.cctray.set_value(server.url)
        self.timezone.setCurrentIndex(max(self.timezone.findText(server.timezone), 0))
        self.prefix.setText(server.prefix)
        self.auth.set_value(Credentials(server.authentication_type, server.username, server.password))
        self.source_kind.setCurrentIndex(KINDS.index(server.kind))
        self.github.set_value(GithubSource(server.repository, server.workflow, server.branch))

    def kind(self) -> SourceKind:
        return KINDS[self.source_kind.currentIndex()]

    def show_kind(self, index: int):
        github = KINDS[index] is SourceKind.GITHUB
        self.github.setVisible(github)
        self.cctray.setVisible(not github)
        self.misc.setRowVisible(self.timezone, not github)
        self.auth.show_type(not github)
        if github:
            self.auth.show_token_field()

    def switch_kind(self, index: int):
        if KINDS[index] is SourceKind.GITHUB:
            self.cctray_authentication_type = self.auth.authentication_type.currentIndex()
            self.auth.select_silently(ServerSettings.AUTH_BEARER_TOKEN)
            self.auth.password.setText("")
        else:
            self.auth.select_silently(self.cctray_authentication_type)
            self.auth.set_authentication_type(self.cctray_authentication_type)
        self.show_kind(index)

    def fetch_data(self):
        error = self.url_error()
        if error:
            QMessageBox.critical(self, self.tr("Invalid input"), error)
            return

        self.load_button.setEnabled(False)
        config = self.get_server_config()
        self.project_loader = ProjectLoader(config, self.timeout, self.connection, apply_excludes=False)
        generation = self.deadline.begin(self.timeout)
        self.loads.start(Fetch(self.project_loader, self, "loaded", generation))

    def on_loaded(self, generation: int, response: ServerSnapshot):
        if not self.deadline.is_current(generation):
            return
        self.deadline.stop()
        self.load_data(response)

    def expire(self):
        self.deadline.invalidate()
        error = TimeoutError("no response before the load deadline")
        self.load_data(ServerSnapshot(self.project_loader.server_config.url, error=error))

    def url_error(self) -> str | None:
        if self.kind() is SourceKind.GITHUB:
            valid = REPOSITORY.fullmatch(self.github.value().repository)
            return None if valid else self.tr("Enter the repository as owner/name.")
        url = self.cctray.value()
        if "" == url:
            return self.tr("Path field cannot be empty.")
        if not url.lower().startswith(("http://", "https://")):
            return self.tr("Only http:// and https:// URLs are supported.")
        return None

    def load_data(self, response: ServerSnapshot):
        self.load_button.setEnabled(True)

        if response.unavailable:
            self.handle_errors(response)
            return

        self.pages.setCurrentIndex(1)
        projects_model = QtGui.QStandardItemModel()
        projects_model.itemChanged.connect(self.project_checked)
        projects_model.setHorizontalHeaderLabels([self.tr("Select Projects")])
        self.projects_list = QtGui.QStandardItem(self.tr("All"))
        self.projects_list.setCheckable(True)
        for project in response.projects:
            item = QtGui.QStandardItem(project.name)
            item.setCheckable(True)
            check = Qt.CheckState.Unchecked if project.name in self.server.excluded_projects else Qt.CheckState.Checked
            item.setCheckState(check)
            self.projects_list.appendRow(item)
        projects_model.appendRow(self.projects_list)
        self.projects_view.setModel(projects_model)
        self.projects_view.expandToDepth(1)
        self.projects_view.setItemsExpandable(False)
        self.projects_view.setRootIsDecorated(False)

    def qtText(self, txt: str) -> str:
        return QtGui.Qt.convertFromPlainText(txt)

    def handle_errors(self, response: ServerSnapshot):
        title = self.tr("Failed to fetch projects")
        if isinstance(response.error, CertificateError):
            reply = QMessageBox.question(
                self,
                title,
                self.tr("<b>SSL error, retry without verification?:</b> {}").format(self.qtText(str(response.error))),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.skip_ssl_verification = True
                self.fetch_data()
            return

        if response.unavailable:
            QMessageBox.critical(self, title, self.tr("<b>Error:</b> {}").format(self.qtText(str(response.error))))

    def project_checked(self, item: QStandardItem):
        if item.hasChildren():
            for index in range(item.rowCount()):
                item.child(index, 0).setCheckState(item.checkState())

    def server_url(self) -> str:
        return self.cctray.value()

    def get_server_config(self) -> ServerSettings:
        return replace(self.source_config(), muted=self.server.muted, muted_projects=list(self.server.muted_projects))

    def source_config(self) -> ServerSettings:
        children = [self.projects_list.child(i) for i in range(self.projects_list.rowCount())]
        excluded_projects = [child.text() for child in children if child.checkState() == Qt.CheckState.Unchecked]
        if self.kind() is SourceKind.GITHUB:
            return self.github_config(excluded_projects)
        credentials = self.auth.value()
        return ServerSettings(
            self.server_url(),
            excluded_projects,
            self.timezone.currentText(),
            self.prefix.text(),
            credentials.username,
            credentials.password,
            self.skip_ssl_verification,
            credentials.authentication_type,
        )

    def github_config(self, excluded_projects: list[str]) -> ServerSettings:
        source = self.github.value()
        return ServerSettings(
            "",
            excluded_projects,
            prefix=self.prefix.text(),
            password=self.auth.password.text(),
            skip_ssl_verification=self.skip_ssl_verification,
            authentication_type=ServerSettings.AUTH_BEARER_TOKEN,
            kind=SourceKind.GITHUB,
            repository=source.repository,
            workflow=source.workflow,
            branch=source.branch,
        )

    def open(self) -> ServerSettings | None:  # type: ignore
        if self.exec() == QDialog.DialogCode.Accepted:
            return self.get_server_config()
        return None
