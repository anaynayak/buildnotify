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
    QDialogButtonBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from buildnotifylib.core.errors import host, summarize
from buildnotifylib.core.model import NONE_TIMEZONE, ServerSnapshot
from buildnotifylib.core.ports import CertificateError, Connection
from buildnotifylib.core.projects import ProjectLoader
from buildnotifylib.core.settings import ServerSettings, SourceKind
from buildnotifylib.ui.dialogs.server.auth_form import NONE, TOKEN, AuthForm, Credentials
from buildnotifylib.ui.dialogs.server.cctray_form import CctrayForm
from buildnotifylib.ui.dialogs.server.github_form import GithubForm, GithubSource
from buildnotifylib.ui.poller import Deadline, Fetch
from buildnotifylib.ui.widgets.forms import MessageLabel, add_row, form_layout, section

KINDS = [SourceKind.CCTRAY, SourceKind.GITHUB]
REPOSITORY = re.compile(r"[\w.-]+/[\w.-]+")


def server_name(server: ServerSettings) -> str:
    if server.prefix:
        return server.prefix
    return server.repository if server.kind is SourceKind.GITHUB else host(server.url)


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
        self.unverified_host: str | None = None
        layout = QVBoxLayout(self)
        layout.addWidget(self.source_section())
        layout.addLayout(self.test_row())
        layout.addLayout(self.certificate_row())
        layout.addWidget(self.projects_section())
        layout.addWidget(self.buttons())

        self.timeout = timeout
        self.projects_list = QtGui.QStandardItem(self.tr("All"))
        self.projects_loaded = False
        self.syncing = False
        self.loads = QThreadPool.globalInstance()
        self.deadline = Deadline(self, self.expire)
        self.timezone.addItems([NONE_TIMEZONE, *sorted(available_timezones())])

        if server is not None:
            self.server = server
            self.set_value(server)
        else:
            self.server = ServerSettings("", timezone="")
        self.setWindowTitle(self.title(server))

        self.test_button.clicked.connect(self.fetch_data)
        self.loaded.connect(self.on_loaded)

        if not keystore_available:
            self.auth.disable_keyring()

        self.cctray_authentication_type = NONE
        self.source_kind.currentIndexChanged.connect(self.switch_kind)
        self.show_kind(self.source_kind.currentIndex())
        self.refresh_validity()
        self.unverified_host = self.source_host() if self.server.skip_ssl_verification else None
        self.refresh_certificate_row()

    def source_section(self) -> QWidget:
        self.source_kind = QComboBox()
        self.source_kind.addItems([self.tr("cctray feed"), self.tr("GitHub Actions")])
        kind_row = form_layout()
        add_row(kind_row, self.tr("S&ource"), self.source_kind)
        self.github = GithubForm()
        self.cctray = CctrayForm()
        self.auth = AuthForm()
        self.timezone = QComboBox()
        self.prefix = QLineEdit()
        self.prefix.setPlaceholderText(self.tr("e.g. branch/release"))
        self.misc = form_layout()
        add_row(self.misc, self.tr("Ser&ver timezone"), self.timezone)
        add_row(self.misc, self.tr("&Display prefix"), self.prefix)
        for field in (self.cctray.url, self.github.repository):
            field.editingFinished.connect(self.validate)
            field.textChanged.connect(self.refresh_validity)
            field.textChanged.connect(self.forget_test)
            field.textChanged.connect(self.refresh_certificate_row)

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(kind_row)
        for widget in (self.github, self.cctray, self.auth, section(self.tr("Misc"), self.misc)):
            layout.addWidget(widget)
        return page

    def test_row(self) -> QHBoxLayout:
        self.test_button = QPushButton(self.tr("Test &connection"))
        self.test_button.setAutoDefault(False)
        self.test_status = MessageLabel()
        row = QHBoxLayout()
        row.addWidget(self.test_button)
        row.addWidget(self.test_status, 1)
        row.addStretch()
        return row

    def certificate_row(self) -> QHBoxLayout:
        self.certificate_status = MessageLabel()
        self.certificate_undo = QPushButton(self.tr("Tur&n checks back on"))
        self.certificate_undo.setAutoDefault(False)
        self.certificate_undo.clicked.connect(self.restore_certificate_checks)
        row = QHBoxLayout()
        row.addWidget(self.certificate_status, 1)
        row.addWidget(self.certificate_undo)
        return row

    def refresh_certificate_row(self) -> None:
        unchecked = self.unverified_host is not None and self.skip_ssl_verification()
        if unchecked:
            self.certificate_status.show_error(self.tr("Certificate checks off for {}").format(self.source_host()))
        else:
            self.certificate_status.clear_message()
        self.certificate_undo.setVisible(unchecked)

    def restore_certificate_checks(self) -> None:
        self.unverified_host = None
        self.refresh_certificate_row()
        self.forget_test()

    def projects_section(self) -> QWidget:
        self.projects_view = QTreeView()
        self.projects_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.projects_view.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.projects_view.setHeaderHidden(True)
        self.projects_view.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.projects_filter = QLineEdit()
        self.projects_filter.setPlaceholderText(self.tr("Filter projects"))
        self.projects_filter.setClearButtonEnabled(True)
        self.projects_filter.textChanged.connect(self.apply_filter)
        self.projects_hint = MessageLabel()
        self.projects_hint.show_hint(self.tr("All projects are included. Test the connection to choose projects."))
        layout = QVBoxLayout()
        layout.addWidget(self.projects_hint)
        layout.addWidget(self.projects_filter)
        layout.addWidget(self.projects_view)
        self.projects_note = MessageLabel()
        self.projects_note.show_hint(self.tr("New projects in this feed are included automatically."))
        layout.addWidget(self.projects_note)
        self.show_picker(False)
        return section(self.tr("Projects"), layout)

    def buttons(self) -> QDialogButtonBox:
        box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Save)
        self.save_button = box.button(QDialogButtonBox.StandardButton.Save)
        self.save_button.setText(self.tr("&Save"))
        self.cancel_button = box.button(QDialogButtonBox.StandardButton.Cancel)
        box.accepted.connect(self.save)
        box.rejected.connect(self.reject)
        return box

    def set_value(self, server: ServerSettings) -> None:
        self.cctray.set_value(server.url)
        self.timezone.setCurrentIndex(max(self.timezone.findText(server.timezone), 0))
        self.prefix.setText(server.prefix)
        self.auth.set_value(Credentials(server.authentication_type, server.username, server.password))
        self.source_kind.setCurrentIndex(KINDS.index(server.kind))
        self.github.set_value(GithubSource(server.repository, server.workflow, server.branch))

    def title(self, server: ServerSettings | None) -> str:
        if server is None:
            return self.tr("Add server")
        return self.tr("Edit server - {}").format(server_name(server))

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
            self.auth.select_silently(TOKEN)
            self.auth.password.setText("")
        else:
            self.auth.select_silently(self.cctray_authentication_type)
            self.auth.set_authentication_type(self.cctray_authentication_type)
        self.show_kind(index)
        self.refresh_validity()
        self.forget_test()

    def forget_test(self) -> None:
        self.deadline.invalidate()
        self.deadline.stop()
        self.test_button.setEnabled(True)
        self.test_status.clear_message()
        self.projects_loaded = False
        self.show_picker(False)
        self.projects_hint.show()

    def done(self, result: int) -> None:
        self.deadline.invalidate()
        self.deadline.stop()
        super().done(result)

    def save(self) -> None:
        if self.validate():
            self.accept()

    def fetch_data(self):
        if not self.validate():
            return

        self.test_button.setEnabled(False)
        self.test_status.show_hint(self.tr("Connecting..."))
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

    def validate(self) -> bool:
        error = self.url_error()
        if error:
            self.source_message().show_error(error)
        else:
            self.source_message().clear_message()
        return error is None

    def refresh_validity(self) -> None:
        valid = self.url_error() is None
        self.save_button.setEnabled(valid)
        if valid:
            self.source_message().clear_message()

    def source_message(self) -> MessageLabel:
        return self.github.message if self.kind() is SourceKind.GITHUB else self.cctray.message

    def url_error(self) -> str | None:
        if self.kind() is SourceKind.GITHUB:
            valid = REPOSITORY.fullmatch(self.github.value().repository)
            return None if valid else self.tr("Enter the repository as owner/name.")
        url = self.cctray.value()
        if "" == url:
            return self.tr("Enter the feed URL.")
        if not url.lower().startswith(("http://", "https://")):
            return self.tr("Only http:// and https:// URLs are supported.")
        return None

    def load_data(self, response: ServerSnapshot):
        self.test_button.setEnabled(True)
        if response.unavailable:
            self.handle_errors(response)
            return
        self.test_status.show_hint(self.found(len(response.projects)))
        self.show_projects(response)

    def found(self, count: int) -> str:
        if count == 1:
            return self.tr("OK - 1 project found")
        return self.tr("OK - {} projects found").format(count)

    def show_projects(self, response: ServerSnapshot) -> None:
        projects_model = QtGui.QStandardItemModel()
        projects_model.itemChanged.connect(self.project_checked)
        self.projects_list = QtGui.QStandardItem()
        self.projects_list.setCheckable(True)
        for project in response.projects:
            item = QtGui.QStandardItem(project.name)
            item.setCheckable(True)
            item.setToolTip(project.name)
            check = Qt.CheckState.Unchecked if project.name in self.server.excluded_projects else Qt.CheckState.Checked
            item.setCheckState(check)
            self.projects_list.appendRow(item)
        projects_model.appendRow(self.projects_list)
        self.syncing = True
        self.sync_all_box()
        self.syncing = False
        self.projects_view.setModel(projects_model)
        self.projects_view.expandToDepth(1)
        self.projects_view.setItemsExpandable(False)
        self.projects_view.setRootIsDecorated(False)
        self.projects_loaded = True
        self.projects_hint.hide()
        self.show_picker(True)
        self.apply_filter()

    def header(self) -> str:
        total = self.projects_list.rowCount()
        children = (self.projects_list.child(row, 0) for row in range(total))
        included = sum(1 for child in children if child.checkState() == Qt.CheckState.Checked)
        return self.tr("All ({} of {})").format(included, total)

    def show_picker(self, visible: bool) -> None:
        self.projects_view.setVisible(visible)
        self.projects_filter.setVisible(visible)
        self.projects_note.setVisible(visible)

    def apply_filter(self) -> None:
        needle = self.projects_filter.text().strip().lower()
        root = self.projects_list.index()
        for row in range(self.projects_list.rowCount()):
            name = self.projects_list.child(row, 0).text().lower()
            self.projects_view.setRowHidden(row, root, needle not in name)

    def qtText(self, txt: str) -> str:
        return QtGui.Qt.convertFromPlainText(txt)

    def handle_errors(self, response: ServerSnapshot):
        error = response.error
        assert error is not None
        self.test_status.show_error(summarize(error))
        if isinstance(error, CertificateError) and self.retry_without_verification(error):
            self.unverified_host = self.source_host()
            self.refresh_certificate_row()
            self.fetch_data()

    def retry_without_verification(self, error: Exception) -> bool:
        reply = QMessageBox.question(
            self,
            self.tr("Failed to fetch projects"),
            self.tr(
                "<b>The certificate for {} isn't trusted.</b> Connect anyway?"
                " This turns off certificate checks for this server.<br>{}"
            ).format(self.source_host(), self.qtText(str(error))),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes

    def project_checked(self, item: QStandardItem):
        if self.syncing:
            return
        self.syncing = True
        try:
            if item is self.projects_list:
                self.check_visible(item.checkState())
            self.sync_all_box()
        finally:
            self.syncing = False

    def check_visible(self, state: Qt.CheckState) -> None:
        if state == Qt.CheckState.PartiallyChecked:
            return
        for row in range(self.projects_list.rowCount()):
            if not self.projects_view.isRowHidden(row, self.projects_list.index()):
                self.projects_list.child(row, 0).setCheckState(state)

    def sync_all_box(self) -> None:
        states = {self.projects_list.child(row, 0).checkState() for row in range(self.projects_list.rowCount())}
        if states == {Qt.CheckState.Checked}:
            state = Qt.CheckState.Checked
        elif states <= {Qt.CheckState.Unchecked}:
            state = Qt.CheckState.Unchecked
        else:
            state = Qt.CheckState.PartiallyChecked
        self.projects_list.setCheckState(state)
        self.projects_list.setText(self.header())

    def server_url(self) -> str:
        return self.cctray.value()

    def source_host(self) -> str:
        return "" if self.kind() is SourceKind.GITHUB else host(self.server_url())

    def skip_ssl_verification(self) -> bool:
        return self.unverified_host == self.source_host()

    def get_server_config(self) -> ServerSettings:
        return replace(self.source_config(), muted=self.server.muted, muted_projects=list(self.server.muted_projects))

    def excluded_projects(self) -> list[str]:
        if not self.projects_loaded:
            return list(self.server.excluded_projects)
        children = [self.projects_list.child(i) for i in range(self.projects_list.rowCount())]
        return [child.text() for child in children if child.checkState() == Qt.CheckState.Unchecked]

    def source_config(self) -> ServerSettings:
        excluded_projects = self.excluded_projects()
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
            self.skip_ssl_verification(),
            credentials.authentication_type,
        )

    def github_config(self, excluded_projects: list[str]) -> ServerSettings:
        source = self.github.value()
        return ServerSettings(
            "",
            excluded_projects,
            prefix=self.prefix.text(),
            password=self.auth.password.text(),
            skip_ssl_verification=self.skip_ssl_verification(),
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
