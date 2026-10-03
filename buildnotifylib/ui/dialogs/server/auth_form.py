from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QGroupBox, QLineEdit, QWidget

from buildnotifylib.core.settings import ServerSettings
from buildnotifylib.ui.widgets.forms import add_message, add_row, form_layout


@dataclass(frozen=True)
class Credentials:
    authentication_type: int = ServerSettings.AUTH_USERNAME_PASSWORD
    username: str = ""
    password: str = ""


NONE, PASSWORD, TOKEN = 0, 1, 2
TOKEN_URL = "https://github.com/settings/personal-access-tokens/new"
STORED_TYPE = {NONE: ServerSettings.AUTH_USERNAME_PASSWORD, PASSWORD: ServerSettings.AUTH_USERNAME_PASSWORD}
STORED_TYPE[TOKEN] = ServerSettings.AUTH_BEARER_TOKEN


def mode_of(credentials: Credentials) -> int:
    if credentials.authentication_type == ServerSettings.AUTH_BEARER_TOKEN:
        return TOKEN
    return PASSWORD if credentials.username else NONE


class AuthForm(QGroupBox):
    """How a source signs in: None, a username and password, or a token."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setTitle(self.tr("Authentication"))
        self.authentication_type = QComboBox()
        self.authentication_type.addItems([self.tr("None"), self.tr("Username and password"), self.tr("Token")])
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.form = form_layout()
        add_row(self.form, self.tr("Sign &in"), self.authentication_type)
        self.username_label = add_row(self.form, self.tr("&Username"), self.username)
        self.password_label = add_row(self.form, self.tr("&Password"), self.password)
        self.message = add_message(self.form)
        self.token_help = add_message(self.form)
        self.token_help.setTextFormat(Qt.TextFormat.RichText)
        self.token_help.setOpenExternalLinks(True)
        self.setLayout(self.form)
        self.show_mode(NONE)
        self.authentication_type.currentIndexChanged.connect(self.set_authentication_type)

    def set_value(self, credentials: Credentials) -> None:
        self.username.setText(credentials.username)
        self.password.setText(credentials.password)
        mode = mode_of(credentials)
        self.select_silently(mode)
        self.show_mode(mode)

    def value(self) -> Credentials:
        mode = self.authentication_type.currentIndex()
        if mode == NONE:
            return Credentials(STORED_TYPE[NONE], "", "")
        return Credentials(STORED_TYPE[mode], self.username.text(), self.password.text())

    def select_silently(self, index: int) -> None:
        self.authentication_type.blockSignals(True)
        self.authentication_type.setCurrentIndex(index)
        self.authentication_type.blockSignals(False)

    def show_mode(self, mode: int) -> None:
        self.token_help.clear_message()
        self.form.setRowVisible(self.username, mode == PASSWORD)
        self.form.setRowVisible(self.password, mode != NONE)
        if mode == TOKEN:
            self.password_label.setText(self.tr("B&earer token"))
            self.password.setPlaceholderText(self.tr("Do not include the 'Bearer' keyword"))
        else:
            self.password_label.setText(self.tr("&Password"))
            self.password.setPlaceholderText("")

    def show_type(self, visible: bool) -> None:
        self.form.setRowVisible(self.authentication_type, visible)

    def show_token_field(self) -> None:
        self.username.setText("")
        self.show_mode(TOKEN)
        self.password_label.setText(self.tr("&Token"))
        self.password.setPlaceholderText(self.tr("Optional for public repositories"))
        self.token_help.show_hint(
            self.tr(
                '<a href="{}">Create a token</a>. It needs Actions: read.'
                " Without a token GitHub allows 60 requests an hour."
            ).format(TOKEN_URL)
        )

    def set_authentication_type(self, index: int) -> None:
        if index not in STORED_TYPE:
            raise NotImplementedError(f'Unsupported value: "{index}". An implementation is missing.')
        self.username.setText("")
        self.password.setText("")
        self.show_mode(index)

    def disable_keyring(self) -> None:
        self.setTitle(self.tr("Authentication (keyring dependency missing)"))
        self.message.show_error(
            self.tr("Credentials can't be stored without a system keyring. Install the 'keyring' package to sign in.")
        )
        for widget in (self.authentication_type, self.username, self.password):
            widget.setEnabled(False)
